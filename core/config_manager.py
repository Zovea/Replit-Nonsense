"""
Configuration manager for application settings
"""

import os
import configparser
from pathlib import Path

class ConfigManager:
    """Manages application configuration"""
    
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config_file = self._get_config_file_path()
        self.load_config()
        
    def _get_config_file_path(self):
        """Get the configuration file path"""
        # Use user's home directory for config
        config_dir = Path.home() / '.media_processor'
        config_dir.mkdir(exist_ok=True)
        return config_dir / 'config.ini'
        
    def load_config(self):
        """Load configuration from file"""
        try:
            if self.config_file.exists():
                self.config.read(self.config_file)
                
            # Ensure all required sections exist
            self._ensure_sections()
            
            # Load defaults for missing values
            self._load_defaults()
            
        except Exception as e:
            print(f"Error loading config: {e}")
            self._load_defaults()
            
    def _ensure_sections(self):
        """Ensure all required configuration sections exist"""
        required_sections = ['download', 'processing', 'output', 'advanced']
        
        for section in required_sections:
            if not self.config.has_section(section):
                self.config.add_section(section)
                
    def _load_defaults(self):
        """Load default configuration values"""
        defaults = {
            'download': {
                'directory': os.path.expanduser('~/Downloads'),
                'video_quality': 'best',
                'audio_quality': 'best',
                'extract_audio': 'False',
                'keep_video': 'True',
                'embed_subs': 'False'
            },
            'processing': {
                'ffmpeg_path': 'ffmpeg',
                'max_concurrent': '2',
                'auto_process': 'True',
                'delete_originals': 'False'
            },
            'output': {
                'directory': os.path.expanduser('~/Downloads/Processed'),
                'naming_pattern': '%(title)s.%(ext)s',
                'video_format': 'mp4',
                'audio_format': 'mp3'
            },
            'advanced': {
                'log_level': 'INFO',
                'browser_integration': 'True',
                'auto_start': 'False',
                'timeout': '60',
                'retry': '3'
            }
        }
        
        for section, options in defaults.items():
            if not self.config.has_section(section):
                self.config.add_section(section)
                
            for option, value in options.items():
                if not self.config.has_option(section, option):
                    self.config.set(section, option, value)
                    
    def load_defaults(self):
        """Reset to default configuration"""
        self.config.clear()
        self._ensure_sections()
        self._load_defaults()
        
    def save(self):
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                self.config.write(f)
        except Exception as e:
            print(f"Error saving config: {e}")
            
    def get(self, section, option, fallback=None):
        """Get configuration value"""
        try:
            return self.config.get(section, option, fallback=fallback)
        except (configparser.NoSectionError, configparser.NoOptionError):
            return fallback
            
    def getint(self, section, option, fallback=None):
        """Get integer configuration value"""
        try:
            return self.config.getint(section, option, fallback=fallback)
        except (configparser.NoSectionError, configparser.NoOptionError, ValueError):
            return fallback
            
    def getfloat(self, section, option, fallback=None):
        """Get float configuration value"""
        try:
            return self.config.getfloat(section, option, fallback=fallback)
        except (configparser.NoSectionError, configparser.NoOptionError, ValueError):
            return fallback
            
    def getboolean(self, section, option, fallback=None):
        """Get boolean configuration value"""
        try:
            return self.config.getboolean(section, option, fallback=fallback)
        except (configparser.NoSectionError, configparser.NoOptionError, ValueError):
            return fallback
            
    def set(self, section, option, value):
        """Set configuration value"""
        if not self.config.has_section(section):
            self.config.add_section(section)
        self.config.set(section, option, str(value))
        
    def get_all_settings(self):
        """Get all configuration settings as a dictionary"""
        settings = {}
        for section_name in self.config.sections():
            settings[section_name] = dict(self.config.items(section_name))
        return settings
