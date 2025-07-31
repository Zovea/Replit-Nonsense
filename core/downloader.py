"""
Media downloader using yt-dlp
"""

import os
import subprocess
import json
import threading
from urllib.parse import urlparse

class MediaDownloader:
    """Handles downloading media using yt-dlp"""
    
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
        self.active_processes = {}
        
    def is_supported_url(self, url):
        """Check if URL is supported by yt-dlp"""
        try:
            # Basic URL validation
            parsed = urlparse(url)
            if not parsed.scheme or not parsed.netloc:
                return False
                
            # Test with yt-dlp
            cmd = ['yt-dlp', '--no-download', '--quiet', '--no-warnings', url]
            result = subprocess.run(cmd, capture_output=True, timeout=30)
            return result.returncode == 0
            
        except Exception as e:
            self.logger.error(f"Error checking URL support: {str(e)}")
            return False
            
    def get_info(self, url):
        """Get media information without downloading"""
        try:
            cmd = [
                'yt-dlp',
                '--dump-json',
                '--no-download',
                '--quiet',
                url
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                return json.loads(result.stdout)
            else:
                raise Exception(f"yt-dlp error: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            raise Exception("Timeout while getting media information")
        except json.JSONDecodeError as e:
            raise Exception(f"Failed to parse media information: {str(e)}")
        except Exception as e:
            self.logger.error(f"Error getting media info: {str(e)}")
            raise
            
    def download(self, url, options=None, progress_callback=None):
        """Download media from URL"""
        try:
            download_dir = self.config.get('download', 'directory', 
                                         fallback=os.path.expanduser('~/Downloads'))
            
            # Ensure download directory exists
            os.makedirs(download_dir, exist_ok=True)
            
            # Build yt-dlp command
            cmd = ['yt-dlp']
            
            # Add output template
            naming_pattern = self.config.get('output', 'naming_pattern', 
                                           fallback='%(title)s.%(ext)s')
            cmd.extend(['-o', os.path.join(download_dir, naming_pattern)])
            
            # Add quality settings
            video_quality = self.config.get('download', 'video_quality', fallback='best')
            if self.config.getboolean('download', 'extract_audio', fallback=False):
                cmd.extend(['--extract-audio'])
                audio_format = self.config.get('output', 'audio_format', fallback='mp3')
                cmd.extend(['--audio-format', audio_format])
                
                audio_quality = self.config.get('download', 'audio_quality', fallback='best')
                if audio_quality != 'best' and audio_quality != 'worst':
                    cmd.extend(['--audio-quality', audio_quality])
                    
                if not self.config.getboolean('download', 'keep_video', fallback=True):
                    cmd.extend(['--keep-video'])
            else:
                if video_quality == 'best':
                    cmd.extend(['-f', 'best'])
                elif video_quality == 'worst':
                    cmd.extend(['-f', 'worst'])
                else:
                    cmd.extend(['-f', f'best[height<={video_quality[:-1]}]'])
                    
            # Add subtitle options
            if self.config.getboolean('download', 'embed_subs', fallback=False):
                cmd.extend(['--embed-subs', '--sub-langs', 'en,en-US'])
                
            # Add other options
            cmd.extend(['--no-mtime'])  # Don't set file modification time
            
            # Add custom options
            if options:
                for key, value in options.items():
                    if key == 'format':
                        cmd.extend(['-f', value])
                    elif key == 'output':
                        cmd.extend(['-o', value])
                        
            # Add URL
            cmd.append(url)
            
            self.logger.info(f"Starting download: {' '.join(cmd)}")
            
            # Start process
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                universal_newlines=True
            )
            
            # Store process for potential cancellation
            process_id = id(process)
            self.active_processes[process_id] = process
            
            try:
                output_files = []
                
                # Monitor progress
                for line in process.stdout:
                    line = line.strip()
                    if line:
                        self.logger.debug(f"yt-dlp: {line}")
                        
                        # Parse progress information
                        if progress_callback:
                            progress = self._parse_progress(line)
                            if progress is not None:
                                progress_callback(progress)
                                
                        # Extract output file information
                        if 'Destination:' in line:
                            filename = line.split('Destination:')[1].strip()
                            output_files.append(filename)
                        elif 'has already been downloaded' in line:
                            # File already exists
                            filename = line.split('[download]')[1].split('has already been downloaded')[0].strip()
                            output_files.append(filename)
                            
                # Wait for completion
                return_code = process.wait()
                
                if return_code == 0:
                    # Success
                    if progress_callback:
                        progress_callback(100.0)
                        
                    return {
                        'success': True,
                        'output_files': output_files,
                        'message': 'Download completed successfully'
                    }
                else:
                    # Error
                    raise Exception(f"Download failed with return code {return_code}")
                    
            finally:
                # Clean up process reference
                if process_id in self.active_processes:
                    del self.active_processes[process_id]
                    
        except subprocess.TimeoutExpired:
            raise Exception("Download timeout")
        except Exception as e:
            self.logger.error(f"Download error: {str(e)}")
            raise
            
    def _parse_progress(self, line):
        """Parse progress from yt-dlp output"""
        try:
            if '[download]' in line and '%' in line:
                # Look for percentage in the line
                parts = line.split()
                for part in parts:
                    if part.endswith('%'):
                        # Remove % and convert to float
                        percent_str = part[:-1]
                        return float(percent_str)
                        
        except (ValueError, IndexError):
            pass
            
        return None
        
    def cancel_download(self, process_id):
        """Cancel an active download"""
        if process_id in self.active_processes:
            process = self.active_processes[process_id]
            try:
                process.terminate()
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
            finally:
                del self.active_processes[process_id]
                
    def cleanup(self):
        """Cleanup all active downloads"""
        for process_id in list(self.active_processes.keys()):
            self.cancel_download(process_id)
