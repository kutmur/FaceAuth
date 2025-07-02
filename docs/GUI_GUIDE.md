# FaceAuth GUI Application

A user-friendly graphical interface for the FaceAuth face recognition and file encryption platform. This GUI provides an intuitive way to perform face enrollment, authentication, and secure file operations without using the command line.

## Features

### 🎯 Core Functionality
- **Face Enrollment**: Register your face with visual camera preview
- **Face Authentication**: Verify your identity with real-time feedback
- **File Encryption**: Secure files using your unique facial features
- **File Decryption**: Access encrypted files after authentication
- **Real-Time Preview**: Live camera feed with face detection visualization

### 🔒 Security Features
- **Local Processing**: All operations performed locally on your device
- **Biometric Encryption**: Files encrypted using facial feature-derived keys
- **No Cloud Storage**: Your biometric data never leaves your computer
- **Secure Storage**: Face templates stored with industry-standard encryption
- **Session-Based Access**: Authentication required for each session

### 🎨 User Experience
- **Intuitive Interface**: Clean, modern GUI built with Python Tkinter
- **Visual Feedback**: Clear status messages and progress indicators
- **Help System**: Built-in help and troubleshooting guidance
- **Cross-Platform**: Native look and feel on Windows, macOS, and Linux
- **Keyboard Shortcuts**: SPACE to capture, ESC to cancel during camera operations

## Installation

### Prerequisites
Ensure you have Python 3.8+ installed and the FaceAuth platform dependencies:

```bash
# Install required packages
pip install -r requirements.txt

# Additional GUI-specific dependencies
pip install pillow face-recognition dlib
```

### Quick Start
```bash
# Launch the GUI application
python faceauth_gui.py
```

## User Guide

### Getting Started

1. **Launch Application**
   ```bash
   python faceauth_gui.py
   ```

2. **First-Time Setup**
   - Click "📷 Enroll Face" to register your face
   - Position your face clearly in the camera preview
   - Press SPACE when ready to capture
   - Wait for confirmation message

3. **Authentication**
   - Click "🔐 Authenticate Face" 
   - Look at the camera and press SPACE to capture
   - Authentication status will update automatically

4. **File Operations**
   - Click "🔒 Encrypt File" to secure a document
   - Click "🔓 Decrypt File" to access encrypted content
   - File operations are only available after successful authentication

### Interface Overview

#### Main Window Components

**Status Panel**
- Current operation status and feedback messages
- Authentication status indicator (✅ Authenticated / ❌ Not Authenticated)
- Color-coded messages (green=success, red=error, blue=info, orange=warning)

**Face Authentication Panel**
- **Enroll Face Button**: Register your face with the system
- **Authenticate Face Button**: Verify your identity

**File Operations Panel**
- **Encrypt File Button**: Secure files (enabled after authentication)
- **Decrypt File Button**: Access encrypted files (enabled after authentication)

**Camera Preview**
- Live camera feed during enrollment and authentication
- Face detection rectangles and guidance text
- Keyboard controls: SPACE (capture), ESC (cancel)

**Control Panel**
- **Clear Enrollment**: Remove current face registration
- **Help**: Display detailed usage instructions
- **Exit**: Close the application safely

### Detailed Workflows

#### Face Enrollment Process

1. **Initiate Enrollment**
   - Click "📷 Enroll Face"
   - Camera will activate automatically

2. **Position Yourself**
   - Ensure good lighting conditions
   - Center your face in the camera view
   - Wait for green rectangle around detected face

3. **Capture Face**
   - Press SPACE when face is clearly visible
   - System will extract and save facial features
   - Confirmation message will appear

4. **Completion**
   - Face encoding saved securely to disk
   - Ready for authentication operations

#### Face Authentication Process

1. **Start Authentication**
   - Click "🔐 Authenticate Face"
   - Camera preview will open

2. **Face Verification**
   - Position face similar to enrollment
   - Press SPACE to capture current image
   - System compares with enrolled face template

3. **Results**
   - **Success**: Green checkmark, file operations enabled
   - **Failure**: Red X, authentication required to continue
   - Confidence percentage displayed for successful matches

#### File Encryption Workflow

1. **Prerequisites**
   - Must be authenticated (green checkmark visible)
   - Have a file ready to encrypt

2. **Select File**
   - Click "🔒 Encrypt File"
   - File dialog opens for selection
   - Choose any file type

3. **Encryption Process**
   - System generates encryption key from facial features
   - File is encrypted using AES encryption
   - Encrypted file saved to `data/encrypted/` directory

4. **Options**
   - Choose to delete original unencrypted file
   - Keep original for backup purposes

#### File Decryption Workflow

1. **Prerequisites**
   - Must be authenticated with the same face used for encryption
   - Have encrypted file available

2. **Select Encrypted File**
   - Click "🔓 Decrypt File"
   - Browse to encrypted file (usually in `data/encrypted/`)
   - Select `.encrypted` file

3. **Decryption Process**
   - System uses facial features to derive decryption key
   - File is decrypted and restored to original format
   - Choose location to save decrypted file

4. **Success**
   - Original file content restored
   - Save to desired location

## Troubleshooting

### Common Issues

#### Camera Problems
- **Camera won't open**: Check if other applications are using the camera
- **No image in preview**: Restart the application and try again
- **Poor image quality**: Improve lighting conditions

#### Face Detection Issues
- **No face detected**: Ensure face is clearly visible and well-lit
- **Multiple faces detected**: Only one person should be in camera view
- **Face too small/large**: Adjust distance from camera

#### Authentication Failures
- **Face doesn't match**: Re-enroll if lighting conditions have changed significantly
- **Low confidence**: Ensure similar positioning and lighting as during enrollment
- **Repeated failures**: Clear enrollment and start fresh

#### File Operation Errors
- **Encryption fails**: Check file permissions and available disk space
- **Decryption fails**: Ensure file was encrypted with the same enrolled face
- **Wrong key error**: Re-authenticate and try again

### Error Messages

| Error | Cause | Solution |
|-------|-------|----------|
| "Could not open camera" | Camera unavailable | Close other camera apps, restart |
| "No face detected" | Face not visible | Improve lighting, position face clearly |
| "Authentication failed" | Face doesn't match | Re-enroll or adjust positioning |
| "File not found" | Missing encrypted file | Check file path and permissions |
| "Decryption failed" | Wrong key/corrupted file | Verify face authentication |

### Performance Optimization

#### System Requirements
- **Minimum**: 4GB RAM, dual-core processor, basic webcam
- **Recommended**: 8GB RAM, quad-core processor, HD webcam
- **Optimal**: Good lighting, high-quality camera, fast SSD

#### Tips for Better Performance
- Close unnecessary applications before use
- Ensure stable lighting conditions
- Use external webcam for better quality
- Keep face templates backed up securely

## Security Considerations

### Data Protection
- **Local Storage**: All biometric data stored locally on your device
- **Encryption**: Face templates encrypted with industry-standard algorithms
- **No Transmission**: Biometric data never sent over networks
- **User Control**: Complete control over data deletion and management

### Best Practices
- **Regular Backups**: Backup encrypted files to secure locations
- **Environment Security**: Use application in private, secure environments
- **Access Control**: Limit physical access to the device
- **Regular Updates**: Keep application and dependencies updated

### Privacy Features
- **Consent Tracking**: Clear indication of data processing
- **Data Minimization**: Only necessary biometric features stored
- **Right to Delete**: Easy enrollment clearing and data removal
- **Transparency**: Open source code for security review

## Advanced Usage

### Configuration
The application uses the existing FaceAuth configuration system:

```bash
# View current settings
python main.py config-show

# Modify storage locations
python main.py config-set storage_dir /custom/path/
```

### Integration
The GUI can work alongside CLI operations:

```bash
# CLI enrollment
python main.py enroll-face username

# GUI authentication and file operations
python faceauth_gui.py
```

### Scripting
Automate GUI launch with system startup:

**Windows (PowerShell)**
```powershell
# Add to startup folder
$startup = "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup"
$shortcut = "$startup\FaceAuth.lnk"
# Create shortcut pointing to faceauth_gui.py
```

**Linux/macOS**
```bash
# Add to .bashrc or equivalent
alias faceauth-gui='cd /path/to/faceauth && python faceauth_gui.py'
```

## Technical Details

### Architecture
- **Frontend**: Python Tkinter for cross-platform GUI
- **Backend**: FaceAuth core libraries for processing
- **Camera**: OpenCV for video capture and processing
- **Recognition**: face_recognition library for biometric processing
- **Encryption**: Cryptography library for file security

### File Structure
```
data/
├── faces/
│   └── enrolled_face.json      # Encrypted face template
├── encrypted/
│   └── *.encrypted            # Encrypted files
└── logs/
    └── faceauth_gui.log       # Application logs
```

### Dependencies
- **Core**: OpenCV, face_recognition, cryptography
- **GUI**: tkinter, pillow
- **System**: numpy, json, base64

## Contributing

### Development Setup
```bash
# Clone repository
git clone [repository-url]
cd FaceAuth

# Install development dependencies
pip install -r requirements.txt
pip install -e .

# Run GUI in development mode
python faceauth_gui.py
```

### Code Structure
The GUI application is organized into logical sections:
- **Initialization**: Setup directories, load configuration
- **GUI Components**: Interface layout and styling
- **Camera Operations**: Video capture and face processing
- **File Operations**: Encryption and decryption workflows
- **Error Handling**: Comprehensive exception management

### Testing
```bash
# Run basic functionality tests
python -m pytest tests/

# Test GUI components
python tests/test_gui.py
```

## Support

### Getting Help
- **Built-in Help**: Click "Help" button in the application
- **Documentation**: See `docs/` directory for comprehensive guides
- **Troubleshooting**: Refer to `docs/TROUBLESHOOTING.md`
- **FAQ**: Check `docs/FAQ.md` for common questions

### Reporting Issues
1. Check existing documentation and troubleshooting guides
2. Reproduce the issue with clear steps
3. Include system information and error messages
4. Submit issue through project repository

### Community
- Follow contributing guidelines in `docs/CONTRIBUTING.md`
- Participate in discussions and feature requests
- Share feedback and improvement suggestions
- Help other users with questions and issues

## License

This GUI application is part of the FaceAuth platform and is licensed under the MIT License with additional privacy considerations. See `LICENSE` file for full details.

---

*FaceAuth GUI - Secure, Private, Local Face Authentication*
