# Data Model: Drag & Drop MP3 to MP4 Conversion

**Feature**: 001-drag-drop-mp3-conversion  
**Phase**: 1 - Design & Contracts  
**Date**: 2025-10-23

## Entities

### AudioFile

Represents an input MP3 file for conversion.

**Attributes**:
- `path: str` - Absolute file path to the MP3 file
- `filename: str` - Original filename without path
- `size_bytes: int` - File size in bytes
- `duration_seconds: float` - Audio duration in seconds
- `sample_rate: int` - Audio sample rate (e.g., 44100 Hz)
- `bitrate: int` - Audio bitrate in kbps (e.g., 320)
- `metadata: dict` - Audio metadata (title, artist, album, etc.)
- `created_at: datetime` - When the file object was created
- `is_valid: bool` - Whether file passed validation

**Validation Rules**:
- File must exist and be readable
- File extension must be .mp3 (case-insensitive)
- File size must be > 0 and < 2GB
- Must contain valid MP3 header
- Duration must be > 0 seconds

**State Transitions**:
1. `Created` → `Validating` → `Valid`/`Invalid`
2. `Valid` → `Queued` → `Processing` → `Completed`/`Failed`

### VideoFile

Represents the output MP4 file after conversion.

**Attributes**:
- `path: str` - Absolute file path for the output MP4
- `filename: str` - Generated filename (based on input + suffix)
- `source_audio_file: AudioFile` - Reference to source audio file
- `video_width: int` - Video dimensions width (default: 1280)
- `video_height: int` - Video dimensions height (default: 720)
- `video_fps: int` - Frames per second (default: 30)
- `created_at: datetime` - When conversion completed
- `file_size_bytes: int` - Output file size

**Business Rules**:
- Output filename format: `{original_name}_video.mp4`
- Default output location: same directory as input file
- Video track is solid black with no content
- Audio track preserves original quality and metadata
- File overwrites existing files with same name (with user confirmation)

### ConversionJob

Represents a conversion task from MP3 to MP4.

**Attributes**:
- `id: str` - Unique identifier (UUID)
- `audio_file: AudioFile` - Input file reference
- `video_file: VideoFile` - Output file reference (created during processing)
- `status: ConversionStatus` - Current job status
- `progress_percent: float` - Conversion progress (0.0 to 100.0)
- `started_at: datetime` - When conversion began
- `completed_at: datetime` - When conversion finished (success or failure)
- `error_message: str` - Error details if failed
- `can_cancel: bool` - Whether job can be cancelled
- `estimated_remaining_seconds: int` - Time estimate for completion

**Status Enum**:
```python
class ConversionStatus(Enum):
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
```

**State Transitions**:
1. `QUEUED` → `PROCESSING` → `COMPLETED`/`FAILED`
2. `QUEUED`/`PROCESSING` → `CANCELLED` (user action)

**Business Rules**:
- Maximum 50 concurrent jobs in queue
- Jobs process sequentially (no parallel conversion)
- Failed jobs retain error information for troubleshooting
- Cancelled jobs clean up temporary files
- Progress updates at least every 2 seconds during processing

### ApplicationState

Represents the overall application state and configuration.

**Attributes**:
- `active_jobs: List[ConversionJob]` - Currently queued/processing jobs
- `completed_jobs: List[ConversionJob]` - Recently completed jobs (last 20)
- `output_directory: str` - Default output directory (optional override)
- `max_concurrent_jobs: int` - Maximum simultaneous conversions (default: 1)
- `preserve_metadata: bool` - Whether to copy MP3 metadata to MP4
- `video_quality: str` - Output video quality setting ("low", "medium", "high")
- `last_used_directory: str` - Remember last input directory for file dialogs

**Configuration Rules**:
- Settings persist between application sessions
- Output directory defaults to same as input file location
- Video quality affects file size but not audio quality
- Maximum 20 completed jobs stored in memory (FIFO cleanup)

## Relationships

- `ConversionJob` → `AudioFile` (1:1, composition)
- `ConversionJob` → `VideoFile` (1:1, composition)
- `ApplicationState` → `ConversionJob` (1:many, aggregation)
- `VideoFile` → `AudioFile` (1:1, reference to source)

## Error Handling

### File Validation Errors
- **Invalid format**: "File is not a valid MP3 audio file"
- **File too large**: "File exceeds 2GB size limit"
- **Corrupted file**: "MP3 file appears to be corrupted or incomplete"
- **Access denied**: "Cannot read file - check file permissions"

### Conversion Errors
- **Disk space**: "Insufficient disk space for output file"
- **FFmpeg error**: "Audio conversion failed: {technical_details}"
- **Write permission**: "Cannot write to output directory"
- **Resource exhaustion**: "System resources insufficient for conversion"

### Recovery Strategies
- Validate files before queuing to catch errors early
- Retry failed jobs with different quality settings
- Clean up partial output files on failure
- Provide user-friendly error messages with suggested actions