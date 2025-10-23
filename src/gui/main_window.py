"""
Main Application Window - Base GUI application window using tkinter + customtkinter.
"""

import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
from typing import Optional, Callable, List
from pathlib import Path
import threading
import sys
import os

from ..models.application_state import ApplicationState
from ..models.conversion_job import ConversionJob, ConversionStatus
from ..utils.logger import get_logger, log_application_shutdown
from ..utils.error_handler import ErrorHandler, ErrorCode, SafeErrorReporter
from ..controllers.file_validation_controller import FileValidationController
from ..controllers.conversion_controller import ConversionController
from ..services.settings_service import get_settings_service
from .widgets.drop_area import DROP_AREA_CLASS, HAS_DND_SUPPORT
from .widgets.file_list import FileListWidget, FileItemStatus
from .widgets.progress_display import ProgressDisplay
from .dialogs.settings_dialog import SettingsDialog


class MainWindow:
    """Main application window."""
    
    def __init__(self):
        self.logger = get_logger("MainWindow")
        self.error_handler = ErrorHandler()
        self.app_state = ApplicationState()
        
        # Initialize controllers
        self.file_validation_controller = FileValidationController()
        self._setup_validation_callbacks()
        
        # Initialize settings service
        self.settings_service = get_settings_service()
        
        try:
            self.conversion_controller = ConversionController(
                max_concurrent_conversions=self.settings_service.get_max_concurrent_conversions()
            )
            self._setup_conversion_callbacks()
        except RuntimeError as e:
            # FFmpeg not available
            self.logger.error(f"Failed to initialize conversion controller: {e}")
            self.conversion_controller = None
        
        # Initialize CustomTkinter
        theme = self.settings_service.get_theme()
        ctk.set_appearance_mode(theme)  # Modes: "System" (standard), "Dark", "Light"
        ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"
        
        # Create main window
        self.root = ctk.CTk()
        self.root.title("MP3 to MP4 Converter")
        
        # Set window size from settings
        width, height = self.settings_service.get_window_size()
        self.root.geometry(f"{width}x{height}")
        self.root.minsize(600, 400)
        
        # Window icon (if available)
        self._set_window_icon()
        
        # Configure grid weights
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        
        # Create main frame
        self.main_frame = ctk.CTkFrame(self.root)
        self.main_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=1)
        
        # Initialize UI components
        self._create_title_section()
        self._create_content_area()
        self._create_status_section()
        
        # Bind window events
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        
        # State management
        self._conversion_jobs: List[ConversionJob] = []
        self._active_conversions = 0
        
        self.logger.info("Main window initialized")
    
    def _set_window_icon(self) -> None:
        """Set window icon if available."""
        try:
            # Look for icon file
            icon_paths = [
                "assets/icons/app_icon.ico",  # Windows
                "assets/icons/app_icon.png",  # Cross-platform
                "assets/app_icon.ico",
                "assets/app_icon.png"
            ]
            
            for icon_path in icon_paths:
                if os.path.exists(icon_path):
                    if icon_path.endswith('.ico'):
                        self.root.iconbitmap(icon_path)
                    else:
                        # For PNG files, need to use PhotoImage
                        icon = tk.PhotoImage(file=icon_path)
                        self.root.iconphoto(True, icon)
                    break
                    
        except Exception as e:
            self.logger.debug(f"Could not set window icon: {e}")
    
    def _create_title_section(self) -> None:
        """Create title and description section."""
        
        # Title
        self.title_label = ctk.CTkLabel(
            self.main_frame,
            text="MP3 to MP4 Converter",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        self.title_label.grid(row=0, column=0, pady=(20, 10))
        
        # Description
        self.description_label = ctk.CTkLabel(
            self.main_frame,
            text="Drag and drop MP3 files to convert them to MP4 videos",
            font=ctk.CTkFont(size=14),
            text_color="gray"
        )
        self.description_label.grid(row=1, column=0, pady=(0, 20))
    
    def _create_content_area(self) -> None:
        """Create main content area."""
        
        # Content frame
        self.content_frame = ctk.CTkFrame(self.main_frame)
        self.content_frame.grid(row=2, column=0, sticky="nsew", padx=20, pady=(0, 20))
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(0, weight=0)  # Drop area - fixed height
        self.content_frame.grid_rowconfigure(1, weight=0)  # Action buttons - fixed height
        self.content_frame.grid_rowconfigure(2, weight=1)  # File list - expandable
        self.content_frame.grid_rowconfigure(3, weight=0)  # Progress display - fixed height
        
        # Drag & Drop area
        self.drop_area = DROP_AREA_CLASS(
            self.content_frame,
            on_files_dropped=self._on_files_dropped,
            height=200
        )
        self.drop_area.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        
        # Action buttons frame
        self._create_action_buttons()
        
        # File list
        self.file_list = FileListWidget(
            self.content_frame,
            on_remove_file=self._on_remove_file
        )
        self.file_list.grid(row=2, column=0, sticky="nsew", pady=(0, 10))
        
        # Progress display
        self.progress_display = ProgressDisplay(
            self.content_frame,
            height=150
        )
        self.progress_display.grid(row=3, column=0, sticky="ew")
        self.progress_display.grid_remove()  # Hide initially
        
        # Info about drag & drop support
        if not HAS_DND_SUPPORT:
            self.logger.info("Running in file browser mode (tkinterdnd2 not available)")
    
    def _create_action_buttons(self) -> None:
        """Create action buttons (convert, clear, etc.)."""
        
        button_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        button_frame.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        button_frame.grid_columnconfigure(0, weight=1)
        
        # Button container (centered)
        button_container = ctk.CTkFrame(button_frame, fg_color="transparent")
        button_container.grid(row=0, column=0)
        
        # Convert button
        self.convert_button = ctk.CTkButton(
            button_container,
            text="変換開始",
            font=ctk.CTkFont(size=14, weight="bold"),
            width=150,
            height=40,
            command=self._start_conversion
        )
        self.convert_button.grid(row=0, column=0, padx=5)
        self.convert_button.configure(state="disabled")  # Disabled until files are ready
        
        # Cancel button
        self.cancel_button = ctk.CTkButton(
            button_container,
            text="キャンセル",
            font=ctk.CTkFont(size=14),
            width=120,
            height=40,
            fg_color="gray",
            hover_color="darkgray",
            command=self._cancel_conversion
        )
        self.cancel_button.grid(row=0, column=1, padx=5)
        self.cancel_button.grid_remove()  # Hidden initially
        
        # Clear button
        self.clear_button = ctk.CTkButton(
            button_container,
            text="クリア",
            font=ctk.CTkFont(size=14),
            width=100,
            height=40,
            fg_color="transparent",
            border_width=2,
            command=self._clear_files
        )
        self.clear_button.grid(row=0, column=2, padx=5)
    
    def _create_status_section(self) -> None:
        """Create status bar section."""
        
        # Status frame
        self.status_frame = ctk.CTkFrame(self.main_frame)
        self.status_frame.grid(row=3, column=0, sticky="ew", padx=20, pady=(0, 20))
        self.status_frame.grid_columnconfigure(1, weight=1)
        
        # Status icon/indicator
        self.status_icon = ctk.CTkLabel(
            self.status_frame,
            text="●",
            font=ctk.CTkFont(size=12),
            text_color="green",
            width=20
        )
        self.status_icon.grid(row=0, column=0, padx=(10, 5), pady=5)
        
        # Status text
        self.status_label = ctk.CTkLabel(
            self.status_frame,
            text="Ready",
            font=ctk.CTkFont(size=12),
            anchor="w"
        )
        self.status_label.grid(row=0, column=1, sticky="w", padx=(0, 10), pady=5)
        
        # Menu button (for future settings/about)
        self.menu_button = ctk.CTkButton(
            self.status_frame,
            text="⋮",
            width=30,
            height=24,
            font=ctk.CTkFont(size=16),
            command=self._show_menu
        )
        self.menu_button.grid(row=0, column=2, padx=(5, 10), pady=2)
    
    def _show_menu(self) -> None:
        """Show application menu."""
        self.logger.debug("Menu button clicked")
        
        # Create popup menu
        menu = tk.Menu(self.root, tearoff=0)
        menu.add_command(label="設定...", command=self._open_settings)
        menu.add_separator()
        menu.add_command(label="バージョン情報", command=self._show_about)
        
        # Show menu at button position
        x = self.menu_button.winfo_rootx()
        y = self.menu_button.winfo_rooty() + self.menu_button.winfo_height()
        menu.tk_popup(x, y)
    
    def _open_settings(self) -> None:
        """Open settings dialog."""
        self.logger.info("Opening settings dialog")
        
        dialog = SettingsDialog(self.root, self.settings_service)
        if dialog.show():
            # Settings were saved
            self.logger.info("Settings updated")
            
            # Update conversion controller with new max concurrent setting
            if self.conversion_controller:
                max_concurrent = self.settings_service.get_max_concurrent_conversions()
                self.conversion_controller.max_concurrent = max_concurrent
    
    def _show_about(self) -> None:
        """Show about dialog."""
        self.show_info_message(
            "MP3 to MP4 Converter\n\n"
            "バージョン: 1.0.0\n\n"
            "MP3ファイルをMP4動画に変換するデスクトップアプリケーション",
            "バージョン情報"
        )
    
    def _on_closing(self) -> None:
        """Handle window closing event."""
        self.logger.info("Application closing requested")
        
        # Check if conversions are running
        if self._active_conversions > 0:
            if not messagebox.askyesno(
                "確認", 
                f"変換処理が{self._active_conversions}件実行中です。終了しますか？",
                parent=self.root
            ):
                return
        
        # Cleanup and close
        self._cleanup()
        self.root.destroy()
    
    def _cleanup(self) -> None:
        """Cleanup resources before closing."""
        try:
            # Cancel any running conversions
            for job in self._conversion_jobs:
                if job.is_running():
                    job.cancel()
            
            # Save window size (check if window still exists)
            try:
                width = self.root.winfo_width()
                height = self.root.winfo_height()
                self.settings_service.set_window_size(width, height)
            except tk.TclError:
                # Window already destroyed
                pass
            
            self.settings_service.save()
            
            # Log shutdown
            log_application_shutdown()
            
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")
    
    # Validation callbacks setup
    
    def _setup_validation_callbacks(self) -> None:
        """Setup file validation controller callbacks."""
        self.file_validation_controller.on_validation_start = self._on_validation_start
        self.file_validation_controller.on_validation_success = self._on_validation_success
        self.file_validation_controller.on_validation_error = self._on_validation_error
    
    # File handling callbacks
    
    def _on_files_dropped(self, file_paths: List[str]) -> None:
        """Handle files dropped into the drop area."""
        self.logger.info(f"Files dropped: {len(file_paths)}")
        
        # Quick filter for MP3 files
        mp3_files = self.file_validation_controller.filter_mp3_files(file_paths)
        non_mp3_files = [fp for fp in file_paths if fp not in mp3_files]
        
        # Show warning for non-MP3 files
        if non_mp3_files:
            non_mp3_names = [Path(fp).name for fp in non_mp3_files[:3]]
            if len(non_mp3_files) > 3:
                non_mp3_names.append(f"...他{len(non_mp3_files) - 3}件")
            
            self.show_warning_message(
                "MP3ファイルのみ対応",
                f"以下のファイルはMP3形式ではないためスキップされます:\n\n" + 
                "\n".join(non_mp3_names)
            )
        
        if not mp3_files:
            self.logger.info("No MP3 files to process")
            return
        
        # Quick validation of paths
        valid_paths, errors = self.file_validation_controller.quick_validate_paths(mp3_files)
        
        # Show errors if any
        if errors:
            error_messages = [f"{Path(fp).name}: {msg}" for fp, msg in errors[:5]]
            if len(errors) > 5:
                error_messages.append(f"...他{len(errors) - 5}件のエラー")
            
            self.show_error_message(
                "ファイル検証エラー",
                "以下のファイルに問題があります:\n\n" + "\n".join(error_messages)
            )
        
        if not valid_paths:
            return
        
        # Add files to list
        for file_path in valid_paths:
            item = self.file_list.add_file(file_path)
            item.status = FileItemStatus.VALIDATING
        
        # Update status
        self.update_status(f"{len(valid_paths)}件のファイルを検証中...", "busy")
        
        # Start validation
        self.file_validation_controller.validate_files(valid_paths)
    
    def _on_remove_file(self, file_path: str) -> None:
        """Handle file removal from list."""
        self.logger.info(f"File removed: {Path(file_path).name}")
        # Future: Cancel any active conversion for this file
    
    def _on_validation_start(self, file_path: str) -> None:
        """Called when validation starts for a file."""
        self.root.after(0, lambda: self.file_list.update_item_status(
            file_path, 
            FileItemStatus.VALIDATING
        ))
    
    def _on_validation_success(self, file_path: str, audio_file) -> None:
        """Called when file validation succeeds."""
        def update():
            self.file_list.set_audio_file(file_path, audio_file)
            self.file_list.update_item_status(file_path, FileItemStatus.READY)
            
            # Update status bar
            ready_count = len([item for item in self.file_list.get_all_items() 
                             if item.status == FileItemStatus.READY])
            self.update_status(f"{ready_count}件のファイルが変換可能です", "info")
            
            # Enable convert button if we have ready files
            self._update_button_states()
        
        self.root.after(0, update)
    
    def _on_validation_error(self, file_path: str, error_message: str) -> None:
        """Called when file validation fails."""
        def update():
            self.file_list.update_item_status(
                file_path,
                FileItemStatus.ERROR,
                error_message
            )
            self._update_button_states()
        
        self.root.after(0, update)
    
    # Conversion callbacks setup
    
    def _setup_conversion_callbacks(self) -> None:
        """Setup conversion controller callbacks."""
        if not self.conversion_controller:
            return
        
        self.conversion_controller.on_job_start = self._on_conversion_start
        self.conversion_controller.on_job_progress = self._on_conversion_progress
        self.conversion_controller.on_job_complete = self._on_conversion_complete
        self.conversion_controller.on_job_error = self._on_conversion_error
        self.conversion_controller.on_all_complete = self._on_all_conversions_complete
    
    def _on_conversion_start(self, job: ConversionJob) -> None:
        """Called when a conversion starts."""
        def update():
            file_path = job.audio_file.file_path
            self.file_list.update_item_status(file_path, FileItemStatus.CONVERTING)
            self.file_list.set_conversion_job(file_path, job)
        
        self.root.after(0, update)
    
    def _on_conversion_progress(self, job: ConversionJob, progress: float) -> None:
        """Called when conversion progress updates."""
        def update():
            file_path = job.audio_file.file_path
            self.file_list.update_item_progress(file_path, progress)
            
            # Update overall progress
            stats = self.conversion_controller.get_statistics()
            self.progress_display.update_progress(
                completed=stats['completed'],
                failed=stats['failed'],
                current_file=Path(file_path).name
            )
        
        self.root.after(0, update)
    
    def _on_conversion_complete(self, job: ConversionJob) -> None:
        """Called when a conversion completes successfully."""
        def update():
            file_path = job.audio_file.file_path
            self.file_list.update_item_status(file_path, FileItemStatus.COMPLETED)
        
        self.root.after(0, update)
    
    def _on_conversion_error(self, job: ConversionJob, error_message: str) -> None:
        """Called when a conversion fails."""
        def update():
            file_path = job.audio_file.file_path
            self.file_list.update_item_status(file_path, FileItemStatus.ERROR, error_message)
        
        self.root.after(0, update)
    
    def _on_all_conversions_complete(self, success_count: int, error_count: int) -> None:
        """Called when all conversions are complete."""
        def update():
            self.progress_display.complete_conversion(success_count, error_count)
            self._update_button_states()
            
            # Show completion message
            if self.settings_service.should_show_completion_notification():
                if error_count > 0:
                    self.update_status(
                        f"変換完了: {success_count}件成功、{error_count}件失敗",
                        "warning" if success_count > 0 else "error"
                    )
                    self.show_warning_message(
                        "変換完了",
                        f"{success_count}件のファイルが正常に変換されました。\n{error_count}件のファイルで問題が発生しました。"
                    )
                else:
                    self.update_status(f"変換完了: {success_count}件成功", "info")
                    self.show_info_message(f"{success_count}件のファイルが正常に変換されました。")
            
            # Auto-clear if enabled
            if self.settings_service.should_auto_clear_on_complete() and error_count == 0:
                self.logger.info("Auto-clearing completed files")
                self.file_list.clear()
                self.progress_display.reset()
                self.progress_display.grid_remove()
                if self.conversion_controller:
                    self.conversion_controller.clear_jobs()
                self.update_status("Ready", "info")
        
        self.root.after(0, update)
    
    # Action button handlers
    
    def _start_conversion(self) -> None:
        """Start conversion process."""
        if not self.conversion_controller:
            self.show_error_message("エラー", "変換機能が利用できません。FFmpegがインストールされていることを確認してください。")
            return
        
        # Get ready files
        ready_items = [item for item in self.file_list.get_all_items() 
                      if item.status == FileItemStatus.READY and item.audio_file]
        
        if not ready_items:
            self.show_warning_message("警告", "変換可能なファイルがありません。")
            return
        
        self.logger.info(f"Starting conversion of {len(ready_items)} files")
        
        # Add conversions to controller
        for item in ready_items:
            # Generate output path using settings service
            output_path = self.settings_service.generate_output_path(
                item.audio_file.file_path
            )
            
            self.conversion_controller.add_conversion(
                audio_file=item.audio_file,
                output_path=output_path
            )
        
        # Show progress display
        self.progress_display.grid()
        self.progress_display.start_conversion(len(ready_items))
        
        # Update UI state
        self.convert_button.grid_remove()
        self.cancel_button.grid()
        self.drop_area.set_enabled(False)
        self.clear_button.configure(state="disabled")
        
        # Start conversions
        self.conversion_controller.start_conversions()
        
        self.update_status("変換処理を開始しました...", "busy")
    
    def _cancel_conversion(self) -> None:
        """Cancel ongoing conversions."""
        if not self.conversion_controller:
            return
        
        if self.ask_yes_no("確認", "変換処理をキャンセルしますか？"):
            self.logger.info("Cancelling conversions")
            self.conversion_controller.cancel_all_conversions()
            
            self.update_status("変換をキャンセルしました", "warning")
            self._update_button_states()
    
    def _clear_files(self) -> None:
        """Clear all files from list."""
        if not self.file_list.get_all_items():
            return
        
        if self.ask_yes_no("確認", "すべてのファイルをクリアしますか？"):
            self.file_list.clear()
            self.progress_display.reset()
            self.progress_display.grid_remove()
            
            if self.conversion_controller:
                self.conversion_controller.clear_jobs()
            
            self._update_button_states()
            self.update_status("Ready", "info")
            self.logger.info("Cleared all files")
    
    def _update_button_states(self) -> None:
        """Update button states based on current state."""
        is_converting = self.conversion_controller and self.conversion_controller.is_converting()
        
        if is_converting:
            # During conversion
            self.convert_button.grid_remove()
            self.cancel_button.grid()
            self.drop_area.set_enabled(False)
            self.clear_button.configure(state="disabled")
        else:
            # Not converting
            self.convert_button.grid()
            self.cancel_button.grid_remove()
            self.drop_area.set_enabled(True)
            self.clear_button.configure(state="normal")
            
            # Enable convert button if we have ready files
            ready_count = len([item for item in self.file_list.get_all_items() 
                             if item.status == FileItemStatus.READY])
            
            if ready_count > 0:
                self.convert_button.configure(state="normal")
            else:
                self.convert_button.configure(state="disabled")
    
    # Status management methods
    
    def update_status(self, message: str, status_type: str = "info") -> None:
        """Update status bar message."""
        
        # Update text
        self.status_label.configure(text=message)
        
        # Update icon color based on status type
        color_map = {
            "info": "green",
            "warning": "orange", 
            "error": "red",
            "busy": "blue"
        }
        
        icon_color = color_map.get(status_type, "green")
        self.status_icon.configure(text_color=icon_color)
        
        # Force UI update
        self.root.update_idletasks()
        
        self.logger.debug(f"Status updated: {message} ({status_type})")
    
    def set_busy_status(self, is_busy: bool, message: Optional[str] = None) -> None:
        """Set busy status (disables UI interactions)."""
        
        if is_busy:
            self.update_status(message or "処理中...", "busy")
            # Disable main interactions (will be implemented with actual UI components)
        else:
            self.update_status("Ready", "info")
            # Re-enable main interactions
    
    # Dialog methods
    
    def show_error_message(self, title: str, message: str) -> None:
        """Show error message dialog."""
        messagebox.showerror(title, message, parent=self.root)
    
    def show_warning_message(self, title: str, message: str) -> None:
        """Show warning message dialog."""
        messagebox.showwarning(title, message, parent=self.root)
    
    def show_info_message(self, message: str, title: str = "情報") -> None:
        """Show info message dialog."""
        messagebox.showinfo(title, message, parent=self.root)
    
    def ask_yes_no(self, title: str, message: str) -> bool:
        """Show yes/no confirmation dialog."""
        return messagebox.askyesno(title, message, parent=self.root)
    
    # Error handling integration
    
    def handle_error(self, error: Exception, context: str = "") -> None:
        """Handle application errors with user-friendly messages."""
        
        safe_reporter = SafeErrorReporter(self.error_handler)
        
        def show_error(error_info):
            self.show_error_message("エラー", error_info.user_message)
            self.update_status(f"エラー: {error_info.user_message}", "error")
        
        safe_reporter.handle_error(error, context, callback=show_error)
    
    # Threading utilities
    
    def run_in_background(self, 
                         target: Callable, 
                         on_success: Optional[Callable] = None,
                         on_error: Optional[Callable] = None,
                         context: str = "") -> None:
        """Run operation in background thread with UI updates."""
        
        def worker():
            try:
                result = target()
                if on_success:
                    # Schedule UI update on main thread
                    self.root.after(0, lambda: on_success(result))
            except Exception as e:
                if on_error:
                    self.root.after(0, lambda: on_error(e))
                else:
                    self.root.after(0, lambda: self.handle_error(e, context))
        
        thread = threading.Thread(target=worker, daemon=True)
        thread.start()
    
    # Conversion job management
    
    def add_conversion_job(self, job: ConversionJob) -> None:
        """Add conversion job to tracking list."""
        self._conversion_jobs.append(job)
        self._active_conversions += 1
        self.update_status(f"変換中: {len([j for j in self._conversion_jobs if j.is_running()])}件", "busy")
    
    def remove_conversion_job(self, job: ConversionJob) -> None:
        """Remove conversion job from tracking list."""
        if job in self._conversion_jobs:
            self._conversion_jobs.remove(job)
        
        if job.is_running():
            self._active_conversions = max(0, self._active_conversions - 1)
        
        active_count = len([j for j in self._conversion_jobs if j.is_running()])
        if active_count == 0:
            self.update_status("Ready", "info")
        else:
            self.update_status(f"変換中: {active_count}件", "busy")
    
    # Application lifecycle
    
    def run(self) -> None:
        """Start the application main loop."""
        self.logger.info("Starting application main loop")
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            self.logger.info("Application interrupted by user")
        except Exception as e:
            self.logger.error(f"Unexpected error in main loop: {e}")
            self.handle_error(e, "application main loop")
        finally:
            self._cleanup()
    
    def quit(self) -> None:
        """Quit the application programmatically."""
        self._on_closing()


def create_application() -> MainWindow:
    """Create and configure main application window."""
    
    try:
        return MainWindow()
    except Exception as e:
        # Fallback error handling if window creation fails
        logger = get_logger("MainWindow")
        logger.error(f"Failed to create main window: {e}")
        
        # Try to show basic error dialog
        try:
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror(
                "アプリケーションエラー",
                f"アプリケーションを起動できませんでした:\n{str(e)}"
            )
            root.destroy()
        except:
            print(f"Critical error: Failed to create main window: {e}")
        
        sys.exit(1)