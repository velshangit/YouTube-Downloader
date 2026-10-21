Youtube Video Downloader — updated build files

Files
- youtube_video_downloader.py: app source with logo.ico window icon support.
- build_exe.bat: installs/updates yt-dlp and PyInstaller, then builds the EXE.
- logo.ico: your app icon, bundled into the EXE and used for the window icon.

Build on Windows
1. Install Python 3 from https://www.python.org/downloads/ and enable “Add Python to PATH”.
2. Keep all three files in the same folder.
3. Double-click build_exe.bat and wait for it to finish.
4. Find dist\YoutubeVideoDownloader.exe.

Notes
- Building a Windows EXE should be done on Windows.
- This does not automatically make the publisher verified or remove all SmartScreen warnings.
- Download only videos you own or are authorized to save, and follow the website's terms.
