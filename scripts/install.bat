@echo off

set SCRIPT_DIR=%~dp0

python -m venv "%SCRIPT_DIR%\..\venv"
"%SCRIPT_DIR%\..\venv\Scripts\pip" install -r "%SCRIPT_DIR%\..\requirements.txt"
