@echo off
:: CAI Setup Script for Windows
:: This script helps set up CAI for bug bounty hunting
echo Setting up CAI for Bug Bounty Hunting...

:: Check for WSL
where wsl >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo WSL not found! Please install Windows Subsystem for Linux first.
    echo Run this command in PowerShell as Administrator: wsl --install
    pause
    exit /b 1
)

:: Run the setup command in WSL
echo Running setup in WSL...
wsl bash -c "cd /mnt/c/Users/logan/code/cai && sudo apt update && sudo apt install -y git python3-pip python3-venv python3.12-venv && python3 -m pip install -e ."

:: Create .env file if it doesn't exist
if not exist "c:\Users\logan\code\cai\.env" (
    echo Creating .env file...
    copy "c:\Users\logan\code\cai\.env.example" "c:\Users\logan\code\cai\.env"
    echo Please edit the .env file to add your API keys.
)

echo.
echo Setup Complete!
echo.
echo To run CAI:
echo 1. Open WSL terminal
echo 2. Navigate to: cd /mnt/c/Users/logan/code/cai
echo 3. Run: python -m cai.cli
echo.
echo For bug bounty, run the example script:
echo cd /mnt/c/Users/logan/code/cai/examples/cybersecurity
echo python bug_bounty_run.py
echo.
echo See WINDOWS_SETUP_GUIDE.md for more details
pause
