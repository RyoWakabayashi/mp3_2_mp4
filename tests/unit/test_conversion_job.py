"""
Unit tests for ConversionJob model.
"""

import pytest
from datetime import datetime
from src.models.audio_file import AudioFile
from src.models.video_file import VideoFile
from src.models.conversion_job import ConversionJob, ConversionStatus


def _create_test_audio_file() -> AudioFile:
    """Helper to create test audio file."""
    return AudioFile(
        path="/test/audio.mp3",
        filename="audio.mp3",
        size_bytes=1024,
        duration_seconds=100.0,
        sample_rate=44100,
        bitrate=320,
        metadata={},
        created_at=datetime.now(),
        is_valid=True
    )


def _create_test_video_file() -> VideoFile:
    """Helper to create test video file."""
    return VideoFile(
        path="/test/output.mp4",
        filename="output.mp4",
        source_audio_file=None,
        video_width=1280,
        video_height=720,
        video_fps=30,
        created_at=datetime.now(),
        file_size_bytes=0
    )


def test_conversion_job_creation():
    """Test ConversionJob creation."""
    audio_file = _create_test_audio_file()
    video_file = _create_test_video_file()
    
    job = ConversionJob(audio_file=audio_file, video_file=video_file)
    
    assert job.audio_file == audio_file
    assert job.video_file == video_file
    assert job.status == ConversionStatus.QUEUED
    assert job.progress_percent == 0.0
    assert job.error_message is None


def test_conversion_job_lifecycle():
    """Test ConversionJob status transitions."""
    audio_file = _create_test_audio_file()
    video_file = _create_test_video_file()
    job = ConversionJob(audio_file=audio_file, video_file=video_file)
    
    # Start
    job.start_processing()
    assert job.status == ConversionStatus.PROCESSING
    assert job.is_active
    
    # Update progress
    job.update_progress(50.0)
    assert job.progress_percent == 50.0
    
    # Complete
    job.complete_success()
    assert job.status == ConversionStatus.COMPLETED
    assert not job.is_active
    assert job.is_finished
    assert job.progress_percent == 100.0


def test_conversion_job_error():
    """Test ConversionJob error handling."""
    audio_file = _create_test_audio_file()
    video_file = _create_test_video_file()
    job = ConversionJob(audio_file=audio_file, video_file=video_file)
    
    job.start_processing()
    job.complete_failure("Test error message")
    
    assert job.status == ConversionStatus.FAILED
    assert job.error_message == "Test error message"
    assert job.is_finished
    assert not job.can_cancel


def test_conversion_job_cancel():
    """Test ConversionJob cancellation."""
    audio_file = _create_test_audio_file()
    video_file = _create_test_video_file()
    job = ConversionJob(audio_file=audio_file, video_file=video_file)
    
    job.start_processing()
    result = job.cancel()
    
    assert result is True
    assert job.status == ConversionStatus.CANCELLED
    assert job.is_finished
    assert not job.can_cancel


def test_conversion_job_create_for_audio_file():
    """Test creating job from audio file."""
    audio_file = _create_test_audio_file()
    job = ConversionJob.create_for_audio_file(audio_file)
    
    assert job.audio_file == audio_file
    assert job.video_file is not None
    assert job.video_file.source_audio_file == audio_file
    assert job.status == ConversionStatus.QUEUED
