#!/bin/bash
# Install dependencies from backend folder
pip install -r backend/requirements.txt
# Start the application
cd backend && python main.py
