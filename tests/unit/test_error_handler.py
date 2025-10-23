"""
Unit tests for ErrorHandler.
"""

import pytest
from src.utils.error_handler import (
    ErrorHandler, 
    ErrorCode, 
    ErrorInfo
)


def test_error_handler_creation():
    """Test ErrorHandler initialization."""
    handler = ErrorHandler()
    assert handler is not None


def test_error_code_enum():
    """Test ErrorCode enumeration."""
    assert ErrorCode.FILE_NOT_FOUND.value == "FILE_NOT_FOUND"
    assert ErrorCode.FILE_INVALID_FORMAT.value == "FILE_INVALID_FORMAT"
    assert ErrorCode.CONVERSION_FAILED.value == "CONVERSION_FAILED"
    assert ErrorCode.SYSTEM_ERROR.value == "SYSTEM_ERROR"


def test_error_info_creation():
    """Test ErrorInfo dataclass creation."""
    error_info = ErrorInfo(
        code=ErrorCode.FILE_NOT_FOUND,
        message="File not found",
        technical_details="Path /test/file.mp3 does not exist",
        suggested_action="Check the file path",
        context={"path": "/test/file.mp3"}
    )
    
    assert error_info.code == ErrorCode.FILE_NOT_FOUND
    assert error_info.message == "File not found"
    assert error_info.technical_details == "Path /test/file.mp3 does not exist"
    assert error_info.suggested_action == "Check the file path"
    assert error_info.context["path"] == "/test/file.mp3"


def test_error_handler_create_error_info():
    """Test creating error info with user-friendly messages."""
    error_info = ErrorHandler.create_error_info(
        code=ErrorCode.FILE_NOT_FOUND,
        technical_details="Test details"
    )
    
    assert error_info.code == ErrorCode.FILE_NOT_FOUND
    assert "ファイル" in error_info.message  # Japanese message
    assert error_info.technical_details == "Test details"
    assert error_info.suggested_action is not None


def test_error_handler_handle_exception():
    """Test exception to ErrorInfo conversion."""
    # Test with FileNotFoundError
    try:
        raise FileNotFoundError("Test file not found")
    except Exception as e:
        error_info = ErrorHandler.handle_exception(e)
        assert error_info.code == ErrorCode.FILE_NOT_FOUND
        assert "FileNotFoundError" in error_info.technical_details
    
    # Test with PermissionError
    try:
        raise PermissionError("Permission denied")
    except Exception as e:
        error_info = ErrorHandler.handle_exception(e)
        assert error_info.code == ErrorCode.FILE_PERMISSION_DENIED
    
    # Test with generic Exception
    try:
        raise Exception("Generic error")
    except Exception as e:
        error_info = ErrorHandler.handle_exception(e)
        assert error_info.code == ErrorCode.SYSTEM_ERROR


def test_error_handler_format_error_message():
    """Test error message formatting."""
    error_info = ErrorInfo(
        code=ErrorCode.FILE_NOT_FOUND,
        message="ファイルが見つかりません",
        technical_details="FileNotFoundError: /test/file.mp3",
        suggested_action="ファイルの存在を確認してください"
    )
    
    # Without technical details
    msg = ErrorHandler.format_error_message(error_info, include_technical=False)
    assert "ファイルが見つかりません" in msg
    assert "ファイルの存在を確認してください" in msg
    assert "FileNotFoundError" not in msg
    
    # With technical details
    msg = ErrorHandler.format_error_message(error_info, include_technical=True)
    assert "FileNotFoundError" in msg
