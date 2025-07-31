"""
Logging utilities for the application
"""

import logging
import os
from datetime import datetime
from pathlib import Path

def setup_logger(name='MediaProcessor', level=logging.INFO):
    """Setup application logger"""
    
    # Create logs directory
    log_dir = Path.home() / '.media_processor' / 'logs'
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Clear any existing handlers
    logger.handlers.clear()
    
    # Create formatters
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_formatter = logging.Formatter(
        '%(levelname)s - %(message)s'
    )
    
    # File handler
    log_file = log_dir / f'media_processor_{datetime.now().strftime("%Y%m%d")}.log'
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # Rotate old log files (keep last 7 days)
    try:
        for log_file in log_dir.glob('media_processor_*.log'):
            # Get file date from name
            try:
                file_date = datetime.strptime(log_file.stem.split('_')[-1], '%Y%m%d')
                days_old = (datetime.now() - file_date).days
                if days_old > 7:
                    log_file.unlink()
            except (ValueError, IndexError):
                pass
    except Exception:
        pass  # Ignore rotation errors
    
    return logger

def get_logger(name='MediaProcessor'):
    """Get existing logger instance"""
    return logging.getLogger(name)

class LogHandler:
    """Custom log handler for GUI applications"""
    
    def __init__(self, callback=None):
        self.callback = callback
        self.messages = []
        
    def emit(self, record):
        """Emit a log record"""
        try:
            message = self.format(record)
            self.messages.append({
                'timestamp': datetime.now(),
                'level': record.levelname,
                'message': message
            })
            
            # Keep only last 1000 messages
            if len(self.messages) > 1000:
                self.messages = self.messages[-1000:]
                
            # Call callback if provided
            if self.callback:
                self.callback(record.levelname, message)
                
        except Exception:
            pass  # Ignore handler errors
            
    def format(self, record):
        """Format log record"""
        return f"{record.getMessage()}"
        
    def get_messages(self, level=None, limit=None):
        """Get log messages"""
        messages = self.messages
        
        if level:
            messages = [msg for msg in messages if msg['level'] == level]
            
        if limit:
            messages = messages[-limit:]
            
        return messages
        
    def clear_messages(self):
        """Clear stored messages"""
        self.messages.clear()
