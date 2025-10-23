"""
Unit tests for AudioFile model.
"""

import pytest
import tempfile
from pathlib import Path
from src.models.audio_file import AudioFile


def test_audio_file_creation_from_dataclass():
    """Test basic AudioFile creation using dataclass."""
    from datetime import datetime
    
    audio_file = AudioFile(
        path="/test/path/audio.mp3",
        filename="audio.mp3",
        size_bytes=1024,
        duration_seconds=180.5,
        sample_rate=44100,
        bitrate=320,
        metadata={},
        created_at=datetime.now(),
        is_valid=True
    )
    
    assert audio_file.path == "/test/path/audio.mp3"
    assert audio_file.duration_seconds == 180.5
    assert audio_file.bitrate == 320
    assert audio_file.sample_rate == 44100
    assert audio_file.filename == "audio.mp3"


def test_audio_file_from_path():
    """Test AudioFile creation from file path."""
    # Create temporary file
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_file:
        temp_path = temp_file.name
        temp_file.write(b"fake mp3 data")
    
    try:
        audio_file = AudioFile.from_path(temp_path)
        
        assert audio_file.path is not None
        assert audio_file.filename.endswith(".mp3")
        assert audio_file.size_bytes > 0
    finally:
        Path(temp_path).unlink(missing_ok=True)


def test_audio_file_from_path_not_found():
    """Test AudioFile creation with non-existent file."""
    with pytest.raises(FileNotFoundError):
        AudioFile.from_path("/nonexistent/path/audio.mp3")


def test_audio_file_extension_property():
    """Test extension property."""
    from datetime import datetime
    
    audio_file = AudioFile(
        path="/path/to/my_song.mp3",
        filename="my_song.mp3",
        size_bytes=1024,
        duration_seconds=100.0,
        sample_rate=44100,
        bitrate=320,
        metadata={},
        created_at=datetime.now(),
        is_valid=True
    )
    
    assert audio_file.extension == ".mp3"
