#!/bin/bash
# Setup and run the Bradley Abstract Cover Page Generator

echo "🚀 Setting up Bradley Abstract Cover Page Generator..."

# Prefer .venv (matches VS Code and tasks). Fallback to existing venv if present.
VENV_DIR=".venv"
if [ -d "venv" ] && [ ! -d ".venv" ]; then
    VENV_DIR="venv"
fi

# Create virtual environment if it doesn't exist
if [ ! -d "$VENV_DIR" ]; then
    echo "📦 Creating virtual environment at $VENV_DIR..."
    python3 -m venv "$VENV_DIR"
fi

# Activate virtual environment
echo "✅ Activating virtual environment ($VENV_DIR)..."
source "$VENV_DIR/bin/activate"

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "📥 Installing requirements..."
pip install -r requirements.txt

# Create output directory
echo "📁 Creating output directory..."
mkdir -p output

echo ""
echo "✅ Setup complete!"
echo ""
echo "🎯 To run the application:"
echo "   source $VENV_DIR/bin/activate"
echo "   streamlit run streamlit_app.py"
echo ""
