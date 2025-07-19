@echo off
REM Setup script for Prem Kumar's AI Engineer Portfolio (Windows)

echo 🚀 Setting up Prem Kumar's AI Engineer Portfolio locally...

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed. Please install Python 3.8 or higher.
    pause
    exit /b 1
)

echo ✅ Python found

REM Install dependencies
echo 📦 Installing dependencies...
pip install -r requirements_local.txt

if errorlevel 1 (
    echo ❌ Failed to install dependencies
    pause
    exit /b 1
)

echo ✅ Dependencies installed successfully

REM Check if .env file exists
if not exist ".env" (
    echo ❌ .env file not found
    pause
    exit /b 1
)

findstr "your-email@gmail.com" .env >nul
if not errorlevel 1 (
    echo ⚠️  Remember to update your .env file with:
    echo    - SESSION_SECRET (random string)
    echo    - MAIL_USERNAME (your Gmail address)
    echo    - MAIL_PASSWORD (Gmail app password)
) else (
    echo ✅ .env file appears to be configured
)

echo.
echo 🎉 Setup complete! To start the portfolio:
echo    python run_local.py
echo.
echo 📖 For detailed instructions, see README_LOCAL.md
echo 🌐 Website will be available at: http://localhost:5000
pause