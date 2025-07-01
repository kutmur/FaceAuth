# FaceAuth 🔐

**Local Face Authentication for File Security**

A modern, privacy-first face authentication platform that enables secure local face recognition without any cloud dependencies. Built with Python, OpenCV, and advanced deep learning models.

## 🚀 Overview

FaceAuth provides a complete solution for face-based authentication that runs entirely on your local machine. No data is ever sent to the cloud, ensuring your biometric information remains private and secure.

**Key Features:**
- 🎯 **Local Processing**: Everything runs on your machine
- 🔒 **Privacy-First**: No cloud dependencies or data transmission
- 🧠 **Modern Deep Learning**: Uses state-of-the-art face recognition models
- ⚡ **Fast Authentication**: Real-time face verification
- 🔐 **Secure Storage**: Military-grade encryption for face data
- 🖥️ **CLI Interface**: Simple command-line tools
- 📱 **Real-time Feedback**: Live webcam preview with guidance

## ⚡ MVP Features

- [x] **Face Registration**: Enroll users via webcam with real-time feedback
- [x] **Secure Storage**: AES-256 encrypted face embeddings with PBKDF2 key derivation
- [x] **Robust Detection**: Handle multiple faces, no face, and poor lighting conditions
- [x] **CLI Interface**: Easy-to-use command-line tools
- [ ] **Face Verification**: Real-time identity verification (coming soon)
- [ ] **File Encryption**: Encrypt/decrypt files with face authentication (coming soon)

## 🛠️ Installation

### Prerequisites
- Python 3.8 or higher
- Webcam/camera device
- Good lighting conditions for face capture

### Quick Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/FaceAuth.git
   cd FaceAuth
   ```

2. **Run the setup script:**
   ```bash
   python setup.py
   ```

   Or install manually:
   ```bash
   pip install -r requirements.txt
   ```

3. **Verify installation:**
   ```bash
   python main.py info
   ```

## 📚 Usage

### Face Enrollment

Enroll your face into the system:

```bash
# Basic enrollment
python main.py enroll-face

# With specific user ID
python main.py enroll-face --user-id john_doe

# Using different AI model
python main.py enroll-face --user-id alice --model ArcFace
```

**Enrollment Process:**
1. **Camera Setup**: The system accesses your webcam
2. **Face Detection**: Real-time feedback guides you to position your face correctly
3. **Quality Check**: Ensures single face with good lighting
4. **Capture**: Takes a high-quality image when you press SPACE
5. **AI Processing**: Generates face embedding using deep learning
6. **Secure Storage**: Encrypts and saves your face data locally

**During enrollment, you'll see:**
- ✅ **Green rectangle**: Face detected and positioned correctly
- ❌ **Red rectangle**: Issues detected (multiple faces, poor positioning, etc.)
- **Crosshair**: Center point for optimal face positioning
- **Instructions**: Real-time guidance and controls

### Available Commands

```bash
# Enroll a new user
python main.py enroll-face [--user-id USER] [--model MODEL]

# Verify identity (coming soon)
python main.py verify-face [--user-id USER]

# Encrypt file with face auth (coming soon)
python main.py encrypt-file --file myfile.txt

# Decrypt file with face auth (coming soon)
python main.py decrypt-file --file myfile.txt.encrypted

# System information
python main.py info

# Setup dependencies
python main.py setup

# Help
python main.py --help
```

### Supported AI Models

- **Facenet** (default): Fast and accurate, good for most users
- **ArcFace**: High accuracy, slightly slower
- **VGG-Face**: Classical approach, reliable
- **Facenet512**: Higher dimensional embeddings for maximum accuracy

## 🔒 Security Architecture

### Encryption Details

FaceAuth uses military-grade security practices:

1. **AES-256-GCM Encryption**: Industry standard with authentication
2. **PBKDF2 Key Derivation**: 100,000 iterations with SHA-256
3. **Random Salt**: Unique salt for each user
4. **No Password Storage**: Passwords are never saved
5. **Secure Random**: Cryptographically secure random generation

### Why Face Reconstruction is Impossible

Face embeddings are mathematical vectors that represent abstract facial features:

- **Not Images**: Embeddings are numerical arrays, not visual data
- **One-Way Process**: Cannot be converted back to images
- **Abstract Features**: Represent mathematical relationships, not physical appearance
- **Model-Specific**: Would require the exact same neural network architecture
- **Missing Data**: Original training data would be needed for any reconstruction

Even if someone decrypts your face data, they only get a list of numbers that represent mathematical relationships between facial features—not your actual face.

### File Structure

```
FaceAuth/
├── face_data/           # Encrypted face embeddings (created after enrollment)
├── main.py             # CLI interface
├── enrollment.py       # Face enrollment module
├── crypto.py          # Cryptographic security functions
├── setup.py           # Installation script
├── requirements.txt   # Python dependencies
└── README.md         # This file
```

## 🎯 Technical Implementation

### Face Enrollment Module (`enrollment.py`)

- **Real-time Detection**: Uses DeepFace with multiple backend options
- **Quality Assurance**: Checks for single face, good lighting, proper positioning
- **User Guidance**: Live feedback with visual indicators
- **Error Handling**: Robust handling of edge cases
- **Multiple Models**: Support for Facenet, ArcFace, VGG-Face

### Security Module (`crypto.py`)

- **AES-256-GCM**: Authenticated encryption mode
- **PBKDF2**: 100,000 iterations for key derivation
- **Salt Generation**: Cryptographically secure random salts
- **Data Integrity**: Authentication tags prevent tampering
- **Secure Storage**: Binary format with embedded metadata

### CLI Interface (`main.py`)

- **Click Framework**: Professional command-line interface
- **Error Handling**: Comprehensive error messages and recovery
- **User Experience**: Clear feedback and progress indicators
- **Modular Design**: Easy to extend with new features

## 🚨 Troubleshooting

### Common Issues

**Camera Access Problems:**
```bash
# Linux: Install v4l-utils
sudo apt-get install v4l-utils

# Check camera devices
ls /dev/video*
```

**Import Errors:**
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Or use setup script
python setup.py
```

**Face Detection Issues:**
- Ensure good lighting
- Remove glasses/masks if possible
- Position face in center of camera
- Make sure only one person is visible

### System Requirements

- **OS**: Linux, Windows, macOS
- **Python**: 3.8+
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 100MB for software, minimal for face data
- **Camera**: Any USB webcam or built-in camera

## 🔮 Roadmap

### Phase 1: Core Features (Current)
- [x] Face enrollment with real-time feedback
- [x] Secure local storage with encryption
- [x] CLI interface
- [x] Multiple AI model support

### Phase 2: Authentication (Next)
- [ ] Real-time face verification
- [ ] Authentication confidence scoring
- [ ] Multi-user support
- [ ] Authentication logging

### Phase 3: File Security (Future)
- [ ] File encryption with face authentication
- [ ] File decryption with face verification
- [ ] Secure file sharing
- [ ] Backup and recovery tools

### Phase 4: Advanced Features (Future)
- [ ] GUI interface
- [ ] Mobile app integration
- [ ] Advanced security features
- [ ] Enterprise deployment tools

## 🤝 Contributing

We welcome contributions! Please see our contributing guidelines for details.

### Development Setup

```bash
# Clone repository
git clone https://github.com/yourusername/FaceAuth.git
cd FaceAuth

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Run tests
python -m pytest tests/
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

FaceAuth is designed for personal and educational use. While we use industry-standard security practices, biometric authentication should be used as part of a multi-factor authentication strategy for critical applications.

## 🙏 Acknowledgments

- **DeepFace**: Excellent face recognition framework
- **OpenCV**: Computer vision library
- **Cryptography**: Security primitives
- **Click**: CLI framework

---

**Made with ❤️ for privacy and security**

## 🛡️ Security & Privacy

### Our Core Philosophy: Your Data, Your Machine

**FaceAuth is built on an unwavering commitment to privacy.** Your biometric data never leaves your computer. Period.

We believe your face is your most personal identifier, and it should remain under your complete control. That's why FaceAuth operates entirely offline, with zero cloud dependencies, no network calls, and no third-party data sharing. Your privacy isn't a feature—it's our foundation.

### What Data Is Stored?

FaceAuth creates only two types of data files on your computer:

1. **Face Data File** (`[user_hash]_face.dat`)
   - Contains your encrypted face embedding (mathematical representation)
   - Stored in the `face_data/` directory where you run FaceAuth
   - File size: Typically 2-8 KB (tiny!)

2. **Encrypted Files** (`<filename>.faceauth`)
   - Your original files encrypted with face authentication
   - Created only when you choose to encrypt files
   - Stored wherever you specify (same directory by default)

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

---