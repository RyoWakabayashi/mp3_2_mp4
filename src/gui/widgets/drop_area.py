"""
Drag and Drop Area Widget - Accept MP3 files via drag and drop.
"""

import tkinter as tk
from tkinter import filedialog
import customtkinter as ctk
from typing import Callable, List, Optional
from pathlib import Path

from ...utils.logger import get_logger


class DropArea(ctk.CTkFrame):
    """Drag and drop area for MP3 files."""
    
    def __init__(self, 
                 parent,
                 on_files_dropped: Optional[Callable[[List[str]], None]] = None,
                 **kwargs):
        """
        Initialize drop area.
        
        Args:
            parent: Parent widget
            on_files_dropped: Callback when files are dropped (receives list of file paths)
            **kwargs: Additional frame arguments
        """
        super().__init__(parent, **kwargs)
        
        self.logger = get_logger("DropArea")
        self._on_files_dropped = on_files_dropped
        self._is_dragging = False
        
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Create drop zone
        self._create_drop_zone()
        
        # Setup drag and drop
        self._setup_drag_drop()
        
        self.logger.debug("Drop area initialized")
    
    def _create_drop_zone(self) -> None:
        """Create visual drop zone."""
        
        # Main drop zone frame
        self.drop_zone = ctk.CTkFrame(
            self,
            fg_color=("gray90", "gray20"),
            border_width=3,
            border_color=("#2196F3", "#1976D2"),
            corner_radius=15
        )
        self.drop_zone.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        self.drop_zone.grid_columnconfigure(0, weight=1)
        self.drop_zone.grid_rowconfigure(0, weight=1)
        
        # Content frame
        content_frame = ctk.CTkFrame(self.drop_zone, fg_color="transparent")
        content_frame.grid(row=0, column=0)
        
        # Icon (using emoji for now, can be replaced with actual icon)
        self.icon_label = ctk.CTkLabel(
            content_frame,
            text="🎵",
            font=ctk.CTkFont(size=64)
        )
        self.icon_label.grid(row=0, column=0, pady=(20, 10))
        
        # Main instruction text
        self.instruction_label = ctk.CTkLabel(
            content_frame,
            text="MP3ファイルをドラッグ＆ドロップ",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        self.instruction_label.grid(row=1, column=0, pady=(0, 5))
        
        # Subtext
        self.subtext_label = ctk.CTkLabel(
            content_frame,
            text="または、クリックしてファイルを選択",
            font=ctk.CTkFont(size=14),
            text_color=("gray40", "gray60")
        )
        self.subtext_label.grid(row=2, column=0, pady=(0, 10))
        
        # Browse button
        self.browse_button = ctk.CTkButton(
            content_frame,
            text="ファイルを選択",
            command=self._browse_files,
            width=150,
            height=35,
            fg_color=("#2196F3", "#1976D2"),
            hover_color=("#1976D2", "#1565C0"),
            text_color=("white", "white")
        )
        self.browse_button.grid(row=3, column=0, pady=(5, 20))
        
        # Supported formats info
        self.formats_label = ctk.CTkLabel(
            content_frame,
            text="対応形式: .mp3",
            font=ctk.CTkFont(size=11),
            text_color="gray"
        )
        self.formats_label.grid(row=4, column=0, pady=(0, 10))
    
    def _setup_drag_drop(self) -> None:
        """Setup drag and drop event handlers."""
        
        # Bind events to all relevant widgets
        widgets = [self, self.drop_zone, self.icon_label, 
                  self.instruction_label, self.subtext_label, self.formats_label]
        
        for widget in widgets:
            # Register as drop target
            widget.drop_target_register(tk.DND_FILES)
            
            # Bind drag events
            widget.dnd_bind('<<DragEnter>>', self._on_drag_enter)
            widget.dnd_bind('<<DragLeave>>', self._on_drag_leave)
            widget.dnd_bind('<<Drop>>', self._on_drop)
            
            # Also bind click event for manual file selection
            widget.bind('<Button-1>', lambda e: self._browse_files())
    
    def _on_drag_enter(self, event) -> str:
        """Handle drag enter event."""
        self._is_dragging = True
        self._update_visual_state()
        self.logger.debug("Drag entered drop area")
        return event.action
    
    def _on_drag_leave(self, event) -> str:
        """Handle drag leave event."""
        self._is_dragging = False
        self._update_visual_state()
        self.logger.debug("Drag left drop area")
        return event.action
    
    def _on_drop(self, event) -> str:
        """Handle drop event."""
        self._is_dragging = False
        self._update_visual_state()
        
        # Get dropped files
        files = self._parse_drop_data(event.data)
        
        if files:
            self.logger.info(f"Files dropped: {len(files)} files")
            self._handle_files(files)
        
        return event.action
    
    def _parse_drop_data(self, data: str) -> List[str]:
        """Parse drag and drop data to extract file paths."""
        
        # Handle different data formats
        # tkinterdnd2 may return paths in different formats depending on platform
        
        if not data:
            return []
        
        files = []
        
        # Remove curly braces and split by spaces
        # Handle both "{path1} {path2}" and "path1 path2" formats
        data = data.strip()
        
        if data.startswith('{'):
            # Format: {path1} {path2}
            current = ""
            in_braces = False
            
            for char in data:
                if char == '{':
                    in_braces = True
                    current = ""
                elif char == '}':
                    in_braces = False
                    if current:
                        files.append(current.strip())
                    current = ""
                elif in_braces:
                    current += char
        else:
            # Simple space-separated format
            # Note: This may not work correctly for paths with spaces
            files = data.split()
        
        # Normalize paths
        normalized_files = []
        for file_path in files:
            file_path = file_path.strip().strip('"\'')
            if file_path:
                normalized_files.append(file_path)
        
        return normalized_files
    
    def _browse_files(self) -> None:
        """Open file browser dialog."""
        
        file_paths = filedialog.askopenfilenames(
            title="MP3ファイルを選択",
            filetypes=[
                ("MP3 Files", "*.mp3"),
                ("All Files", "*.*")
            ]
        )
        
        if file_paths:
            self.logger.info(f"Files selected via browser: {len(file_paths)} files")
            self._handle_files(list(file_paths))
    
    def _handle_files(self, file_paths: List[str]) -> None:
        """Handle received files."""
        
        # Filter for valid paths
        valid_paths = []
        for path in file_paths:
            path_obj = Path(path)
            if path_obj.exists() and path_obj.is_file():
                valid_paths.append(str(path_obj.absolute()))
            else:
                self.logger.warning(f"Invalid file path: {path}")
        
        # Call callback if provided
        if valid_paths and self._on_files_dropped:
            try:
                self._on_files_dropped(valid_paths)
            except Exception as e:
                self.logger.error(f"Error in files dropped callback: {e}")
    
    def _update_visual_state(self) -> None:
        """Update visual appearance based on drag state."""
        
        if self._is_dragging:
            # Highlight drop zone
            self.drop_zone.configure(
                border_color="blue",
                border_width=4
            )
            self.icon_label.configure(text="📥")
            self.instruction_label.configure(text="ここにドロップ")
        else:
            # Normal state
            self.drop_zone.configure(
                border_color="gray",
                border_width=3
            )
            self.icon_label.configure(text="🎵")
            self.instruction_label.configure(text="MP3ファイルをドラッグ＆ドロップ")
    
    def set_enabled(self, enabled: bool) -> None:
        """Enable or disable the drop area."""
        
        if enabled:
            self.browse_button.configure(state="normal")
            self.drop_zone.configure(border_color="gray")
        else:
            self.browse_button.configure(state="disabled")
            self.drop_zone.configure(border_color="darkgray")
    
    def reset(self) -> None:
        """Reset drop area to initial state."""
        self._is_dragging = False
        self._update_visual_state()
        self.logger.debug("Drop area reset")


# Alternative implementation without tkinterdnd2 for broader compatibility
class SimpleDropArea(ctk.CTkFrame):
    """
    Simplified drop area without tkinterdnd2 dependency.
    Only supports file browser selection.
    """
    
    def __init__(self, 
                 parent,
                 on_files_dropped: Optional[Callable[[List[str]], None]] = None,
                 **kwargs):
        super().__init__(parent, **kwargs)
        
        self.logger = get_logger("SimpleDropArea")
        self._on_files_dropped = on_files_dropped
        
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Create UI
        self._create_ui()
        
        self.logger.debug("Simple drop area initialized (file browser only)")
    
    def _create_ui(self) -> None:
        """Create user interface."""
        
        # Drop zone frame
        self.drop_zone = ctk.CTkFrame(
            self,
            fg_color="transparent",
            border_width=3,
            border_color="gray",
            corner_radius=15
        )
        self.drop_zone.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        self.drop_zone.grid_columnconfigure(0, weight=1)
        self.drop_zone.grid_rowconfigure(0, weight=1)
        
        # Content
        content_frame = ctk.CTkFrame(self.drop_zone, fg_color="transparent")
        content_frame.grid(row=0, column=0)
        
        # Icon
        icon_label = ctk.CTkLabel(
            content_frame,
            text="🎵",
            font=ctk.CTkFont(size=64)
        )
        icon_label.grid(row=0, column=0, pady=(20, 10))
        
        # Instruction
        instruction_label = ctk.CTkLabel(
            content_frame,
            text="MP3ファイルを選択",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        instruction_label.grid(row=1, column=0, pady=(0, 10))
        
        # Browse button
        self.browse_button = ctk.CTkButton(
            content_frame,
            text="ファイルを選択",
            command=self._browse_files,
            width=150,
            height=40,
            font=ctk.CTkFont(size=14)
        )
        self.browse_button.grid(row=2, column=0, pady=(10, 20))
        
        # Make entire area clickable
        self.drop_zone.bind('<Button-1>', lambda e: self._browse_files())
    
    def _browse_files(self) -> None:
        """Open file browser."""
        
        file_paths = filedialog.askopenfilenames(
            title="MP3ファイルを選択",
            filetypes=[
                ("MP3 Files", "*.mp3"),
                ("All Files", "*.*")
            ]
        )
        
        if file_paths and self._on_files_dropped:
            self.logger.info(f"Files selected: {len(file_paths)} files")
            valid_paths = [str(Path(p).absolute()) for p in file_paths if Path(p).exists()]
            
            try:
                self._on_files_dropped(valid_paths)
            except Exception as e:
                self.logger.error(f"Error in callback: {e}")
    
    def set_enabled(self, enabled: bool) -> None:
        """Enable or disable the area."""
        self.browse_button.configure(state="normal" if enabled else "disabled")
    
    def reset(self) -> None:
        """Reset to initial state."""
        pass


# Determine which implementation to use
try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
    DROP_AREA_CLASS = DropArea
    HAS_DND_SUPPORT = True
except ImportError:
    DROP_AREA_CLASS = SimpleDropArea
    HAS_DND_SUPPORT = False
    get_logger("DropArea").info("tkinterdnd2 not available, using simplified file browser mode")
