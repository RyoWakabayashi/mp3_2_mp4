"""
ConversionJob model - Represents a conversion task from MP3 to MP4.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional
import uuid

from .audio_file import AudioFile
from .video_file import VideoFile


class ConversionStatus(Enum):
    """Conversion job status enumeration."""
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class ConversionJob:
    """Represents a conversion task from MP3 to MP4."""
    
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    audio_file: Optional[AudioFile] = None
    video_file: Optional[VideoFile] = None
    status: ConversionStatus = ConversionStatus.QUEUED
    progress_percent: float = 0.0
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    can_cancel: bool = True
    estimated_remaining_seconds: int = 0
    
    @classmethod
    def create_for_audio_file(cls, audio_file: AudioFile, output_directory: Optional[str] = None) -> 'ConversionJob':
        """Create a new conversion job for an audio file."""
        job = cls(audio_file=audio_file)
        
        # Create corresponding video file
        if output_directory:
            video_file = VideoFile.for_audio_file(audio_file, output_directory)
        else:
            video_file = VideoFile.for_audio_file(audio_file)
        
        job.video_file = video_file
        return job
    
    def start_processing(self) -> None:
        """Mark job as started."""
        self.status = ConversionStatus.PROCESSING
        self.started_at = datetime.now()
        self.progress_percent = 0.0
        self.can_cancel = True
    
    def update_progress(self, percent: float, estimated_remaining: int = 0) -> None:
        """Update conversion progress."""
        if self.status != ConversionStatus.PROCESSING:
            raise ValueError("Cannot update progress for non-processing job")
        
        self.progress_percent = max(0.0, min(100.0, percent))
        self.estimated_remaining_seconds = max(0, estimated_remaining)
    
    def complete_success(self) -> None:
        """Mark job as successfully completed."""
        self.status = ConversionStatus.COMPLETED
        self.completed_at = datetime.now()
        self.progress_percent = 100.0
        self.can_cancel = False
        self.error_message = None
    
    def complete_failure(self, error_message: str) -> None:
        """Mark job as failed."""
        self.status = ConversionStatus.FAILED
        self.completed_at = datetime.now()
        self.can_cancel = False
        self.error_message = error_message
    
    def cancel(self) -> bool:
        """Cancel the job if possible."""
        if not self.can_cancel:
            return False
        
        self.status = ConversionStatus.CANCELLED
        self.completed_at = datetime.now()
        self.can_cancel = False
        return True
    
    @property
    def is_active(self) -> bool:
        """Check if job is currently active (queued or processing)."""
        return self.status in [ConversionStatus.QUEUED, ConversionStatus.PROCESSING]
    
    @property
    def is_finished(self) -> bool:
        """Check if job is finished (completed, failed, or cancelled)."""
        return self.status in [ConversionStatus.COMPLETED, ConversionStatus.FAILED, ConversionStatus.CANCELLED]
    
    @property
    def duration_seconds(self) -> Optional[float]:
        """Get job duration in seconds."""
        if not self.started_at:
            return None
        
        end_time = self.completed_at or datetime.now()
        return (end_time - self.started_at).total_seconds()
    
    def __str__(self) -> str:
        """String representation of ConversionJob."""
        if self.audio_file:
            filename = self.audio_file.filename
        else:
            filename = "Unknown"
        
        return f"ConversionJob({filename}, {self.status.value}, {self.progress_percent:.1f}%)"