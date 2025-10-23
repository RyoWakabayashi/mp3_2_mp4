"""
Settings Service - Manages application settings with persistence.
"""

import json
import os
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import dataclass, asdict

from ..utils.logger import get_logger


@dataclass
class ApplicationSettings:
    """Application settings data."""
    
    # Output settings
    output_folder: Optional[str] = None  # None = same as input
    output_filename_template: str = "{original_name}"  # Template for output filename
    
    # Conversion settings
    video_resolution: str = "1280x720"  # Default resolution
    video_fps: int = 30  # Frames per second
    background_color: str = "#000000"  # Black background
    
    # UI settings
    window_width: int = 800
    window_height: int = 600
    theme: str = "System"  # System, Dark, Light
    
    # Advanced settings
    max_concurrent_conversions: int = 2
    auto_clear_on_complete: bool = False
    show_completion_notification: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ApplicationSettings':
        """Create from dictionary."""
        # Filter to only known fields
        valid_fields = {f for f in cls.__dataclass_fields__}
        filtered_data = {k: v for k, v in data.items() if k in valid_fields}
        return cls(**filtered_data)


class SettingsService:
    """Service for managing application settings."""
    
    def __init__(self, config_dir: Optional[str] = None):
        """
        Initialize settings service.
        
        Args:
            config_dir: Directory for config file. If None, uses default location.
        """
        self.logger = get_logger("SettingsService")
        
        # Determine config directory
        if config_dir is None:
            config_dir = self._get_default_config_dir()
        
        self.config_dir = Path(config_dir)
        self.config_file = self.config_dir / "settings.json"
        
        # Current settings
        self.settings = ApplicationSettings()
        
        # Create config directory if needed
        self._ensure_config_dir()
        
        # Load settings
        self.load()
        
        self.logger.info(f"Settings service initialized. Config: {self.config_file}")
    
    def _get_default_config_dir(self) -> str:
        """Get default configuration directory."""
        if os.name == 'nt':  # Windows
            base_dir = os.environ.get('APPDATA', os.path.expanduser('~'))
            return os.path.join(base_dir, 'MP3toMP4Converter')
        else:  # macOS/Linux
            return os.path.join(os.path.expanduser('~'), '.mp3_to_mp4')
    
    def _ensure_config_dir(self) -> None:
        """Ensure configuration directory exists."""
        try:
            self.config_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            self.logger.error(f"Could not create config directory: {e}")
    
    def load(self) -> bool:
        """
        Load settings from file.
        
        Returns:
            True if settings were loaded successfully
        """
        if not self.config_file.exists():
            self.logger.info("No settings file found, using defaults")
            return False
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.settings = ApplicationSettings.from_dict(data)
            self.logger.info("Settings loaded successfully")
            return True
            
        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON in settings file: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Error loading settings: {e}")
            return False
    
    def save(self) -> bool:
        """
        Save settings to file.
        
        Returns:
            True if settings were saved successfully
        """
        try:
            # Ensure directory exists
            self._ensure_config_dir()
            
            # Write settings
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings.to_dict(), f, indent=2, ensure_ascii=False)
            
            self.logger.info("Settings saved successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving settings: {e}")
            return False
    
    def reset_to_defaults(self) -> None:
        """Reset settings to defaults."""
        self.settings = ApplicationSettings()
        self.logger.info("Settings reset to defaults")
    
    def get_output_folder(self, default: Optional[str] = None) -> Optional[str]:
        """
        Get output folder setting.
        
        Args:
            default: Default value if not set
            
        Returns:
            Output folder path or None
        """
        return self.settings.output_folder or default
    
    def set_output_folder(self, folder: Optional[str]) -> None:
        """Set output folder."""
        self.settings.output_folder = folder
    
    def get_output_filename_template(self) -> str:
        """Get output filename template."""
        return self.settings.output_filename_template
    
    def set_output_filename_template(self, template: str) -> None:
        """Set output filename template."""
        self.settings.output_filename_template = template
    
    def generate_output_path(self, input_path: str, custom_name: Optional[str] = None) -> str:
        """
        Generate output path based on settings.
        
        Args:
            input_path: Input file path
            custom_name: Optional custom output name
            
        Returns:
            Full output path
        """
        input_path_obj = Path(input_path)
        
        # Determine output directory
        if self.settings.output_folder:
            output_dir = Path(self.settings.output_folder)
        else:
            output_dir = input_path_obj.parent
        
        # Determine output filename
        if custom_name:
            output_name = custom_name
        else:
            # Apply template
            template = self.settings.output_filename_template
            original_name = input_path_obj.stem
            
            # Simple template replacement
            output_name = template.replace("{original_name}", original_name)
            
            # Add timestamp if requested
            if "{timestamp}" in template:
                from datetime import datetime
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_name = output_name.replace("{timestamp}", timestamp)
        
        # Ensure .mp4 extension
        if not output_name.endswith('.mp4'):
            output_name += '.mp4'
        
        # Combine
        output_path = output_dir / output_name
        
        # Handle existing files
        if output_path.exists():
            counter = 1
            stem = Path(output_name).stem
            while output_path.exists():
                output_name_numbered = f"{stem}_{counter}.mp4"
                output_path = output_dir / output_name_numbered
                counter += 1
        
        return str(output_path)
    
    def get_video_settings(self) -> Dict[str, Any]:
        """Get video conversion settings."""
        return {
            'resolution': self.settings.video_resolution,
            'fps': self.settings.video_fps,
            'background_color': self.settings.background_color
        }
    
    def get_window_size(self) -> tuple[int, int]:
        """Get saved window size."""
        return (self.settings.window_width, self.settings.window_height)
    
    def set_window_size(self, width: int, height: int) -> None:
        """Save window size."""
        self.settings.window_width = width
        self.settings.window_height = height
    
    def get_theme(self) -> str:
        """Get UI theme setting."""
        return self.settings.theme
    
    def set_theme(self, theme: str) -> None:
        """Set UI theme."""
        if theme in ["System", "Dark", "Light"]:
            self.settings.theme = theme
    
    def get_max_concurrent_conversions(self) -> int:
        """Get maximum concurrent conversions."""
        return self.settings.max_concurrent_conversions
    
    def set_max_concurrent_conversions(self, count: int) -> None:
        """Set maximum concurrent conversions."""
        if 1 <= count <= 10:
            self.settings.max_concurrent_conversions = count
    
    def should_auto_clear_on_complete(self) -> bool:
        """Check if should auto-clear completed files."""
        return self.settings.auto_clear_on_complete
    
    def should_show_completion_notification(self) -> bool:
        """Check if should show completion notification."""
        return self.settings.show_completion_notification


# Global settings instance
_settings_service: Optional[SettingsService] = None


def get_settings_service() -> SettingsService:
    """Get global settings service instance."""
    global _settings_service
    if _settings_service is None:
        _settings_service = SettingsService()
    return _settings_service


def save_settings() -> bool:
    """Save current settings."""
    return get_settings_service().save()
