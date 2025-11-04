#!/bin/bash
# Install dependencies from backend folder using python -m pip
curl -LsSf https://astral.sh/uv/install.sh | sh


uv pip install --upgrade pip
uv pip install -r backend/requirements.txt
# Start the application
cd backend && python main.py
