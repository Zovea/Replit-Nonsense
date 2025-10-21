#!/usr/bin/env python3
"""
Desktop Media Processing Application
Main entry point for the application
"""

import sys
import os
import threading
import tkinter as tk
from tkinter import messagebox
import logging

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gui.main_window import MainWindow
from core.config_manager import ConfigManager
from utils.logger import setup_logger
from utils.protocol_handler import ProtocolHandler

class MediaProcessorApp:
    def __init__(self):
        self.config = ConfigManager()
        self.logger = setup_logger()
        self.protocol_handler = None
        self.main_window = None
        
    def initialize(self):
        """Initialize the application"""
        try:
            # Setup protocol handler for browser integration
            self.protocol_handler = ProtocolHandler()
            
            # Create main window
            try:
                from ttkthemes import ThemedTk
                root = ThemedTk(theme="arc")
            except ImportError:
                root = tk.Tk()
                messagebox.showwarning("Theme Warning", "ttkthemes library not found. The application will use the default theme.")

            self.main_window = MainWindow(root, self.config, self.logger)
            
            # Setup protocol handler callback
            if self.protocol_handler:
                self.protocol_handler.set_callback(self.main_window.handle_protocol_url)
            
            self.logger.info("Application initialized successfully")
            return root
            
        except Exception as e:
            self.logger.error(f"Failed to initialize application: {str(e)}")
            messagebox.showerror("Initialization Error", f"Failed to start application: {str(e)}")
            return None
    
    def run(self):
        """Run the application"""
        root = self.initialize()
        if root:
            try:
                # Start the main loop
                root.mainloop()
            except KeyboardInterrupt:
                self.logger.info("Application interrupted by user")
            except Exception as e:
                self.logger.error(f"Application error: {str(e)}")
                messagebox.showerror("Application Error", f"An error occurred: {str(e)}")
            finally:
                self.cleanup()
    
    def cleanup(self):
        """Cleanup resources"""
        try:
            if self.main_window:
                self.main_window.cleanup()
            self.logger.info("Application cleanup completed")
        except Exception as e:
            self.logger.error(f"Error during cleanup: {str(e)}")

def main():
    """Main entry point"""
    app = MediaProcessorApp()
    app.run()

if __name__ == "__main__":
    main()
