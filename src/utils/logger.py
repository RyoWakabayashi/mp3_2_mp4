"""
Logging Configuration - Debug and production modes.
"""

import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional


class Logger:
    """Centralized logging configuration."""
    
    _logger: Optional[logging.Logger] = None
    _log_file_path: Optional[str] = None
    
    @classmethod
    def setup(cls, 
              name: str = "mp3_to_mp4",
              level: Optional[str] = None,
              log_to_file: bool = True,
              log_directory: Optional[str] = None) -> logging.Logger:
        """
        Setup application logging.
        
        Args:
            name: Logger name
            level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            log_to_file: Whether to log to file
            log_directory: Directory for log files
            
        Returns:
            Configured logger instance
        """
        
        if cls._logger is not None:
            return cls._logger
        
        # Determine log level
        if level is None:
            level = os.environ.get("LOG_LEVEL", "INFO").upper()
        
        # Create logger
        logger = logging.getLogger(name)
        logger.setLevel(getattr(logging, level, logging.INFO))
        
        # Clear existing handlers
        logger.handlers.clear()
        
        # Create formatter
        formatter = cls._create_formatter(level == "DEBUG")
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # File handler
        if log_to_file:
            file_handler = cls._create_file_handler(log_directory, formatter)
            if file_handler:
                logger.addHandler(file_handler)
        
        # Prevent duplicate logs
        logger.propagate = False
        
        cls._logger = logger
        return logger
    
    @classmethod
    def _create_formatter(cls, debug_mode: bool = False) -> logging.Formatter:
        """Create log formatter based on mode."""
        
        if debug_mode:
            # Detailed format for debugging
            format_string = (
                "%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | "
                "%(funcName)s() | %(message)s"
            )
        else:
            # Simpler format for production
            format_string = "%(asctime)s | %(levelname)-8s | %(message)s"
        
        return logging.Formatter(
            format_string,
            datefmt="%Y-%m-%d %H:%M:%S"
        )
    
    @classmethod
    def _create_file_handler(cls, 
                           log_directory: Optional[str], 
                           formatter: logging.Formatter) -> Optional[logging.FileHandler]:
        """Create file handler for logging."""
        
        try:
            # Determine log directory
            if log_directory is None:
                # Use user's home directory or temp directory
                if os.name == 'nt':  # Windows
                    log_directory = os.path.join(os.environ.get('APPDATA', '.'), 'MP3toMP4Converter')
                else:  # macOS/Linux
                    log_directory = os.path.join(os.path.expanduser('~'), '.mp3_to_mp4')
            
            # Create log directory
            log_dir_path = Path(log_directory)
            log_dir_path.mkdir(parents=True, exist_ok=True)
            
            # Create log file name with timestamp
            timestamp = datetime.now().strftime("%Y%m%d")
            log_filename = f"mp3_to_mp4_{timestamp}.log"
            log_file_path = log_dir_path / log_filename
            
            # Create file handler
            file_handler = logging.FileHandler(log_file_path, encoding='utf-8')
            file_handler.setFormatter(formatter)
            
            cls._log_file_path = str(log_file_path)
            
            return file_handler
            
        except Exception as e:
            # If file logging fails, just continue with console logging
            print(f"Warning: Could not setup file logging: {e}")
            return None
    
    @classmethod
    def get_logger(cls, name: Optional[str] = None) -> logging.Logger:
        """Get logger instance."""
        if cls._logger is None:
            cls.setup()
        
        if name and name != cls._logger.name:
            # Return child logger
            return cls._logger.getChild(name)
        
        return cls._logger
    
    @classmethod
    def get_log_file_path(cls) -> Optional[str]:
        """Get current log file path."""
        return cls._log_file_path
    
    @classmethod
    def set_level(cls, level: str) -> None:
        """Change log level dynamically."""
        if cls._logger:
            cls._logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    
    @classmethod
    def cleanup_old_logs(cls, log_directory: Optional[str] = None, days_to_keep: int = 7) -> None:
        """Clean up old log files."""
        try:
            if log_directory is None:
                if cls._log_file_path:
                    log_directory = str(Path(cls._log_file_path).parent)
                else:
                    return
            
            log_dir = Path(log_directory)
            if not log_dir.exists():
                return
            
            # Find old log files
            cutoff_timestamp = datetime.now().timestamp() - (days_to_keep * 24 * 60 * 60)
            
            for log_file in log_dir.glob("mp3_to_mp4_*.log"):
                try:
                    if log_file.stat().st_mtime < cutoff_timestamp:
                        log_file.unlink()
                except OSError:
                    continue
                    
        except Exception:
            # Ignore cleanup errors
            pass


# Convenience functions
def get_logger(name: Optional[str] = None) -> logging.Logger:
    """Get logger instance."""
    return Logger.get_logger(name)


def setup_logging(level: Optional[str] = None, 
                 log_to_file: bool = True,
                 log_directory: Optional[str] = None) -> logging.Logger:
    """Setup application logging."""
    return Logger.setup(level=level, log_to_file=log_to_file, log_directory=log_directory)


def log_system_info(logger: Optional[logging.Logger] = None) -> None:
    """Log system information for debugging."""
    
    if logger is None:
        logger = get_logger()
    
    logger.info("=== MP3 to MP4 Converter Started ===")
    logger.info(f"Python version: {sys.version}")
    logger.info(f"Platform: {sys.platform}")
    logger.info(f"Working directory: {os.getcwd()}")
    logger.info(f"Log file: {Logger.get_log_file_path()}")
    
    # Log environment variables (filtered)
    env_vars = ["LOG_LEVEL", "DEVELOPMENT", "PYTHONPATH"]
    for var in env_vars:
        value = os.environ.get(var)
        if value:
            logger.info(f"Environment {var}: {value}")


def log_application_shutdown(logger: Optional[logging.Logger] = None) -> None:
    """Log application shutdown."""
    
    if logger is None:
        logger = get_logger()
    
    logger.info("=== MP3 to MP4 Converter Shutdown ===")
    
    # Cleanup old logs
    Logger.cleanup_old_logs()


class PerformanceTimer:
    """Context manager for timing operations."""
    
    def __init__(self, operation_name: str, logger: Optional[logging.Logger] = None):
        self.operation_name = operation_name
        self.logger = logger or get_logger()
        self.start_time = None
    
    def __enter__(self):
        self.start_time = datetime.now()
        self.logger.debug(f"Starting: {self.operation_name}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time:
            duration = datetime.now() - self.start_time
            duration_ms = duration.total_seconds() * 1000
            
            if exc_type:
                self.logger.error(f"Failed: {self.operation_name} ({duration_ms:.1f}ms)")
            else:
                self.logger.debug(f"Completed: {self.operation_name} ({duration_ms:.1f}ms)")


# Performance timing decorator
def timed_operation(operation_name: str):
    """Decorator to time function execution."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            with PerformanceTimer(operation_name):
                return func(*args, **kwargs)
        return wrapper
    return decorator