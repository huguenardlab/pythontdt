@echo off
rem Starts the TDT experiment launcher (see README_launcher.md).
rem The desktop shortcut made by make_desktop_shortcut.bat runs this file.
rem This console shows the [Launcher] messages and closes with the launcher.

pushd "%~dp0"
where python >nul 2>nul
if errorlevel 1 (
    echo Python was not found. Install it or add it to the PATH.
    pause
    exit /b 1
)
python launcher_gui.py
rem keep the window open if the launcher crashed, so the error can be read
if errorlevel 1 pause
popd
