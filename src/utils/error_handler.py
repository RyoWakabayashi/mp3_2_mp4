"""
Error Handling Framework - User-friendly error messages and handling.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional, Dict, Any
import traceback


class ErrorCode(Enum):
    """Standard error codes for the application."""
    
    # File related errors
    FILE_NOT_FOUND = "FILE_NOT_FOUND"
    FILE_INVALID_FORMAT = "FILE_INVALID_FORMAT"
    FILE_CORRUPTED = "FILE_CORRUPTED"
    FILE_TOO_LARGE = "FILE_TOO_LARGE"
    FILE_PERMISSION_DENIED = "FILE_PERMISSION_DENIED"
    
    # Conversion errors
    CONVERSION_FAILED = "CONVERSION_FAILED"
    FFMPEG_NOT_AVAILABLE = "FFMPEG_NOT_AVAILABLE"
    DISK_SPACE_LOW = "DISK_SPACE_LOW"
    
    # System errors
    SYSTEM_ERROR = "SYSTEM_ERROR"
    OPERATION_CANCELLED = "OPERATION_CANCELLED"
    RESOURCE_EXHAUSTED = "RESOURCE_EXHAUSTED"
    
    # Configuration errors
    INVALID_SETTINGS = "INVALID_SETTINGS"
    OUTPUT_DIRECTORY_INVALID = "OUTPUT_DIRECTORY_INVALID"


@dataclass
class ErrorInfo:
    """Detailed error information with user-friendly messages."""
    
    code: ErrorCode
    message: str
    technical_details: Optional[str] = None
    suggested_action: Optional[str] = None
    context: Optional[Dict[str, Any]] = None


class ErrorHandler:
    """Central error handling and message generation."""
    
    # User-friendly error messages
    ERROR_MESSAGES = {
        ErrorCode.FILE_NOT_FOUND: {
            "message": "ファイルが見つかりません",
            "action": "ファイルが存在することを確認してから、もう一度お試しください。"
        },
        ErrorCode.FILE_INVALID_FORMAT: {
            "message": "サポートされていないファイル形式です",
            "action": "MP3ファイルのみサポートされています。ファイル形式を確認してください。"
        },
        ErrorCode.FILE_CORRUPTED: {
            "message": "ファイルが破損している可能性があります",
            "action": "別のMP3ファイルをお試しいただくか、元のファイルを確認してください。"
        },
        ErrorCode.FILE_TOO_LARGE: {
            "message": "ファイルサイズが大きすぎます",
            "action": "2GB以下のファイルをご利用ください。"
        },
        ErrorCode.FILE_PERMISSION_DENIED: {
            "message": "ファイルにアクセスできません",
            "action": "ファイルの読み取り権限を確認してください。"
        },
        ErrorCode.CONVERSION_FAILED: {
            "message": "変換処理に失敗しました",
            "action": "しばらく時間をおいてから再度お試しください。"
        },
        ErrorCode.FFMPEG_NOT_AVAILABLE: {
            "message": "変換ソフトウェアが利用できません",
            "action": "アプリケーションを再起動してお試しください。"
        },
        ErrorCode.DISK_SPACE_LOW: {
            "message": "ディスク容量が不足しています",
            "action": "ディスクの空き容量を増やしてからお試しください。"
        },
        ErrorCode.SYSTEM_ERROR: {
            "message": "システムエラーが発生しました",
            "action": "アプリケーションを再起動してお試しください。"
        },
        ErrorCode.OPERATION_CANCELLED: {
            "message": "操作がキャンセルされました",
            "action": "必要に応じて操作を再開してください。"
        },
        ErrorCode.RESOURCE_EXHAUSTED: {
            "message": "システムリソースが不足しています",
            "action": "他のアプリケーションを終了してからお試しください。"
        },
        ErrorCode.INVALID_SETTINGS: {
            "message": "設定に問題があります",
            "action": "設定を確認して修正してください。"
        },
        ErrorCode.OUTPUT_DIRECTORY_INVALID: {
            "message": "出力先フォルダに問題があります",
            "action": "書き込み可能なフォルダを選択してください。"
        }
    }
    
    @classmethod
    def create_error_info(cls, 
                         code: ErrorCode, 
                         technical_details: Optional[str] = None,
                         context: Optional[Dict[str, Any]] = None) -> ErrorInfo:
        """Create ErrorInfo with user-friendly message."""
        
        error_config = cls.ERROR_MESSAGES.get(code, {
            "message": "予期しないエラーが発生しました",
            "action": "アプリケーションを再起動してお試しください。"
        })
        
        return ErrorInfo(
            code=code,
            message=error_config["message"],
            technical_details=technical_details,
            suggested_action=error_config["action"],
            context=context or {}
        )
    
    @classmethod
    def handle_exception(cls, 
                        exception: Exception,
                        context: Optional[Dict[str, Any]] = None) -> ErrorInfo:
        """Convert an exception to ErrorInfo."""
        
        # Map common exceptions to error codes
        if isinstance(exception, FileNotFoundError):
            code = ErrorCode.FILE_NOT_FOUND
        elif isinstance(exception, PermissionError):
            code = ErrorCode.FILE_PERMISSION_DENIED
        elif isinstance(exception, OSError):
            code = ErrorCode.SYSTEM_ERROR
        elif isinstance(exception, ValueError):
            code = ErrorCode.INVALID_SETTINGS
        else:
            code = ErrorCode.SYSTEM_ERROR
        
        # Get technical details
        technical_details = f"{type(exception).__name__}: {str(exception)}"
        
        return cls.create_error_info(
            code=code,
            technical_details=technical_details,
            context=context
        )
    
    @classmethod
    def format_error_message(cls, error_info: ErrorInfo, include_technical: bool = False) -> str:
        """Format error message for display."""
        
        message = error_info.message
        
        if error_info.suggested_action:
            message += f"\n\n{error_info.suggested_action}"
        
        if include_technical and error_info.technical_details:
            message += f"\n\n技術的詳細: {error_info.technical_details}"
        
        return message
    
    @classmethod
    def log_error(cls, error_info: ErrorInfo, logger=None) -> None:
        """Log error information."""
        
        log_message = f"Error [{error_info.code.value}]: {error_info.message}"
        
        if error_info.technical_details:
            log_message += f" | Technical: {error_info.technical_details}"
        
        if error_info.context:
            log_message += f" | Context: {error_info.context}"
        
        if logger:
            logger.error(log_message)
        else:
            # Fallback to print if no logger available
            print(f"ERROR: {log_message}")


class ConversionError(Exception):
    """Base exception for conversion-related errors."""
    
    def __init__(self, message: str, error_code: ErrorCode = ErrorCode.CONVERSION_FAILED):
        super().__init__(message)
        self.error_code = error_code


class FileValidationError(ConversionError):
    """Raised when file validation fails."""
    
    def __init__(self, message: str, file_path: Optional[str] = None):
        super().__init__(message, ErrorCode.FILE_INVALID_FORMAT)
        self.file_path = file_path


class ConversionProcessError(ConversionError):
    """Raised when conversion process fails."""
    
    def __init__(self, message: str, ffmpeg_output: Optional[str] = None):
        super().__init__(message, ErrorCode.CONVERSION_FAILED)
        self.ffmpeg_output = ffmpeg_output


class InsufficientSpaceError(ConversionError):
    """Raised when insufficient disk space for output."""
    
    def __init__(self, message: str, required_space: Optional[int] = None):
        super().__init__(message, ErrorCode.DISK_SPACE_LOW)
        self.required_space = required_space


class SafeErrorReporter:
    """Safe error reporting that doesn't crash the application."""
    
    @staticmethod
    def report_error(error_info: ErrorInfo, show_dialog: bool = True) -> None:
        """Report error safely without crashing."""
        try:
            # Log the error
            ErrorHandler.log_error(error_info)
            
            # Show dialog if requested (GUI will implement this)
            if show_dialog:
                # This will be implemented by the GUI layer
                pass
                
        except Exception as e:
            # Last resort - print to console
            print(f"CRITICAL: Error reporting failed: {e}")
            print(f"Original error: {error_info.message}")
    
    @staticmethod
    def safe_execute(func, *args, **kwargs) -> tuple[bool, Any, Optional[ErrorInfo]]:
        """
        Execute a function safely and return error info if it fails.
        
        Returns:
            tuple: (success, result, error_info)
        """
        try:
            result = func(*args, **kwargs)
            return True, result, None
        except Exception as e:
            error_info = ErrorHandler.handle_exception(e)
            return False, None, error_info