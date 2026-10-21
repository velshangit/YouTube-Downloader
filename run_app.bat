@echo off
cd /d "%~dp0"
py -m pip install --upgrade yt-dlp
py youtube_video_downloader.py
if errorlevel 1 pause
