@echo off
setlocal

REM Check if Python is installed
python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo Python is not installed. Please install Python and try again.
    pause
    exit /b 1
)

REM Upgrade pip to ensure the latest version is used
python -m pip install --upgrade pip

REM Install required Python packages
python -m pip install requests fake_useragent termcolor tqdm

REM Check if the installation was successful
IF %ERRORLEVEL% NEQ 0 (
    echo Failed to install required packages. Please check your network connection and try again.
    pause
    exit /b 1
)

REM Execute the Python script
python DDostool.py

REM Check if the script executed successfully
IF %ERRORLEVEL% NEQ 0 (
    echo The script encountered an error. Please check the script and try again.
    pause
    exit /b 1
)

pause
