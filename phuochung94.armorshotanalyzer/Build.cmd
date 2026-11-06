@echo off
setlocal
where py >nul 2>nul
if errorlevel 1 (
  echo Python Launcher was not found. Run Python 3 directly; see README_WINDOWS.md.
  exit /b 1
)
py -3 "%~dp0res\development\windows_project.py" build %*
exit /b %errorlevel%
