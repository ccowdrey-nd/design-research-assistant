#!/bin/bash
# Setup script for Design Assistant Chatbot

set -e

echo "🎨 Design Assistant Setup Script"
echo "=================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.9 or higher."
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 16 or higher."
    exit 1
fi

echo "✅ Node.js found: $(node --version)"
echo ""

# Backend setup
echo "📦 Setting up backend..."
cd backend

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install Python dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create .env if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    cp env.example .env
    echo "⚠️  Please edit backend/.env with your API keys and configuration"
else
    echo "✅ .env file already exists"
fi

cd ..

# Frontend setup
echo ""
echo "📦 Setting up frontend..."
cd frontend

# Install Node dependencies
echo "Installing Node dependencies..."
npm install

# Create .env if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    cp env.example .env
    echo "⚠️  Please edit frontend/.env with your Okta configuration"
else
    echo "✅ .env file already exists"
fi

cd ..

# Create data directory
echo ""
echo "📁 Creating data directory..."
mkdir -p data/chromadb

echo ""
echo "✅ Setup complete!"
echo ""
echo "📝 Next steps:"
echo "1. Edit backend/.env with your API keys (OpenAI, Figma, Google, Okta)"
echo "2. Edit frontend/.env with your Okta configuration"
echo "3. Start the backend: cd backend && source venv/bin/activate && python main.py"
echo "4. Start the frontend (in a new terminal): cd frontend && npm start"
echo "5. Open http://localhost:3000 in your browser"
echo ""
echo "📖 See README.md for detailed configuration instructions"

