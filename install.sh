#!/bin/bash

echo "============================================================"
echo "   AI Study Assistant - Installation Script"
echo "============================================================"
echo ""

echo "Step 1: Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.8+ from python.org"
    exit 1
fi

python3 --version

echo ""
echo "Step 2: Creating virtual environment (recommended)..."
read -p "Do you want to create a virtual environment? (y/n) " CREATE_VENV
if [[ $CREATE_VENV == "y" || $CREATE_VENV == "Y" ]]; then
    python3 -m venv venv
    source venv/bin/activate
    echo "Virtual environment created and activated"
fi

echo ""
echo "Step 3: Installing Python dependencies..."
python3 -m pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "Step 4: Creating necessary directories..."
mkdir -p data logs

echo ""
echo "Step 5: Creating configuration file..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "Created .env configuration file"
else
    echo ".env already exists, skipping..."
fi

echo ""
echo "============================================================"
echo "   Installation Complete!"
echo "============================================================"
echo ""
echo "IMPORTANT: You need to install OLLAMA separately"
echo ""
echo "1. Download OLLAMA from: https://ollama.ai/download"
echo "2. Install OLLAMA"
echo "3. Run: ollama pull phi3:mini"
echo ""
echo "For Core i3 laptops, use one of these models:"
echo "   - phi3:mini (3.8GB) - RECOMMENDED - Good balance"
echo "   - llama3.2:1b (1.3GB) - Lighter, faster but less capable"
echo ""
echo "After installing OLLAMA, you can:"
echo "   - Run: python3 setup.py     (to verify everything)"
echo "   - Run: python3 main.py      (to start the assistant)"
echo "   - Run: python3 demo.py      (to see examples)"
echo ""
