"""
Settings Dialog for configuring application preferences
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os

class SettingsDialog:
    """Settings configuration dialog"""
    
    def __init__(self, parent, config):
        self.parent = parent
        self.config = config
        
        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Settings")
        self.dialog.geometry("600x500")
        self.dialog.resizable(True, True)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.geometry("+%d+%d" % (
            parent.winfo_rootx() + 50,
            parent.winfo_rooty() + 50
        ))
        
        self.setup_ui()
        self.load_settings()
        
    def setup_ui(self):
        """Setup the settings dialog UI"""
        # Create notebook for tabs
        notebook = ttk.Notebook(self.dialog)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Download settings tab
        self.setup_download_tab(notebook)
        
        # Processing settings tab
        self.setup_processing_tab(notebook)
        
        # Output settings tab
        self.setup_output_tab(notebook)
        
        # Advanced settings tab
        self.setup_advanced_tab(notebook)
        
        # Buttons frame
        button_frame = ttk.Frame(self.dialog)
        button_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        ttk.Button(button_frame, text="OK", command=self.save_and_close).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text="Cancel", command=self.cancel).pack(side=tk.RIGHT)
        ttk.Button(button_frame, text="Apply", command=self.apply_settings).pack(side=tk.RIGHT, padx=(0, 5))
        ttk.Button(button_frame, text="Restore Defaults", command=self.restore_defaults).pack(side=tk.LEFT)
        
    def setup_download_tab(self, notebook):
        """Setup download settings tab"""
        frame = ttk.Frame(notebook, padding="10")
        notebook.add(frame, text="Download")
        
        # Output directory
        ttk.Label(frame, text="Download Directory:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        dir_frame = ttk.Frame(frame)
        dir_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        dir_frame.columnconfigure(0, weight=1)
        
        self.download_dir_var = tk.StringVar()
        ttk.Entry(dir_frame, textvariable=self.download_dir_var).grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        ttk.Button(dir_frame, text="Browse", command=self.browse_download_dir).grid(row=0, column=1)
        
        # Quality settings
        ttk.Label(frame, text="Video Quality:").grid(row=2, column=0, sticky=tk.W, pady=(0, 5))
        self.video_quality_var = tk.StringVar()
        quality_combo = ttk.Combobox(frame, textvariable=self.video_quality_var, state="readonly")
        quality_combo['values'] = ('best', 'worst', '720p', '480p', '360p', '240p')
        quality_combo.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Audio quality
        ttk.Label(frame, text="Audio Quality:").grid(row=4, column=0, sticky=tk.W, pady=(0, 5))
        self.audio_quality_var = tk.StringVar()
        audio_combo = ttk.Combobox(frame, textvariable=self.audio_quality_var, state="readonly")
        audio_combo['values'] = ('best', 'worst', '320k', '256k', '192k', '128k')
        audio_combo.grid(row=5, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Download options
        self.extract_audio_var = tk.BooleanVar()
        ttk.Checkbutton(frame, text="Extract audio only", variable=self.extract_audio_var).grid(row=6, column=0, sticky=tk.W, pady=2)
        
        self.keep_video_var = tk.BooleanVar()
        ttk.Checkbutton(frame, text="Keep original video after audio extraction", variable=self.keep_video_var).grid(row=7, column=0, sticky=tk.W, pady=2)
        
        self.embed_subs_var = tk.BooleanVar()
        ttk.Checkbutton(frame, text="Embed subtitles", variable=self.embed_subs_var).grid(row=8, column=0, sticky=tk.W, pady=2)
        
        frame.columnconfigure(0, weight=1)
        
    def setup_processing_tab(self, notebook):
        """Setup processing settings tab"""
        frame = ttk.Frame(notebook, padding="10")
        notebook.add(frame, text="Processing")
        
        # FFMPEG settings
        ttk.Label(frame, text="FFMPEG Path:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        ffmpeg_frame = ttk.Frame(frame)
        ffmpeg_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        ffmpeg_frame.columnconfigure(0, weight=1)
        
        self.ffmpeg_path_var = tk.StringVar()
        ttk.Entry(ffmpeg_frame, textvariable=self.ffmpeg_path_var).grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        ttk.Button(ffmpeg_frame, text="Browse", command=self.browse_ffmpeg_path).grid(row=0, column=1)
        
        # yt-dlp settings
        ttk.Label(frame, text="yt-dlp Path:").grid(row=2, column=0, sticky=tk.W, pady=(0, 5))
        
        yt_dlp_frame = ttk.Frame(frame)
        yt_dlp_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        yt_dlp_frame.columnconfigure(0, weight=1)
        
        self.yt_dlp_path_var = tk.StringVar()
        ttk.Entry(yt_dlp_frame, textvariable=self.yt_dlp_path_var).grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        ttk.Button(yt_dlp_frame, text="Browse", command=self.browse_yt_dlp_path).grid(row=0, column=1)
        
        # Concurrent processing
        ttk.Label(frame, text="Maximum Concurrent Downloads:").grid(row=4, column=0, sticky=tk.W, pady=(0, 5))
        self.max_concurrent_var = tk.IntVar()
        concurrent_spin = ttk.Spinbox(frame, from_=1, to=8, textvariable=self.max_concurrent_var, width=10)
        concurrent_spin.grid(row=5, column=0, sticky=tk.W, pady=(0, 10))
        
        # Processing options
        self.auto_process_var = tk.BooleanVar()
        ttk.Checkbutton(frame, text="Auto-process downloaded files", variable=self.auto_process_var).grid(row=6, column=0, sticky=tk.W, pady=2)
        
        self.delete_originals_var = tk.BooleanVar()
        ttk.Checkbutton(frame, text="Delete original files after processing", variable=self.delete_originals_var).grid(row=7, column=0, sticky=tk.W, pady=2)
        
        frame.columnconfigure(0, weight=1)
        
    def setup_output_tab(self, notebook):
        """Setup output settings tab"""
        frame = ttk.Frame(notebook, padding="10")
        notebook.add(frame, text="Output")
        
        # Output directory
        ttk.Label(frame, text="Output Directory:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        output_frame = ttk.Frame(frame)
        output_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        output_frame.columnconfigure(0, weight=1)
        
        self.output_dir_var = tk.StringVar()
        ttk.Entry(output_frame, textvariable=self.output_dir_var).grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        ttk.Button(output_frame, text="Browse", command=self.browse_output_dir).grid(row=0, column=1)
        
        # File naming
        ttk.Label(frame, text="File Naming Pattern:").grid(row=2, column=0, sticky=tk.W, pady=(0, 5))
        self.naming_pattern_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.naming_pattern_var).grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Output formats
        ttk.Label(frame, text="Default Video Format:").grid(row=4, column=0, sticky=tk.W, pady=(0, 5))
        self.video_format_var = tk.StringVar()
        video_format_combo = ttk.Combobox(frame, textvariable=self.video_format_var, state="readonly")
        video_format_combo['values'] = ('mp4', 'mkv', 'avi', 'mov', 'webm')
        video_format_combo.grid(row=5, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(frame, text="Default Audio Format:").grid(row=6, column=0, sticky=tk.W, pady=(0, 5))
        self.audio_format_var = tk.StringVar()
        audio_format_combo = ttk.Combobox(frame, textvariable=self.audio_format_var, state="readonly")
        audio_format_combo['values'] = ('mp3', 'wav', 'flac', 'aac', 'ogg')
        audio_format_combo.grid(row=7, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        frame.columnconfigure(0, weight=1)
        
    def setup_advanced_tab(self, notebook):
        """Setup advanced settings tab"""
        frame = ttk.Frame(notebook, padding="10")
        notebook.add(frame, text="Advanced")
        
        # Logging level
        ttk.Label(frame, text="Logging Level:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        self.log_level_var = tk.StringVar()
        log_combo = ttk.Combobox(frame, textvariable=self.log_level_var, state="readonly")
        log_combo['values'] = ('DEBUG', 'INFO', 'WARNING', 'ERROR')
        log_combo.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Browser integration
        self.browser_integration_var = tk.BooleanVar()
        ttk.Checkbutton(frame, text="Enable browser integration", variable=self.browser_integration_var).grid(row=2, column=0, sticky=tk.W, pady=2)
        
        # Auto-start with system
        self.auto_start_var = tk.BooleanVar()
        ttk.Checkbutton(frame, text="Start with system", variable=self.auto_start_var).grid(row=3, column=0, sticky=tk.W, pady=2)
        
        # Network settings
        ttk.Label(frame, text="Connection Timeout (seconds):").grid(row=4, column=0, sticky=tk.W, pady=(10, 5))
        self.timeout_var = tk.IntVar()
        ttk.Spinbox(frame, from_=10, to=300, textvariable=self.timeout_var, width=10).grid(row=5, column=0, sticky=tk.W, pady=(0, 10))
        
        ttk.Label(frame, text="Retry Attempts:").grid(row=6, column=0, sticky=tk.W, pady=(0, 5))
        self.retry_var = tk.IntVar()
        ttk.Spinbox(frame, from_=1, to=10, textvariable=self.retry_var, width=10).grid(row=7, column=0, sticky=tk.W, pady=(0, 10))
        
        frame.columnconfigure(0, weight=1)
        
    def browse_download_dir(self):
        """Browse for download directory"""
        directory = filedialog.askdirectory(title="Select Download Directory")
        if directory:
            self.download_dir_var.set(directory)
            
    def browse_output_dir(self):
        """Browse for output directory"""
        directory = filedialog.askdirectory(title="Select Output Directory")
        if directory:
            self.output_dir_var.set(directory)
            
    def browse_ffmpeg_path(self):
        """Browse for FFMPEG executable"""
        filename = filedialog.askopenfilename(
            title="Select FFMPEG Executable",
            filetypes=[("Executable files", "*.exe"), ("All files", "*.*")]
        )
        if filename:
            self.ffmpeg_path_var.set(filename)
            
    def browse_yt_dlp_path(self):
        """Browse for yt-dlp executable"""
        filename = filedialog.askopenfilename(
            title="Select yt-dlp Executable",
            filetypes=[("Executable files", "*.exe"), ("All files", "*.*")]
        )
        if filename:
            self.yt_dlp_path_var.set(filename)
            
    def load_settings(self):
        """Load current settings into dialog"""
        # Download settings
        self.download_dir_var.set(self.config.get('download', 'directory', fallback=os.path.expanduser('~/Downloads')))
        self.video_quality_var.set(self.config.get('download', 'video_quality', fallback='best'))
        self.audio_quality_var.set(self.config.get('download', 'audio_quality', fallback='best'))
        self.extract_audio_var.set(self.config.getboolean('download', 'extract_audio', fallback=False))
        self.keep_video_var.set(self.config.getboolean('download', 'keep_video', fallback=True))
        self.embed_subs_var.set(self.config.getboolean('download', 'embed_subs', fallback=False))
        
        # Processing settings
        self.ffmpeg_path_var.set(self.config.get('processing', 'ffmpeg_path', fallback='ffmpeg'))
        self.yt_dlp_path_var.set(self.config.get('processing', 'yt_dlp_path', fallback='yt-dlp'))
        self.max_concurrent_var.set(self.config.getint('processing', 'max_concurrent', fallback=2))
        self.auto_process_var.set(self.config.getboolean('processing', 'auto_process', fallback=True))
        self.delete_originals_var.set(self.config.getboolean('processing', 'delete_originals', fallback=False))
        
        # Output settings
        self.output_dir_var.set(self.config.get('output', 'directory', fallback=os.path.expanduser('~/Downloads/Processed')))
        self.naming_pattern_var.set(self.config.get('output', 'naming_pattern', fallback='%(title)s.%(ext)s', raw=True))
        self.video_format_var.set(self.config.get('output', 'video_format', fallback='mp4'))
        self.audio_format_var.set(self.config.get('output', 'audio_format', fallback='mp3'))
        
        # Advanced settings
        self.log_level_var.set(self.config.get('advanced', 'log_level', fallback='INFO'))
        self.browser_integration_var.set(self.config.getboolean('advanced', 'browser_integration', fallback=True))
        self.auto_start_var.set(self.config.getboolean('advanced', 'auto_start', fallback=False))
        self.timeout_var.set(self.config.getint('advanced', 'timeout', fallback=60))
        self.retry_var.set(self.config.getint('advanced', 'retry', fallback=3))
        
    def apply_settings(self):
        """Apply current settings"""
        try:
            # Download settings
            self.config.set('download', 'directory', self.download_dir_var.get())
            self.config.set('download', 'video_quality', self.video_quality_var.get())
            self.config.set('download', 'audio_quality', self.audio_quality_var.get())
            self.config.set('download', 'extract_audio', str(self.extract_audio_var.get()))
            self.config.set('download', 'keep_video', str(self.keep_video_var.get()))
            self.config.set('download', 'embed_subs', str(self.embed_subs_var.get()))
            
            # Processing settings
            self.config.set('processing', 'ffmpeg_path', self.ffmpeg_path_var.get())
            self.config.set('processing', 'yt_dlp_path', self.yt_dlp_path_var.get())
            self.config.set('processing', 'max_concurrent', str(self.max_concurrent_var.get()))
            self.config.set('processing', 'auto_process', str(self.auto_process_var.get()))
            self.config.set('processing', 'delete_originals', str(self.delete_originals_var.get()))
            
            # Output settings
            self.config.set('output', 'directory', self.output_dir_var.get())
            self.config.set('output', 'naming_pattern', self.naming_pattern_var.get())
            self.config.set('output', 'video_format', self.video_format_var.get())
            self.config.set('output', 'audio_format', self.audio_format_var.get())
            
            # Advanced settings
            self.config.set('advanced', 'log_level', self.log_level_var.get())
            self.config.set('advanced', 'browser_integration', str(self.browser_integration_var.get()))
            self.config.set('advanced', 'auto_start', str(self.auto_start_var.get()))
            self.config.set('advanced', 'timeout', str(self.timeout_var.get()))
            self.config.set('advanced', 'retry', str(self.retry_var.get()))
            
            # Save settings
            self.config.save()
            
            messagebox.showinfo("Settings", "Settings applied successfully!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to apply settings: {str(e)}")
            
    def restore_defaults(self):
        """Restore default settings"""
        if messagebox.askyesno("Restore Defaults", "This will reset all settings to their default values. Continue?"):
            self.config.load_defaults()
            self.load_settings()
            
    def save_and_close(self):
        """Save settings and close dialog"""
        self.apply_settings()
        self.dialog.destroy()
        
    def cancel(self):
        """Cancel and close dialog"""
        self.dialog.destroy()
