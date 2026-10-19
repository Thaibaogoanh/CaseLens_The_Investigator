@echo off
cd /d "%~dp0"
echo CaseLens - open http://127.0.0.1:8000 after the server starts.
where py >nul 2>nul
if %errorlevel% equ 0 (
  py -3 server.py
) else (
  python server.py
)
pause
