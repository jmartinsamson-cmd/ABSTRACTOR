#!/bin/bash
# Setup and run the Bradley Abstract Cover Page Generator

echo "🚀 Setting up Bradley Abstract Cover Page Generator..."

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "✅ Activating virtual environment..."
source venv/bin/activate

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
echo "   source venv/bin/activate"
echo "   streamlit run streamlit_app.py"
echo ""
