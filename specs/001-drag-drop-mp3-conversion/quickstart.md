# Quick Start Guide: MP3 to MP4 Converter

**Feature**: 001-drag-drop-mp3-conversion  
**Target Audience**: Developers setting up the project  
**Date**: 2025-10-23

## Prerequisites

- **macOS 12+** (for development)
- **Windows 10+** (for testing and distribution)
- **mise** - Development tool management
- **Git** - Version control

## Development Setup

### 1. Install mise (if not already installed)

```bash
# macOS with Homebrew
brew install mise

# Or using curl
curl https://mise.run | sh
```

### 2. Clone and Setup Project

```bash
git clone <repository-url>
cd mp3_2_mp4
```

### 3. Install Development Tools with mise

The project uses `.mise.toml` to manage development dependencies:

```bash
# Install Python, FFmpeg, and other tools
mise install

# Verify installation
mise current
```

Expected output:
```
python  3.11.x
ffmpeg  6.0.x
```

### 4. Install Python Dependencies

```bash
# Create virtual environment and install packages
mise exec -- python -m venv venv
source venv/bin/activate  # macOS/Linux
# or venv\Scripts\activate  # Windows

pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### 5. Verify Setup

```bash
# Run basic tests
mise exec -- python -m pytest tests/unit -v

# Test GUI components (requires display)
mise exec -- python -m pytest tests/gui -v

# Verify FFmpeg integration
mise exec -- python -c "import ffmpeg; print('FFmpeg available')"
```

## Development Workflow

### Running the Application

```bash
# Development mode with debug logging
mise exec -- python src/main.py --debug

# Production mode
mise exec -- python src/main.py
```

### Running Tests

```bash
# All tests
mise exec -- python -m pytest

# Unit tests only
mise exec -- python -m pytest tests/unit

# GUI tests (requires display)
mise exec -- python -m pytest tests/gui

# Integration tests (requires FFmpeg samples)
mise exec -- python -m pytest tests/integration
```

### Code Quality

```bash
# Format code
mise exec -- black src/ tests/

# Lint code
mise exec -- flake8 src/ tests/

# Type checking
mise exec -- mypy src/
```

## Building Executables

### Development Build

```bash
# Build for current platform
mise exec -- python build.py --dev

# Output: dist/mp3_to_mp4_dev
```

### Production Build

```bash
# Build for macOS
mise exec -- python build.py --platform macos --release

# Build for Windows (requires Windows system or CI)
mise exec -- python build.py --platform windows --release

# Output: dist/mp3_to_mp4_v1.0.0_macos/
#         dist/mp3_to_mp4_v1.0.0_windows/
```

## Project Structure

```
mp3_2_mp4/
├── .mise.toml              # Development tool configuration
├── requirements.txt        # Python dependencies
├── requirements-dev.txt    # Development dependencies
├── src/
│   ├── main.py            # Application entry point
│   ├── core/              # Core conversion logic
│   ├── gui/               # GUI framework code
│   ├── models/            # Data models
│   ├── services/          # Business logic services
│   └── utils/             # Utility functions
├── tests/
│   ├── unit/              # Unit tests
│   ├── integration/       # Integration tests
│   └── gui/               # GUI automation tests
├── assets/
│   ├── icons/             # Application icons
│   └── samples/           # Sample MP3 files for testing
├── docs/
│   ├── manual_jp.md       # Japanese user manual
│   └── build.md           # Build and deployment guide
└── .github/
    └── workflows/         # CI/CD pipeline
```

## Configuration Files

### .mise.toml
```toml
[tools]
python = "3.11"
ffmpeg = "6.0"

[env]
PYTHONPATH = "src"
DEVELOPMENT = "true"
```

### requirements.txt (Key Dependencies)
```
customtkinter>=5.2.0
ffmpeg-python>=0.2.0
pytest>=7.4.0
pyinstaller>=6.0.0
```

## Troubleshooting

### Common Issues

**mise install fails on FFmpeg**:
```bash
# Try manual FFmpeg installation
brew install ffmpeg  # macOS
# Then run: mise install python
```

**GUI tests fail in headless environment**:
```bash
# Skip GUI tests in CI
pytest tests/unit tests/integration
```

**PyInstaller build fails**:
```bash
# Clean build cache
rm -rf build/ dist/
mise exec -- python build.py --clean --platform current
```

### Development Tips

1. **Use debug mode** during development for detailed logging
2. **Test with various MP3 formats** - keep samples in `assets/samples/`
3. **Test cross-platform builds** using CI before release
4. **Monitor memory usage** during batch conversion testing

## CI/CD Pipeline

The project uses GitHub Actions for continuous integration:

- **Push to main**: Runs all tests on macOS and Windows
- **Pull requests**: Runs tests and code quality checks
- **Release tags**: Builds distribution packages for both platforms
- **Nightly**: Runs extended integration tests with large files

### Triggering Builds

```bash
# Create release
git tag v1.0.0
git push origin v1.0.0

# Manual CI trigger
gh workflow run ci.yml
```

## Next Steps

1. Review [spec.md](spec.md) for feature requirements
2. Check [data-model.md](data-model.md) for entity definitions
3. Examine [contracts/api-interfaces.md](contracts/api-interfaces.md) for API design
4. Read [docs/manual_jp.md](../../../docs/manual_jp.md) for user-facing documentation

## Getting Help

- **Issues**: Check existing GitHub issues or create new ones
- **Development**: Review code comments and docstrings
- **Building**: See [docs/build.md](../../../docs/build.md) for detailed build instructions
- **User Guide**: Japanese manual available at [docs/manual_jp.md](../../../docs/manual_jp.md)