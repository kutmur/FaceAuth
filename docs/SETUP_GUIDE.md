# FaceAuth Setup Guide

This guide will walk you through setting up FaceAuth on your system step by step.

## Table of Contents
- [System Requirements](#system-requirements)
- [Installation](#installation)
- [Platform-Specific Setup](#platform-specific-setup)
- [Configuration](#configuration)
- [Verification](#verification)
- [Troubleshooting](#troubleshooting)

## System Requirements

### Hardware Requirements
- **Camera**: USB webcam, built-in camera, or external camera
- **RAM**: Minimum 4GB (8GB recommended for better performance)
- **Storage**: At least 500MB free space
- **Architecture**: 64-bit processor (x86_64 or ARM64)

### Software Requirements
- **Python**: Version 3.8 or higher
- **Operating System**: 
  - Windows 10/11 (64-bit)
  - macOS 10.15+ (Catalina or newer)
  - Linux (Ubuntu 18.04+, CentOS 7+, or equivalent)

### Camera Compatibility
- USB UVC-compatible cameras
- Built-in laptop cameras
- External USB cameras
- IP cameras (with RTSP support)

## Installation

### Method 1: Quick Install (Recommended)

#### Step 1: Clone the Repository
```bash
# Clone FaceAuth
git clone https://github.com/your-username/faceauth.git
cd faceauth
```

#### Step 2: Run Setup Script

**Windows (PowerShell):**
```powershell
# Download and run setup script
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/your-username/faceauth/main/scripts/setup_windows.ps1" -OutFile "setup.ps1"
.\setup.ps1
```

**macOS/Linux:**
```bash
# Download and run setup script
curl -fsSL https://raw.githubusercontent.com/your-username/faceauth/main/scripts/setup_unix.sh | bash
```

### Method 2: Manual Installation

#### Step 1: Install Python Dependencies
```bash
# Create virtual environment (recommended)
python -m venv faceauth_env

# Activate virtual environment
# Windows:
faceauth_env\Scripts\activate
# macOS/Linux:
source faceauth_env/bin/activate

# Install dependencies
pip install -r requirements.txt
```

#### Step 2: Install System Dependencies

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install -y python3-dev libopencv-dev ffmpeg
```

**CentOS/RHEL:**
```bash
sudo yum groupinstall -y "Development Tools"
sudo yum install -y python3-devel opencv-devel ffmpeg
```

**macOS (with Homebrew):**
```bash
brew install opencv ffmpeg
```

**Windows:**
- No additional system dependencies required
- Windows Defender may require approval for camera access

## Platform-Specific Setup

### Windows Setup

#### Prerequisites
1. **Install Python 3.8+** from [python.org](https://python.org)
2. **Install Microsoft Visual C++ Redistributable** (if not already installed)
3. **Install Git** from [git-scm.com](https://git-scm.com)

#### Installation Steps
```powershell
# 1. Clone repository
git clone https://github.com/your-username/faceauth.git
cd faceauth

# 2. Create virtual environment
python -m venv faceauth_env
faceauth_env\Scripts\activate

# 3. Upgrade pip
python -m pip install --upgrade pip

# 4. Install dependencies
pip install -r requirements.txt

# 5. Initialize configuration
python main.py config-init

# 6. Run system check
python main.py system-check

# 7. Test camera access
python main.py test-camera
```

#### Windows Security Settings
1. **Allow camera access**: Settings → Privacy → Camera → Allow apps to access camera
2. **Windows Defender**: Add FaceAuth folder to exclusions if needed
3. **Firewall**: No network access needed, but ensure local file access

### macOS Setup

#### Prerequisites
1. **Install Homebrew**: `/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"`
2. **Install Python**: `brew install python@3.11`
3. **Install Xcode Command Line Tools**: `xcode-select --install`

#### Installation Steps
```bash
# 1. Clone repository
git clone https://github.com/your-username/faceauth.git
cd faceauth

# 2. Create virtual environment
python3 -m venv faceauth_env
source faceauth_env/bin/activate

# 3. Install system dependencies
brew install opencv ffmpeg

# 4. Install Python dependencies
pip install -r requirements.txt

# 5. Initialize configuration
python main.py config-init

# 6. Run system check
python main.py system-check
```

#### macOS Privacy Settings
1. **Camera permission**: System Preferences → Security & Privacy → Privacy → Camera
2. **Allow Terminal** (or your terminal app) access to camera
3. **Gatekeeper**: You may need to approve the Python executable

### Linux Setup (Ubuntu)

#### Prerequisites
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install prerequisites
sudo apt install -y python3 python3-pip python3-venv git
sudo apt install -y python3-dev build-essential
sudo apt install -y libopencv-dev ffmpeg
```

#### Installation Steps
```bash
# 1. Clone repository
git clone https://github.com/your-username/faceauth.git
cd faceauth

# 2. Create virtual environment
python3 -m venv faceauth_env
source faceauth_env/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Initialize configuration
python main.py config-init

# 5. Run system check
python main.py system-check

# 6. Set up permissions (if needed)
sudo usermod -a -G video $USER
```

## Configuration

### Initial Configuration

#### 1. Initialize Configuration
```bash
python main.py config-init
```

This creates the configuration file at:
- **Windows**: `%USERPROFILE%\.faceauth\config.ini`
- **macOS/Linux**: `~/.faceauth/config.ini`

#### 2. Customize Settings
```bash
# Set custom storage directory
python main.py config-set storage_dir "/path/to/secure/location"

# Set security level
python main.py config-set security_level high

# Configure camera settings
python main.py config-set camera_device 0  # Default camera
python main.py config-set camera_resolution "640x480"
```

#### 3. Security Configuration
```bash
# Set encryption method
python main.py config-set encryption_method aes256

# Configure key derivation
python main.py config-set kdf_method argon2

# Set audit logging
python main.py config-set audit_logging true
```

### Advanced Configuration

#### Custom Configuration File
You can create a custom configuration file:

```ini
[general]
storage_dir = ~/.faceauth/data
log_level = INFO
debug_mode = false

[security]
encryption_method = aes256
kdf_method = argon2
similarity_threshold = 0.6
max_login_attempts = 5

[camera]
device_id = 0
resolution = 640x480
fps = 30
timeout = 30

[privacy]
data_retention_days = 365
consent_required = true
audit_logging = true
```

## Verification

### System Check
```bash
# Run comprehensive system check
python main.py system-check
```

Expected output:
```
🔍 FaceAuth System Check
========================
✅ Python version: 3.11.0
✅ Required packages installed
✅ Camera access: Available
✅ Storage directory: Created
✅ Configuration: Valid
✅ Permissions: Correct
✅ Security: Configured

🎉 System ready for use!
```

### Test Camera Access
```bash
# Test camera functionality
python main.py test-camera
```

### Quick Demo
```bash
# Run the demo script
python demo.py
```

### Verify Installation
```bash
# Check installed packages
pip list | grep -E "(opencv|torch|facenet|cryptography)"

# Test core functionality
python -c "from faceauth import FaceEnrollmentManager; print('✅ Import successful')"
```

## Performance Optimization

### Hardware Acceleration

#### GPU Support (Optional)
If you have an NVIDIA GPU, you can enable GPU acceleration:

```bash
# Install CUDA-enabled PyTorch
pip uninstall torch torchvision
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

#### Apple Silicon (M1/M2) Optimization
```bash
# Install optimized packages for Apple Silicon
pip uninstall torch torchvision
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
```

### Memory Optimization
```bash
# Set memory-efficient mode
python main.py config-set memory_efficient true

# Reduce model precision (faster but slightly less accurate)
python main.py config-set precision_mode fast
```

## Security Hardening

### File Permissions
```bash
# Set secure permissions (Unix-like systems)
chmod 700 ~/.faceauth
chmod 600 ~/.faceauth/config.ini
```

### Security Audit
```bash
# Run security audit
python main.py security-audit

# Auto-fix common issues
python main.py security-audit --fix
```

### Backup Configuration
```bash
# Create secure backup
python main.py backup --encrypted secure_backup.zip

# Test restore process
python main.py restore secure_backup.zip --dry-run
```

## Environment Variables

You can use environment variables for configuration:

```bash
# Set via environment variables
export FACEAUTH_STORAGE_DIR="/secure/path"
export FACEAUTH_LOG_LEVEL="DEBUG"
export FACEAUTH_CAMERA_DEVICE="0"

# Windows (PowerShell)
$env:FACEAUTH_STORAGE_DIR="C:\secure\path"
```

## IDE Integration

### VS Code Setup
1. Install Python extension
2. Set Python interpreter to your virtual environment
3. Add `.vscode/settings.json`:

```json
{
    "python.defaultInterpreterPath": "./faceauth_env/bin/python",
    "python.formatting.provider": "black",
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true
}
```

### PyCharm Setup
1. Open project in PyCharm
2. Configure Python interpreter: Settings → Project → Python Interpreter
3. Select the virtual environment interpreter

## Docker Setup (Advanced)

### Build Docker Image
```bash
# Build the image
docker build -t faceauth .

# Run with camera access
docker run --device=/dev/video0 -v $HOME/.faceauth:/root/.faceauth faceauth
```

### Docker Compose
```yaml
version: '3.8'
services:
  faceauth:
    build: .
    devices:
      - /dev/video0:/dev/video0
    volumes:
      - ~/.faceauth:/root/.faceauth
    environment:
      - FACEAUTH_LOG_LEVEL=INFO
```

## Troubleshooting

### Common Issues

#### Camera Not Found
```bash
# List available cameras
python main.py list-cameras

# Test specific camera
python main.py test-camera --device 1
```

#### Permission Denied
```bash
# Linux: Add user to video group
sudo usermod -a -G video $USER

# Restart your session after this change
```

#### Import Errors
```bash
# Reinstall dependencies
pip install --force-reinstall -r requirements.txt

# Check for conflicts
pip check
```

#### Poor Performance
```bash
# Use CPU-only mode
python main.py config-set device cpu

# Reduce image resolution
python main.py config-set camera_resolution "320x240"
```

### Getting Help

1. **Check logs**: `tail -f ~/.faceauth/logs/faceauth.log`
2. **Run diagnostics**: `python main.py diagnose`
3. **Report issues**: [GitHub Issues](https://github.com/your-username/faceauth/issues)
4. **Community support**: [Discussions](https://github.com/your-username/faceauth/discussions)

## Next Steps

1. **Complete setup verification**: `python main.py system-check`
2. **Read the user guide**: [USER_GUIDE.md](USER_GUIDE.md)
3. **Try the demo**: `python demo.py`
4. **Enroll your first user**: `python main.py enroll-face your-username`
5. **Explore the CLI**: `python main.py --help`

## Updates and Maintenance

### Automatic Updates
```bash
# Check for updates
python main.py check-updates

# Update FaceAuth
git pull origin main
pip install -r requirements.txt --upgrade
```

### Manual Updates
```bash
# Backup before updating
python main.py backup update_backup.zip

# Update dependencies
pip install -r requirements.txt --upgrade

# Migrate configuration if needed
python main.py config-migrate
```

For more detailed usage instructions, see the [User Guide](USER_GUIDE.md).
