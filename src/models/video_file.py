"""
VideoFile model - Represents the output MP4 file after conversion.
"""

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .audio_file import AudioFile


@dataclass
class VideoFile:
    """Represents the output MP4 file after conversion."""
    
    path: str
    filename: str
    source_audio_file: Optional['AudioFile']
    video_width: int = 1280
    video_height: int = 720
    video_fps: int = 30
    created_at: Optional[datetime] = None
    file_size_bytes: int = 0
    
    @classmethod
    def for_audio_file(cls, audio_file: 'AudioFile', output_directory: Optional[str] = None) -> 'VideoFile':
        """Create VideoFile instance for a given AudioFile."""
        from .audio_file import AudioFile  # Import here to avoid circular import
        
        input_path = Path(audio_file.path)
        
        # Determine output directory
        if output_directory:
            output_dir = Path(output_directory)
        else:
            output_dir = input_path.parent
        
        # Generate output filename: {original_name}_video.mp4
        base_name = input_path.stem
        output_filename = f"{base_name}_video.mp4"
        output_path = output_dir / output_filename
        
        return cls(
            path=str(output_path.absolute()),
            filename=output_filename,
            source_audio_file=audio_file
        )
    
    @property
    def exists(self) -> bool:
        """Check if output file exists."""
        return Path(self.path).exists()
    
    @property
    def directory(self) -> str:
        """Get output directory path."""
        return str(Path(self.path).parent)
    
    @property
    def size_mb(self) -> float:
        """Get file size in megabytes."""
        return self.file_size_bytes / (1024 * 1024)
    
    @property
    def video_resolution(self) -> str:
        """Get video resolution as string."""
        return f"{self.video_width}x{self.video_height}"
    
    def update_file_info(self) -> None:
        """Update file information after conversion."""
        path_obj = Path(self.path)
        
        if path_obj.exists():
            stat_info = path_obj.stat()
            self.file_size_bytes = stat_info.st_size
            self.created_at = datetime.fromtimestamp(stat_info.st_mtime)
    
    def would_overwrite(self) -> bool:
        """Check if creating this file would overwrite an existing file."""
        return self.exists
    
    def delete(self) -> bool:
        """Delete the output file if it exists."""
        try:
            path_obj = Path(self.path)
            if path_obj.exists():
                path_obj.unlink()
                self.file_size_bytes = 0
                self.created_at = None
                return True
            return False
        except OSError:
            return False
    
    def validate_output_location(self) -> tuple[bool, Optional[str]]:
        """
        Validate that output location is writable.
        
        Returns:
            tuple: (is_valid, error_message)
        """
        output_dir = Path(self.path).parent
        
        # Check if directory exists
        if not output_dir.exists():
            return False, f"Output directory does not exist: {output_dir}"
        
        # Check if directory is writable
        if not output_dir.is_dir():
            return False, f"Output path is not a directory: {output_dir}"
        
        # Try to create a test file to check write permissions
        test_file = output_dir / f".test_write_{datetime.now().timestamp()}"
        try:
            test_file.touch()
            test_file.unlink()
            return True, None
        except (OSError, PermissionError):
            return False, f"Cannot write to output directory: {output_dir}"
    
    def __str__(self) -> str:
        """String representation of VideoFile."""
        return f"VideoFile({self.filename}, {self.video_resolution}, {self.size_mb:.1f}MB)"