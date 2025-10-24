"""
FFmpeg Integration Service - Handles audio to video conversion using FFmpeg.
"""

import os
import subprocess
import threading
from pathlib import Path
from typing import Callable, Optional, Tuple
import ffmpeg
from mutagen.mp3 import MP3
from mutagen.id3 import ID3NoHeaderError

from ..models.audio_file import AudioFile
from ..models.video_file import VideoFile
from ..models.conversion_job import ConversionJob


class FFmpegService:
    """Service for FFmpeg-based audio to video conversion."""
    
    def __init__(self):
        self._ffmpeg_path = self._find_ffmpeg()
        self._video_encoder = self._detect_video_encoder()
    
    def _find_ffmpeg(self) -> Optional[str]:
        """Find FFmpeg executable in system PATH."""
        # Try common FFmpeg locations
        common_paths = [
            "ffmpeg",  # System PATH
            "/usr/local/bin/ffmpeg",  # Homebrew on macOS
            "/opt/homebrew/bin/ffmpeg",  # Apple Silicon Homebrew
            "C:\\ffmpeg\\bin\\ffmpeg.exe",  # Windows common location
        ]
        
        for path in common_paths:
            try:
                result = subprocess.run([path, "-version"], 
                                      capture_output=True, 
                                      timeout=5)
                if result.returncode == 0:
                    return path
            except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
                continue
        
        return None
    
    def _detect_video_encoder(self) -> str:
        """Detect the best available video encoder."""
        if not self._ffmpeg_path:
            return "libx264"  # Default fallback
        
        try:
            # Get list of available encoders
            result = subprocess.run(
                [self._ffmpeg_path, "-encoders"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                encoders = result.stdout.lower()
                
                # Priority order: hardware accelerated encoders first, then software
                if "h264_videotoolbox" in encoders:
                    return "h264_videotoolbox"  # macOS hardware acceleration
                elif "h264_qsv" in encoders:
                    return "h264_qsv"  # Intel Quick Sync
                elif "h264_nvenc" in encoders:
                    return "h264_nvenc"  # NVIDIA hardware acceleration
                elif "libx264" in encoders:
                    return "libx264"  # Standard software encoder
                elif "mpeg4" in encoders:
                    return "mpeg4"  # Fallback
                
        except Exception:
            pass
        
        return "libx264"  # Default fallback
    
    def is_available(self) -> bool:
        """Check if FFmpeg is available on the system."""
        return self._ffmpeg_path is not None
    
    def validate_audio_file(self, audio_file: AudioFile) -> Tuple[bool, Optional[str]]:
        """
        Validate MP3 file using FFmpeg and mutagen.
        
        Args:
            audio_file: AudioFile instance to validate
            
        Returns:
            tuple: (is_valid, error_message)
        """
        if not self.is_available():
            return False, "FFmpeg is not available on this system"
        
        try:
            # Use mutagen to read MP3 metadata and validate format
            mp3_file = MP3(audio_file.path)
            
            # Update audio file with metadata
            audio_file.duration_seconds = mp3_file.info.length if mp3_file.info else 0.0
            audio_file.sample_rate = mp3_file.info.sample_rate if mp3_file.info else 0
            audio_file.bitrate = mp3_file.info.bitrate if mp3_file.info else 0
            
            # Extract metadata tags
            metadata = {}
            if mp3_file.tags:
                for key, value in mp3_file.tags.items():
                    if isinstance(value, list) and value:
                        metadata[key] = str(value[0])
                    else:
                        metadata[key] = str(value)
            
            audio_file.metadata = metadata
            
            # Additional validation with FFmpeg
            try:
                probe = ffmpeg.probe(audio_file.path)
                audio_streams = [stream for stream in probe['streams'] if stream['codec_type'] == 'audio']
                
                if not audio_streams:
                    return False, "No audio stream found in file"
                
                # File is valid
                audio_file.is_valid = True
                return True, None
                
            except ffmpeg.Error as e:
                return False, f"FFmpeg validation failed: {str(e)}"
            
        except ID3NoHeaderError:
            return False, "Invalid MP3 file - no ID3 header found"
        except Exception as e:
            return False, f"File validation failed: {str(e)}"
    
    def convert_to_mp4(self, 
                      job: ConversionJob,
                      progress_callback: Optional[Callable[[float], None]] = None,
                      completion_callback: Optional[Callable[[bool, Optional[str]], None]] = None) -> None:
        """
        Convert MP3 to MP4 with black video track.
        
        Args:
            job: ConversionJob to process
            progress_callback: Called with progress percentage (0.0-100.0)
            completion_callback: Called with (success, error_message) when done
        """
        if not self.is_available():
            if completion_callback:
                completion_callback(False, "FFmpeg is not available")
            return
        
        if not job.audio_file or not job.video_file:
            if completion_callback:
                completion_callback(False, "Invalid conversion job - missing audio or video file")
            return
        
        def conversion_thread():
            stderr_lines = []
            try:
                input_path = job.audio_file.path
                output_path = job.video_file.path
                
                # Ensure output directory exists
                Path(output_path).parent.mkdir(parents=True, exist_ok=True)
                
                # Build FFmpeg command
                input_stream = ffmpeg.input(input_path)
                
                # Create black video stream
                video_stream = ffmpeg.input(
                    'color=black:size={}x{}:rate={}'.format(
                        job.video_file.video_width,
                        job.video_file.video_height,
                        job.video_file.video_fps
                    ),
                    f='lavfi',
                    t=job.audio_file.duration_seconds
                )
                
                # Combine audio and video
                # Use detected video encoder
                output_kwargs = {
                    'vcodec': self._video_encoder,
                    'acodec': 'aac',
                    'shortest': None,
                    'y': None  # Overwrite output file
                }
                
                # Add pixel format for software encoders
                if self._video_encoder in ['libx264', 'mpeg4']:
                    output_kwargs['pix_fmt'] = 'yuv420p'
                
                output = ffmpeg.output(
                    video_stream,
                    input_stream,
                    output_path,
                    **output_kwargs
                )
                
                # Run conversion with progress monitoring
                process = ffmpeg.run_async(output, pipe_stderr=True, pipe_stdout=True)
                
                # Monitor progress and capture stderr
                if process.stderr:
                    while True:
                        line = process.stderr.readline()
                        if not line:
                            break
                        line_str = line.decode('utf-8', errors='ignore')
                        stderr_lines.append(line_str)
                        
                        # Parse progress
                        if progress_callback and 'time=' in line_str:
                            try:
                                time_str = line_str.split('time=')[1].split()[0]
                                time_parts = time_str.split(':')
                                if len(time_parts) == 3:
                                    hours = float(time_parts[0])
                                    minutes = float(time_parts[1])
                                    seconds = float(time_parts[2])
                                    current_time = hours * 3600 + minutes * 60 + seconds
                                    
                                    if job.audio_file.duration_seconds > 0:
                                        progress = (current_time / job.audio_file.duration_seconds) * 100
                                        progress = max(0.0, min(100.0, progress))
                                        progress_callback(progress)
                            except (ValueError, IndexError):
                                pass
                
                # Wait for completion
                process.wait()
                
                if process.returncode == 0:
                    # Update video file info
                    job.video_file.update_file_info()
                    if completion_callback:
                        completion_callback(True, None)
                else:
                    stderr_output = ''.join(stderr_lines[-20:]) if stderr_lines else "No error output"
                    if completion_callback:
                        completion_callback(False, f"FFmpeg conversion failed (code {process.returncode}): {stderr_output}")
                
            except Exception as e:
                stderr_output = ''.join(stderr_lines[-10:]) if stderr_lines else ""
                error_msg = f"Conversion error: {str(e)}"
                if stderr_output:
                    error_msg += f"\nFFmpeg output: {stderr_output}"
                if completion_callback:
                    completion_callback(False, error_msg)
        
        # Start conversion in separate thread
        thread = threading.Thread(target=conversion_thread)
        thread.daemon = True
        thread.start()
    
    def _monitor_progress(self, 
                         process: subprocess.Popen,
                         total_duration: float,
                         progress_callback: Optional[Callable[[float], None]]) -> None:
        """Monitor FFmpeg progress by parsing stderr output."""
        if not progress_callback or not process.stderr:
            return
        
        try:
            while True:
                line = process.stderr.readline().decode()
                if not line:
                    break
                
                # Parse time progress from FFmpeg output
                if 'time=' in line:
                    try:
                        time_str = line.split('time=')[1].split()[0]
                        # Convert time format HH:MM:SS.ss to seconds
                        time_parts = time_str.split(':')
                        if len(time_parts) == 3:
                            hours = float(time_parts[0])
                            minutes = float(time_parts[1])
                            seconds = float(time_parts[2])
                            current_time = hours * 3600 + minutes * 60 + seconds
                            
                            if total_duration > 0:
                                progress = (current_time / total_duration) * 100
                                progress = max(0.0, min(100.0, progress))
                                progress_callback(progress)
                    except (ValueError, IndexError):
                        continue
        except Exception:
            # Ignore progress monitoring errors
            pass
    
    def get_ffmpeg_info(self) -> dict:
        """Get FFmpeg version and configuration information."""
        if not self.is_available():
            return {"available": False, "error": "FFmpeg not found"}
        
        try:
            result = subprocess.run([self._ffmpeg_path, "-version"], 
                                  capture_output=True, 
                                  text=True, 
                                  timeout=10)
            
            version_info = {"available": True, "path": self._ffmpeg_path}
            
            if result.returncode == 0:
                lines = result.stdout.split('\n')
                if lines:
                    version_info["version"] = lines[0]
                version_info["full_output"] = result.stdout
            else:
                version_info["error"] = result.stderr
            
            return version_info
            
        except Exception as e:
            return {"available": False, "error": str(e)}