#!/usr/bin/env python3
"""
MP3 to MP4 Converter - Main Entry Point

A desktop application that converts MP3 audio files to MP4 video files
with black video track through drag-and-drop interface.
"""

import argparse
import sys
import os
from pathlib import Path

# Add parent directory to Python path so 'src' can be imported as a package
parent_path = Path(__file__).parent.parent
if str(parent_path) not in sys.path:
    sys.path.insert(0, str(parent_path))

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="MP3 to MP4 Converter - Convert audio files to video format",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="MP3 to MP4 Converter v1.0.0"
    )
    
    parser.add_argument(
        "files",
        nargs="*",
        help="MP3 files to convert (optional, GUI supports drag-and-drop)"
    )
    
    return parser.parse_args()

def main():
    """Main application entry point."""
    args = parse_arguments()
    
    # Configure logging level based on debug flag
    log_level = "DEBUG" if args.debug else "INFO"
    os.environ["LOG_LEVEL"] = log_level
    
    try:
        # Import GUI after path setup
        from src.gui.main_window import create_application
        from src.utils.logger import setup_logging, log_system_info
        
        # Setup logging
        logger = setup_logging(level=log_level)
        log_system_info(logger)
        
        # Create and run the application
        app = create_application()
        
        # If files provided via command line, add them to the app
        # (Note: queue_files functionality can be added later if needed)
        if args.files:
            logger.info(f"Command line files provided: {args.files}")
            # TODO: Implement file queuing from command line
        
        # Start the GUI main loop
        app.run()
        
    except ImportError as e:
        print(f"Error: Required modules not found: {e}")
        print("Please install dependencies: pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()