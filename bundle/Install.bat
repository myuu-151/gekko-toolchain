@echo off
rem gekko-toolchain: points DEVKITPRO and DEVKITPPC at this folder (for you, not the whole machine).
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0setup\install.ps1"
pause
