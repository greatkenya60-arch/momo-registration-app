#!/bin/bash
# Build script for Render deployment

echo "🚀 Building MTN MoMo Registration App for Render..."

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p static
mkdir -p templates
mkdir -p images

# Set permissions
echo "🔧 Setting permissions..."
chmod -R 755 static templates images

echo "✅ Build completed successfully!"