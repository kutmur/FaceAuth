# 🚀 Quick Start

1.  **Clone the repository:**
    ```bash
    git clone <your-repo-url>
    cd FaceAuth
    ```
2.  **Create a virtual environment (Recommended):**
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # Linux/Mac
    # or venv\Scripts\activate  # Windows
    ```
3.  **Install Basic Dependencies First:**
    ```bash
    # Install minimal dependencies to bootstrap the setup command
    pip install opencv-python>=4.8.0 click
    ```
    
4.  **🔧 Run the Automated Setup and Repair Command**
    
    ### ⚠️ THIS IS THE MOST IMPORTANT STEP ⚠️
    
    This command will clean your environment and install all necessary dependencies correctly.
    It performs aggressive cleanup of conflicting packages (especially OpenCV variants) and
    ensures a fresh, working installation.

    ```bash
    python main.py setup
    ```
    
4.  **🔧 Run the Automated Setup and Repair Command**
    
    ### ⚠️ THIS IS THE MOST IMPORTANT STEP ⚠️
    
    This command will clean your environment and install all necessary dependencies correctly.
    It performs aggressive cleanup of conflicting packages (especially OpenCV variants) and
    ensures a fresh, working installation.

    ```bash
    python main.py setup
    ```
    
    **💡 If you ever encounter ANY error, run this command again to fix it.**
    
    The setup command is your one-stop solution for:
    - ✅ Cleaning conflicting OpenCV installations
    - ✅ Upgrading pip to latest version  
    - ✅ Installing all dependencies correctly
    - ✅ Fixing environment issues automatically

5.  **Enroll your face:**
    Once setup is complete, you can enroll your face.
    ```bash
    python main.py enroll
    ```

# 🔐 FaceAuth

```
███████╗ █████╗  ██- 🎯 **Face Enrollment**: Register your face with real-time feedback and quality validation
- 🔓 **Face Verification**: Instant identity verification via webcam
- 📁 **File Encryption**: Encrypt any file using your face as the key
- 🔓 **File Decryption**: Decrypt files with face authentication
- 💻 **CLI Interface**: Simple, powerful command-line tools
- 🖥️ **GUI Interface**: User-friendly graphical interface (NEW!)
- 🔐 **Secure Storage**: Military-grade AES-256-GCM encryption
- 🌐 **Offline First**: Zero network dependencies
- 🔧 **Multiple AI Models**: Facenet, ArcFace, VGG-Face support████╗     █████╗ ██╗   ██╗████████╗██╗  ██╗
██╔════╝██╔══██╗██╔════╝██╔════╝    ██╔══██╗██║   ██║╚══██╔══╝██║  ██║
█████╗  ███████║██║     █████╗      ███████║██║   ██║   ██║   ███████║
██╔══╝  ██╔══██║██║     ██╔══╝      ██╔══██║██║   ██║   ██║   ██╔══██║
██║     ██║  ██║╚██████╗███████╗    ██║  ██║╚██████╔╝   ██║   ██║  ██║
╚═╝     ╚═╝  ╚═╝ ╚═════╝╚══════╝    ╚═╝  ╚═╝ ╚═════╝    ╚═╝   ╚═╝  ╚═╝
```

![Python version](https://img.shields.io/badge/python-3.8%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Security](https://img.shields.io/badge/security-local%20only-brightgreen)
![Status](https://img.shields.io/badge/status-MVP%20ready-orange)

**Your Face is Your Key. Your Data Stays Yours.**

<!-- DEMO GIF WILL GO HERE -->
*Demo showing complete workflow: face enrollment → file encryption with face authentication → secure decryption*

---

## 🚀 Overview

**FaceAuth** is a privacy-first face authentication system that turns your face into a secure key for protecting your files. Unlike cloud-based solutions, FaceAuth runs entirely on your local machine, ensuring your biometric data never leaves your computer.

**Core Principles:**
- 🔒 **Privacy-First**: No cloud, no tracking, no data sharing
- 🧠 **AI-Powered**: Advanced face recognition with multiple models
- 🛡️ **Military-Grade Security**: AES-256 encryption with PBKDF2
- ⚡ **Lightning Fast**: Sub-2-second authentication

---

## ✨ Features

- 🎯 **Face Enrollment**: Register your face with real-time feedback and quality validation
- 🔓 **Face Verification**: Instant identity verification via webcam
- 🔓 **File Encryption**: Encrypt any file using your face as the key
- 🔓 **File Decryption**: Decrypt files with face authentication
- 💻 **CLI Interface**: Simple, powerful command-line tools
- 🔐 **Secure Storage**: Military-grade AES-256-GCM encryption
- 🌐 **Offline First**: Zero network dependencies
- 🔧 **Multiple AI Models**: Facenet, ArcFace, VGG-Face support

---

## ⚙️ How It Works

```
[User Enrolls Face] 
        ↓
[AI Creates Face Embedding] 
        ↓
[Embedding Encrypted with Password] 
        ↓
[Stored Locally as .dat file]
        ↓
[User Wants to Encrypt File] 
        ↓
[Face Verification via Webcam] 
        ↓
[Password Entered] 
        ↓
[File Encrypted with Random Key] 
        ↓
[File Key Encrypted with Face Auth] 
        ↓
[Original File → Secure .faceauth File]
```

**The Magic:** Your face is converted to a mathematical "embedding" (not an image!) that can't be reverse-engineered back to your face. This embedding, encrypted with your password, becomes the key to unlock your files.

---

## 🛠️ Installation

### Prerequisites
- **Python 3.8+** 
- **Webcam/Camera** (built-in or USB)
- **Good lighting** for face capture

### Quick Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/FaceAuth.git
cd FaceAuth

# Install dependencies
pip install -r requirements.txt

# Verify installation
python main.py --help
```

### Alternative Setup
```bash
# Using the setup script
python setup.py
```

---

## ⚡️ Usage

FaceAuth offers both command-line and graphical interfaces:

### 🖥️ GUI Interface (Recommended for Beginners)

Launch the user-friendly graphical interface:

```bash
python main.py --gui
```

The GUI provides:
- 🎯 **Intuitive buttons** for each operation
- 📁 **File dialogs** for easy file selection  
- ⏱️ **Real-time status** updates
- 🚨 **Clear error** messages
- 📖 **Built-in help** and tooltips

**GUI Workflow:**
1. Launch GUI with `python main.py --gui`
2. Click "Enroll Face" to register your biometrics
3. Click "Encrypt File" to secure files with face authentication
4. Click "Decrypt File" to access your secured files
5. Monitor the status area for real-time feedback

### 💻 CLI Interface (Advanced Users)

FaceAuth uses a simple command-line interface. Here are the core commands:

### 🎯 **Enroll Your Face**
Register your face for the first time:

```bash
# Basic enrollment
python main.py enroll-face

# With custom user ID
python main.py enroll-face --user-id john_doe

# Using different AI model
python main.py enroll-face --user-id alice --model ArcFace
```

**What happens:** Opens webcam → Detects your face → Guides positioning → Captures on SPACE → Encrypts & saves locally

### 🔓 **Verify Your Identity**
Test face authentication:

```bash
# Verify your enrolled face
python main.py verify-face

# Verify specific user
python main.py verify-face --user-id john_doe
```

**What happens:** Opens webcam → Detects face → Compares with stored data → Shows success/failure

### 🔐 **Encrypt Files**
Protect files with face authentication:

```bash
# Encrypt a file
python main.py encrypt-file myfile.txt

# Encrypt with specific output name
python main.py encrypt-file document.pdf --output secure_doc.faceauth
```

**What happens:** Face verification → Password prompt → File encrypted → Creates .faceauth file

### 🔓 **Decrypt Files**
Unlock your protected files:

```bash
# Decrypt a file
python main.py decrypt-file myfile.txt.faceauth

# Decrypt to specific location
python main.py decrypt-file secure_doc.faceauth --output recovered_document.pdf
```

**What happens:** Face verification → Password prompt → File decrypted → Original file restored

### ℹ️ **System Information**
```bash
# Check system status
python main.py info

# View help
python main.py --help
```
---

## 🔒 Security & Privacy

### 🛡️ **Our Privacy Promise**

**Your biometric data NEVER leaves your computer. Period.**

FaceAuth is built on an unwavering commitment to privacy. We believe your face is your most personal identifier and should remain under your complete control.

### 📊 **What Data is Stored?**

FaceAuth creates only minimal, encrypted data on your machine:

1. **Face Embedding File** (`[user_hash]_face.dat`)
   - Mathematical representation of facial features (NOT an image)
   - Encrypted with AES-256-GCM
   - Typically 2-8 KB in size
   - Stored in `face_data/` directory

2. **Encrypted Files** (`filename.faceauth`)
   - Your original files protected with face authentication
   - Created only when you choose to encrypt files
   - Stored wherever you specify

### 🔐 **How is Your Data Secured?**

**Military-Grade Encryption:**
- **AES-256-GCM**: Same encryption used by governments and banks
- **PBKDF2**: 100,000 iterations to prevent password attacks
- **Random Salts**: Unique for each user and file
- **Authentication Tags**: Detect tampering attempts

**Face Embedding Security:**
- Face embeddings are mathematical vectors, not images
- Cannot be converted back to photos
- Would require exact AI model + training data to reverse
- Even if decrypted, only shows numbers like `[0.23, -0.85, 1.42...]`

### ❌ **What We NEVER Do**

- ❌ Store raw images of your face
- ❌ Store your passwords
- ❌ Send data over the internet
- ❌ Connect to cloud services
- ❌ Share data with third parties
- ❌ Log your biometric information
- ❌ Install system-wide components

### 📍 **Where is Your Data?**

All data stays in your FaceAuth directory:

```
FaceAuth/
├── face_data/                    # Your encrypted face embeddings
│   └── [hash]_face.dat          # Example: a1b2c3d4_face.dat
├── yourfile.txt.faceauth         # Your encrypted files (when created)
└── anotherdoc.pdf.faceauth       # More encrypted files
```

**Complete transparency:** No hidden files, no system modifications, no registry entries.

### 🔒 **Threat Model**

**✅ Protected Against:**
- Computer theft or unauthorized access
- Malware scanning your files
- Network interception (nothing to intercept!)
- Government data requests (no data to request)
- Corporate surveillance
- Cloud provider breaches

**⚠️ Not Protected Against:**
- Someone watching you enter your password
- Sophisticated state-level attacks on your device
- Physical access while you're logged in

### 🏛️ **Privacy Compliance**

Designed to comply with:
- **GDPR**: Local processing with user consent
- **CCPA**: No data sale/sharing (impossible!)
- **BIPA**: User-controlled biometric data
- **PIPEDA**: Privacy by design

---

## 🧪 Testing

FaceAuth includes a comprehensive test suite to ensure reliability:

```bash
# Run all tests
pytest

# Run specific test module
pytest tests/test_crypto.py

# Run with verbose output
pytest -v

# Run with coverage (if pytest-cov installed)
pytest --cov
```

The test suite includes:
- 75+ unit tests across all modules
- Encryption/decryption validation
- Error handling scenarios
- Mock-based testing (no webcam required)
- CI/CD ready

---

## 🎯 Roadmap

### ✅ **Current (MVP)**
- Face enrollment with real-time feedback
- Secure local storage with AES-256 encryption
- Face verification system
- File encryption/decryption
- CLI interface

### 🔄 **Coming Soon**
- GUI interface for non-technical users
- Batch file operations
- Advanced authentication options
- Mobile companion app
- Enterprise deployment tools

### 🚀 **Future Vision**
- Browser integration
- API for developers
- Advanced biometric features
- Multi-factor authentication
- Secure file sharing

---

## 🤝 Contributing

We welcome contributions! Here's how to get started:

```bash
# Clone and setup development environment
git clone https://github.com/yourusername/FaceAuth.git
cd FaceAuth

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Run tests
pytest

# Make your changes and submit a PR!
```

### 🐛 **Bug Reports**
Found a bug? Please open an issue with:
- Your OS and Python version
- Steps to reproduce
- Expected vs actual behavior
- Any error messages

### 💡 **Feature Requests**
Have an idea? We'd love to hear it! Please include:
- Use case description
- Proposed implementation
- Security considerations

---

## ❓ FAQ

**Q: Can someone steal my face data and impersonate me?**
A: No. Face embeddings are mathematical abstractions that cannot be converted back to images or used with other systems.

**Q: What happens if I forget my password?**
A: Unfortunately, your encrypted data cannot be recovered. This is by design - even we cannot access your data without your password.

**Q: Can I use this for business/commercial purposes?**
A: Yes! FaceAuth is MIT licensed. However, consider implementing additional security measures for critical business applications.

**Q: Does this work in low light?**
A: Face detection works best in good lighting. Consider adding a desk lamp or ring light for consistent results.

**Q: Can multiple people use the same computer?**
A: Yes! Each user gets their own encrypted face data. Use different user IDs during enrollment.

**Q: Is this secure enough for sensitive documents?**
A: FaceAuth uses industry-standard encryption, but we recommend using it as part of a multi-layered security approach for highly sensitive data.

---

## 🛠️ Troubleshooting

### Common Issues

**Camera not detected:**
```bash
# Linux: Install camera utilities
sudo apt-get install v4l-utils

# Check available cameras
ls /dev/video*
```

**Import errors:**
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

**Face detection problems:**
- Ensure good, even lighting
- Remove glasses/masks if possible
- Position face in center of camera
- Only one person should be visible

### System Requirements

- **OS**: Linux, Windows, macOS
- **Python**: 3.8 or higher
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 100MB for software + minimal for face data
- **Camera**: Any USB webcam or built-in camera

---

## 📄 License

Distributed under the MIT License. See `LICENSE` file for more information.

```
MIT License

Copyright (c) 2025 FaceAuth Project

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## 🙏 Acknowledgments

- **[DeepFace](https://github.com/serengil/deepface)**: Excellent face recognition framework
- **[OpenCV](https://opencv.org/)**: Computer vision library
- **[Cryptography](https://cryptography.io/)**: Python cryptographic toolkit
- **[Click](https://click.palletsprojects.com/)**: Command line interface framework

Built with ❤️ for privacy and security.

---

## 🔗 Links

- **Documentation**: [Read the full docs](TESTING.md)
- **Issues**: [Report bugs or request features](https://github.com/yourusername/FaceAuth/issues)
- **Discussions**: [Join the community](https://github.com/yourusername/FaceAuth/discussions)
- **Security**: [Report security issues](mailto:security@faceauth.dev)

---

**⭐ If FaceAuth helps you secure your data, please star this repository!**

**Made with ❤️ by developers who believe in privacy.**

### How Is Your Data Secured?

**🔬 Face Embedding Process:**
Your face is never stored as a picture. Instead, FaceAuth uses advanced AI to convert your face into a "face embedding"—a mathematical code made of numbers that represents the unique patterns of your facial features. Think of it like a numerical fingerprint that can't be turned back into a photo.

**🔐 Military-Grade Encryption:**
- Your face embedding is encrypted using AES-256-GCM (the same encryption used by governments and banks)
- Your password is your master key—we use it to encrypt your face data and protect your files
- Each file gets its own unique encryption key for maximum security
- We use PBKDF2 with 100,000 iterations to make password attacks extremely difficult

**🔑 Zero Password Storage:**
We never store your password anywhere. It exists only in your computer's memory when you're using it, then it's gone. This means even if someone gets your encrypted files, they can't access them without your password.

### What Data Is NEVER Stored or Sent?

We want to be crystal clear about what FaceAuth will never do:

- ❌ **Never store raw images of your face** - Only mathematical embeddings
- ❌ **Never store your password** - Only derived encryption keys
- ❌ **Never send data over the internet** - Zero network activity
- ❌ **Never connect to the cloud** - Everything runs locally
- ❌ **Never share data with third parties** - No external services
- ❌ **Never log your biometric data** - Privacy by design

### Where Is Your Data Stored?

All FaceAuth data is stored right on your computer in the directory where you run the application:

```
your-faceauth-folder/
├── face_data/                    # Encrypted face embeddings
│   └── [hash]_face.dat          # Your encrypted face data
├── document.pdf.faceauth         # Your encrypted files (optional)
└── sensitive.txt.faceauth        # Created only when you encrypt files
```

**Key Points:**
- No hidden files or system-wide storage
- No registry entries or system modifications
- You can backup, move, or delete everything yourself
- Complete transparency in data location

### How Secure Is This Really?

**🛡️ Cryptographic Strength:**
- **AES-256-GCM**: Used by the U.S. government for TOP SECRET information
- **PBKDF2**: Industry standard for password security (100,000 iterations)
- **Authenticated Encryption**: Detects if anyone tampers with your files

**🔍 Face Reconstruction Prevention:**
Face embeddings are mathematical abstractions that cannot be reversed into images. Even if an attacker:
- Decrypts your face data
- Has advanced technical skills
- Uses powerful computers

They would only see a list of numbers like `[0.23, -0.85, 1.42, ...]` that represent abstract facial features—not your actual face.

**🔒 Defense in Depth:**
1. **Layer 1**: Face embedding (not an image)
2. **Layer 2**: AES-256 encryption
3. **Layer 3**: Password-based key derivation
4. **Layer 4**: No network exposure
5. **Layer 5**: Local-only processing

### Privacy Compliance

FaceAuth is designed to comply with privacy regulations:

- **GDPR**: All processing is local with explicit user consent
- **CCPA**: No data sale or sharing (impossible—it never leaves your device)
- **BIPA**: No biometric data storage without user control
- **PIPEDA**: Privacy by design principles throughout

### Third-Party Dependencies

FaceAuth uses these trusted, security-focused libraries:
- **OpenCV**: Open-source computer vision (local processing only)
- **DeepFace**: Face recognition framework (runs locally)
- **Cryptography**: Python's gold-standard crypto library
- **NumPy**: Mathematical operations

All dependencies run locally—none make network connections for FaceAuth operations.

### Threat Model: What We Protect Against

✅ **Protected Scenarios:**
- Someone steals your computer
- Malware scans your files
- Hackers breach your network
- Government data requests
- Corporate surveillance
- Cloud provider breaches
- Internet service provider monitoring

⚠️ **Not Protected Against:**
- Someone watching you enter your password
- Physical access while you're logged in
- Keyloggers capturing your password
- Sophisticated state-level attacks on your device

### Your Privacy Rights

With FaceAuth, you maintain complete control:

- **Right to Access**: View all your data anytime
- **Right to Delete**: Remove data permanently
- **Right to Export**: Copy your encrypted data
- **Right to Modify**: Change passwords or settings
- **Right to Audit**: Inspect all source code

### Questions About Security?

We believe security through transparency. Our code is open source, our methods are documented, and our approach is auditable. If you have security questions or concerns:

1. Review our source code on GitHub
2. Read our security documentation
3. Run your own security audit
4. Contact us with specific concerns

**Remember**: The most secure system is one you understand and control. That's why FaceAuth puts you in charge of your own security.
