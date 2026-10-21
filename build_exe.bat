@echo off
setlocal
cd /d "%~dp0"

echo ========================================
echo  Youtube Video Downloader - EXE Builder
echo ========================================
echo.

where python >nul 2>nul
if errorlevel 1 (
  echo ERROR: Python was not found. Install Python 3 and enable Add Python to PATH.
  pause
  exit /b 1
)

echo Installing or updating build dependencies...
python -m pip install --upgrade yt-dlp pyinstaller
if errorlevel 1 (
  echo ERROR: Could not install dependencies. Check your internet connection.
  pause
  exit /b 1
)

if not exist "logo.ico" (
  echo ERROR: logo.ico is missing. Put logo.ico in this same folder.
  pause
  exit /b 1
)

echo Building Windows executable...
python -m PyInstaller --noconfirm --clean --onefile --windowed --icon="logo.ico" --add-data "logo.ico;." --name "YoutubeVideoDownloader" "youtube_video_downloader.py"
if errorlevel 1 (
  echo ERROR: Build failed. Read the messages above.
  pause
  exit /b 1
)

echo.
echo Build complete. Your EXE is: dist\YoutubeVideoDownloader.exe
echo.
pause
