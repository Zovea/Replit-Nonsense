"""
FFMPEG wrapper for media processing
"""

import os
import subprocess
import json
import re
import threading
from pathlib import Path

class FFMPEGWrapper:
    """Wrapper for FFMPEG operations"""
    
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
        self.active_processes = {}
        
    def get_ffmpeg_path(self):
        """Get FFMPEG executable path"""
        ffmpeg_path = self.config.get('processing', 'ffmpeg_path', fallback='ffmpeg')
        return ffmpeg_path
        
    def is_available(self):
        """Check if FFMPEG is available"""
        try:
            cmd = [self.get_ffmpeg_path(), '-version']
            result = subprocess.run(cmd, capture_output=True, timeout=10)
            return result.returncode == 0
        except Exception:
            return False
            
    def get_media_info(self, file_path):
        """Get media file information using ffprobe"""
        try:
            ffprobe_path = self.get_ffmpeg_path().replace('ffmpeg', 'ffprobe')
            
            cmd = [
                ffprobe_path,
                '-v', 'quiet',
                '-print_format', 'json',
                '-show_format',
                '-show_streams',
                file_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                return json.loads(result.stdout)
            else:
                raise Exception(f"ffprobe error: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            raise Exception("Timeout while getting media information")
        except json.JSONDecodeError as e:
            raise Exception(f"Failed to parse media information: {str(e)}")
        except Exception as e:
            self.logger.error(f"Error getting media info: {str(e)}")
            raise
            
    def convert_video(self, input_file, output_file, options=None, progress_callback=None):
        """Convert video file"""
        try:
            cmd = [self.get_ffmpeg_path()]
            
            # Input file
            cmd.extend(['-i', input_file])
            
            # Add conversion options
            if options:
                # Video codec
                if 'video_codec' in options:
                    cmd.extend(['-c:v', options['video_codec']])
                    
                # Audio codec
                if 'audio_codec' in options:
                    cmd.extend(['-c:a', options['audio_codec']])
                    
                # Video bitrate
                if 'video_bitrate' in options:
                    cmd.extend(['-b:v', options['video_bitrate']])
                    
                # Audio bitrate
                if 'audio_bitrate' in options:
                    cmd.extend(['-b:a', options['audio_bitrate']])
                    
                # Resolution
                if 'resolution' in options:
                    cmd.extend(['-s', options['resolution']])
                    
                # Frame rate
                if 'framerate' in options:
                    cmd.extend(['-r', str(options['framerate'])])
                    
                # Custom filters
                if 'filters' in options:
                    cmd.extend(['-vf', options['filters']])
                    
            else:
                # Default conversion settings
                video_format = self.config.get('output', 'video_format', fallback='mp4')
                if video_format == 'mp4':
                    cmd.extend(['-c:v', 'libx264', '-c:a', 'aac'])
                elif video_format == 'mkv':
                    cmd.extend(['-c:v', 'libx264', '-c:a', 'aac'])
                elif video_format == 'webm':
                    cmd.extend(['-c:v', 'libvpx-vp9', '-c:a', 'libopus'])
                    
            # Output file
            cmd.extend(['-y', output_file])  # -y to overwrite
            
            return self._run_ffmpeg_process(cmd, progress_callback, input_file)
            
        except Exception as e:
            self.logger.error(f"Video conversion error: {str(e)}")
            raise
            
    def extract_audio(self, input_file, output_file, options=None, progress_callback=None):
        """Extract audio from video file"""
        try:
            cmd = [self.get_ffmpeg_path()]
            
            # Input file
            cmd.extend(['-i', input_file])
            
            # Audio extraction options
            if options:
                if 'audio_codec' in options:
                    cmd.extend(['-c:a', options['audio_codec']])
                if 'audio_bitrate' in options:
                    cmd.extend(['-b:a', options['audio_bitrate']])
                if 'sample_rate' in options:
                    cmd.extend(['-ar', str(options['sample_rate'])])
            else:
                # Default audio settings
                audio_format = self.config.get('output', 'audio_format', fallback='mp3')
                if audio_format == 'mp3':
                    cmd.extend(['-c:a', 'libmp3lame'])
                elif audio_format == 'aac':
                    cmd.extend(['-c:a', 'aac'])
                elif audio_format == 'flac':
                    cmd.extend(['-c:a', 'flac'])
                elif audio_format == 'wav':
                    cmd.extend(['-c:a', 'pcm_s16le'])
                    
            # No video
            cmd.extend(['-vn'])
            
            # Output file
            cmd.extend(['-y', output_file])
            
            return self._run_ffmpeg_process(cmd, progress_callback, input_file)
            
        except Exception as e:
            self.logger.error(f"Audio extraction error: {str(e)}")
            raise
            
    def merge_files(self, input_files, output_file, progress_callback=None):
        """Merge multiple media files"""
        try:
            cmd = [self.get_ffmpeg_path()]
            
            # Add input files
            for input_file in input_files:
                cmd.extend(['-i', input_file])
                
            # Filter complex for concatenation
            filter_inputs = ''.join([f'[{i}:v][{i}:a]' for i in range(len(input_files))])
            filter_concat = f'{filter_inputs}concat=n={len(input_files)}:v=1:a=1[outv][outa]'
            cmd.extend(['-filter_complex', filter_concat])
            cmd.extend(['-map', '[outv]', '-map', '[outa]'])
            
            # Output file
            cmd.extend(['-y', output_file])
            
            return self._run_ffmpeg_process(cmd, progress_callback)
            
        except Exception as e:
            self.logger.error(f"File merge error: {str(e)}")
            raise
            
    def _run_ffmpeg_process(self, cmd, progress_callback=None, input_file=None):
        """Run FFMPEG process with progress monitoring"""
        try:
            self.logger.info(f"Running FFMPEG: {' '.join(cmd)}")
            
            # Get duration for progress calculation
            duration = None
            if input_file and progress_callback:
                try:
                    info = self.get_media_info(input_file)
                    duration = float(info['format']['duration'])
                except Exception:
                    pass
                    
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
                output_lines = []
                
                # Monitor progress
                for line in process.stdout:
                    line = line.strip()
                    if line:
                        output_lines.append(line)
                        self.logger.debug(f"ffmpeg: {line}")
                        
                        # Parse progress
                        if progress_callback and duration:
                            progress = self._parse_ffmpeg_progress(line, duration)
                            if progress is not None:
                                progress_callback(progress)
                                
                # Wait for completion
                return_code = process.wait()
                
                if return_code == 0:
                    if progress_callback:
                        progress_callback(100.0)
                        
                    return {
                        'success': True,
                        'message': 'Processing completed successfully',
                        'output': '\n'.join(output_lines)
                    }
                else:
                    raise Exception(f"FFMPEG failed with return code {return_code}: {' '.join(output_lines[-5:])}")
                    
            finally:
                # Clean up process reference
                if process_id in self.active_processes:
                    del self.active_processes[process_id]
                    
        except Exception as e:
            self.logger.error(f"FFMPEG process error: {str(e)}")
            raise
            
    def _parse_ffmpeg_progress(self, line, duration):
        """Parse progress from FFMPEG output"""
        try:
            # Look for time= in the output
            time_match = re.search(r'time=(\d{2}):(\d{2}):(\d{2}(?:\.\d+)?)', line)
            if time_match:
                hours = int(time_match.group(1))
                minutes = int(time_match.group(2))
                seconds = float(time_match.group(3))
                
                current_time = hours * 3600 + minutes * 60 + seconds
                progress = (current_time / duration) * 100
                
                return min(progress, 100.0)
                
        except (ValueError, AttributeError):
            pass
            
        return None
        
    def cancel_process(self, process_id):
        """Cancel an active FFMPEG process"""
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
        """Cleanup all active processes"""
        for process_id in list(self.active_processes.keys()):
            self.cancel_process(process_id)
