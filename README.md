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