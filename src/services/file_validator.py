"""
File Validator - Validates MP3 files before conversion.
"""

from pathlib import Path
from typing import Optional
import os

from ..models.audio_file import AudioFile
from ..utils.error_handler import ConversionError, ErrorCode
from ..utils.logger import get_logger

try:
    from mutagen.mp3 import MP3
    from mutagen import MutagenError
    HAS_MUTAGEN = True
except ImportError:
    HAS_MUTAGEN = False


class FileValidator:
    """Validates audio files for conversion."""
    
    def __init__(self):
        self.logger = get_logger("FileValidator")
        
        if not HAS_MUTAGEN:
            self.logger.warning("mutagen not available, metadata extraction will be limited")
    
    def validate_audio_file(self, file_path: str) -> AudioFile:
        """
        Validate MP3 file and create AudioFile model.
        
        Args:
            file_path: Path to the MP3 file
            
        Returns:
            AudioFile model with metadata
            
        Raises:
            ConversionError: If file is invalid
        """
        self.logger.debug(f"Validating audio file: {file_path}")
        
        # Check file exists
        path = Path(file_path)
        if not path.exists():
            raise ConversionError(
                ErrorCode.FILE_NOT_FOUND,
                f"File not found: {file_path}"
            )
        
        # Check is file
        if not path.is_file():
            raise ConversionError(
                ErrorCode.INVALID_FILE,
                f"Not a file: {file_path}"
            )
        
        # Check extension
        if path.suffix.lower() != '.mp3':
            raise ConversionError(
                ErrorCode.INVALID_FILE_FORMAT,
                f"Not an MP3 file: {path.name}"
            )
        
        # Check file size
        file_size = path.stat().st_size
        if file_size == 0:
            raise ConversionError(
                ErrorCode.INVALID_FILE,
                f"File is empty: {path.name}"
            )
        
        # Check maximum size (1GB)
        max_size = 1024 * 1024 * 1024  # 1GB in bytes
        if file_size > max_size:
            raise ConversionError(
                ErrorCode.INVALID_FILE,
                f"File too large (max 1GB): {path.name}"
            )
        
        # Check file is readable
        if not os.access(file_path, os.R_OK):
            raise ConversionError(
                ErrorCode.FILE_ACCESS_ERROR,
                f"Cannot read file: {path.name}"
            )
        
        # Extract metadata
        duration = None
        bitrate = None
        sample_rate = None
        channels = None
        
        if HAS_MUTAGEN:
            try:
                audio = MP3(file_path)
                
                # Get duration
                if audio.info.length:
                    duration = audio.info.length
                
                # Get bitrate (in kbps)
                if audio.info.bitrate:
                    bitrate = audio.info.bitrate // 1000
                
                # Get sample rate
                if audio.info.sample_rate:
                    sample_rate = audio.info.sample_rate
                
                # Get channels
                if audio.info.channels:
                    channels = audio.info.channels
                
                self.logger.debug(
                    f"Extracted metadata: duration={duration}s, "
                    f"bitrate={bitrate}kbps, sample_rate={sample_rate}Hz"
                )
                
            except MutagenError as e:
                # Invalid MP3 file
                raise ConversionError(
                    ErrorCode.INVALID_FILE_FORMAT,
                    f"Invalid MP3 file format: {path.name}"
                ) from e
            except Exception as e:
                # Other metadata extraction errors - log but don't fail
                self.logger.warning(f"Could not extract metadata from {path.name}: {e}")
        
        # Create AudioFile model
        audio_file = AudioFile(
            file_path=str(path.absolute()),
            duration=duration,
            bitrate=bitrate,
            sample_rate=sample_rate,
            channels=channels
        )
        
        # Validate the model
        if not audio_file.is_valid():
            raise ConversionError(
                ErrorCode.INVALID_FILE,
                f"Audio file validation failed: {path.name}"
            )
        
        self.logger.info(f"File validation successful: {path.name}")
        return audio_file
    
    def quick_check(self, file_path: str) -> bool:
        """
        Quick validation without metadata extraction.
        
        Args:
            file_path: Path to check
            
        Returns:
            True if file passes basic checks
        """
        try:
            path = Path(file_path)
            
            # Basic checks
            if not path.exists():
                return False
            
            if not path.is_file():
                return False
            
            if path.suffix.lower() != '.mp3':
                return False
            
            if path.stat().st_size == 0:
                return False
            
            return True
            
        except Exception:
            return False
    
    def is_mp3_file(self, file_path: str) -> bool:
        """Check if file has MP3 extension."""
        return Path(file_path).suffix.lower() == '.mp3'
    
    def get_file_info(self, file_path: str) -> dict:
        """
        Get basic file information without full validation.
        
        Returns:
            Dictionary with file info (name, size, extension)
        """
        try:
            path = Path(file_path)
            
            return {
                'name': path.name,
                'size_bytes': path.stat().st_size if path.exists() else 0,
                'size_mb': path.stat().st_size / (1024 * 1024) if path.exists() else 0,
                'extension': path.suffix.lower(),
                'exists': path.exists(),
                'is_file': path.is_file() if path.exists() else False,
                'absolute_path': str(path.absolute())
            }
        except Exception as e:
            self.logger.error(f"Error getting file info: {e}")
            return {
                'name': Path(file_path).name,
                'error': str(e)
            }
