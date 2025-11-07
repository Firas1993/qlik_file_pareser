#!/bin/bash
# Installation script for Canadian Store Locator Scraper

echo "🍁 Installing Canadian Store Locator Scraper Dependencies..."
echo "============================================================"

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    echo "   Please install Python 3 first."
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"

# Check if pip3 is available
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is required but not installed."
    echo "   Please install pip3 first."
    exit 1
fi

echo "✅ pip3 found: $(pip3 --version)"

# Install requirements
echo ""
echo "📦 Installing Python dependencies..."
pip3 install -r requirements.txt

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 Installation completed successfully!"
    echo ""
    echo "🚀 To run the scraper:"
    echo "   python3 main_scraper.py"
    echo ""
    echo "📁 Output files will be saved to: ./output/"
    echo "🌐 Supported websites: GM Collin, YK Canada"
else
    echo ""
    echo "❌ Installation failed. Please check the error messages above."
    exit 1
fi