@echo off
setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo Creating virtual environment...
    py -m venv .venv
    if errorlevel 1 goto setup_failed
)

call ".venv\Scripts\activate.bat"
if errorlevel 1 goto activation_failed

echo Installing requirements...
python -m pip install -r requirements.txt
if errorlevel 1 goto install_failed

echo Running backtest...
python main.py
exit /b %ERRORLEVEL%

:setup_failed
echo Failed to create the virtual environment. Make sure Python and the py launcher are installed.
exit /b 1

:activation_failed
echo Failed to activate the virtual environment.
exit /b 1

:install_failed
echo Failed to install requirements.
exit /b 1
