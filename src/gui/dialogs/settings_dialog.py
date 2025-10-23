"""
Settings Dialog - Configure output folder and conversion settings.
"""

import tkinter as tk
from tkinter import filedialog
import customtkinter as ctk
from typing import Optional
from pathlib import Path

from ...services.settings_service import SettingsService, get_settings_service
from ...utils.logger import get_logger


class SettingsDialog(ctk.CTkToplevel):
    """Settings configuration dialog."""
    
    def __init__(self, parent, settings_service: Optional[SettingsService] = None):
        """
        Initialize settings dialog.
        
        Args:
            parent: Parent window
            settings_service: Settings service instance
        """
        super().__init__(parent)
        
        self.logger = get_logger("SettingsDialog")
        self.settings_service = settings_service or get_settings_service()
        
        # Dialog setup
        self.title("設定")
        self.geometry("600x500")
        self.resizable(False, False)
        
        # Modal dialog
        self.transient(parent)
        self.grab_set()
        
        # Center on parent
        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - self.winfo_width()) // 2
        y = parent.winfo_y() + (parent.winfo_height() - self.winfo_height()) // 2
        self.geometry(f"+{x}+{y}")
        
        # Result
        self.result = False
        
        # Create UI
        self._create_ui()
        
        # Load current settings
        self._load_settings()
        
        self.logger.debug("Settings dialog opened")
    
    def _create_ui(self) -> None:
        """Create dialog UI."""
        
        # Main frame
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        main_frame.grid_columnconfigure(0, weight=1)
        
        # Title
        title_label = ctk.CTkLabel(
            main_frame,
            text="アプリケーション設定",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.grid(row=0, column=0, pady=(0, 20), sticky="w")
        
        # Tabs
        self.tabview = ctk.CTkTabview(main_frame)
        self.tabview.grid(row=1, column=0, sticky="nsew", pady=(0, 20))
        main_frame.grid_rowconfigure(1, weight=1)
        
        # Output settings tab
        self.tab_output = self.tabview.add("出力設定")
        self._create_output_settings(self.tab_output)
        
        # Video settings tab
        self.tab_video = self.tabview.add("動画設定")
        self._create_video_settings(self.tab_video)
        
        # Advanced settings tab
        self.tab_advanced = self.tabview.add("詳細設定")
        self._create_advanced_settings(self.tab_advanced)
        
        # Buttons
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.grid(row=2, column=0, sticky="ew")
        button_frame.grid_columnconfigure(0, weight=1)
        
        # Button container (right-aligned)
        btn_container = ctk.CTkFrame(button_frame, fg_color="transparent")
        btn_container.grid(row=0, column=0, sticky="e")
        
        # Reset button
        self.reset_button = ctk.CTkButton(
            btn_container,
            text="デフォルトに戻す",
            width=120,
            fg_color="transparent",
            border_width=2,
            command=self._reset_to_defaults
        )
        self.reset_button.grid(row=0, column=0, padx=5)
        
        # Cancel button
        self.cancel_button = ctk.CTkButton(
            btn_container,
            text="キャンセル",
            width=100,
            fg_color="gray",
            hover_color="darkgray",
            command=self._on_cancel
        )
        self.cancel_button.grid(row=0, column=1, padx=5)
        
        # Save button
        self.save_button = ctk.CTkButton(
            btn_container,
            text="保存",
            width=100,
            command=self._on_save
        )
        self.save_button.grid(row=0, column=2, padx=5)
    
    def _create_output_settings(self, parent) -> None:
        """Create output settings tab."""
        
        parent.grid_columnconfigure(0, weight=1)
        
        # Output folder section
        folder_frame = ctk.CTkFrame(parent, fg_color="transparent")
        folder_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        folder_frame.grid_columnconfigure(0, weight=1)
        
        # Label
        folder_label = ctk.CTkLabel(
            folder_frame,
            text="出力フォルダ",
            font=ctk.CTkFont(size=13, weight="bold"),
            anchor="w"
        )
        folder_label.grid(row=0, column=0, sticky="w", pady=(0, 5))
        
        # Description
        folder_desc = ctk.CTkLabel(
            folder_frame,
            text="変換後のMP4ファイルを保存する場所を指定します。\n未指定の場合は元のMP3ファイルと同じフォルダに保存されます。",
            font=ctk.CTkFont(size=11),
            text_color="gray",
            anchor="w",
            justify="left"
        )
        folder_desc.grid(row=1, column=0, sticky="w", pady=(0, 10))
        
        # Folder selection frame
        folder_select_frame = ctk.CTkFrame(folder_frame, fg_color="transparent")
        folder_select_frame.grid(row=2, column=0, sticky="ew")
        folder_select_frame.grid_columnconfigure(0, weight=1)
        
        # Folder entry
        self.output_folder_var = tk.StringVar()
        self.output_folder_entry = ctk.CTkEntry(
            folder_select_frame,
            textvariable=self.output_folder_var,
            placeholder_text="未指定（元ファイルと同じ場所）",
            height=35
        )
        self.output_folder_entry.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        
        # Browse button
        browse_button = ctk.CTkButton(
            folder_select_frame,
            text="参照",
            width=80,
            height=35,
            command=self._browse_output_folder
        )
        browse_button.grid(row=0, column=1)
        
        # Clear button
        clear_button = ctk.CTkButton(
            folder_select_frame,
            text="クリア",
            width=80,
            height=35,
            fg_color="transparent",
            border_width=2,
            command=lambda: self.output_folder_var.set("")
        )
        clear_button.grid(row=0, column=2, padx=(5, 0))
        
        # Filename template section
        template_frame = ctk.CTkFrame(parent, fg_color="transparent")
        template_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=10)
        template_frame.grid_columnconfigure(0, weight=1)
        
        # Label
        template_label = ctk.CTkLabel(
            template_frame,
            text="ファイル名テンプレート",
            font=ctk.CTkFont(size=13, weight="bold"),
            anchor="w"
        )
        template_label.grid(row=0, column=0, sticky="w", pady=(0, 5))
        
        # Description
        template_desc = ctk.CTkLabel(
            template_frame,
            text="出力ファイル名のテンプレート。{original_name}は元のファイル名に置き換えられます。",
            font=ctk.CTkFont(size=11),
            text_color="gray",
            anchor="w",
            justify="left"
        )
        template_desc.grid(row=1, column=0, sticky="w", pady=(0, 10))
        
        # Template entry
        self.filename_template_var = tk.StringVar()
        self.filename_template_entry = ctk.CTkEntry(
            template_frame,
            textvariable=self.filename_template_var,
            placeholder_text="{original_name}",
            height=35
        )
        self.filename_template_entry.grid(row=2, column=0, sticky="ew")
        
        # Template presets
        preset_frame = ctk.CTkFrame(template_frame, fg_color="transparent")
        preset_frame.grid(row=3, column=0, sticky="w", pady=(5, 0))
        
        preset_label = ctk.CTkLabel(
            preset_frame,
            text="プリセット:",
            font=ctk.CTkFont(size=11),
            text_color="gray"
        )
        preset_label.grid(row=0, column=0, padx=(0, 10))
        
        presets = [
            ("元のまま", "{original_name}"),
            ("タイムスタンプ付き", "{original_name}_{timestamp}"),
            ("Converted_付き", "Converted_{original_name}")
        ]
        
        for idx, (label, template) in enumerate(presets):
            btn = ctk.CTkButton(
                preset_frame,
                text=label,
                width=120,
                height=28,
                fg_color="transparent",
                border_width=1,
                command=lambda t=template: self.filename_template_var.set(t)
            )
            btn.grid(row=0, column=idx+1, padx=5)
    
    def _create_video_settings(self, parent) -> None:
        """Create video settings tab."""
        
        parent.grid_columnconfigure(0, weight=1)
        
        # Resolution section
        resolution_frame = ctk.CTkFrame(parent, fg_color="transparent")
        resolution_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        resolution_frame.grid_columnconfigure(1, weight=1)
        
        resolution_label = ctk.CTkLabel(
            resolution_frame,
            text="解像度:",
            font=ctk.CTkFont(size=13),
            width=120,
            anchor="w"
        )
        resolution_label.grid(row=0, column=0, sticky="w", pady=5)
        
        self.resolution_var = tk.StringVar()
        self.resolution_dropdown = ctk.CTkOptionMenu(
            resolution_frame,
            variable=self.resolution_var,
            values=["1280x720 (HD)", "1920x1080 (Full HD)", "854x480 (SD)", "640x360"],
            width=200
        )
        self.resolution_dropdown.grid(row=0, column=1, sticky="w", padx=10, pady=5)
        
        # FPS section
        fps_frame = ctk.CTkFrame(parent, fg_color="transparent")
        fps_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=10)
        fps_frame.grid_columnconfigure(1, weight=1)
        
        fps_label = ctk.CTkLabel(
            fps_frame,
            text="フレームレート:",
            font=ctk.CTkFont(size=13),
            width=120,
            anchor="w"
        )
        fps_label.grid(row=0, column=0, sticky="w", pady=5)
        
        self.fps_var = tk.StringVar()
        self.fps_dropdown = ctk.CTkOptionMenu(
            fps_frame,
            variable=self.fps_var,
            values=["30 fps", "25 fps", "24 fps", "60 fps"],
            width=200
        )
        self.fps_dropdown.grid(row=0, column=1, sticky="w", padx=10, pady=5)
        
        # Background color section
        color_frame = ctk.CTkFrame(parent, fg_color="transparent")
        color_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=10)
        color_frame.grid_columnconfigure(1, weight=1)
        
        color_label = ctk.CTkLabel(
            color_frame,
            text="背景色:",
            font=ctk.CTkFont(size=13),
            width=120,
            anchor="w"
        )
        color_label.grid(row=0, column=0, sticky="w", pady=5)
        
        self.bg_color_var = tk.StringVar()
        self.bg_color_dropdown = ctk.CTkOptionMenu(
            color_frame,
            variable=self.bg_color_var,
            values=["黒 (#000000)", "白 (#FFFFFF)", "グレー (#808080)", "ネイビー (#000080)"],
            width=200
        )
        self.bg_color_dropdown.grid(row=0, column=1, sticky="w", padx=10, pady=5)
    
    def _create_advanced_settings(self, parent) -> None:
        """Create advanced settings tab."""
        
        parent.grid_columnconfigure(0, weight=1)
        
        # Concurrent conversions
        concurrent_frame = ctk.CTkFrame(parent, fg_color="transparent")
        concurrent_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        concurrent_frame.grid_columnconfigure(1, weight=1)
        
        concurrent_label = ctk.CTkLabel(
            concurrent_frame,
            text="同時変換数:",
            font=ctk.CTkFont(size=13),
            width=150,
            anchor="w"
        )
        concurrent_label.grid(row=0, column=0, sticky="w", pady=5)
        
        self.concurrent_var = tk.StringVar()
        self.concurrent_slider = ctk.CTkSlider(
            concurrent_frame,
            from_=1,
            to=5,
            number_of_steps=4,
            command=self._on_concurrent_change
        )
        self.concurrent_slider.grid(row=0, column=1, sticky="ew", padx=10, pady=5)
        
        self.concurrent_value_label = ctk.CTkLabel(
            concurrent_frame,
            text="2",
            width=30
        )
        self.concurrent_value_label.grid(row=0, column=2, padx=5)
        
        # Auto-clear checkbox
        self.auto_clear_var = tk.BooleanVar()
        self.auto_clear_check = ctk.CTkCheckBox(
            parent,
            text="変換完了後に自動的にファイルリストをクリア",
            variable=self.auto_clear_var,
            font=ctk.CTkFont(size=12)
        )
        self.auto_clear_check.grid(row=1, column=0, sticky="w", padx=10, pady=10)
        
        # Notification checkbox
        self.notification_var = tk.BooleanVar()
        self.notification_check = ctk.CTkCheckBox(
            parent,
            text="変換完了時に通知を表示",
            variable=self.notification_var,
            font=ctk.CTkFont(size=12)
        )
        self.notification_check.grid(row=2, column=0, sticky="w", padx=10, pady=10)
    
    def _browse_output_folder(self) -> None:
        """Browse for output folder."""
        folder = filedialog.askdirectory(
            title="出力フォルダを選択",
            initialdir=self.output_folder_var.get() or Path.home()
        )
        
        if folder:
            self.output_folder_var.set(folder)
    
    def _on_concurrent_change(self, value: float) -> None:
        """Handle concurrent conversions slider change."""
        int_value = int(value)
        self.concurrent_value_label.configure(text=str(int_value))
    
    def _load_settings(self) -> None:
        """Load current settings into UI."""
        settings = self.settings_service.settings
        
        # Output settings
        self.output_folder_var.set(settings.output_folder or "")
        self.filename_template_var.set(settings.output_filename_template)
        
        # Video settings
        self.resolution_var.set(f"{settings.video_resolution} (HD)")
        self.fps_var.set(f"{settings.video_fps} fps")
        
        # Map background color
        color_map = {
            "#000000": "黒 (#000000)",
            "#FFFFFF": "白 (#FFFFFF)",
            "#808080": "グレー (#808080)",
            "#000080": "ネイビー (#000080)"
        }
        self.bg_color_var.set(color_map.get(settings.background_color, "黒 (#000000)"))
        
        # Advanced settings
        self.concurrent_slider.set(settings.max_concurrent_conversions)
        self.concurrent_value_label.configure(text=str(settings.max_concurrent_conversions))
        self.auto_clear_var.set(settings.auto_clear_on_complete)
        self.notification_var.set(settings.show_completion_notification)
    
    def _save_settings(self) -> None:
        """Save settings from UI."""
        settings = self.settings_service.settings
        
        # Output settings
        output_folder = self.output_folder_var.get().strip()
        settings.output_folder = output_folder if output_folder else None
        settings.output_filename_template = self.filename_template_var.get()
        
        # Video settings
        resolution_text = self.resolution_var.get()
        settings.video_resolution = resolution_text.split()[0]  # Extract resolution part
        
        fps_text = self.fps_var.get()
        settings.video_fps = int(fps_text.split()[0])  # Extract fps number
        
        color_text = self.bg_color_var.get()
        if "(" in color_text:
            settings.background_color = color_text.split("(")[1].rstrip(")")
        
        # Advanced settings
        settings.max_concurrent_conversions = int(self.concurrent_slider.get())
        settings.auto_clear_on_complete = self.auto_clear_var.get()
        settings.show_completion_notification = self.notification_var.get()
    
    def _reset_to_defaults(self) -> None:
        """Reset settings to defaults."""
        if tk.messagebox.askyesno("確認", "設定をデフォルトに戻しますか？", parent=self):
            self.settings_service.reset_to_defaults()
            self._load_settings()
            self.logger.info("Settings reset to defaults")
    
    def _on_save(self) -> None:
        """Save and close dialog."""
        self._save_settings()
        
        if self.settings_service.save():
            self.result = True
            self.logger.info("Settings saved")
            self.destroy()
        else:
            tk.messagebox.showerror("エラー", "設定の保存に失敗しました", parent=self)
    
    def _on_cancel(self) -> None:
        """Cancel and close dialog."""
        self.result = False
        self.destroy()
    
    def show(self) -> bool:
        """
        Show dialog and wait for result.
        
        Returns:
            True if settings were saved
        """
        self.wait_window()
        return self.result
