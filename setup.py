#!/usr/bin/env python3
"""
FaceAuth Setup Script
====================

This script sets up the FaceAuth environment and installs all required dependencies.
"""

import sys
import subprocess
import os
from pathlib import Path


def check_python_version():
    """Check if Python version is 3.8 or higher."""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"   Current version: {sys.version}")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    return True


def install_requirements():
    """Install required packages from requirements.txt."""
    print("📦 Installing dependencies...")
    
    try:
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ], check=True, capture_output=True, text=True)
        
        print("✅ Dependencies installed successfully!")
        return True
        
    except subprocess.CalledProcessError as e:
        print("❌ Failed to install dependencies:")
        print(e.stderr)
        return False
    except Exception as e:
        print(f"❌ Installation error: {e}")
        return False


def create_directories():
    """Create necessary directories."""
    print("📁 Creating directories...")
    
    directories = ["face_data", "logs"]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ Created: {directory}/")
    
    return True


def test_imports():
    """Test if all required packages can be imported."""
    print("🧪 Testing imports...")
    
    required_packages = [
        ("cv2", "OpenCV"),
        ("numpy", "NumPy"),
        ("cryptography", "Cryptography"),
        ("click", "Click"),
        ("deepface", "DeepFace")
    ]
    
    all_success = True
    
    for package, name in required_packages:
        try:
            __import__(package)
            print(f"✅ {name}")
        except ImportError:
            print(f"❌ {name} - not available")
            all_success = False
    
    return all_success


def main():
    """Main setup function."""
    print("🚀 FaceAuth Setup")
    print("=" * 40)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Check if requirements.txt exists
    if not Path("requirements.txt").exists():
        print("❌ requirements.txt not found")
        print("   Please run this script from the FaceAuth directory")
        sys.exit(1)
    
    # Install requirements
    if not install_requirements():
        sys.exit(1)
    
    # Create directories
    if not create_directories():
        sys.exit(1)
    
    # Test imports
    if not test_imports():
        print("\n⚠️  Some packages failed to import")
        print("   You may need to restart your terminal or Python environment")
    
    print("\n🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Enroll your face: python main.py enroll-face")
    print("2. Get help: python main.py --help")
    print("3. Check system info: python main.py info")


if __name__ == "__main__":
    main()
