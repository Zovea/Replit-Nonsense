# Media Processor Desktop Application

## Overview

This is a desktop media processing application built with Python and Tkinter that allows users to download and process media from various online sources. The application features a GUI-based interface with drag-and-drop functionality, browser integration through custom protocols, and queue-based media processing using yt-dlp and FFmpeg.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **GUI Framework**: Tkinter with ttk widgets for native desktop appearance
- **Main Window**: Centralized interface with tabbed settings and queue management
- **Drag & Drop**: Custom mixin class providing cross-platform file/URL drop support
- **Threading**: Separate UI and processing threads to maintain responsiveness

### Backend Architecture
- **Core Processing**: Modular design with separate components for downloading, media processing, and configuration
- **Queue Management**: Asynchronous queue system for handling multiple media processing tasks
- **Protocol Handler**: Custom URL protocol registration for browser integration
- **Configuration**: File-based configuration management using ConfigParser

### Browser Integration
- **Chrome Extension**: Manifest V3 extension with context menus and popup interface
- **Custom Protocol**: System-level protocol handler (`mediaprocessor://`) for seamless browser-to-app communication
- **Bookmark Interface**: HTML-based bookmark page for easy URL submission

## Key Components

### Core Components
1. **MediaProcessor** (`core/processor.py`): Main orchestrator coordinating downloads and processing
2. **MediaDownloader** (`core/downloader.py`): yt-dlp wrapper for media downloading
3. **FFMPEGWrapper** (`core/ffmpeg_wrapper.py`): FFmpeg integration for media processing
4. **ConfigManager** (`core/config_manager.py`): Application settings and preferences management

### GUI Components
1. **MainWindow** (`gui/main_window.py`): Primary application interface
2. **QueueManager** (`gui/queue_manager.py`): Task queue visualization and management
3. **SettingsDialog** (`gui/settings_dialog.py`): Configuration interface
4. **DragDropMixin** (`gui/drag_drop.py`): Cross-platform drag-and-drop functionality

### Utility Components
1. **Logger** (`utils/logger.py`): Centralized logging with file rotation
2. **ProtocolHandler** (`utils/protocol_handler.py`): System protocol registration and handling

### Browser Integration
1. **Chrome Extension**: Complete browser extension with background service worker
2. **Bookmark Interface**: HTML page for manual URL submission
3. **Protocol Communication**: Socket-based communication between browser and desktop app

## Data Flow

1. **URL Input**: Users can input URLs via GUI, drag-and-drop, browser extension, or custom protocol
2. **Queue Addition**: URLs are added to processing queue with user-specified options
3. **Media Information**: yt-dlp extracts metadata before downloading
4. **Download Process**: Media files downloaded to temporary or specified directory
5. **Processing**: Optional FFmpeg processing (conversion, compression, etc.)
6. **Output**: Processed files moved to final output directory
7. **Notification**: User notified of completion or errors

## External Dependencies

### Required External Tools
- **yt-dlp**: Media downloading from various platforms
- **FFmpeg**: Media processing and conversion
- **Python 3.x**: Runtime environment

### Python Libraries
- **tkinter**: GUI framework (built-in)
- **configparser**: Configuration management (built-in)
- **threading**: Concurrent processing (built-in)
- **subprocess**: External tool execution (built-in)
- **pathlib**: File system operations (built-in)

### Browser Integration
- **Chrome Extension API**: For browser extension functionality
- **System Protocol Registration**: Platform-specific protocol handlers

## Deployment Strategy

### Desktop Application
- **Standalone Python**: Direct Python execution with dependency management
- **Executable Packaging**: Support for PyInstaller or similar tools for distribution
- **Cross-Platform**: Windows, macOS, and Linux support through platform-specific protocol handlers

### Configuration Storage
- **User Directory**: Settings stored in `~/.media_processor/`
- **Portable Mode**: Configuration can be stored alongside executable

### Browser Extension
- **Chrome Web Store**: Standard extension distribution
- **Developer Mode**: Local installation for development/testing

### Installation Requirements
1. Python 3.x installation
2. yt-dlp installation (`pip install yt-dlp`)
3. FFmpeg installation (system PATH or configured path)
4. Optional: Browser extension installation

The architecture prioritizes modularity, cross-platform compatibility, and user experience through seamless browser integration and intuitive GUI design.