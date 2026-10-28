@echo off
rem Run once on the TDT computer: puts a "TDT Launcher" shortcut on the
rem desktop that runs TDT_Launcher.bat, with the OpenWorkbench icon if
rem OpenWorkbench is installed at the path below.

set "TARGET=%~dp0TDT_Launcher.bat"
set "ICON=C:\TDT\OpenEx\OpenWorkbench.exe"

powershell -NoProfile -ExecutionPolicy Bypass -Command "$s=(New-Object -ComObject WScript.Shell).CreateShortcut([Environment]::GetFolderPath('Desktop')+'\TDT Launcher.lnk'); $s.TargetPath=$env:TARGET; $s.WorkingDirectory=(Split-Path $env:TARGET); if (Test-Path $env:ICON) { $s.IconLocation=$env:ICON+',0' }; $s.Description='Start OpenEx and the TDT controller'; $s.Save()"

if errorlevel 1 (
    echo Could not create the shortcut.
) else (
    echo "TDT Launcher" shortcut created on the desktop.
)
pause
