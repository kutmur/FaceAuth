# 🚀 FaceAuth Quick Start Guide

*Get up and running with FaceAuth in under 5 minutes!*

---

## ⚡ Instant Setup

### 1. **Clone & Navigate**
```powershell
# If you have the project folder, navigate to it:
cd C:\Users\ereny\OneDrive\Desktop\project\FaceAuth

# Or if downloading fresh:
git clone <repository-url>
cd FaceAuth
```

### 2. **Automated Setup** (Recommended)
```powershell
# Windows (Run as Administrator)
.\scripts\setup_windows.ps1

# Or manual Python setup:
python -m pip install -r requirements.txt
```

### 3. **Launch GUI Application**
```powershell
# Full-featured interface
python faceauth_gui.py

# Or simplified interface
python simple_faceauth_gui.py
```

**🎉 You're ready to go!**

---

## 🎯 First Time Use

### **Step 1: Enroll Your Face**
1. Click **"Enroll Face"** in the GUI
2. Look at your camera and click **"Capture"** when face is detected (green box)
3. Wait for **"Enrollment Successful!"** message
4. Your biometric template is now saved locally and encrypted

### **Step 2: Test Authentication**
1. Click **"Authenticate"** 
2. Look at camera until face is detected
3. See **"Authentication Successful!"** with confidence score
4. You're now ready to encrypt files!

### **Step 3: Encrypt Your First File**
1. Click **"Browse Files"** and select any file
2. Click **"Encrypt File"**
3. Authenticate with your face when prompted
4. File is encrypted with your biometric key!
5. Original file is securely deleted

### **Step 4: Decrypt the File**
1. Select the encrypted file (ends with `.encrypted`)
2. Click **"Decrypt File"**
3. Authenticate with your face
4. File is decrypted and restored!

---

## 🚀 Command Line Usage

### **Basic Commands**
```powershell
# Show help
python main.py --help

# Enroll a new face
python main.py enroll

# Authenticate
python main.py authenticate

# Encrypt a file
python main.py encrypt --file "path\to\file.txt"

# Decrypt a file  
python main.py decrypt --file "path\to\file.txt.encrypted"

# List enrolled users
python main.py list-users
```

### **Advanced Options**
```powershell
# Set custom confidence threshold
python main.py authenticate --threshold 0.85

# Verbose output for debugging
python main.py encrypt --file "document.pdf" --verbose

# Use specific config file
python main.py --config custom_config.json encrypt
```

---

## 🎛️ GUI Interface Overview

### **Main Window**
```
┌─────────────────────────────────────────┐
│             FaceAuth v1.0               │
├─────────────────────────────────────────┤
│  [Enroll Face]    [Authenticate]        │
│                                         │
│  ┌─────────────────────────────────────┐ │
│  │        Camera Preview               │ │
│  │     (Live face detection)           │ │
│  └─────────────────────────────────────┘ │
│                                         │
│  [Browse Files]   [Encrypt] [Decrypt]   │
│                                         │
│  Status: Ready                          │
│  ┌─────────────────────────────────────┐ │
│  │ Selected: document.pdf              │ │
│  │ Size: 1.2 MB                       │ │
│  └─────────────────────────────────────┘ │
│                                         │
│  [Settings]  [Help]  [About]            │
└─────────────────────────────────────────┘
```

### **Key Features**
- **🔴 Real-time Camera**: Live preview with face detection overlay
- **🎯 One-Click Operations**: Simple enrollment and authentication
- **📁 Drag & Drop**: Easy file selection for encryption
- **📊 Status Updates**: Real-time progress and feedback
- **⚙️ Settings**: Configurable security and performance options

---

## 🔧 Troubleshooting

### **Camera Issues**
```powershell
# Test camera access
python -c "import cv2; print('Camera OK' if cv2.VideoCapture(0).read()[0] else 'Camera Failed')"
```
**Solution**: Check camera permissions, restart application, try different camera index.

### **Permission Errors**
```powershell
# Run as administrator or check file permissions
python main.py --verbose
```
**Solution**: Run PowerShell as administrator, check antivirus settings.

### **Module Not Found**
```powershell
# Reinstall dependencies
python -m pip install -r requirements.txt --upgrade
```
**Solution**: Ensure Python 3.8+, run in virtual environment if needed.

### **Face Not Detected**
- **Lighting**: Ensure good, even lighting on your face
- **Distance**: Position 18-24 inches from camera
- **Angle**: Look directly at camera, avoid extreme angles
- **Quality**: Use decent quality webcam (720p minimum)

---

## 📋 System Requirements

### **Minimum**
- **OS**: Windows 10, macOS 10.14, Ubuntu 18.04
- **Python**: 3.8+
- **RAM**: 4GB
- **Storage**: 1GB free space
- **Camera**: Any USB webcam

### **Recommended**
- **OS**: Windows 11, macOS 12+, Ubuntu 20.04+
- **Python**: 3.10+
- **RAM**: 8GB
- **Storage**: 5GB free space  
- **Camera**: HD webcam (1080p)
- **CPU**: Multi-core processor for faster recognition

---

## 🔐 Security Quick Facts

### **Privacy-First Design**
- ✅ **100% Local Processing** - No internet required
- ✅ **No Data Transmission** - Everything stays on your device
- ✅ **Encrypted Storage** - All biometric data encrypted
- ✅ **Military-Grade Encryption** - AES-256 for file protection
- ✅ **Secure Key Derivation** - Keys derived from your biometric data

### **Authentication Process**
1. **Face Capture** → Camera captures your face
2. **Feature Extraction** → Mathematical representation created
3. **Template Matching** → Compared with stored template
4. **Key Derivation** → Biometric features generate encryption key
5. **File Operations** → Secure encryption/decryption performed

---

## 📚 Quick Reference

### **File Extensions**
- `.encrypted` - Files encrypted by FaceAuth
- `.faceauth` - Biometric template files
- `.log` - Application log files

### **Default Locations**
- **Templates**: `./data/templates/`
- **Logs**: `./logs/`
- **Config**: `./config/`
- **Encrypted Files**: Same location as original with `.encrypted` extension

### **Keyboard Shortcuts** (GUI)
- **Ctrl+E**: Enroll new face
- **Ctrl+A**: Authenticate
- **Ctrl+O**: Open file for encryption
- **F1**: Help documentation
- **Escape**: Cancel current operation

---

## 💡 Pro Tips

### **Best Practices**
1. **Good Lighting**: Use consistent, well-lit environment
2. **Multiple Angles**: Enroll from different angles for better recognition
3. **Regular Updates**: Re-enroll periodically if appearance changes significantly
4. **Backup Templates**: Keep secure backups of your biometric templates
5. **Test First**: Always test authentication before encrypting important files

### **Performance Optimization**
1. **Close Other Apps**: Free up system resources during use
2. **USB 3.0**: Use high-speed USB ports for external cameras
3. **SSD Storage**: Faster file encryption on SSD drives
4. **Regular Cleanup**: Clear logs and temporary files periodically

### **Security Tips**
1. **Physical Security**: Secure your device with encrypted face templates
2. **Regular Audits**: Monitor access logs for unusual activity
3. **Update Software**: Keep dependencies updated for security patches
4. **Backup Strategy**: Secure backup of important encrypted files

---

## 🆘 Need Help?

### **Documentation**
- 📖 **Full Setup Guide**: `docs/SETUP.md`
- 🔧 **Troubleshooting**: `docs/TROUBLESHOOTING.md`
- ❓ **FAQ**: `docs/FAQ.md`
- 🔐 **Security Info**: `docs/SECURITY.md`

### **Support**
- 📧 **Issues**: Create GitHub issue with error details
- 💬 **Discussions**: Community support and feature requests
- 📝 **Logs**: Check `./logs/` for detailed error information
- 🔍 **Verbose Mode**: Run with `--verbose` for debugging

---

**🎉 Congratulations! You now have a fully functional, privacy-first face authentication system running on your local machine. Start with the GUI interface, then explore the command-line options for automation. Your biometric data never leaves your device!**

*For advanced features and enterprise deployment, see the full documentation suite in the `docs/` directory.*
