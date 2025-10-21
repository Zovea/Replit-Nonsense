"""
Main media processor that coordinates downloading and processing
"""

import os
import tempfile
from pathlib import Path
from urllib.parse import urlparse

from core.downloader import MediaDownloader
from core.ffmpeg_wrapper import FFMPEGWrapper

class MediaProcessor:
    """Main processor for handling media downloads and processing"""
    
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
        self.downloader = MediaDownloader(config, logger)
        self.ffmpeg = FFMPEGWrapper(config, logger)

        # Check for yt-dlp availability
        self.yt_dlp_available = self.downloader.is_yt_dlp_available()
        if not self.yt_dlp_available:
            self.logger.warning("yt-dlp executable not found or not working. Please configure its path in settings.")

        # Check for FFMPEG availability
        self.ffmpeg_available = self.ffmpeg.is_available()
        if not self.ffmpeg_available:
            self.logger.warning("FFMPEG executable not found or not working. Please configure its path in settings.")
        
    def process_url(self, url, options=None, progress_callback=None):
        """Process a URL by downloading and optionally converting"""
        try:
            self.logger.info(f"Processing URL: {url}")

            if not self.yt_dlp_available:
                raise Exception("yt-dlp is not configured or not working. Please check settings.")
            
            # Check if URL is supported
            if not self.downloader.is_supported_url(url):
                raise Exception("URL not supported by yt-dlp")
                
            # Get media information
            try:
                info = self.downloader.get_info(url)
                self.logger.info(f"Media info: {info.get('title', 'Unknown')} - {info.get('duration', 'Unknown duration')}")
            except Exception as e:
                self.logger.warning(f"Could not get media info: {str(e)}")
                info = {}
                
            # Download the media
            def download_progress(progress):
                if progress_callback:
                    # Download takes 70% of total progress
                    progress_callback(progress * 0.7)
                    
            download_result = self.downloader.download(url, options, download_progress)
            
            if not download_result['success']:
                raise Exception("Download failed")
                
            downloaded_files = download_result['output_files']
            if not downloaded_files:
                raise Exception("No files were downloaded")
                
            # Process downloaded files if needed
            processed_files = []
            for i, file_path in enumerate(downloaded_files):
                try:
                    if progress_callback:
                        # Processing starts at 70% and goes to 100%
                        base_progress = 70 + (i * 30 / len(downloaded_files))
                        
                        def process_progress(progress):
                            total_progress = base_progress + (progress * 30 / len(downloaded_files) / 100)
                            progress_callback(min(total_progress, 100))
                            
                    processed_file = self._process_downloaded_file(file_path, options, process_progress)
                    processed_files.append(processed_file)
                    
                except Exception as e:
                    self.logger.error(f"Error processing file {file_path}: {str(e)}")
                    # Add original file if processing failed
                    processed_files.append(file_path)
                    
            return {
                'success': True,
                'source': url,
                'original_files': downloaded_files,
                'processed_files': processed_files,
                'output_file': processed_files[0] if processed_files else None,
                'info': info
            }
            
        except Exception as e:
            self.logger.error(f"Error processing URL {url}: {str(e)}")
            raise
            
    def process_file(self, file_path, options=None, progress_callback=None):
        """Process a local media file"""
        try:
            self.logger.info(f"Processing file: {file_path}")
            
            if not os.path.exists(file_path):
                raise Exception(f"File not found: {file_path}")
                
            # Get file information
            try:
                info = self.ffmpeg.get_media_info(file_path)
                self.logger.info(f"File info: {info.get('format', {}).get('duration', 'Unknown duration')}")
            except Exception as e:
                self.logger.warning(f"Could not get file info: {str(e)}")
                info = {}
                
            # Process the file
            processed_file = self._process_downloaded_file(file_path, options, progress_callback)
            
            return {
                'success': True,
                'source': file_path,
                'original_files': [file_path],
                'processed_files': [processed_file],
                'output_file': processed_file,
                'info': info
            }
            
        except Exception as e:
            self.logger.error(f"Error processing file {file_path}: {str(e)}")
            raise
            
    def _process_downloaded_file(self, file_path, options=None, progress_callback=None):
        """Process a downloaded file with FFMPEG if needed"""
        try:
            # Check if processing is enabled
            if not self.config.getboolean('processing', 'auto_process', fallback=True):
                return file_path
                
            if not self.ffmpeg_available:
                self.logger.warning("FFMPEG is not configured or not working, skipping processing.")
                return file_path
                
            # Determine output directory
            output_dir = self.config.get('output', 'directory', 
                                       fallback=os.path.expanduser('~/Downloads/Processed'))
            os.makedirs(output_dir, exist_ok=True)
            
            # Get file extension and determine processing
            file_ext = Path(file_path).suffix.lower()
            file_name = Path(file_path).stem
            
            # Determine what processing to do based on options or defaults
            processing_needed = False
            output_file = file_path
            
            if options:
                # Custom processing options
                if 'convert_to' in options:
                    target_format = options['convert_to']
                    output_file = os.path.join(output_dir, f"{file_name}.{target_format}")
                    
                    if target_format in ['mp3', 'wav', 'flac', 'aac']:
                        # Audio extraction
                        self.ffmpeg.extract_audio(file_path, output_file, options, progress_callback)
                    else:
                        # Video conversion
                        self.ffmpeg.convert_video(file_path, output_file, options, progress_callback)
                        
                    processing_needed = True
                    
                elif 'extract_audio' in options and options['extract_audio']:
                    # Extract audio
                    audio_format = self.config.get('output', 'audio_format', fallback='mp3')
                    output_file = os.path.join(output_dir, f"{file_name}.{audio_format}")
                    self.ffmpeg.extract_audio(file_path, output_file, options, progress_callback)
                    processing_needed = True
                    
            else:
                # Default processing based on file type and configuration
                if file_ext in ['.mp4', '.avi', '.mkv', '.mov', '.webm']:
                    # Video file - check if conversion needed
                    target_format = self.config.get('output', 'video_format', fallback='mp4')
                    if file_ext[1:] != target_format:
                        output_file = os.path.join(output_dir, f"{file_name}.{target_format}")
                        self.ffmpeg.convert_video(file_path, output_file, None, progress_callback)
                        processing_needed = True
                        
                elif file_ext in ['.mp3', '.wav', '.flac', '.aac', '.ogg']:
                    # Audio file - check if conversion needed
                    target_format = self.config.get('output', 'audio_format', fallback='mp3')
                    if file_ext[1:] != target_format:
                        output_file = os.path.join(output_dir, f"{file_name}.{target_format}")
                        self.ffmpeg.convert_video(file_path, output_file, None, progress_callback)  # Use convert_video for audio too
                        processing_needed = True
                        
            # Handle original file deletion
            if processing_needed and self.config.getboolean('processing', 'delete_originals', fallback=False):
                try:
                    os.remove(file_path)
                    self.logger.info(f"Deleted original file: {file_path}")
                except Exception as e:
                    self.logger.warning(f"Could not delete original file: {str(e)}")
                    
            return output_file
            
        except Exception as e:
            self.logger.error(f"Error processing downloaded file: {str(e)}")
            # Return original file if processing failed
            return file_path
            
    def cleanup(self):
        """Cleanup resources"""
        try:
            self.downloader.cleanup()
            self.ffmpeg.cleanup()
        except Exception as e:
            self.logger.error(f"Error during processor cleanup: {str(e)}")
