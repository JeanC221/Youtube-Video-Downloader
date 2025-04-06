import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import os
import sys
import urllib.request
from io import BytesIO
from PIL import Image, ImageTk
import json
import re
from datetime import datetime
from yt_dlp import YoutubeDL

class ModernTheme:
    """Custom theme for the application"""
    def __init__(self, is_dark=False):
        self.is_dark = is_dark
        self.update_colors()
        
    def update_colors(self):
        if self.is_dark:
            self.bg_color = "#1e1e2e"
            self.fg_color = "#cdd6f4"
            self.accent_color = "#f38ba8"
            self.secondary_bg = "#313244"
            self.hover_color = "#45475a"
            self.success_color = "#a6e3a1"
            self.warning_color = "#f9e2af"
            self.button_bg = "#89b4fa"
            self.button_fg = "#1e1e2e"
        else:
            self.bg_color = "#f8f9fa"
            self.fg_color = "#212529"
            self.accent_color = "#ff5c8d"
            self.secondary_bg = "#e9ecef"
            self.hover_color = "#dee2e6"
            self.success_color = "#40c057"
            self.warning_color = "#fd7e14"
            self.button_bg = "#01050a"
            self.button_fg = "#01050a"
    
    def toggle(self):
        self.is_dark = not self.is_dark
        self.update_colors()

class YouTubeDownloaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("YouTube Video Downloader")
        self.root.geometry("800x600")
        self.root.minsize(700, 500)
        
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.abspath(".")
            
        icon_path = os.path.join(base_path, "assets", "icon.ico")
        self.root.iconbitmap(icon_path) 
        
        self.theme = ModernTheme()
        
        self.download_path = tk.StringVar()
        self.video_url = tk.StringVar()
        self.download_format = tk.StringVar(value="mp4")
        self.downloading = False
        self.download_history = []
        self.current_thumbnail = None
        self.video_info = None
        
        default_path = os.path.join(os.path.expanduser("~"), "Downloads")
        self.download_path.set(default_path)
        
        self.history_file = os.path.join(os.path.expanduser("~"), ".youtube_downloader_history.json")
        self.load_history()
        
        self.create_styles()
        
        self.create_widgets()
        
        self.video_url.trace_add("write", self.on_url_change)
        
    def create_styles(self):
        self.style = ttk.Style()
        
        self.style.configure("TFrame", background=self.theme.bg_color)
        self.style.configure("TLabel", background=self.theme.bg_color, foreground=self.theme.fg_color)
        self.style.configure("TButton", 
                             background=self.theme.button_bg, 
                             foreground=self.theme.button_fg,
                             borderwidth=0,
                             focusthickness=3,
                             focuscolor=self.theme.accent_color)
        self.style.map("TButton",
                      background=[("active", self.theme.accent_color)],
                      foreground=[("active", self.theme.button_fg)])
        
        self.style.configure("TEntry", 
                             fieldbackground=self.theme.secondary_bg,
                             foreground=self.theme.fg_color,
                             bordercolor=self.theme.accent_color)
        
        self.style.configure("TRadiobutton", 
                             background=self.theme.bg_color,
                             foreground=self.theme.fg_color)
        
        self.style.configure("TProgressbar", 
                             background=self.theme.accent_color,
                             troughcolor=self.theme.secondary_bg,
                             borderwidth=0,
                             thickness=10)
        
        # Custom styles
        self.style.configure("Title.TLabel", 
                             font=("Helvetica", 16, "bold"),
                             foreground=self.theme.accent_color)
        
        self.style.configure("Subtitle.TLabel", 
                             font=("Helvetica", 12, "bold"))
        
        self.style.configure("Primary.TButton", 
                             font=("Helvetica", 11, "bold"),
                             padding=10)
        
        self.style.configure("Secondary.TButton", 
                             background=self.theme.secondary_bg,
                             foreground=self.theme.fg_color)
        
        self.style.map("Secondary.TButton",
                      background=[("active", self.theme.hover_color)])
        
    def create_widgets(self):
        self.main_container = ttk.Frame(self.root, style="TFrame")
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
        
        header_frame = ttk.Frame(self.main_container, style="TFrame")
        header_frame.pack(fill=tk.X, padx=20, pady=(20, 10))
        
        ttk.Label(header_frame, text="YouTube Video Downloader", style="Title.TLabel").pack(side=tk.LEFT)
        
        self.theme_btn = ttk.Button(header_frame, text="🌙 Dark Mode", style="Secondary.TButton", 
                                   command=self.toggle_theme)
        self.theme_btn.pack(side=tk.RIGHT)
        
        content_frame = ttk.Frame(self.main_container, style="TFrame")
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        left_panel = ttk.Frame(content_frame, style="TFrame")
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        url_frame = ttk.Frame(left_panel, style="TFrame")
        url_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(url_frame, text="Video URL:", style="Subtitle.TLabel").pack(anchor=tk.W, pady=(0, 5))
        
        url_input_frame = ttk.Frame(url_frame, style="TFrame")
        url_input_frame.pack(fill=tk.X)
        
        url_entry = ttk.Entry(url_input_frame, textvariable=self.video_url, style="TEntry")
        url_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        clear_btn = ttk.Button(url_input_frame, text="✕", style="Secondary.TButton", width=3,
                              command=lambda: self.video_url.set(""))
        clear_btn.pack(side=tk.RIGHT, padx=(5, 0))
        
        format_frame = ttk.Frame(left_panel, style="TFrame")
        format_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(format_frame, text="Download Format:", style="Subtitle.TLabel").pack(anchor=tk.W, pady=(0, 5))
        
        formats_container = ttk.Frame(format_frame, style="TFrame")
        formats_container.pack(fill=tk.X)
        
        ttk.Radiobutton(formats_container, text="MP4 Video", variable=self.download_format, value="mp4").pack(side=tk.LEFT, padx=(0, 15))
        ttk.Radiobutton(formats_container, text="MP3 Audio", variable=self.download_format, value="mp3").pack(side=tk.LEFT, padx=(0, 15))
        ttk.Radiobutton(formats_container, text="Original Format", variable=self.download_format, value="original").pack(side=tk.LEFT)
        
        location_frame = ttk.Frame(left_panel, style="TFrame")
        location_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(location_frame, text="Download Location:", style="Subtitle.TLabel").pack(anchor=tk.W, pady=(0, 5))
        
        location_input_frame = ttk.Frame(location_frame, style="TFrame")
        location_input_frame.pack(fill=tk.X)
        
        ttk.Entry(location_input_frame, textvariable=self.download_path, style="TEntry").pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        browse_btn = ttk.Button(location_input_frame, text="Browse", style="Secondary.TButton",
                               command=self.select_directory)
        browse_btn.pack(side=tk.RIGHT, padx=(5, 0))
        
        progress_frame = ttk.Frame(left_panel, style="TFrame")
        progress_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.progress_label = ttk.Label(progress_frame, text="Ready to download", style="TLabel")
        self.progress_label.pack(anchor=tk.W, pady=(0, 5))
        
        self.progress_bar = ttk.Progressbar(progress_frame, orient=tk.HORIZONTAL, mode='determinate', style="TProgressbar")
        self.progress_bar.pack(fill=tk.X)
        
        self.download_btn = ttk.Button(left_panel, text="Download Video", style="Primary.TButton",
                                      command=self.start_download)
        self.download_btn.pack(fill=tk.X, pady=(10, 0))
        
        right_panel = ttk.Frame(content_frame, style="TFrame", width=300)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(10, 0))
        right_panel.pack_propagate(False)
        
        self.info_frame = ttk.Frame(right_panel, style="TFrame")
        self.info_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(self.info_frame, text="Video Information", style="Subtitle.TLabel").pack(anchor=tk.W, pady=(0, 10))
        
        self.thumbnail_label = ttk.Label(self.info_frame, style="TLabel")
        self.thumbnail_label.pack(fill=tk.X, pady=(0, 10))
        
        self.video_title_label = ttk.Label(self.info_frame, text="", style="TLabel", wraplength=280)
        self.video_title_label.pack(anchor=tk.W, pady=(0, 5))
        
        self.video_duration_label = ttk.Label(self.info_frame, text="", style="TLabel")
        self.video_duration_label.pack(anchor=tk.W, pady=(0, 5))
        
        history_frame = ttk.Frame(right_panel, style="TFrame")
        history_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(history_frame, text="Download History", style="Subtitle.TLabel").pack(anchor=tk.W, pady=(0, 10))
        
        history_container = ttk.Frame(history_frame, style="TFrame")
        history_container.pack(fill=tk.BOTH, expand=True)
        
        history_canvas = tk.Canvas(history_container, bg=self.theme.bg_color, 
                                  highlightthickness=0)
        history_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(history_container, orient=tk.VERTICAL, command=history_canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        history_canvas.configure(yscrollcommand=scrollbar.set)
        history_canvas.bind('<Configure>', lambda e: history_canvas.configure(scrollregion=history_canvas.bbox("all")))
        
        self.history_inner_frame = ttk.Frame(history_canvas, style="TFrame")
        history_canvas.create_window((0, 0), window=self.history_inner_frame, anchor=tk.NW, width=280)
        
        self.update_history_display()
        
        status_bar = ttk.Frame(self.main_container, style="TFrame")
        status_bar.pack(fill=tk.X, padx=20, pady=10)
        
        self.status_label = ttk.Label(status_bar, text="Ready", style="TLabel")
        self.status_label.pack(side=tk.LEFT)
        
        self.apply_theme()
    
    def apply_theme(self):
        self.root.configure(bg=self.theme.bg_color)
        
        for widget in self.root.winfo_children():
            self.update_widget_colors(widget)
            
        self.create_styles()
        
        if self.theme.is_dark:
            self.theme_btn.configure(text="☀️ Light Mode")
        else:
            self.theme_btn.configure(text="🌙 Dark Mode")
    
    def update_widget_colors(self, widget):
        """Update colors for non-ttk widgets only"""
        widget_class = widget.winfo_class()
        
        if widget_class == 'Canvas':
            widget.configure(bg=self.theme.bg_color)
        elif widget_class == 'Frame':  
            widget.configure(bg=self.theme.bg_color)
        elif widget_class == 'Label':  
            widget.configure(bg=self.theme.bg_color, fg=self.theme.fg_color)
        
        for child in widget.winfo_children():
            self.update_widget_colors(child)
    
    def toggle_theme(self):
        self.theme.toggle()
        self.apply_theme()
    
    def select_directory(self):
        directory = filedialog.askdirectory()
        if directory:
            self.download_path.set(directory)
    
    def on_url_change(self, *args):
        url = self.video_url.get().strip()
        
        if not url:
            self.clear_video_info()
            return
            
        if hasattr(self, '_url_check_after_id'):
            self.root.after_cancel(self._url_check_after_id)
        
        self._url_check_after_id = self.root.after(1000, self.fetch_video_info)
    
    def clear_video_info(self):
        self.video_title_label.configure(text="")
        self.video_duration_label.configure(text="")
        self.thumbnail_label.configure(image="")
        self.video_info = None
        self.current_thumbnail = None
    
    def fetch_video_info(self):
        url = self.video_url.get().strip()
        if not url:
            return
            
        if not re.match(r'(https?://)?(www\.)?(youtube\.com|youtu\.be)/.*', url):
            return
            
        self.status_label.configure(text="Fetching video information...")
        
        def fetch_info_thread():
            try:
                ydl_opts = {
                    'quiet': True,
                    'no_warnings': True,
                    'skip_download': True,
                    'noplaylist': True,
                }
                
                with YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=False)
                    
                    self.root.after(0, lambda: self.update_video_info(info))
            except Exception as e:
                self.root.after(0, lambda: self.status_label.configure(
                    text=f"Error fetching video info: {str(e)[:50]}..."))
        
        threading.Thread(target=fetch_info_thread, daemon=True).start()
    
    def update_video_info(self, info):
        if not info:
            return
            
        self.video_info = info
        
        title = info.get('title', 'Unknown Title')
        self.video_title_label.configure(text=f"Title: {title}")
        
        duration = info.get('duration')
        if duration:
            minutes, seconds = divmod(duration, 60)
            hours, minutes = divmod(minutes, 60)
            
            if hours > 0:
                duration_str = f"{hours}:{minutes:02d}:{seconds:02d}"
            else:
                duration_str = f"{minutes}:{seconds:02d}"
                
            self.video_duration_label.configure(text=f"Duration: {duration_str}")
        
        self.fetch_thumbnail(info.get('thumbnail'))
        
        self.status_label.configure(text="Video information loaded")
    
    def fetch_thumbnail(self, thumbnail_url):
        if not thumbnail_url:
            return
            
        def download_thumbnail():
            try:
                with urllib.request.urlopen(thumbnail_url) as response:
                    image_data = response.read()
                    
                image = Image.open(BytesIO(image_data))
                image = image.resize((280, 158), Image.LANCZOS)  
                
                photo_image = ImageTk.PhotoImage(image)
                
                self.root.after(0, lambda: self.set_thumbnail(photo_image))
            except Exception as e:
                print(f"Error fetching thumbnail: {e}")
        
        threading.Thread(target=download_thumbnail, daemon=True).start()
    
    def set_thumbnail(self, photo_image):
        self.current_thumbnail = photo_image
        self.thumbnail_label.configure(image=photo_image)
    
    def download_progress_hook(self, d):
        if d['status'] == 'downloading':
            total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
            downloaded_bytes = d.get('downloaded_bytes', 0)
            
            if total_bytes > 0:
                percent = (downloaded_bytes / total_bytes) * 100
                speed = d.get('speed', 0)
                eta = d.get('eta', 0)
                
                if speed:
                    speed_str = f"{speed / 1024 / 1024:.2f} MB/s"
                else:
                    speed_str = "-- MB/s"
                    
                if eta:
                    eta_str = f"{eta} seconds remaining"
                else:
                    eta_str = "calculating..."
                
                progress_text = f"Downloading: {percent:.1f}% ({speed_str}, {eta_str})"
                
                self.root.after(0, lambda: self.update_progress(percent, progress_text))
        
        elif d['status'] == 'finished':
            self.root.after(0, lambda: self.update_progress(100, "Download finished, processing file..."))
    
    def update_progress(self, percent, text):
        self.progress_bar['value'] = percent
        self.progress_label.configure(text=text)
        self.status_label.configure(text=text)
    
    def download_video(self):
        try:
            url = self.video_url.get().strip()
            download_dir = self.download_path.get()
            format_selection = self.download_format.get()
            
            if not url or not download_dir:
                messagebox.showerror("Error", "Please complete all fields")
                return
                
            self.root.after(0, lambda: self.update_progress(0, "Starting download..."))
            
            ydl_opts = {
                'outtmpl': os.path.join(download_dir, '%(title)s.%(ext)s'),
                'progress_hooks': [self.download_progress_hook],
                'noplaylist': True
            }
            
            if format_selection == "mp4":
                ydl_opts['format'] = 'best[ext=mp4]'
            elif format_selection == "mp3":
                ydl_opts['format'] = 'bestaudio/best'
                ydl_opts['postprocessors'] = [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }]
            else: 
                ydl_opts['format'] = 'best'
            
            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                
                if info:
                    self.add_to_history({
                        'title': info.get('title', 'Unknown'),
                        'url': url,
                        'format': format_selection,
                        'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    })
            
            self.root.after(0, lambda: messagebox.showinfo("Success", "Download completed successfully"))
            
        except Exception as e:
            error_msg = str(e)
            self.root.after(0, lambda: messagebox.showerror("Error", f"An error occurred: {error_msg}"))
        finally:
            self.downloading = False
            self.root.after(0, lambda: self.reset_download_state())
    
    def reset_download_state(self):
        self.progress_bar['value'] = 0
        self.progress_label.configure(text="Ready to download")
        self.status_label.configure(text="Ready")
        self.download_btn['state'] = tk.NORMAL
    
    def start_download(self):
        if not self.downloading:
            self.downloading = True
            self.download_btn['state'] = tk.DISABLED
            download_thread = threading.Thread(target=self.download_video)
            download_thread.daemon = True
            download_thread.start()
    
    def add_to_history(self, entry):
        self.download_history.insert(0, entry)
        
        if len(self.download_history) > 20:
            self.download_history = self.download_history[:20]
        
        self.save_history()
        
        self.root.after(0, self.update_history_display)
    
    def update_history_display(self):
        for widget in self.history_inner_frame.winfo_children():
            widget.destroy()
        
        if not self.download_history:
            ttk.Label(self.history_inner_frame, text="No download history yet", style="TLabel").pack(pady=10)
            return
        
        for i, entry in enumerate(self.download_history):
            item_frame = ttk.Frame(self.history_inner_frame, style="TFrame")
            item_frame.pack(fill=tk.X, pady=(0, 10))
            
            title = entry.get('title', 'Unknown')
            if len(title) > 30:
                title = title[:27] + "..."
            
            ttk.Label(item_frame, text=title, style="TLabel", wraplength=260).pack(anchor=tk.W)
            
            details = f"{entry.get('format', 'unknown')} • {entry.get('date', '')}"
            ttk.Label(item_frame, text=details, style="TLabel").pack(anchor=tk.W)
            
            if i < len(self.download_history) - 1:
                separator = ttk.Frame(self.history_inner_frame, height=1)
                separator.pack(fill=tk.X, pady=(0, 10))
                separator.configure(style="TFrame")
    
    def load_history(self):
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r') as f:
                    self.download_history = json.load(f)
        except Exception as e:
            print(f"Error loading history: {e}")
            self.download_history = []
    
    def save_history(self):
        try:
            with open(self.history_file, 'w') as f:
                json.dump(self.download_history, f)
        except Exception as e:
            print(f"Error saving history: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = YouTubeDownloaderApp(root)
    root.mainloop()