"""
ApplicationState model - Represents the overall application state and configuration.
"""

from dataclasses import dataclass, field
from typing import List, Optional
from .conversion_job import ConversionJob


@dataclass
class ApplicationState:
    """Represents the overall application state and configuration."""
    
    active_jobs: List[ConversionJob] = field(default_factory=list)
    completed_jobs: List[ConversionJob] = field(default_factory=list)
    output_directory: Optional[str] = None
    max_concurrent_jobs: int = 1
    preserve_metadata: bool = True
    video_quality: str = "medium"  # "low", "medium", "high"
    window_width: int = 800
    window_height: int = 600
    last_used_directory: Optional[str] = None
    
    def add_job(self, job: ConversionJob) -> None:
        """Add a new conversion job to the active queue."""
        if job not in self.active_jobs:
            self.active_jobs.append(job)
    
    def remove_active_job(self, job: ConversionJob) -> None:
        """Remove a job from active queue."""
        if job in self.active_jobs:
            self.active_jobs.remove(job)
    
    def move_to_completed(self, job: ConversionJob) -> None:
        """Move a job from active to completed queue."""
        self.remove_active_job(job)
        
        # Add to completed jobs (keep only last 20)
        self.completed_jobs.append(job)
        if len(self.completed_jobs) > 20:
            self.completed_jobs = self.completed_jobs[-20:]
    
    def clear_completed_jobs(self) -> None:
        """Clear the completed jobs list."""
        self.completed_jobs.clear()
    
    def get_job_by_id(self, job_id: str) -> Optional[ConversionJob]:
        """Find a job by its ID in active or completed jobs."""
        # Search in active jobs first
        for job in self.active_jobs:
            if job.id == job_id:
                return job
        
        # Search in completed jobs
        for job in self.completed_jobs:
            if job.id == job_id:
                return job
        
        return None
    
    @property
    def has_active_jobs(self) -> bool:
        """Check if there are any active jobs."""
        return len(self.active_jobs) > 0
    
    @property
    def active_job_count(self) -> int:
        """Get number of active jobs."""
        return len(self.active_jobs)
    
    @property
    def completed_job_count(self) -> int:
        """Get number of completed jobs."""
        return len(self.completed_jobs)
    
    @property
    def processing_jobs(self) -> List[ConversionJob]:
        """Get currently processing jobs."""
        from .conversion_job import ConversionStatus
        return [job for job in self.active_jobs if job.status == ConversionStatus.PROCESSING]
    
    @property
    def queued_jobs(self) -> List[ConversionJob]:
        """Get queued jobs."""
        from .conversion_job import ConversionStatus
        return [job for job in self.active_jobs if job.status == ConversionStatus.QUEUED]
    
    @property
    def can_start_new_job(self) -> bool:
        """Check if a new job can be started based on concurrent job limit."""
        processing_count = len(self.processing_jobs)
        return processing_count < self.max_concurrent_jobs
    
    def update_last_used_directory(self, directory: str) -> None:
        """Update the last used directory."""
        self.last_used_directory = directory
    
    def validate_settings(self) -> tuple[bool, Optional[str]]:
        """
        Validate application settings.
        
        Returns:
            tuple: (is_valid, error_message)
        """
        # Validate video quality
        valid_qualities = ["low", "medium", "high"]
        if self.video_quality not in valid_qualities:
            return False, f"Invalid video quality: {self.video_quality}. Must be one of {valid_qualities}"
        
        # Validate concurrent jobs limit
        if self.max_concurrent_jobs < 1 or self.max_concurrent_jobs > 10:
            return False, "Max concurrent jobs must be between 1 and 10"
        
        # Validate window dimensions
        if self.window_width < 400 or self.window_height < 300:
            return False, "Window dimensions too small (minimum 400x300)"
        
        return True, None
    
    def to_dict(self) -> dict:
        """Convert settings to dictionary for persistence."""
        return {
            "output_directory": self.output_directory,
            "max_concurrent_jobs": self.max_concurrent_jobs,
            "preserve_metadata": self.preserve_metadata,
            "video_quality": self.video_quality,
            "window_width": self.window_width,
            "window_height": self.window_height,
            "last_used_directory": self.last_used_directory
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'ApplicationState':
        """Create ApplicationState from dictionary."""
        return cls(
            output_directory=data.get("output_directory"),
            max_concurrent_jobs=data.get("max_concurrent_jobs", 1),
            preserve_metadata=data.get("preserve_metadata", True),
            video_quality=data.get("video_quality", "medium"),
            window_width=data.get("window_width", 800),
            window_height=data.get("window_height", 600),
            last_used_directory=data.get("last_used_directory")
        )