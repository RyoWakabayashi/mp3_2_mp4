"""
File Validation Utilities - MP3 format checking and validation.
"""

import os
from pathlib import Path
from typing import List, Tuple, Optional

from models.audio_file import AudioFile


class FileValidator:
    """Utility class for validating audio files."""
    
    # Supported file extensions
    SUPPORTED_EXTENSIONS = ['.mp3']
    
    # File size limits
    MIN_FILE_SIZE = 1024  # 1KB minimum
    MAX_FILE_SIZE = 2 * 1024 * 1024 * 1024  # 2GB maximum
    
    @classmethod
    def is_supported_format(cls, file_path: str) -> bool:
        """Check if file format is supported."""
        extension = Path(file_path).suffix.lower()
        return extension in cls.SUPPORTED_EXTENSIONS
    
    @classmethod
    def validate_file_basic(cls, file_path: str) -> Tuple[bool, Optional[str]]:
        """
        Perform basic file validation without opening the file.
        
        Args:
            file_path: Path to the file to validate
            
        Returns:
            tuple: (is_valid, error_message)
        """
        path_obj = Path(file_path)
        
        # Check if file exists
        if not path_obj.exists():
            return False, f"File does not exist: {file_path}"
        
        # Check if it's a file (not directory)
        if not path_obj.is_file():
            return False, f"Path is not a file: {file_path}"
        
        # Check file extension
        if not cls.is_supported_format(file_path):
            return False, f"Unsupported file format: {path_obj.suffix}"
        
        # Check file size
        try:
            file_size = path_obj.stat().st_size
            
            if file_size < cls.MIN_FILE_SIZE:
                return False, f"File is too small: {file_size} bytes"
            
            if file_size > cls.MAX_FILE_SIZE:
                return False, f"File is too large: {file_size / (1024*1024*1024):.1f}GB (max 2GB)"
        
        except OSError as e:
            return False, f"Cannot access file: {str(e)}"
        
        # Check file permissions
        if not os.access(file_path, os.R_OK):
            return False, f"File is not readable: {file_path}"
        
        return True, None
    
    @classmethod
    def validate_audio_file(cls, audio_file: AudioFile) -> Tuple[bool, Optional[str]]:
        """
        Validate an AudioFile instance.
        
        Args:
            audio_file: AudioFile to validate
            
        Returns:
            tuple: (is_valid, error_message)
        """
        # First run basic validation
        is_valid, error = cls.validate_file_basic(audio_file.path)
        if not is_valid:
            return is_valid, error
        
        # Run AudioFile's own validation
        return audio_file.validate()
    
    @classmethod
    def filter_valid_files(cls, file_paths: List[str]) -> Tuple[List[str], List[Tuple[str, str]]]:
        """
        Filter a list of file paths, returning valid files and errors.
        
        Args:
            file_paths: List of file paths to validate
            
        Returns:
            tuple: (valid_files, errors) where errors is list of (file_path, error_message)
        """
        valid_files = []
        errors = []
        
        for file_path in file_paths:
            is_valid, error = cls.validate_file_basic(file_path)
            if is_valid:
                valid_files.append(file_path)
            else:
                errors.append((file_path, error))
        
        return valid_files, errors
    
    @classmethod
    def create_audio_files(cls, file_paths: List[str]) -> Tuple[List[AudioFile], List[Tuple[str, str]]]:
        """
        Create AudioFile instances from file paths, validating each one.
        
        Args:
            file_paths: List of file paths
            
        Returns:
            tuple: (audio_files, errors) where errors is list of (file_path, error_message)
        """
        audio_files = []
        errors = []
        
        for file_path in file_paths:
            try:
                # Create AudioFile instance
                audio_file = AudioFile.from_path(file_path)
                
                # Validate it
                is_valid, error = cls.validate_audio_file(audio_file)
                if is_valid:
                    audio_files.append(audio_file)
                else:
                    errors.append((file_path, error))
                    
            except Exception as e:
                errors.append((file_path, f"Failed to create AudioFile: {str(e)}"))
        
        return audio_files, errors
    
    @classmethod
    def get_file_info_summary(cls, file_path: str) -> dict:
        """
        Get summary information about a file without full validation.
        
        Args:
            file_path: Path to the file
            
        Returns:
            dict: File information summary
        """
        try:
            path_obj = Path(file_path)
            
            if not path_obj.exists():
                return {"error": "File does not exist"}
            
            stat_info = path_obj.stat()
            
            return {
                "filename": path_obj.name,
                "size_bytes": stat_info.st_size,
                "size_mb": stat_info.st_size / (1024 * 1024),
                "extension": path_obj.suffix.lower(),
                "is_supported": cls.is_supported_format(file_path),
                "is_readable": os.access(file_path, os.R_OK),
                "modified_time": stat_info.st_mtime
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    @classmethod
    def batch_file_info(cls, file_paths: List[str]) -> List[dict]:
        """
        Get summary information for multiple files.
        
        Args:
            file_paths: List of file paths
            
        Returns:
            list: List of file information dictionaries
        """
        return [cls.get_file_info_summary(path) for path in file_paths]


class DirectoryValidator:
    """Utility class for validating output directories."""
    
    @classmethod
    def validate_output_directory(cls, directory_path: str) -> Tuple[bool, Optional[str]]:
        """
        Validate that a directory can be used for output files.
        
        Args:
            directory_path: Path to the directory
            
        Returns:
            tuple: (is_valid, error_message)
        """
        try:
            path_obj = Path(directory_path)
            
            # Check if directory exists
            if not path_obj.exists():
                return False, f"Directory does not exist: {directory_path}"
            
            # Check if it's actually a directory
            if not path_obj.is_dir():
                return False, f"Path is not a directory: {directory_path}"
            
            # Check write permissions
            if not os.access(directory_path, os.W_OK):
                return False, f"Directory is not writable: {directory_path}"
            
            # Check disk space (at least 100MB free)
            try:
                stat_info = os.statvfs(directory_path)
                free_bytes = stat_info.f_frsize * stat_info.f_bavail
                min_free_bytes = 100 * 1024 * 1024  # 100MB
                
                if free_bytes < min_free_bytes:
                    free_mb = free_bytes / (1024 * 1024)
                    return False, f"Insufficient disk space: {free_mb:.1f}MB free (minimum 100MB required)"
            
            except (AttributeError, OSError):
                # statvfs not available on Windows, skip disk space check
                pass
            
            return True, None
            
        except Exception as e:
            return False, f"Directory validation error: {str(e)}"
    
    @classmethod
    def get_directory_info(cls, directory_path: str) -> dict:
        """
        Get information about a directory.
        
        Args:
            directory_path: Path to the directory
            
        Returns:
            dict: Directory information
        """
        try:
            path_obj = Path(directory_path)
            
            if not path_obj.exists():
                return {"error": "Directory does not exist"}
            
            info = {
                "path": str(path_obj.absolute()),
                "exists": True,
                "is_directory": path_obj.is_dir(),
                "is_writable": os.access(directory_path, os.W_OK)
            }
            
            # Get disk space info if available
            try:
                stat_info = os.statvfs(directory_path)
                total_bytes = stat_info.f_frsize * stat_info.f_blocks
                free_bytes = stat_info.f_frsize * stat_info.f_bavail
                
                info.update({
                    "total_space_gb": total_bytes / (1024**3),
                    "free_space_gb": free_bytes / (1024**3),
                    "free_space_percent": (free_bytes / total_bytes) * 100 if total_bytes > 0 else 0
                })
            except (AttributeError, OSError):
                # Not available on all systems
                pass
            
            return info
            
        except Exception as e:
            return {"error": str(e)}