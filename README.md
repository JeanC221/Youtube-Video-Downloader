# YouTube Video Downloader Pro 🎥

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![Download Now](https://img.shields.io/badge/Download-Windows%20EXE-brightgreen)](https://drive.google.com/your-download-link)  (Soon)

Modern desktop application to download YouTube videos in MP4, MP3, or original format with customizable themes and persistent history.


## 🌟 Features
- **One-Click Downloads** - MP4, MP3, or original format
- **Smart Preview** - Thumbnails & video details before downloading
- **Dark/Light Themes** - Customizable interface colors
- **Portable Version** - No installation required
- **Download History** - Track your last 20 downloads

## 🚀 Quick Start for Everyone

### For Non-Technical Users
1. **[Download Windows Installer](https://drive.google.com/your-download-link)**  
   ![Installation Demo](https://i.imgur.com/install-demo.gif)

2. **Run Setup**  
   ```text
   Double-click → Next → Install → Finish


## For Power Users & Developers

1. Clone repository
git clone https://github.com/JeanC221/Youtube-Video-Downloader.git

2. Create virtual environment
python -m venv venv && source venv/bin/activate  # Linux/Mac
venv\Scripts\activate                            # Windows

3. Install requirements
pip install -r requirements.txt

# 4. Run application
python main.py


## 🔨 Build Your Own Executable

pyinstaller --onefile --windowed \
--icon=assets/icon.ico \
--add-data "assets/*;assets" \
--name "YouTube Downloader" main.py


MIT Licensed - See LICENSE for full details.
Supported Platforms: Windows 10/11 (64-bit)


Star this repo if you find it useful! ⭐
Developer: JeanC221 • 🚀 Passionate about open source tools
