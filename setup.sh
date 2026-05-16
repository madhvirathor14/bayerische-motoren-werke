#!/bin/bash

# ============================================
# BMW GraphRAG Project - Mac/Linux Setup Script
# ============================================

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  🚗 Bayerische Motoren Werke - GraphRAG Project              ║"
echo "║     Mac/Linux Setup Script                                   ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed"
    echo "   Install from: https://www.python.org or use:"
    echo "   Mac: brew install python3"
    echo "   Linux: sudo apt-get install python3"
    exit 1
fi

echo "✅ Python found: $(python3 --version)"

# Create virtual environment
if [ ! -d "venv" ]; then
    echo ""
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo ""
echo "🔄 Activating virtual environment..."
source venv/bin/activate
if [ $? -ne 0 ]; then
    echo "❌ Failed to activate virtual environment"
    exit 1
fi
echo "✅ Virtual environment activated"

# Install dependencies
echo ""
echo "📦 Installing dependencies..."
pip install -q -r requirements.txt
if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies"
    echo "   Try: pip install -r requirements.txt"
    exit 1
fi
echo "✅ Dependencies installed"

# Check if .env exists
echo ""
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found!"
    echo ""
    echo "Please follow these steps:"
    echo "1. Copy .env.example to .env:"
    echo "   cp .env.example .env"
    echo ""
    echo "2. Edit .env and add your GROQ API key:"
    echo "   Get free key: https://console.groq.com"
    echo ""
    echo "3. Save and run this script again"
    echo ""
    exit 1
else
    echo "✅ .env file found"
fi

# Ready to launch
echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  ✅ Setup Complete! Launching Streamlit Dashboard...         ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Launch Streamlit
streamlit run app.py

# If streamlit fails
if [ $? -ne 0 ]; then
    echo ""
    echo "❌ Failed to launch Streamlit"
    echo ""
    echo "Try running manually:"
    echo "   streamlit run app.py"
    echo ""
    exit 1
fi
