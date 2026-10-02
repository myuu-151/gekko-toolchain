@echo off
rem gekko-toolchain: undoes Install.bat (DEVKITPRO and DEVKITPPC back to what they were, or removed).
rem The folder itself can then be deleted.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0setup\install.ps1" -Uninstall
pause
