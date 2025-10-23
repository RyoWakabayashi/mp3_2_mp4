"""
Conversion Controller - Orchestrates MP3 to MP4 conversion process.
"""

from typing import List, Callable, Optional, Dict
from pathlib import Path
import threading
from queue import Queue
import time

from ..models.audio_file import AudioFile
from ..models.video_file import VideoFile
from ..models.conversion_job import ConversionJob, ConversionStatus
from ..services.ffmpeg_service import FFmpegService
from ..utils.logger import get_logger
from ..utils.error_handler import ErrorHandler, ConversionError, ErrorCode


class ConversionController:
    """Manages conversion workflow for multiple files."""
    
    def __init__(self, max_concurrent_conversions: int = 2):
        """
        Initialize conversion controller.
        
        Args:
            max_concurrent_conversions: Maximum number of simultaneous conversions
        """
        self.logger = get_logger("ConversionController")
        self.ffmpeg_service = FFmpegService()
        self.error_handler = ErrorHandler()
        
        self.max_concurrent = max_concurrent_conversions
        
        # Job management
        self._jobs: Dict[str, ConversionJob] = {}  # file_path -> ConversionJob
        self._job_queue: Queue = Queue()
        self._active_jobs: List[ConversionJob] = []
        self._is_running = False
        self._worker_thread: Optional[threading.Thread] = None
        
        # Callbacks
        self.on_job_start: Optional[Callable[[ConversionJob], None]] = None
        self.on_job_progress: Optional[Callable[[ConversionJob, float], None]] = None
        self.on_job_complete: Optional[Callable[[ConversionJob], None]] = None
        self.on_job_error: Optional[Callable[[ConversionJob, str], None]] = None
        self.on_all_complete: Optional[Callable[[int, int], None]] = None  # (success_count, error_count)
        
        # Check FFmpeg availability
        if not self.ffmpeg_service.is_available():
            self.logger.error("FFmpeg is not available")
            raise RuntimeError("FFmpeg が見つかりません。インストールしてください。")
        
        self.logger.info("Conversion controller initialized")
    
    def add_conversion(self, 
                      audio_file: AudioFile, 
                      output_path: str,
                      background_image: Optional[str] = None) -> ConversionJob:
        """
        Add a conversion job to the queue.
        
        Args:
            audio_file: AudioFile to convert
            output_path: Path for output MP4 file
            background_image: Optional path to background image
            
        Returns:
            Created ConversionJob
        """
        # Create video file spec
        video_file = VideoFile(
            file_path=output_path,
            background_image=background_image
        )
        
        # Create conversion job
        job = ConversionJob(
            audio_file=audio_file,
            video_file=video_file
        )
        
        # Store job
        self._jobs[audio_file.file_path] = job
        
        # Add to queue
        self._job_queue.put(job)
        
        self.logger.info(f"Added conversion job: {Path(audio_file.file_path).name}")
        
        return job
    
    def start_conversions(self) -> None:
        """Start processing conversion queue."""
        if self._is_running:
            self.logger.warning("Conversions already running")
            return
        
        if self._job_queue.empty():
            self.logger.warning("No jobs in queue")
            return
        
        self._is_running = True
        
        # Start worker thread
        self._worker_thread = threading.Thread(
            target=self._process_queue,
            daemon=True
        )
        self._worker_thread.start()
        
        self.logger.info("Started conversion processing")
    
    def cancel_conversion(self, file_path: str) -> bool:
        """
        Cancel a specific conversion job.
        
        Args:
            file_path: Path of the audio file to cancel
            
        Returns:
            True if job was cancelled
        """
        if file_path not in self._jobs:
            return False
        
        job = self._jobs[file_path]
        
        if job.is_running():
            job.cancel()
            self.logger.info(f"Cancelled conversion: {Path(file_path).name}")
            return True
        
        return False
    
    def cancel_all_conversions(self) -> None:
        """Cancel all active and queued conversions."""
        self.logger.info("Cancelling all conversions")
        
        # Stop processing
        self._is_running = False
        
        # Cancel active jobs
        for job in self._active_jobs:
            if job.is_running():
                job.cancel()
        
        # Clear queue
        while not self._job_queue.empty():
            try:
                job = self._job_queue.get_nowait()
                if job.status == ConversionStatus.PENDING:
                    job.fail("キャンセルされました")
            except:
                break
    
    def get_job(self, file_path: str) -> Optional[ConversionJob]:
        """Get conversion job for a file."""
        return self._jobs.get(file_path)
    
    def get_all_jobs(self) -> List[ConversionJob]:
        """Get all conversion jobs."""
        return list(self._jobs.values())
    
    def get_statistics(self) -> Dict[str, int]:
        """Get conversion statistics."""
        jobs = self.get_all_jobs()
        
        return {
            'total': len(jobs),
            'pending': len([j for j in jobs if j.status == ConversionStatus.PENDING]),
            'running': len([j for j in jobs if j.status == ConversionStatus.RUNNING]),
            'completed': len([j for j in jobs if j.status == ConversionStatus.COMPLETED]),
            'failed': len([j for j in jobs if j.status == ConversionStatus.FAILED]),
            'cancelled': len([j for j in jobs if j.status == ConversionStatus.CANCELLED])
        }
    
    def _process_queue(self) -> None:
        """Worker thread to process conversion queue."""
        self.logger.info("Conversion queue processing started")
        
        while self._is_running:
            # Remove completed jobs from active list
            self._active_jobs = [j for j in self._active_jobs if j.is_running()]
            
            # Start new jobs if slots available
            while len(self._active_jobs) < self.max_concurrent and not self._job_queue.empty():
                try:
                    job = self._job_queue.get_nowait()
                    
                    # Start conversion in separate thread
                    thread = threading.Thread(
                        target=self._execute_conversion,
                        args=(job,),
                        daemon=True
                    )
                    thread.start()
                    
                    self._active_jobs.append(job)
                    
                except:
                    break
            
            # Check if all jobs are done
            if self._job_queue.empty() and len(self._active_jobs) == 0:
                self._on_queue_complete()
                break
            
            # Sleep briefly
            time.sleep(0.1)
        
        self.logger.info("Conversion queue processing stopped")
    
    def _execute_conversion(self, job: ConversionJob) -> None:
        """Execute a single conversion job."""
        try:
            self.logger.info(f"Starting conversion: {job.audio_file.filename}")
            
            # Update status
            job.start()
            
            # Notify start
            if self.on_job_start:
                self.on_job_start(job)
            
            # Progress callback
            def progress_callback(progress: float):
                job.update_progress(progress)
                if self.on_job_progress:
                    self.on_job_progress(job, progress)
            
            # Perform conversion
            self.ffmpeg_service.convert_to_mp4(
                audio_file=job.audio_file,
                video_file=job.video_file,
                progress_callback=progress_callback
            )
            
            # Check if cancelled during conversion
            if job.status == ConversionStatus.CANCELLED:
                self.logger.info(f"Conversion cancelled: {job.audio_file.filename}")
                return
            
            # Mark as complete
            job.complete()
            
            # Notify completion
            if self.on_job_complete:
                self.on_job_complete(job)
            
            self.logger.info(f"Conversion complete: {job.audio_file.filename}")
            
        except ConversionError as e:
            # Handle known conversion errors
            error_info = self.error_handler.get_error_info(e)
            job.fail(error_info.user_message)
            
            if self.on_job_error:
                self.on_job_error(job, error_info.user_message)
            
            self.logger.error(f"Conversion failed: {job.audio_file.filename} - {error_info.user_message}")
            
        except Exception as e:
            # Handle unexpected errors
            error_info = self.error_handler.get_error_info(e, "conversion")
            job.fail(error_info.user_message)
            
            if self.on_job_error:
                self.on_job_error(job, error_info.user_message)
            
            self.logger.error(f"Unexpected error during conversion: {job.audio_file.filename} - {e}")
    
    def _on_queue_complete(self) -> None:
        """Called when all conversions are complete."""
        self._is_running = False
        
        # Calculate statistics
        stats = self.get_statistics()
        success_count = stats['completed']
        error_count = stats['failed'] + stats['cancelled']
        
        # Notify
        if self.on_all_complete:
            self.on_all_complete(success_count, error_count)
        
        self.logger.info(f"All conversions complete: {success_count} succeeded, {error_count} failed")
    
    def clear_jobs(self) -> None:
        """Clear all completed jobs."""
        # Remove completed/failed/cancelled jobs
        active_statuses = {ConversionStatus.PENDING, ConversionStatus.RUNNING}
        self._jobs = {
            path: job for path, job in self._jobs.items()
            if job.status in active_statuses
        }
        
        self.logger.debug(f"Cleared completed jobs. {len(self._jobs)} jobs remaining")
    
    def is_converting(self) -> bool:
        """Check if any conversions are currently running."""
        return self._is_running or len(self._active_jobs) > 0
