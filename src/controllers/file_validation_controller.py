"""
File Validation Controller - Validates dropped files and integrates with UI.
"""

from typing import List, Callable, Optional
from pathlib import Path
import threading

from ..models.audio_file import AudioFile
from ..services.file_validator import FileValidator
from ..utils.logger import get_logger
from ..utils.error_handler import ErrorHandler, ConversionError


class FileValidationController:
    """Handles file validation workflow."""
    
    def __init__(self):
        self.logger = get_logger("FileValidationController")
        self.validator = FileValidator()
        self.error_handler = ErrorHandler()
        
        # Callbacks
        self.on_validation_start: Optional[Callable[[str], None]] = None
        self.on_validation_success: Optional[Callable[[str, AudioFile], None]] = None
        self.on_validation_error: Optional[Callable[[str, str], None]] = None
    
    def validate_files(self, file_paths: List[str]) -> None:
        """
        Validate multiple files asynchronously.
        
        Args:
            file_paths: List of file paths to validate
        """
        if not file_paths:
            return
        
        self.logger.info(f"Starting validation for {len(file_paths)} files")
        
        for file_path in file_paths:
            # Validate each file in a separate thread
            thread = threading.Thread(
                target=self._validate_single_file,
                args=(file_path,),
                daemon=True
            )
            thread.start()
    
    def _validate_single_file(self, file_path: str) -> None:
        """Validate a single file."""
        
        try:
            # Notify validation start
            if self.on_validation_start:
                self.on_validation_start(file_path)
            
            self.logger.debug(f"Validating file: {Path(file_path).name}")
            
            # Validate file
            audio_file = self.validator.validate_audio_file(file_path)
            
            # Notify success
            if self.on_validation_success:
                self.on_validation_success(file_path, audio_file)
            
            self.logger.info(f"Validation successful: {Path(file_path).name}")
            
        except ConversionError as e:
            # Handle known conversion errors
            error_info = self.error_handler.get_error_info(e)
            error_message = error_info.user_message
            
            if self.on_validation_error:
                self.on_validation_error(file_path, error_message)
            
            self.logger.warning(f"Validation failed: {Path(file_path).name} - {error_message}")
            
        except Exception as e:
            # Handle unexpected errors
            error_info = self.error_handler.get_error_info(e, "file validation")
            error_message = error_info.user_message
            
            if self.on_validation_error:
                self.on_validation_error(file_path, error_message)
            
            self.logger.error(f"Unexpected error validating {Path(file_path).name}: {e}")
    
    def quick_validate_paths(self, file_paths: List[str]) -> tuple[List[str], List[tuple[str, str]]]:
        """
        Quickly validate file paths without deep inspection.
        Returns valid paths and error list.
        
        Args:
            file_paths: List of file paths to check
            
        Returns:
            Tuple of (valid_paths, errors)
            errors is list of (file_path, error_message) tuples
        """
        valid_paths = []
        errors = []
        
        for file_path in file_paths:
            try:
                path = Path(file_path)
                
                # Check if file exists
                if not path.exists():
                    errors.append((file_path, "ファイルが存在しません"))
                    continue
                
                # Check if it's a file
                if not path.is_file():
                    errors.append((file_path, "ファイルではありません"))
                    continue
                
                # Check extension
                if path.suffix.lower() != '.mp3':
                    errors.append((file_path, "MP3ファイルではありません"))
                    continue
                
                # Check file size (not empty, not too large)
                size_mb = path.stat().st_size / (1024 * 1024)
                if size_mb == 0:
                    errors.append((file_path, "ファイルが空です"))
                    continue
                
                if size_mb > 1000:  # 1GB limit
                    errors.append((file_path, "ファイルサイズが大きすぎます (上限: 1GB)"))
                    continue
                
                # Valid
                valid_paths.append(file_path)
                
            except Exception as e:
                errors.append((file_path, f"エラー: {str(e)}"))
        
        return valid_paths, errors
    
    def is_mp3_file(self, file_path: str) -> bool:
        """Quick check if file is MP3."""
        return Path(file_path).suffix.lower() == '.mp3'
    
    def filter_mp3_files(self, file_paths: List[str]) -> List[str]:
        """Filter list to only MP3 files."""
        return [fp for fp in file_paths if self.is_mp3_file(fp)]
