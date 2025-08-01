# Media Processor Desktop Application

A powerful desktop application for downloading and processing media from various online sources with browser integration, drag-and-drop support, and comprehensive FFMPEG processing capabilities.

## Features

### Core Functionality
- **Multi-source Media Download**: Support for YouTube, Vimeo, SoundCloud, and many other platforms via yt-dlp
- **FFMPEG Integration**: Complete media processing with format conversion, audio extraction, and quality optimization
- **Drag & Drop Interface**: Simply drag URLs or files into the application
- **Queue Management**: Process multiple media files simultaneously with progress tracking
- **Browser Integration**: Chrome extension and protocol handler for seamless web-to-desktop workflow

### Advanced Features
- **Format Conversion**: Convert between video formats (MP4, MKV, AVI, WebM) and audio formats (MP3, WAV, FLAC, AAC)
- **Quality Control**: Customizable video/audio quality settings
- **Batch Processing**: Handle multiple downloads and conversions concurrently
- **Progress Monitoring**: Real-time progress tracking for all operations
- **Configurable Settings**: Extensive customization options for downloads and processing

## Installation

### Prerequisites
- Python 3.7 or higher
- FFMPEG (for media processing)
- yt-dlp (automatically installed)

### Setup Steps

1. **Clone or download the application**
   ```bash
   git clone <repository-url>
   cd media-processor
   ```

2. **Install Python dependencies**
   ```bash
   pip install yt-dlp
   ```

3. **Install FFMPEG**
   - **Windows**: Download from https://ffmpeg.org/download.html
   - **macOS**: `brew install ffmpeg`
   - **Linux**: `sudo apt install ffmpeg` (Ubuntu/Debian) or equivalent

4. **Run the application**
   ```bash
   python main.py
   ```

## Usage

### Basic Usage

1. **Launch the application**
   - Run `python main.py`
   - The main window will open with URL input, drag-drop area, and processing queue

2. **Add media for processing**
   - **Method 1**: Paste URLs in the input field and click "Add URL"
   - **Method 2**: Drag and drop URLs or local files onto the gray drop area
   - **Method 3**: Use "Add Files" button to select local media files
   - **Method 4**: Use browser integration (see Browser Integration section)

3. **Monitor progress**
   - View processing status in the queue table
   - Track download/conversion progress in real-time
   - Check output files location

### Browser Integration

#### Chrome Extension Setup

1. **Install the extension**
   - Open Chrome and go to `chrome://extensions/`
   - Enable "Developer mode"
   - Click "Load unpacked" and select the `browser` folder

2. **Use the extension**
   - Click the Media Processor icon in the toolbar on any media page
   - Right-click on pages and select "Send to Media Processor"
   - The extension automatically detects media-rich pages

#### Protocol Handler
The application registers a custom protocol (`mediaprocessor://`) for browser integration:
- Windows: Automatic registration (may require running as Administrator first)
- macOS: Creates necessary protocol handler files
- Linux: Creates .desktop file and registers with xdg-mime

#### Bookmark Method
Use the provided bookmark.html file:
1. Open `browser/bookmark.html` in your browser
2. Bookmark the page or drag the bookmarklet to your bookmarks bar
3. Use the bookmark on any media page to send URLs to the application

### Configuration

Access settings through the Settings dialog:

#### Download Settings
- **Output Directory**: Where downloaded files are stored
- **Video Quality**: Choose from best, 720p, 480p, 360p, etc.
- **Audio Quality**: Select audio bitrate (best, 320k, 256k, etc.)
- **Audio Extraction**: Extract audio-only from videos
- **Subtitle Embedding**: Include subtitles in downloads

#### Processing Settings
- **FFMPEG Path**: Custom path to FFMPEG executable
- **Concurrent Downloads**: Maximum simultaneous downloads (1-8)
- **Auto-processing**: Automatically process downloaded files
- **Delete Originals**: Remove source files after processing

#### Output Settings
- **Output Directory**: Where processed files are saved
- **File Naming**: Customize output file naming pattern
- **Default Formats**: Set preferred video and audio formats

## Supported Sites

The application supports hundreds of sites through yt-dlp, including:
- YouTube
- Vimeo
- SoundCloud
- Twitch
- Facebook Video
- Instagram
- TikTok
- Twitter/X
- Dailymotion
- And many more...

## File Formats

### Input Formats
- **Video**: MP4, AVI, MKV, MOV, WebM, FLV, and more
- **Audio**: MP3, WAV, FLAC, AAC, OGG, M4A, and more
- **URLs**: Any URL supported by yt-dlp

### Output Formats
- **Video**: MP4, MKV, AVI, WebM
- **Audio**: MP3, WAV, FLAC, AAC, OGG

## Advanced Usage

### Custom FFMPEG Options
You can specify custom processing options through the settings or by modifying the configuration:
- Video codec selection
- Audio codec selection
- Bitrate control
- Resolution scaling
- Custom filters

### Batch Processing
The application supports processing multiple files simultaneously:
- Add multiple URLs or files to the queue
- Set maximum concurrent processing in settings
- Monitor all operations in the queue view

### Command Line Integration
The application can handle protocol URLs from command line:
```bash
python main.py --protocol-url "mediaprocessor://https://youtube.com/watch?v=..."
```

## Architecture

### Core Components
- **MediaProcessor**: Main orchestrator for downloads and processing
- **MediaDownloader**: yt-dlp wrapper for media downloading
- **FFMPEGWrapper**: FFMPEG integration for media processing
- **QueueManager**: Handles processing queue and threading
- **ConfigManager**: Application settings and preferences

### GUI Components
- **MainWindow**: Primary application interface
- **DragDropMixin**: Cross-platform drag-and-drop support
- **SettingsDialog**: Configuration interface

### Browser Integration
- **Chrome Extension**: Complete Manifest V3 extension
- **Protocol Handler**: System-level protocol registration
- **Bookmark Interface**: HTML-based URL submission

## Configuration Files

The application stores configuration in `~/.media_processor/`:
- `config.ini`: User settings and preferences
- `logs/`: Application logs with rotation
- Platform-specific protocol handler files

## Troubleshooting

### Common Issues

1. **FFMPEG not found**
   - Install FFMPEG and ensure it's in your system PATH
   - Or specify custom FFMPEG path in settings

2. **Protocol handler not working**
   - On Windows: Run application as Administrator once
   - Restart browser after first setup
   - Check that Media Processor is running

3. **Download failures**
   - Check internet connection
   - Some sites may require specific yt-dlp options
   - Verify URL is supported

4. **Permission errors**
   - Check write permissions for output directories
   - Ensure antivirus isn't blocking the application

### Logs
Check application logs in `~/.media_processor/logs/` for detailed error information.

## Development

### Project Structure
```
media-processor/
├── main.py                 # Application entry point
├── core/                   # Core processing logic
│   ├── processor.py
│   ├── downloader.py
│   ├── ffmpeg_wrapper.py
│   └── config_manager.py
├── gui/                    # GUI components
│   ├── main_window.py
│   ├── queue_manager.py
│   ├── settings_dialog.py
│   └── drag_drop.py
├── utils/                  # Utility functions
│   ├── logger.py
│   └── protocol_handler.py
├── browser/                # Browser integration
│   ├── manifest.json
│   ├── background.js
│   ├── popup.html
│   ├── popup.js
│   ├── content.js
│   └── bookmark.html
└── config/                 # Configuration files
    └── default_settings.ini
```

### Adding New Features
1. Core functionality goes in the `core/` directory
2. GUI components in `gui/` directory
3. Utilities and helpers in `utils/`
4. Browser integration in `browser/`

## License

This project is provided as-is for educational and personal use.

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review application logs
3. Verify all dependencies are installed correctly

---

**Note**: This application is designed for personal use. Please respect copyright laws and terms of service of the platforms you're downloading from.