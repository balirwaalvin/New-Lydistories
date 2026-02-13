#!/bin/bash
# Build script for DigitalOcean App Platform
# Installs both Node.js (React frontend) and Python (Flask backend) dependencies

set -e

echo "📦 Installing Node.js dependencies and building React frontend..."
cd /workspace
npm install
npm run build

echo "📦 Installing Python dependencies..."
cd /workspace/server
pip install -r requirements.txt

echo "✅ Build complete!"
