"""
Main GUI Window for the Media Processing Application
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import os
from datetime import datetime

from gui.drag_drop import DragDropMixin
from gui.queue_manager import QueueManager
from gui.settings_dialog import SettingsDialog
from core.processor import MediaProcessor

class MainWindow(DragDropMixin):
    def __init__(self, root, config, logger):
        self.root = root
        self.config = config
        self.logger = logger
        self.processor = MediaProcessor(config, logger)
        self.queue_manager = QueueManager(self.processor)
        
        # Initialize drag and drop
        super().__init__(root)
        
        self.setup_ui()
        self.setup_menu()
        self.bind_events()
        
        # Start processor thread
        self.processor_thread = threading.Thread(target=self.queue_manager.process_queue, daemon=True)
        self.processor_thread.start()
        
    def setup_ui(self):
        """Setup the main user interface"""
        self.root.title("DCD")
        self.root.geometry("800x600")
        self.root.minsize(600, 400)

        # Create main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)

        # URL input section
        url_frame = ttk.LabelFrame(main_frame, text="Add Media", padding="10")
        url_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        url_frame.columnconfigure(0, weight=1)

        self.url_var = tk.StringVar()
        self.url_entry = ttk.Entry(url_frame, textvariable=self.url_var, font=("Segoe UI", 10))
        self.url_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), ipady=5, padx=(0, 10))

        add_url_button = ttk.Button(url_frame, text="Add URL", command=self.add_url, style="Accent.TButton")
        add_url_button.grid(row=0, column=1, padx=(0, 5))

        add_files_button = ttk.Button(url_frame, text="Add Files", command=self.add_files)
        add_files_button.grid(row=0, column=2)

        # Drag and drop area
        self.drop_frame = tk.Frame(main_frame, bg="#F0F0F0", relief="sunken", bd=1, height=100)
        self.drop_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        self.drop_frame.columnconfigure(0, weight=1)
        self.drop_frame.rowconfigure(0, weight=1)
        self.drop_frame.grid_propagate(False)

        drop_label = tk.Label(self.drop_frame, text="Drag and drop URLs or files here",
                             bg="#F0F0F0", fg="#777777", font=("Segoe UI", 12, "italic"))
        drop_label.pack(expand=True)

        # Queue display
        queue_frame = ttk.LabelFrame(main_frame, text="Processing Queue", padding="10")
        queue_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        queue_frame.columnconfigure(0, weight=1)
        queue_frame.rowconfigure(0, weight=1)

        # Create treeview for queue
        columns = ("URL/File", "Status", "Progress", "Output")
        self.queue_tree = ttk.Treeview(queue_frame, columns=columns, show="headings")

        self.queue_tree.heading("URL/File", text="URL/File")
        self.queue_tree.column("URL/File", width=300)
        self.queue_tree.heading("Status", text="Status")
        self.queue_tree.column("Status", width=100, anchor="center")
        self.queue_tree.heading("Progress", text="Progress")
        self.queue_tree.column("Progress", width=100, anchor="center")
        self.queue_tree.heading("Output", text="Output")
        self.queue_tree.column("Output", width=200)

        # Scrollbars
        v_scroll = ttk.Scrollbar(queue_frame, orient="vertical", command=self.queue_tree.yview)
        h_scroll = ttk.Scrollbar(queue_frame, orient="horizontal", command=self.queue_tree.xview)
        self.queue_tree.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)

        self.queue_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        v_scroll.grid(row=0, column=1, sticky=(tk.N, tk.S))
        h_scroll.grid(row=1, column=0, sticky=(tk.W, tk.E))

        # Control buttons
        control_frame = ttk.Frame(main_frame, padding=(0, 10, 0, 0))
        control_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E))

        clear_completed_button = ttk.Button(control_frame, text="Clear Completed", command=self.clear_completed)
        clear_completed_button.pack(side=tk.LEFT)

        clear_all_button = ttk.Button(control_frame, text="Clear All", command=self.clear_all)
        clear_all_button.pack(side=tk.LEFT, padx=5)

        settings_button = ttk.Button(control_frame, text="Settings", command=self.open_settings)
        settings_button.pack(side=tk.RIGHT)

        # Status bar
        status_bar_frame = ttk.Frame(main_frame, relief="sunken", padding=2)
        status_bar_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E))
        
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_bar = ttk.Label(status_bar_frame, textvariable=self.status_var)
        status_bar.pack(side=tk.LEFT, padx=5)

        # Start UI update timer
        self.update_ui()
        
    def setup_menu(self):
        """Setup the application menu"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Add Files...", command=self.add_files)
        file_menu.add_separator()
        file_menu.add_command(label="Settings", command=self.open_settings)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
        
    def bind_events(self):
        """Bind keyboard and other events"""
        self.url_entry.bind("<Return>", lambda e: self.add_url())
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def add_url(self):
        """Add URL to processing queue"""
        url = self.url_var.get().strip()
        if url:
            self.queue_manager.add_item(url, "url")
            self.url_var.set("")
            self.logger.info(f"Added URL to queue: {url}")
            
    def add_files(self):
        """Add files to processing queue"""
        files = filedialog.askopenfilenames(
            title="Select media files",
            filetypes=[
                ("All supported", "*.mp4 *.avi *.mkv *.mov *.mp3 *.wav *.flac"),
                ("Video files", "*.mp4 *.avi *.mkv *.mov"),
                ("Audio files", "*.mp3 *.wav *.flac"),
                ("All files", "*.*")
            ]
        )
        
        for file_path in files:
            self.queue_manager.add_item(file_path, "file")
            self.logger.info(f"Added file to queue: {file_path}")
            
    def handle_drop(self, data):
        """Handle drag and drop data"""
        items = data.split('\n')
        for item in items:
            item = item.strip()
            if item:
                if item.startswith(('http://', 'https://')):
                    self.queue_manager.add_item(item, "url")
                elif os.path.exists(item):
                    self.queue_manager.add_item(item, "file")
                    
    def handle_protocol_url(self, url):
        """Handle URLs from browser integration"""
        self.queue_manager.add_item(url, "url")
        self.root.lift()  # Bring window to front
        self.root.focus_force()
        
    def clear_completed(self):
        """Clear completed items from queue"""
        self.queue_manager.clear_completed()
        
    def clear_all(self):
        """Clear all items from queue"""
        if messagebox.askyesno("Confirm", "Clear all items from queue?"):
            self.queue_manager.clear_all()
            
    def open_settings(self):
        """Open settings dialog"""
        dialog = SettingsDialog(self.root, self.config)
        
    def show_about(self):
        """Show about dialog"""
        messagebox.showinfo("About", 
            "Media Processor v1.0\n\n"
            "A desktop application for downloading and processing media files\n"
            "with support for yt-dlp and FFMPEG.")
            
    def update_ui(self):
        """Update UI with current queue status"""
        try:
            # Clear existing items
            for item in self.queue_tree.get_children():
                self.queue_tree.delete(item)
                
            # Add current queue items
            for item in self.queue_manager.get_queue_items():
                self.queue_tree.insert("", "end", values=(
                    item.get('source', ''),
                    item.get('status', ''),
                    f"{item.get('progress', 0):.1f}%",
                    item.get('output_file', '')
                ))
                
            # Update status
            active_count = len([item for item in self.queue_manager.get_queue_items() 
                              if item.get('status') == 'processing'])
            if active_count > 0:
                self.status_var.set(f"Processing {active_count} item(s)...")
            else:
                self.status_var.set("Ready")
                
        except Exception as e:
            self.logger.error(f"Error updating UI: {str(e)}")
            
        # Schedule next update
        self.root.after(1000, self.update_ui)
        
    def on_closing(self):
        """Handle window closing"""
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.cleanup()
            self.root.destroy()
            
    def cleanup(self):
        """Cleanup resources"""
        try:
            self.queue_manager.stop()
            self.processor.cleanup()
        except Exception as e:
            self.logger.error(f"Error during cleanup: {str(e)}")
