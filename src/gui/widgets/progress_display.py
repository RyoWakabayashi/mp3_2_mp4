"""
Progress Display Widget - Show conversion progress for multiple files.
"""

import tkinter as tk
import customtkinter as ctk
from typing import Optional, Dict
from datetime import datetime, timedelta

from ...utils.logger import get_logger


class ProgressDisplay(ctk.CTkFrame):
    """Display conversion progress with statistics."""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.logger = get_logger("ProgressDisplay")
        
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        
        # Progress tracking
        self._total_files = 0
        self._completed_files = 0
        self._failed_files = 0
        self._current_file: Optional[str] = None
        self._start_time: Optional[datetime] = None
        
        # Create UI
        self._create_ui()
        
        self.logger.debug("Progress display initialized")
    
    def _create_ui(self) -> None:
        """Create user interface."""
        
        # Main progress section
        progress_section = ctk.CTkFrame(self, fg_color="transparent")
        progress_section.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        progress_section.grid_columnconfigure(1, weight=1)
        
        # Overall progress label
        self.overall_label = ctk.CTkLabel(
            progress_section,
            text="準備完了",
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w"
        )
        self.overall_label.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 5))
        
        # Progress percentage
        self.percentage_label = ctk.CTkLabel(
            progress_section,
            text="0%",
            font=ctk.CTkFont(size=12),
            width=50,
            anchor="e"
        )
        self.percentage_label.grid(row=1, column=0, sticky="e", padx=(0, 10))
        
        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(
            progress_section,
            height=20
        )
        self.progress_bar.set(0)
        self.progress_bar.grid(row=1, column=1, sticky="ew", pady=5)
        
        # Statistics section
        stats_section = ctk.CTkFrame(self, fg_color="transparent")
        stats_section.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 10))
        stats_section.grid_columnconfigure(0, weight=1)
        stats_section.grid_columnconfigure(1, weight=1)
        stats_section.grid_columnconfigure(2, weight=1)
        
        # Completed count
        self.completed_frame = self._create_stat_item(
            stats_section, "✅ 完了", "0", 0
        )
        
        # Failed count
        self.failed_frame = self._create_stat_item(
            stats_section, "❌ 失敗", "0", 1
        )
        
        # Remaining count
        self.remaining_frame = self._create_stat_item(
            stats_section, "⏳ 残り", "0", 2
        )
        
        # Current file section
        current_section = ctk.CTkFrame(self, fg_color="transparent")
        current_section.grid(row=2, column=0, sticky="ew", padx=10, pady=(0, 10))
        current_section.grid_columnconfigure(0, weight=1)
        
        # Current file label
        self.current_file_label = ctk.CTkLabel(
            current_section,
            text="",
            font=ctk.CTkFont(size=11),
            text_color="gray",
            anchor="w"
        )
        self.current_file_label.grid(row=0, column=0, sticky="w")
        
        # Elapsed time label
        self.time_label = ctk.CTkLabel(
            current_section,
            text="",
            font=ctk.CTkFont(size=11),
            text_color="gray",
            anchor="e"
        )
        self.time_label.grid(row=0, column=1, sticky="e", padx=(10, 0))
    
    def _create_stat_item(self, parent, label: str, value: str, column: int) -> ctk.CTkFrame:
        """Create a statistics item."""
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.grid(row=0, column=column, padx=5)
        
        # Value
        value_label = ctk.CTkLabel(
            frame,
            text=value,
            font=ctk.CTkFont(size=16, weight="bold")
        )
        value_label.pack()
        frame._value_label = value_label
        
        # Label
        label_widget = ctk.CTkLabel(
            frame,
            text=label,
            font=ctk.CTkFont(size=11),
            text_color="gray"
        )
        label_widget.pack()
        
        return frame
    
    def start_conversion(self, total_files: int) -> None:
        """Start conversion progress tracking."""
        self._total_files = total_files
        self._completed_files = 0
        self._failed_files = 0
        self._start_time = datetime.now()
        
        self.overall_label.configure(text=f"{total_files}件のファイルを変換中...")
        self.progress_bar.set(0)
        self.percentage_label.configure(text="0%")
        
        self._update_stats()
        
        self.logger.info(f"Started conversion tracking for {total_files} files")
    
    def update_progress(self, 
                       completed: int, 
                       failed: int,
                       current_file: Optional[str] = None) -> None:
        """Update conversion progress."""
        self._completed_files = completed
        self._failed_files = failed
        self._current_file = current_file
        
        # Calculate overall progress
        total_processed = completed + failed
        if self._total_files > 0:
            progress = total_processed / self._total_files
            self.progress_bar.set(progress)
            percentage = int(progress * 100)
            self.percentage_label.configure(text=f"{percentage}%")
        
        # Update stats
        self._update_stats()
        
        # Update current file
        if current_file:
            self.current_file_label.configure(text=f"変換中: {current_file}")
        else:
            self.current_file_label.configure(text="")
        
        # Update time
        self._update_time()
    
    def complete_conversion(self, completed: int, failed: int) -> None:
        """Mark conversion as complete."""
        self._completed_files = completed
        self._failed_files = failed
        self._current_file = None
        
        self.progress_bar.set(1.0)
        self.percentage_label.configure(text="100%")
        
        if failed > 0:
            self.overall_label.configure(
                text=f"変換完了 ({completed}件成功、{failed}件失敗)"
            )
        else:
            self.overall_label.configure(text=f"変換完了 ({completed}件)")
        
        self.current_file_label.configure(text="")
        
        self._update_stats()
        self._update_time()
        
        self.logger.info(f"Conversion complete: {completed} succeeded, {failed} failed")
    
    def reset(self) -> None:
        """Reset progress display."""
        self._total_files = 0
        self._completed_files = 0
        self._failed_files = 0
        self._current_file = None
        self._start_time = None
        
        self.overall_label.configure(text="準備完了")
        self.progress_bar.set(0)
        self.percentage_label.configure(text="0%")
        self.current_file_label.configure(text="")
        self.time_label.configure(text="")
        
        self._update_stats()
        
        self.logger.debug("Progress display reset")
    
    def _update_stats(self) -> None:
        """Update statistics display."""
        # Completed
        self.completed_frame._value_label.configure(text=str(self._completed_files))
        
        # Failed
        self.failed_frame._value_label.configure(text=str(self._failed_files))
        
        # Remaining
        remaining = max(0, self._total_files - self._completed_files - self._failed_files)
        self.remaining_frame._value_label.configure(text=str(remaining))
    
    def _update_time(self) -> None:
        """Update elapsed time display."""
        if not self._start_time:
            self.time_label.configure(text="")
            return
        
        elapsed = datetime.now() - self._start_time
        
        # Format time
        total_seconds = int(elapsed.total_seconds())
        if total_seconds < 60:
            time_str = f"{total_seconds}秒"
        elif total_seconds < 3600:
            minutes = total_seconds // 60
            seconds = total_seconds % 60
            time_str = f"{minutes}分{seconds}秒"
        else:
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            time_str = f"{hours}時間{minutes}分"
        
        self.time_label.configure(text=f"経過時間: {time_str}")
    
    def get_statistics(self) -> Dict[str, int]:
        """Get current statistics."""
        return {
            'total': self._total_files,
            'completed': self._completed_files,
            'failed': self._failed_files,
            'remaining': max(0, self._total_files - self._completed_files - self._failed_files)
        }
