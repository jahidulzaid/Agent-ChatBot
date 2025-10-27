#!/bin/bash
# Install dependencies from backend folder using python -m pip
python -m pip install --upgrade pip
python -m pip install -r backend/requirements.txt
# Start the application
cd backend && python main.py
