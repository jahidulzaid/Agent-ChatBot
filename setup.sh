#!/bin/bash

# Agentic RAG Chatbot - Quick Setup Script
# This script helps you set up the project quickly

echo "🤖 Agentic RAG Chatbot Setup"
echo "============================="
echo ""

# Check Python
echo "Checking Python installation..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo "✓ Python found: $PYTHON_VERSION"
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_VERSION=$(python --version)
    echo "✓ Python found: $PYTHON_VERSION"
    PYTHON_CMD="python"
else
    echo "✗ Python not found. Please install Python 3.8+"
    exit 1
fi

# Check Node.js
echo "Checking Node.js installation..."
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    echo "✓ Node.js found: $NODE_VERSION"
else
    echo "✗ Node.js not found. Please install Node.js 16+"
    exit 1
fi

echo ""
echo "Setting up Backend..."
echo "--------------------"

# Backend setup
cd backend

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    $PYTHON_CMD -m venv venv
    echo "✓ Virtual environment created"
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt
echo "✓ Backend dependencies installed"

# Create .env if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    cp .env.example .env
    echo "✓ .env file created - PLEASE UPDATE WITH YOUR API KEY"
fi

cd ..

echo ""
echo "Setting up Frontend..."
echo "---------------------"

# Frontend setup
cd frontend

echo "Installing Node.js dependencies..."
npm install
echo "✓ Frontend dependencies installed"

cd ..

echo ""
echo "============================================"
echo "✓ Setup Complete!"
echo "============================================"
echo ""
echo "Next steps:"
echo "1. Edit backend/.env and add your OpenRouter API key"
echo "2. Start the backend:"
echo "   cd backend"
echo "   source venv/bin/activate"
echo "   python main.py"
echo ""
echo "3. In a new terminal, start the frontend:"
echo "   cd frontend"
echo "   npm run dev"
echo ""
echo "4. Open http://localhost:3000 in your browser"
echo ""
echo "Happy chatting! 🚀"
