#!/bin/bash
# Build script for DigitalOcean App Platform
# Installs both Node.js (React frontend) and Python (Flask backend) dependencies

set -e

echo "📦 Installing Node.js dependencies and building React frontend..."
npm install
npm run build

echo "📦 Installing Python dependencies..."
cd server

# Use pip3 if pip is not available
if command -v pip &> /dev/null; then
    pip install -r requirements.txt
elif command -v pip3 &> /dev/null; then
    pip3 install -r requirements.txt
else
    echo "Installing pip..."
    python3 -m ensurepip --upgrade
    python3 -m pip install -r requirements.txt
fi

echo "✅ Build complete!"
