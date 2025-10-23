# Research: Drag & Drop MP3 to MP4 Conversion

**Feature**: 001-drag-drop-mp3-conversion  
**Phase**: 0 - Research & Technology Selection  
**Date**: 2025-10-23

## Research Questions

Based on Technical Context NEEDS CLARIFICATION items, the following research was conducted:

### 1. Cross-Platform GUI Framework Selection

**Question**: Python 3.11+ vs Rust vs Go for cross-platform desktop GUI development

**Decision**: **Python 3.11+ with tkinter + customtkinter**

**Rationale**:

- tkinter is built into Python, reducing dependencies
- customtkinter provides modern, professional-looking GUI components
- Python has excellent FFmpeg bindings (python-ffmpeg)
- Easier to create self-contained executables with PyInstaller
- Faster development cycle for GUI prototyping
- Strong cross-platform support for Windows and macOS

**Alternatives considered**:

- **Rust + egui**: Excellent performance but longer development time, complex GUI testing
- **Go + fyne**: Good performance but limited GUI customization options
- **Electron + Node.js**: Too heavy (>100MB), violates self-contained principle
- **Qt/PyQt**: Licensing concerns for distribution, larger dependency footprint

### 2. Audio/Video Processing Library

**Question**: Primary dependencies for MP3 to MP4 conversion

**Decision**: **FFmpeg via python-ffmpeg library**

**Rationale**:

- Industry-standard for audio/video processing
- Handles all MP3 formats and edge cases
- Built-in progress callbacks for UI integration
- Can generate silent black video tracks
- Cross-platform static binary distribution available
- Extensive error handling and format validation

**Alternatives considered**:

- **MoviePy**: Python-native but slower, less robust error handling
- **OpenCV**: Overkill for audio-only processing, larger dependency
- **Direct FFmpeg CLI**: More complex progress parsing, subprocess management issues

### 3. Testing Framework for GUI Applications

**Question**: GUI testing framework + unit tests for desktop application

**Decision**: **pytest + pytest-qt for GUI testing**

**Rationale**:
- pytest provides excellent unit testing for core logic
- pytest-qt enables automated GUI testing with tkinter
- Can simulate drag-and-drop events programmatically
- Integrates with CI/CD pipelines
- Good assertion libraries for file validation

**Alternatives considered**:
- **unittest**: Built-in but less flexible, no GUI testing support
- **Selenium**: Web-focused, doesn't work with desktop applications
- **Manual testing only**: Violates constitution requirement for automated testing

### 4. Development Environment Management

**Question**: Managing development tools and dependencies consistently

**Decision**: **mise for tool management + requirements.txt for Python dependencies**

**Rationale**:
- mise handles Python version, FFmpeg binaries, and development tools
- Consistent environment across macOS development and Windows CI
- Version locking for reproducible builds
- Simple setup for new developers

**Configuration**:
```toml
# .mise.toml
[tools]
python = "3.11"
ffmpeg = "6.0"
```

### 5. CI/CD Pipeline Requirements

**Question**: Automated testing and build pipeline for cross-platform distribution

**Decision**: **GitHub Actions with matrix builds**

**Rationale**:
- Free for open source projects
- Native Windows and macOS runners
- Can build and test on both platforms simultaneously
- Artifact storage for distributable executables
- Integration with dependency scanning and security checks

**Pipeline stages**:
1. **Test Stage**: Run unit tests, GUI tests, integration tests
2. **Build Stage**: Create executable with PyInstaller for each platform
3. **Package Stage**: Create distribution packages with bundled FFmpeg
4. **Release Stage**: Automated release creation with binaries

### 6. Distribution Strategy

**Question**: Self-contained distribution without installation requirements

**Decision**: **PyInstaller with bundled FFmpeg binaries**

**Rationale**:
- Creates single executable or single folder distribution
- Automatically bundles Python runtime and dependencies
- Can embed FFmpeg static binaries for each platform
- Meets zero-install requirement for Windows users
- Supports both GUI and console applications

## Implementation Technology Stack

**Language**: Python 3.11+  
**GUI Framework**: tkinter + customtkinter  
**Video Processing**: FFmpeg via python-ffmpeg  
**Testing**: pytest + pytest-qt  
**Build Tool**: PyInstaller  
**Development Environment**: mise  
**CI/CD**: GitHub Actions  
**Documentation**: Markdown (Japanese manual)

## Next Phase

All NEEDS CLARIFICATION items resolved. Ready to proceed to Phase 1: Design & Contracts.