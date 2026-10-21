@echo off
cd /d "%~dp0"
py -m pip install --upgrade pip
py -m pip install --upgrade yt-dlp pyinstaller
if errorlevel 1 (echo Install failed. Check Python and internet connection.& pause & exit /b 1)
echo Dependencies installed. FFmpeg is recommended for merging separate video and audio.
pause
