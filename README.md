# FaceAuth - Local Face Authentication System

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Security](https://img.shields.io/badge/Security-Local%20Only-brightgreen)](README.md#security)

A **privacy-first** face authentication platform that keeps all face data local. No cloud dependencies, no third-party services, no data sharing.

## 🔒 Privacy & Security First

- **100% Local**: All face data stays on your device
- **Encrypted Storage**: Face embeddings are encrypted with AES-256
- **No Reconstruction**: Stored data cannot recreate original images  
- **Secure Deletion**: Proper secure file deletion when removing users
- **No Network**: Zero network requests or cloud dependencies

## ✨ Features

- **Modern Deep Learning**: Uses FaceNet with VGGFace2 for high accuracy
- **Fast Enrollment**: Complete face enrollment in under 30 seconds
- **Robust Detection**: Handles multiple faces, poor lighting, edge cases
- **CLI Interface**: Easy-to-use command-line interface
- **Backup/Restore**: Encrypted backup and restore functionality
- **Cross-Platform**: Works on Windows, macOS, and Linux

## 🚀 Quick Start

### Installation

1. **Clone the repository:**
```bash
git clone https://github.com/your-username/faceauth.git
cd faceauth
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Run system check:**
```bash
python main.py system-check
```

4. **Try the demo:**
```bash
python demo.py
```

### Basic Usage

**Enroll a new user:**
```bash
python main.py enroll-face john.doe
```

**List enrolled users:**
```bash
python main.py list-users
```

**Delete a user:**
```bash
python main.py delete-user john.doe
```

## 📖 Documentation

### System Requirements

- **Python**: 3.8 or higher
- **Camera**: Webcam or built-in camera
- **Memory**: 2GB+ RAM recommended
- **Storage**: 10MB+ free space
- **OS**: Windows, macOS, or Linux

### Face Enrollment Process

The enrollment process captures multiple face samples to create a robust face profile:

1. **Face Detection**: Uses MTCNN for accurate face detection
2. **Quality Check**: Ensures high-quality face images (>95% confidence)
3. **Multiple Samples**: Collects 5-10 different face angles
4. **Embedding Generation**: Creates 512-dimensional face embedding using FaceNet
5. **Secure Storage**: Encrypts and stores the final averaged embedding

### CLI Commands

#### Core Commands

```bash
# Enroll a new user
python main.py enroll-face <user_id> [options]

# List all enrolled users  
python main.py list-users [options]

# Delete a user's enrollment
python main.py delete-user <user_id> [options]

# Show storage information
python main.py storage-info [options]

# System health check
python main.py system-check
```

#### Backup & Restore

```bash
# Create encrypted backup
python main.py backup backup.zip

# Restore from backup  
python main.py restore backup.zip
```

#### Options

```bash
--storage-dir, -s    Custom storage directory
--master-key, -k     Master encryption key
--timeout, -t        Enrollment timeout (seconds)
--force, -f          Force operation without confirmation
--quiet, -q          Minimal output mode
```

### Programming API

```python
from faceauth import FaceEnrollmentManager

# Initialize the enrollment manager
manager = FaceEnrollmentManager()

# Enroll a user
result = manager.enroll_user("john.doe", timeout=30)

if result['success']:
    print(f"Enrolled successfully! Quality: {result['average_quality']:.3f}")
else:
    print(f"Enrollment failed: {result['error']}")

# Check if user exists
if manager.verify_enrollment("john.doe"):
    print("User is enrolled")

# Get all enrolled users
users = manager.get_enrolled_users()
print(f"Total users: {len(users)}")

# Delete a user
manager.delete_user("john.doe")
```

## 🏗️ Architecture

### Project Structure

```
FaceAuth/
├── main.py                 # CLI interface
├── demo.py                 # Demo script
├── requirements.txt        # Dependencies
├── setup.py               # Package setup
├── README.md              # Documentation
├── faceauth/              # Main package
│   ├── __init__.py
│   ├── core/              # Core functionality
│   │   ├── __init__.py
│   │   ├── enrollment.py  # Face enrollment logic
│   │   └── authentication.py  # Future: authentication
│   └── utils/             # Utilities
│       ├── __init__.py
│       ├── security.py    # Encryption & security
│       └── storage.py     # Local storage management
├── data/                  # Face data storage (created automatically)
└── tests/                 # Unit tests
    └── test_basic.py
```

### Security Architecture

1. **Encryption Layer**: AES-256 encryption for all face embeddings
2. **Obfuscation**: Additional XOR obfuscation layer
3. **Key Management**: PBKDF2 key derivation with 100,000 iterations
4. **Secure Storage**: Restrictive file permissions (600/700)
5. **Hash-based IDs**: User IDs are hashed for filename generation

### AI Models

- **Face Detection**: MTCNN (Multi-task Cascaded Convolutional Networks)
- **Face Recognition**: FaceNet with InceptionResNetV1 backbone
- **Training Data**: VGGFace2 dataset (530K+ identities)
- **Embedding Size**: 512-dimensional vectors
- **Accuracy**: 99.6%+ on standard face recognition benchmarks

## 🔧 Configuration

### Storage Configuration

By default, FaceAuth stores data in:
- **Windows**: `%USERPROFILE%\.faceauth\`
- **macOS/Linux**: `~/.faceauth/`

You can customize the storage location:

```bash
python main.py enroll-face john.doe --storage-dir /custom/path
```

### Encryption Configuration

**Default**: Auto-generated system key
```bash
python main.py enroll-face john.doe
```

**Custom Master Key**: Use your own encryption key
```bash
python main.py enroll-face john.doe --master-key "my-secure-password"
```

### Performance Tuning

**GPU Acceleration** (if available):
- Automatically uses CUDA if available
- Falls back to CPU processing
- CPU mode is still very fast (~1-2 seconds per embedding)

**Memory Usage**:
- Enrollment: ~500MB peak memory usage
- Storage: ~1KB per enrolled user
- Models: ~100MB loaded in memory

## 🧪 Testing

Run the test suite:

```bash
# Install test dependencies
pip install pytest pytest-cov

# Run tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=faceauth --cov-report=html
```

Run the demo:

```bash
python demo.py
```

## 🚨 Security Considerations

### What's Stored

- **Face Embeddings**: 512-dimensional mathematical vectors
- **Metadata**: Enrollment time, quality scores, sample count
- **No Images**: Original face images are never stored

### What's NOT Stored

- ❌ Original camera images
- ❌ Face photos or videos  
- ❌ Biometric templates that can reconstruct faces
- ❌ Personal information beyond user ID

### Threat Model

**Protects Against**:
- ✅ Face image reconstruction from stored data
- ✅ Unauthorized access to face data
- ✅ Man-in-the-middle attacks (no network)
- ✅ Data breaches (encrypted storage)

**Does NOT Protect Against**:
- ❌ Physical access to unlocked device
- ❌ Compromised master key
- ❌ Malware with root/admin access
- ❌ Live camera access by malicious software

### Best Practices

1. **Use Strong Master Keys**: If using custom encryption keys
2. **Secure Your Device**: Use device encryption and screen locks
3. **Regular Backups**: Create encrypted backups periodically
4. **Access Control**: Limit access to the storage directory
5. **Clean Up**: Delete enrollments when no longer needed

**FaceAuth** - Because your face data should stay on your device. 🔒