"""
File List Widget - Display added MP3 files with status.
"""

import tkinter as tk
import customtkinter as ctk
from typing import List, Optional, Callable, Dict
from pathlib import Path
from dataclasses import dataclass
from enum import Enum

from ...models.audio_file import AudioFile
from ...models.conversion_job import ConversionJob, ConversionStatus
from ...utils.logger import get_logger


class FileItemStatus(Enum):
    """Status of file item in the list."""
    PENDING = "pending"
    VALIDATING = "validating"
    READY = "ready"
    CONVERTING = "converting"
    COMPLETED = "completed"
    ERROR = "error"


@dataclass
class FileListItem:
    """Represents a file in the list."""
    file_path: str
    audio_file: Optional[AudioFile] = None
    conversion_job: Optional[ConversionJob] = None
    status: FileItemStatus = FileItemStatus.PENDING
    error_message: Optional[str] = None
    
    @property
    def filename(self) -> str:
        """Get filename from path."""
        return Path(self.file_path).name
    
    @property
    def size_mb(self) -> float:
        """Get file size in MB."""
        try:
            size_bytes = Path(self.file_path).stat().st_size
            return size_bytes / (1024 * 1024)
        except:
            return 0.0
    
    @property
    def progress(self) -> float:
        """Get conversion progress (0-100)."""
        if self.conversion_job:
            return self.conversion_job.progress
        return 0.0


class FileListWidget(ctk.CTkScrollableFrame):
    """Scrollable list of MP3 files with status."""
    
    def __init__(self,
                 parent,
                 on_remove_file: Optional[Callable[[str], None]] = None,
                 **kwargs):
        """
        Initialize file list widget.
        
        Args:
            parent: Parent widget
            on_remove_file: Callback when file is removed (receives file path)
            **kwargs: Additional frame arguments
        """
        super().__init__(parent, **kwargs)
        
        self.logger = get_logger("FileListWidget")
        self._on_remove_file = on_remove_file
        
        # File items storage
        self._items: Dict[str, FileListItem] = {}  # file_path -> FileListItem
        self._item_widgets: Dict[str, ctk.CTkFrame] = {}  # file_path -> widget frame
        
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        
        # Empty state label
        self._create_empty_state()
        
        self.logger.debug("File list widget initialized")
    
    def _create_empty_state(self) -> None:
        """Create empty state display."""
        self.empty_label = ctk.CTkLabel(
            self,
            text="ファイルが追加されていません\n\n上のエリアにMP3ファイルをドロップしてください",
            font=ctk.CTkFont(size=14),
            text_color="gray",
            justify="center"
        )
        self.empty_label.grid(row=0, column=0, pady=50)
    
    def _hide_empty_state(self) -> None:
        """Hide empty state label."""
        if self.empty_label:
            self.empty_label.grid_remove()
    
    def _show_empty_state(self) -> None:
        """Show empty state label."""
        if self.empty_label and len(self._items) == 0:
            self.empty_label.grid()
    
    def add_file(self, file_path: str) -> FileListItem:
        """
        Add file to the list.
        
        Args:
            file_path: Absolute path to the file
            
        Returns:
            Created FileListItem
        """
        # Check if already exists
        if file_path in self._items:
            self.logger.debug(f"File already in list: {file_path}")
            return self._items[file_path]
        
        # Create item
        item = FileListItem(
            file_path=file_path,
            status=FileItemStatus.PENDING
        )
        self._items[file_path] = item
        
        # Create widget
        self._create_item_widget(item)
        
        # Hide empty state
        self._hide_empty_state()
        
        self.logger.info(f"Added file to list: {Path(file_path).name}")
        return item
    
    def remove_file(self, file_path: str) -> None:
        """
        Remove file from the list.
        
        Args:
            file_path: Path of file to remove
        """
        if file_path not in self._items:
            return
        
        # Remove widget
        if file_path in self._item_widgets:
            self._item_widgets[file_path].destroy()
            del self._item_widgets[file_path]
        
        # Remove item
        del self._items[file_path]
        
        # Show empty state if needed
        self._show_empty_state()
        
        # Call callback
        if self._on_remove_file:
            try:
                self._on_remove_file(file_path)
            except Exception as e:
                self.logger.error(f"Error in remove callback: {e}")
        
        self.logger.info(f"Removed file from list: {Path(file_path).name}")
    
    def update_item_status(self, 
                          file_path: str, 
                          status: FileItemStatus,
                          error_message: Optional[str] = None) -> None:
        """Update file item status."""
        if file_path not in self._items:
            return
        
        item = self._items[file_path]
        item.status = status
        item.error_message = error_message
        
        # Update widget
        self._update_item_widget(file_path)
    
    def update_item_progress(self, file_path: str, progress: float) -> None:
        """Update conversion progress."""
        if file_path not in self._items:
            return
        
        item = self._items[file_path]
        if item.conversion_job:
            # Progress will be read from conversion_job
            pass
        
        # Update widget
        self._update_item_widget(file_path)
    
    def set_audio_file(self, file_path: str, audio_file: AudioFile) -> None:
        """Set AudioFile for item."""
        if file_path in self._items:
            self._items[file_path].audio_file = audio_file
            self._update_item_widget(file_path)
    
    def set_conversion_job(self, file_path: str, job: ConversionJob) -> None:
        """Set ConversionJob for item."""
        if file_path in self._items:
            self._items[file_path].conversion_job = job
            self._update_item_widget(file_path)
    
    def get_all_items(self) -> List[FileListItem]:
        """Get all file items."""
        return list(self._items.values())
    
    def clear(self) -> None:
        """Clear all items from list."""
        for file_path in list(self._items.keys()):
            self.remove_file(file_path)
    
    def _create_item_widget(self, item: FileListItem) -> None:
        """Create widget for file item."""
        
        row = len(self._item_widgets)
        
        # Item frame
        item_frame = ctk.CTkFrame(
            self,
            fg_color="transparent",
            border_width=1,
            border_color="gray",
            corner_radius=8
        )
        item_frame.grid(row=row, column=0, sticky="ew", pady=5, padx=5)
        item_frame.grid_columnconfigure(1, weight=1)
        
        # Status icon
        status_label = ctk.CTkLabel(
            item_frame,
            text=self._get_status_icon(item.status),
            font=ctk.CTkFont(size=20),
            width=40
        )
        status_label.grid(row=0, column=0, padx=(10, 5), pady=10, rowspan=2)
        
        # Filename
        filename_label = ctk.CTkLabel(
            item_frame,
            text=item.filename,
            font=ctk.CTkFont(size=13, weight="bold"),
            anchor="w"
        )
        filename_label.grid(row=0, column=1, sticky="w", padx=5, pady=(10, 2))
        
        # File info / status text
        info_text = self._get_info_text(item)
        info_label = ctk.CTkLabel(
            item_frame,
            text=info_text,
            font=ctk.CTkFont(size=11),
            text_color="gray",
            anchor="w"
        )
        info_label.grid(row=1, column=1, sticky="w", padx=5, pady=(2, 10))
        
        # Progress bar (initially hidden)
        progress_bar = ctk.CTkProgressBar(
            item_frame,
            width=150,
            height=8
        )
        progress_bar.set(0)
        progress_bar.grid(row=0, column=2, padx=10, pady=5, rowspan=2)
        progress_bar.grid_remove()  # Hide initially
        
        # Remove button
        remove_button = ctk.CTkButton(
            item_frame,
            text="✕",
            width=30,
            height=30,
            font=ctk.CTkFont(size=16),
            fg_color="transparent",
            hover_color="red",
            command=lambda: self.remove_file(item.file_path)
        )
        remove_button.grid(row=0, column=3, padx=(5, 10), pady=5, rowspan=2)
        
        # Store widget references
        self._item_widgets[item.file_path] = item_frame
        item_frame._status_label = status_label
        item_frame._filename_label = filename_label
        item_frame._info_label = info_label
        item_frame._progress_bar = progress_bar
        item_frame._remove_button = remove_button
    
    def _update_item_widget(self, file_path: str) -> None:
        """Update existing item widget."""
        
        if file_path not in self._items or file_path not in self._item_widgets:
            return
        
        item = self._items[file_path]
        widget = self._item_widgets[file_path]
        
        # Update status icon
        widget._status_label.configure(text=self._get_status_icon(item.status))
        
        # Update info text
        widget._info_label.configure(text=self._get_info_text(item))
        
        # Update progress bar
        if item.status == FileItemStatus.CONVERTING:
            widget._progress_bar.grid()
            widget._progress_bar.set(item.progress / 100.0)
        else:
            widget._progress_bar.grid_remove()
        
        # Update border color based on status
        if item.status == FileItemStatus.ERROR:
            widget.configure(border_color="red")
        elif item.status == FileItemStatus.COMPLETED:
            widget.configure(border_color="green")
        else:
            widget.configure(border_color="gray")
    
    def _get_status_icon(self, status: FileItemStatus) -> str:
        """Get emoji icon for status."""
        icons = {
            FileItemStatus.PENDING: "⏳",
            FileItemStatus.VALIDATING: "🔍",
            FileItemStatus.READY: "✓",
            FileItemStatus.CONVERTING: "⚙️",
            FileItemStatus.COMPLETED: "✅",
            FileItemStatus.ERROR: "❌"
        }
        return icons.get(status, "⏳")
    
    def _get_info_text(self, item: FileListItem) -> str:
        """Get info text for item."""
        
        if item.error_message:
            return f"エラー: {item.error_message}"
        
        if item.status == FileItemStatus.VALIDATING:
            return "検証中..."
        
        if item.status == FileItemStatus.CONVERTING:
            return f"変換中... {item.progress:.0f}%"
        
        if item.status == FileItemStatus.COMPLETED:
            return "変換完了"
        
        # Show file info
        info_parts = [f"{item.size_mb:.1f} MB"]
        
        if item.audio_file:
            if item.audio_file.duration:
                duration_min = int(item.audio_file.duration // 60)
                duration_sec = int(item.audio_file.duration % 60)
                info_parts.append(f"{duration_min}:{duration_sec:02d}")
            
            if item.audio_file.bitrate:
                info_parts.append(f"{item.audio_file.bitrate} kbps")
        
        return " • ".join(info_parts)
