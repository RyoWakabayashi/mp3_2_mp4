#!/usr/bin/env python3
"""
PyInstaller build script for MP3 to MP4 Converter.

This script builds standalone executables for Windows and macOS.
"""

import os
import sys
import shutil
import subprocess
import platform
from pathlib import Path


def get_platform_name():
    """Get normalized platform name."""
    system = platform.system().lower()
    if system == "darwin":
        return "macos"
    return system


def clean_build_dirs():
    """Clean previous build artifacts."""
    print("🧹 Cleaning previous build artifacts...")
    
    dirs_to_clean = ["build", "dist", "__pycache__"]
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"   Removed {dir_name}/")
    
    # Clean .spec files
    for spec_file in Path(".").glob("*.spec"):
        spec_file.unlink()
        print(f"   Removed {spec_file}")


def check_ffmpeg():
    """Check if FFmpeg is available."""
    print("\n🔍 Checking FFmpeg availability...")
    
    try:
        result = subprocess.run(
            ["ffmpeg", "-version"],
            capture_output=True,
            text=True,
            check=True
        )
        print("   ✓ FFmpeg found")
        # Extract version
        first_line = result.stdout.split('\n')[0]
        print(f"   {first_line}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("   ✗ FFmpeg not found")
        print("   ⚠️  Application will require FFmpeg to be installed separately")
        return False


def install_pyinstaller():
    """Ensure PyInstaller is installed."""
    print("\n📦 Checking PyInstaller...")
    
    try:
        import PyInstaller
        print(f"   ✓ PyInstaller {PyInstaller.__version__} found")
        return True
    except ImportError:
        print("   Installing PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("   ✓ PyInstaller installed")
        return True


def build_executable():
    """Build the executable using PyInstaller."""
    platform_name = get_platform_name()
    print(f"\n🔨 Building executable for {platform_name}...")
    
    # PyInstaller arguments
    args = [
        "pyinstaller",
        "--name=MP3toMP4Converter",
        "--windowed",  # No console window
        "--onedir",    # Create a directory bundle (easier to include FFmpeg)
        "--clean",
        "--noconfirm",
        
        # Icon (if available)
        # "--icon=assets/icons/app.ico",  # Uncomment when icon is available
        
        # Add data files
        "--add-data=README.md:.",
        
        # Hidden imports (tkinter, customtkinter)
        "--hidden-import=tkinter",
        "--hidden-import=customtkinter",
        "--hidden-import=PIL",
        "--hidden-import=mutagen",
        
        # Entry point
        "run.py",
    ]
    
    # Platform-specific icon
    if platform_name == "windows":
        icon_path = "assets/icons/app.ico"
        if os.path.exists(icon_path):
            args.insert(1, f"--icon={icon_path}")
    elif platform_name == "macos":
        icon_path = "assets/icons/app.icns"
        if os.path.exists(icon_path):
            args.insert(1, f"--icon={icon_path}")
    
    print(f"   Running: {' '.join(args)}")
    
    try:
        subprocess.check_call(args)
        print("   ✓ Build successful")
        return True
    except subprocess.CalledProcessError as e:
        print(f"   ✗ Build failed: {e}")
        return False


def create_ffmpeg_notice():
    """Create a notice file about FFmpeg requirement."""
    notice_content = """
MP3 to MP4 Converter - FFmpeg Requirement
==========================================

This application requires FFmpeg to be installed on your system.

Installation Instructions:
--------------------------

Windows:
1. Download FFmpeg from https://ffmpeg.org/download.html
2. Extract the archive
3. Add the bin/ directory to your system PATH
4. Restart the application

macOS:
1. Install Homebrew if not already installed: https://brew.sh/
2. Run: brew install ffmpeg
3. Restart the application

Linux:
1. Ubuntu/Debian: sudo apt install ffmpeg
2. Fedora: sudo dnf install ffmpeg
3. Arch: sudo pacman -S ffmpeg

Verification:
-------------
Open a terminal and run: ffmpeg -version

If FFmpeg is installed correctly, you should see version information.

For more help, see README.md or visit the project repository.
"""
    
    dist_dir = Path("dist/MP3toMP4Converter")
    if dist_dir.exists():
        notice_file = dist_dir / "FFMPEG_REQUIRED.txt"
        notice_file.write_text(notice_content)
        print(f"   ✓ Created {notice_file}")


def create_launcher_scripts():
    """Create launcher scripts for the application."""
    platform_name = get_platform_name()
    dist_dir = Path("dist/MP3toMP4Converter")
    
    if not dist_dir.exists():
        return
    
    print("\n📝 Creating launcher scripts...")
    
    if platform_name == "windows":
        # Windows batch file
        launcher = dist_dir / "Launch_MP3toMP4Converter.bat"
        launcher.write_text("""@echo off
cd /d "%~dp0"
start "" "MP3toMP4Converter.exe"
""")
        print(f"   ✓ Created {launcher.name}")
    
    elif platform_name == "macos":
        # macOS shell script
        launcher = dist_dir / "Launch_MP3toMP4Converter.command"
        launcher.write_text("""#!/bin/bash
cd "$(dirname "$0")"
./MP3toMP4Converter
""")
        launcher.chmod(0o755)
        print(f"   ✓ Created {launcher.name}")


def copy_readme():
    """Copy README to dist directory."""
    dist_dir = Path("dist/MP3toMP4Converter")
    if dist_dir.exists() and os.path.exists("README.md"):
        shutil.copy("README.md", dist_dir / "README.md")
        print(f"   ✓ Copied README.md to distribution")


def create_distribution_package():
    """Create a distribution package (zip/dmg)."""
    platform_name = get_platform_name()
    dist_dir = Path("dist/MP3toMP4Converter")
    
    if not dist_dir.exists():
        print("   ✗ Distribution directory not found")
        return
    
    print(f"\n📦 Creating distribution package for {platform_name}...")
    
    if platform_name == "windows":
        # Create ZIP for Windows
        output_file = f"dist/MP3toMP4Converter-{platform_name}"
        shutil.make_archive(output_file, "zip", "dist", "MP3toMP4Converter")
        print(f"   ✓ Created {output_file}.zip")
    
    elif platform_name == "macos":
        # Create ZIP for macOS (DMG creation requires additional tools)
        output_file = f"dist/MP3toMP4Converter-{platform_name}"
        shutil.make_archive(output_file, "zip", "dist", "MP3toMP4Converter")
        print(f"   ✓ Created {output_file}.zip")
        print(f"   ℹ️  For DMG creation, use: hdiutil create -volname MP3toMP4Converter -srcfolder dist/MP3toMP4Converter -ov -format UDZO dist/MP3toMP4Converter.dmg")


def print_summary():
    """Print build summary."""
    platform_name = get_platform_name()
    
    print("\n" + "="*60)
    print("🎉 Build Complete!")
    print("="*60)
    
    print(f"\nPlatform: {platform_name}")
    print(f"Output directory: dist/MP3toMP4Converter/")
    
    dist_dir = Path("dist/MP3toMP4Converter")
    if dist_dir.exists():
        # List main files
        print("\nMain files:")
        for item in sorted(dist_dir.iterdir()):
            if item.is_file():
                size = item.stat().st_size
                size_mb = size / (1024 * 1024)
                print(f"  - {item.name} ({size_mb:.2f} MB)")
    
    print("\n⚠️  Important Notes:")
    print("  1. FFmpeg must be installed separately on the target system")
    print("  2. See FFMPEG_REQUIRED.txt in the distribution for installation instructions")
    print("  3. Test the application on a clean system before distribution")
    
    print("\n📋 Distribution packages:")
    if platform_name == "windows":
        print(f"  - dist/MP3toMP4Converter-{platform_name}.zip")
    elif platform_name == "macos":
        print(f"  - dist/MP3toMP4Converter-{platform_name}.zip")
    
    print("\n✅ Ready for distribution!")


def main():
    """Main build process."""
    print("🚀 MP3 to MP4 Converter - Build Script")
    print("="*60)
    
    # Step 1: Clean previous builds
    clean_build_dirs()
    
    # Step 2: Check FFmpeg
    ffmpeg_available = check_ffmpeg()
    
    # Step 3: Install PyInstaller
    if not install_pyinstaller():
        print("\n❌ Failed to install PyInstaller")
        return 1
    
    # Step 4: Build executable
    if not build_executable():
        print("\n❌ Build failed")
        return 1
    
    # Step 5: Post-build tasks
    create_ffmpeg_notice()
    create_launcher_scripts()
    copy_readme()
    
    # Step 6: Create distribution package
    create_distribution_package()
    
    # Step 7: Print summary
    print_summary()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
