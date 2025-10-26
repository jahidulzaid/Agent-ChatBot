# Agentic RAG Chatbot - Quick Setup Script
# This script helps you set up the project quickly

Write-Host "🤖 Agentic RAG Chatbot Setup" -ForegroundColor Cyan
Write-Host "=============================" -ForegroundColor Cyan
Write-Host ""

# Check Python
Write-Host "Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version
    Write-Host "✓ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Python not found. Please install Python 3.8+" -ForegroundColor Red
    exit 1
}

# Check Node.js
Write-Host "Checking Node.js installation..." -ForegroundColor Yellow
try {
    $nodeVersion = node --version
    Write-Host "✓ Node.js found: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Node.js not found. Please install Node.js 16+" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Setting up Backend..." -ForegroundColor Cyan
Write-Host "--------------------" -ForegroundColor Cyan

# Backend setup
Set-Location backend

# Create virtual environment
if (!(Test-Path "venv")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
    Write-Host "✓ Virtual environment created" -ForegroundColor Green
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"

# Install dependencies
Write-Host "Installing Python dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt
Write-Host "✓ Backend dependencies installed" -ForegroundColor Green

# Create .env if it doesn't exist
if (!(Test-Path ".env")) {
    Write-Host "Creating .env file..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    Write-Host "✓ .env file created - PLEASE UPDATE WITH YOUR API KEY" -ForegroundColor Yellow
}

Set-Location ..

Write-Host ""
Write-Host "Setting up Frontend..." -ForegroundColor Cyan
Write-Host "---------------------" -ForegroundColor Cyan

# Frontend setup
Set-Location frontend

Write-Host "Installing Node.js dependencies..." -ForegroundColor Yellow
npm install
Write-Host "✓ Frontend dependencies installed" -ForegroundColor Green

Set-Location ..

Write-Host ""
Write-Host "============================================" -ForegroundColor Green
Write-Host "✓ Setup Complete!" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Edit backend/.env and add your OpenRouter API key" -ForegroundColor Yellow
Write-Host "2. Start the backend:" -ForegroundColor Yellow
Write-Host "   cd backend" -ForegroundColor White
Write-Host "   .\venv\Scripts\Activate.ps1" -ForegroundColor White
Write-Host "   python main.py" -ForegroundColor White
Write-Host ""
Write-Host "3. In a new terminal, start the frontend:" -ForegroundColor Yellow
Write-Host "   cd frontend" -ForegroundColor White
Write-Host "   npm run dev" -ForegroundColor White
Write-Host ""
Write-Host "4. Open http://localhost:3000 in your browser" -ForegroundColor Yellow
Write-Host ""
Write-Host "Happy chatting! 🚀" -ForegroundColor Cyan
