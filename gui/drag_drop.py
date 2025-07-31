"""
Drag and Drop functionality for the GUI
"""

import tkinter as tk
from tkinter import dnd
import os
import sys

class DragDropMixin:
    """Mixin class to add drag and drop functionality"""
    
    def __init__(self, root):
        self.root = root
        self.setup_drag_drop()
        
    def setup_drag_drop(self):
        """Setup drag and drop functionality"""
        # Enable drag and drop for the entire window
        self.root.drop_target_register(dnd.DND_FILES)
        self.root.dnd_bind('<<Drop>>', self.handle_drop_event)
        
        # For cross-platform compatibility, also bind to specific widgets
        if hasattr(self, 'drop_frame'):
            self.drop_frame.drop_target_register(dnd.DND_FILES)
            self.drop_frame.dnd_bind('<<Drop>>', self.handle_drop_event)
            
    def handle_drop_event(self, event):
        """Handle drop event"""
        try:
            data = event.data
            self.handle_drop(data)
        except Exception as e:
            print(f"Error handling drop event: {e}")
            
    def handle_drop(self, data):
        """Override this method in subclasses to handle dropped data"""
        pass

# For systems where tkinter dnd is not available, provide fallback
if not hasattr(dnd, 'DND_FILES'):
    # Simple fallback implementation
    class DragDropMixin:
        def __init__(self, root):
            self.root = root
            self.setup_drag_drop()
            
        def setup_drag_drop(self):
            """Fallback drag and drop setup"""
            # Bind to standard events that might indicate drops
            if hasattr(self, 'drop_frame'):
                self.drop_frame.bind('<Button-1>', self.on_click)
                self.drop_frame.bind('<B1-Motion>', self.on_drag)
                self.drop_frame.bind('<ButtonRelease-1>', self.on_release)
                
        def on_click(self, event):
            """Handle click event"""
            pass
            
        def on_drag(self, event):
            """Handle drag event"""
            pass
            
        def on_release(self, event):
            """Handle release event"""
            pass
            
        def handle_drop(self, data):
            """Override this method in subclasses to handle dropped data"""
            pass

# Platform-specific implementations
if sys.platform == "win32":
    try:
        import win32gui
        import win32con
        
        class WindowsDragDrop(DragDropMixin):
            """Windows-specific drag and drop implementation"""
            
            def setup_drag_drop(self):
                """Setup Windows drag and drop"""
                try:
                    # Enable drag and drop for the window
                    hwnd = self.root.winfo_id()
                    win32gui.DragAcceptFiles(hwnd, True)
                    
                    # Bind to Windows message
                    self.root.bind('<Map>', self.on_map)
                except ImportError:
                    # Fallback to basic implementation
                    super().setup_drag_drop()
                    
            def on_map(self, event):
                """Handle window mapping"""
                pass
                
        DragDropMixin = WindowsDragDrop
        
    except ImportError:
        pass  # Use default implementation

elif sys.platform == "darwin":
    # macOS specific implementation would go here
    pass
    
elif sys.platform.startswith("linux"):
    # Linux specific implementation would go here
    pass
