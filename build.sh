#!/bin/bash
set -e

echo "📦 Building React frontend..."
npm run build

echo "📦 Installing pip and Python dependencies..."
cd server
curl -sS https://bootstrap.pypa.io/get-pip.py | python3
python3 -m pip install --no-cache-dir -r requirements.txt

echo "✅ Build complete!"
