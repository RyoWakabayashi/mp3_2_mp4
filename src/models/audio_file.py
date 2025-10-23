"""
AudioFile model - Represents an input MP3 file for conversion.
"""

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional
import os


@dataclass
class AudioFile:
    """Represents an input MP3 file for conversion."""
    
    path: str
    filename: str
    size_bytes: int
    duration_seconds: float
    sample_rate: int
    bitrate: int
    metadata: Dict[str, str]
    created_at: datetime
    is_valid: bool
    
    @classmethod
    def from_path(cls, file_path: str) -> 'AudioFile':
        """Create AudioFile instance from file path."""
        path_obj = Path(file_path)
        
        if not path_obj.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Get basic file info
        stat_info = path_obj.stat()
        
        return cls(
            path=str(path_obj.absolute()),
            filename=path_obj.name,
            size_bytes=stat_info.st_size,
            duration_seconds=0.0,  # Will be populated by validation
            sample_rate=0,         # Will be populated by validation
            bitrate=0,             # Will be populated by validation
            metadata={},           # Will be populated by validation
            created_at=datetime.now(),
            is_valid=False         # Will be set by validation
        )
    
    @property
    def extension(self) -> str:
        """Get file extension."""
        return Path(self.path).suffix.lower()
    
    @property
    def is_mp3(self) -> bool:
        """Check if file has MP3 extension."""
        return self.extension == '.mp3'
    
    @property
    def size_mb(self) -> float:
        """Get file size in megabytes."""
        return self.size_bytes / (1024 * 1024)
    
    @property
    def duration_minutes(self) -> float:
        """Get duration in minutes."""
        return self.duration_seconds / 60.0
    
    def validate(self) -> tuple[bool, Optional[str]]:
        """
        Validate the audio file.
        
        Returns:
            tuple: (is_valid, error_message)
        """
        # Check if file exists and is readable
        try:
            if not os.access(self.path, os.R_OK):
                return False, "File cannot be read - check permissions"
        except OSError:
            return False, "File access error"
        
        # Check file extension
        if not self.is_mp3:
            return False, "File is not an MP3 audio file"
        
        # Check file size limits
        if self.size_bytes == 0:
            return False, "File is empty"
        
        if self.size_bytes > 2 * 1024 * 1024 * 1024:  # 2GB limit
            return False, "File exceeds 2GB size limit"
        
        # If all basic checks pass, detailed validation will be done by FFmpeg service
        return True, None
    
    def __str__(self) -> str:
        """String representation of AudioFile."""
        return f"AudioFile({self.filename}, {self.size_mb:.1f}MB, {self.duration_minutes:.1f}min)"