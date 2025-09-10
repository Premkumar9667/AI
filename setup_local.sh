#!/bin/bash
# Setup script for Prem Kumar's AI Engineer Portfolio

echo "🚀 Setting up Prem Kumar's AI Engineer Portfolio locally..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Check if pip is installed
if ! command -v pip &> /dev/null && ! command -v pip3 &> /dev/null; then
    echo "❌ pip is not installed. Please install pip."
    exit 1
fi

echo "✅ Python and pip found"

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements_local.txt

if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed successfully"
else
    echo "❌ Failed to install dependencies"
    exit 1
fi

# Check if .env file exists and has been configured
if [ -f ".env" ]; then
    if grep -q "your-email@gmail.com" .env; then
        echo "⚠️  Remember to update your .env file with:"
        echo "   - SESSION_SECRET (random string)"
        echo "   - MAIL_USERNAME (your Gmail address)"
        echo "   - MAIL_PASSWORD (Gmail app password)"
    else
        echo "✅ .env file appears to be configured"
    fi
else
    echo "❌ .env file not found"
    exit 1
fi

echo ""
echo "🎉 Setup complete! To start the portfolio:"
echo "   python run_local.py"
echo ""
echo "📖 For detailed instructions, see README_LOCAL.md"
echo "🌐 Website will be available at: http://localhost:5000"