#!/bin/bash

# FaceAuth Environment Fix Script
# This script sets up the correct environment variables to fix Qt/OpenCV issues on Linux

echo "🔧 Setting up FaceAuth environment..."
echo "🖥️  Configuring Qt platform for Linux compatibility..."

# Fix Qt platform issues (common on Ubuntu/Linux with OpenCV)
export QT_QPA_PLATFORM=xcb
export QT_QPA_PLATFORM_PLUGIN_PATH=""

# Additional OpenCV stability fixes
export OPENCV_VIDEOIO_PRIORITY_MSMF=0
export OPENCV_VIDEOIO_DEBUG=1

echo "✅ Environment configured!"
echo "🚀 Running FaceAuth enrollment..."
echo "📋 Any detailed errors will be shown below:"
printf '=%.0s' {1..60}

# Run the enrollment command
python main.py enroll

echo ""
echo "🔍 If you see detailed error messages above, please copy ALL the output"
echo "   from 'Running FaceAuth enrollment...' to the very end and share it."
