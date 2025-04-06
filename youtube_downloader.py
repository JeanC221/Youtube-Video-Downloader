import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import os
from yt_dlp import YoutubeDL

class YouTubeDownloaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("YouTube Video Downloader")
        self.root.geometry("600x400")
        self.root.resizable(False, False)
        
        # Variables
        self.download_path = tk.StringVar()
        self.video_url = tk.StringVar()
        self.download_format = tk.StringVar(value="mp4")
        self.downloading = False
        
        # Crear interfaz
        self.create_widgets()
        
    def create_widgets(self):
        # Frame principal
        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Entrada de URL
        ttk.Label(main_frame, text="URL del video de YouTube:").grid(row=0, column=0, sticky=tk.W)
        url_entry = ttk.Entry(main_frame, textvariable=self.video_url, width=50)
        url_entry.grid(row=1, column=0, columnspan=2, pady=5, sticky=tk.EW)
        
        # Selector de formato
        ttk.Label(main_frame, text="Formato de descarga:").grid(row=2, column=0, sticky=tk.W, pady=10)
        ttk.Radiobutton(main_frame, text="MP4", variable=self.download_format, value="mp4").grid(row=3, column=0, sticky=tk.W)
        ttk.Radiobutton(main_frame, text="Formato original", variable=self.download_format, value="original").grid(row=3, column=1, sticky=tk.W)
        
        # Selector de ubicación
        ttk.Label(main_frame, text="Ubicación de descarga:").grid(row=4, column=0, sticky=tk.W, pady=10)
        ttk.Entry(main_frame, textvariable=self.download_path, width=40).grid(row=5, column=0, sticky=tk.EW)
        ttk.Button(main_frame, text="Examinar", command=self.select_directory).grid(row=5, column=1, padx=5)
        
        # Barra de progreso
        self.progress_bar = ttk.Progressbar(main_frame, orient=tk.HORIZONTAL, mode='determinate')
        self.progress_bar.grid(row=6, column=0, columnspan=2, pady=20, sticky=tk.EW)
        
        # Botón de descarga
        self.download_btn = ttk.Button(main_frame, text="Descargar Video", command=self.start_download)
        self.download_btn.grid(row=7, column=0, columnspan=2, pady=10)
        
        # Configurar grid
        main_frame.columnconfigure(0, weight=1)
        
    def select_directory(self):
        directory = filedialog.askdirectory()
        if directory:
            self.download_path.set(directory)
    
    def download_progress_hook(self, d):
        if d['status'] == 'downloading':
            total_bytes = d.get('total_bytes')
            downloaded_bytes = d.get('downloaded_bytes')
            if total_bytes and downloaded_bytes:
                percent = (downloaded_bytes / total_bytes) * 100
                self.progress_bar['value'] = percent
                self.root.update_idletasks()
    
    def download_video(self):
        try:
            url = self.video_url.get()
            download_dir = self.download_path.get()
            format_selection = self.download_format.get()
            
            if not url or not download_dir:
                messagebox.showerror("Error", "Por favor completa todos los campos")
                return
                
            ydl_opts = {
                'outtmpl': os.path.join(download_dir, '%(title)s.%(ext)s'),
                'progress_hooks': [self.download_progress_hook],
                'noplaylist': True
            }
            
            # Modificación clave para evitar requerir FFmpeg
            if format_selection == "mp4":
                ydl_opts['format'] = 'best[ext=mp4]'  # Formatos MP4 que ya incluyen audio
            else:
                ydl_opts['format'] = 'best'
            
            with YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
                
            messagebox.showinfo("Éxito", "Descarga completada correctamente")
            
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error: {str(e)}")
        finally:
            self.downloading = False
            self.progress_bar['value'] = 0
            self.download_btn['state'] = tk.NORMAL
    
    def start_download(self):
        if not self.downloading:
            self.downloading = True
            self.download_btn['state'] = tk.DISABLED
            download_thread = threading.Thread(target=self.download_video)
            download_thread.start()

if __name__ == "__main__":
    root = tk.Tk()
    app = YouTubeDownloaderApp(root)
    root.mainloop()