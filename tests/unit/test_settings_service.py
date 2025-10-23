"""
Unit tests for SettingsService.
"""

import pytest
import json
import tempfile
from pathlib import Path
from src.services.settings_service import SettingsService, ApplicationSettings


def test_settings_service_initialization():
    """Test SettingsService initialization."""
    with tempfile.TemporaryDirectory() as temp_dir:
        service = SettingsService(config_dir=temp_dir)
        assert service.settings is not None
        assert isinstance(service.settings, ApplicationSettings)


def test_settings_default_values():
    """Test default settings values."""
    settings = ApplicationSettings()
    
    assert settings.output_folder is None
    assert settings.output_filename_template == "{original_name}"
    assert settings.video_resolution == "1280x720"
    assert settings.video_fps == 30
    assert settings.max_concurrent_conversions == 2


def test_settings_save_and_load():
    """Test settings persistence."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create and save settings
        service = SettingsService(config_dir=temp_dir)
        service.settings.output_folder = "/test/output"
        service.settings.max_concurrent_conversions = 3
        
        assert service.save()
        
        # Load settings in new instance
        service2 = SettingsService(config_dir=temp_dir)
        assert service2.settings.output_folder == "/test/output"
        assert service2.settings.max_concurrent_conversions == 3


def test_generate_output_path():
    """Test output path generation."""
    with tempfile.TemporaryDirectory() as temp_dir:
        service = SettingsService(config_dir=temp_dir)
        
        # Default: same directory
        input_path = "/test/audio.mp3"
        output_path = service.generate_output_path(input_path)
        assert output_path.endswith(".mp4")
        assert "audio" in output_path
        
        # Custom output folder
        service.settings.output_folder = temp_dir
        output_path = service.generate_output_path(input_path)
        assert output_path.startswith(temp_dir)


def test_settings_to_dict_and_from_dict():
    """Test settings serialization."""
    settings = ApplicationSettings(
        output_folder="/test",
        max_concurrent_conversions=5
    )
    
    # To dict
    data = settings.to_dict()
    assert data['output_folder'] == "/test"
    assert data['max_concurrent_conversions'] == 5
    
    # From dict
    settings2 = ApplicationSettings.from_dict(data)
    assert settings2.output_folder == "/test"
    assert settings2.max_concurrent_conversions == 5
