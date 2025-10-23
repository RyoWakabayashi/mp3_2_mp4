# API Contracts: Drag & Drop MP3 to MP4 Conversion

**Feature**: 001-drag-drop-mp3-conversion  
**Phase**: 1 - Design & Contracts  
**Date**: 2025-10-23

## Internal API Interfaces

Since this is a desktop application, these represent internal function signatures and events rather than REST endpoints.

### File Processing Interface

#### validate_audio_file()
```python
def validate_audio_file(file_path: str) -> ValidationResult:
    """
    Validate an MP3 file for conversion eligibility.
    
    Args:
        file_path: Absolute path to the MP3 file
        
    Returns:
        ValidationResult with is_valid flag and error details
        
    Raises:
        FileNotFoundError: If file doesn't exist
        PermissionError: If file cannot be read
    """
```

**Input Contract**:
- `file_path` must be absolute path string
- File must exist and be readable
- File extension should be .mp3 (case-insensitive)

**Output Contract**:
```python
@dataclass
class ValidationResult:
    is_valid: bool
    file_size_bytes: int
    duration_seconds: float
    sample_rate: int
    bitrate: int
    metadata: dict
    error_message: Optional[str]
```

#### create_conversion_job()
```python
def create_conversion_job(
    audio_file: AudioFile, 
    output_directory: Optional[str] = None
) -> ConversionJob:
    """
    Create a new conversion job for MP3 to MP4.
    
    Args:
        audio_file: Validated AudioFile instance
        output_directory: Optional custom output location
        
    Returns:
        ConversionJob with QUEUED status
    """
```

#### start_conversion()
```python
def start_conversion(
    job: ConversionJob,
    progress_callback: Callable[[float], None],
    completion_callback: Callable[[ConversionResult], None]
) -> None:
    """
    Start asynchronous conversion process.
    
    Args:
        job: ConversionJob to process
        progress_callback: Called with progress percentage (0.0-100.0)
        completion_callback: Called when conversion finishes
    """
```

**Progress Callback Contract**:
- Called every 1-2 seconds during conversion
- Parameter is float between 0.0 and 100.0
- Should not block or perform heavy operations

**Completion Callback Contract**:
```python
@dataclass
class ConversionResult:
    job_id: str
    success: bool
    output_file_path: Optional[str]
    error_message: Optional[str]
    processing_time_seconds: float
```

### GUI Event Interface

#### on_files_dropped()
```python
def on_files_dropped(file_paths: List[str]) -> None:
    """
    Handle drag-and-drop of files onto the application.
    
    Args:
        file_paths: List of absolute file paths dropped by user
        
    Side Effects:
        - Validates each file
        - Creates conversion jobs for valid MP3 files
        - Updates UI with validation results
        - Shows error messages for invalid files
    """
```

**Contract Requirements**:
- Must handle empty list gracefully
- Must validate all files before creating any jobs
- Must provide user feedback for each file (success/error)
- Must not freeze UI during validation

#### on_conversion_progress()
```python
def on_conversion_progress(job_id: str, progress: float) -> None:
    """
    Update UI with conversion progress.
    
    Args:
        job_id: Unique identifier for the conversion job
        progress: Completion percentage (0.0-100.0)
    """
```

#### on_conversion_complete()
```python
def on_conversion_complete(result: ConversionResult) -> None:
    """
    Handle conversion completion or failure.
    
    Args:
        result: ConversionResult with success/failure details
        
    Side Effects:
        - Updates UI to show completion status
        - Shows success message with output file location
        - Shows error message if conversion failed
        - Removes job from active queue
    """
```

### Configuration Interface

#### get_application_settings()
```python
def get_application_settings() -> ApplicationSettings:
    """
    Retrieve current application configuration.
    
    Returns:
        ApplicationSettings with user preferences
    """
```

#### save_application_settings()
```python
def save_application_settings(settings: ApplicationSettings) -> None:
    """
    Persist application configuration.
    
    Args:
        settings: ApplicationSettings to save
        
    Side Effects:
        - Saves settings to local configuration file
        - Settings persist between application restarts
    """
```

**Settings Contract**:
```python
@dataclass
class ApplicationSettings:
    default_output_directory: Optional[str]
    preserve_metadata: bool = True
    video_quality: str = "medium"  # "low", "medium", "high"
    max_concurrent_jobs: int = 1
    window_width: int = 800
    window_height: int = 600
    last_used_directory: Optional[str] = None
```

## Error Handling Contracts

### Exception Hierarchy
```python
class ConversionError(Exception):
    """Base exception for conversion-related errors."""
    pass

class FileValidationError(ConversionError):
    """Raised when MP3 file validation fails."""
    pass

class ConversionProcessError(ConversionError):
    """Raised when FFmpeg conversion process fails."""
    pass

class InsufficientSpaceError(ConversionError):
    """Raised when insufficient disk space for output."""
    pass
```

### Error Response Format
All error conditions should be handled gracefully with user-friendly messages:

```python
@dataclass
class ErrorInfo:
    code: str  # Machine-readable error code
    message: str  # User-friendly error message
    technical_details: Optional[str]  # Debug information
    suggested_action: Optional[str]  # What user can do
```

**Standard Error Codes**:
- `FILE_NOT_FOUND`: Input file doesn't exist
- `FILE_INVALID_FORMAT`: Not a valid MP3 file
- `FILE_CORRUPTED`: MP3 file is damaged
- `DISK_SPACE_LOW`: Insufficient space for output
- `PERMISSION_DENIED`: Cannot read input or write output
- `CONVERSION_FAILED`: FFmpeg process failed
- `OPERATION_CANCELLED`: User cancelled the operation

## Testing Contracts

### Unit Test Interfaces
Each API function must have corresponding test cases that verify:
- Valid input handling
- Invalid input rejection with appropriate errors
- Edge cases and boundary conditions
- Callback invocation with correct parameters

### Integration Test Scenarios
- End-to-end file conversion with real MP3 samples
- GUI automation tests for drag-and-drop workflows
- Cross-platform compatibility testing
- Performance benchmarks with various file sizes

### Mock Interfaces
For testing, provide mock implementations that:
- Simulate FFmpeg behavior without actual conversion
- Generate predictable progress updates
- Allow testing of error conditions
- Support automated GUI testing scenarios