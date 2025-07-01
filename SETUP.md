# FaceAuth Installation & Setup Guide

## 🚀 Quick Setup

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/faceauth.git
cd faceauth
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. System Check
```bash
python main.py system-check
```

### 4. Try the Demo
```bash
python demo.py
```

## 📋 System Requirements

- **Python**: 3.8 or higher
- **Camera**: Webcam or built-in camera
- **Memory**: 2GB+ RAM recommended  
- **Storage**: 10MB+ free space
- **OS**: Windows, macOS, or Linux

## 🔧 Installation Options

### Option 1: Direct Installation (Recommended)
```bash
# Clone repository
git clone https://github.com/your-username/faceauth.git
cd faceauth

# Install dependencies
pip install -r requirements.txt

# Verify installation
python main.py system-check
```

### Option 2: Virtual Environment
```bash
# Create virtual environment
python -m venv faceauth_env

# Activate virtual environment
# Windows:
faceauth_env\Scripts\activate
# macOS/Linux:
source faceauth_env/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Option 3: Conda Environment
```bash
# Create conda environment
conda create -n faceauth python=3.10

# Activate environment
conda activate faceauth

# Install dependencies
pip install -r requirements.txt
```

## 🎯 Basic Usage

### Command Line Interface

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

**Storage information:**
```bash
python main.py storage-info
```

**Create backup:**
```bash
python main.py backup my_backup.zip
```

**Restore from backup:**
```bash
python main.py restore my_backup.zip
```

### Python API

```python
from faceauth import FaceEnrollmentManager

# Initialize system
manager = FaceEnrollmentManager()

# Enroll a user
result = manager.enroll_user("alice", timeout=30)

if result['success']:
    print(f"✅ Enrolled! Quality: {result['average_quality']:.3f}")
else:
    print(f"❌ Failed: {result['error']}")

# Check if user exists
if manager.verify_enrollment("alice"):
    print("User exists!")

# List all users
users = manager.get_enrolled_users()
print(f"Total users: {len(users)}")
```

## 🛠️ Configuration

### Storage Location
By default, FaceAuth stores data in:
- **Windows**: `%USERPROFILE%\.faceauth\`
- **macOS/Linux**: `~/.faceauth/`

**Custom storage directory:**
```bash
python main.py enroll-face john --storage-dir /custom/path
```

### Encryption
**Auto-generated key (default):**
```bash
python main.py enroll-face john
```

**Custom master key:**
```bash
python main.py enroll-face john --master-key "my-secure-password"
```

### Performance Tuning
- **GPU**: Automatically uses CUDA if available
- **CPU**: Falls back to CPU processing (still very fast)
- **Memory**: ~500MB peak during enrollment
- **Storage**: ~1KB per enrolled user

## 🚨 Troubleshooting

### Common Issues

**1. Camera not detected:**
```bash
# Check camera permissions
# Windows: Settings > Privacy > Camera
# macOS: System Preferences > Security & Privacy > Camera
# Linux: Check /dev/video0 permissions
```

**2. Import errors:**
```bash
# Reinstall dependencies
pip uninstall -y opencv-python torch facenet-pytorch
pip install -r requirements.txt
```

**3. CUDA issues:**
```bash
# Force CPU mode if GPU causes issues
export CUDA_VISIBLE_DEVICES=""
python main.py enroll-face john
```

**4. Permission denied:**
```bash
# Check storage directory permissions
ls -la ~/.faceauth/
# Fix permissions if needed
chmod 700 ~/.faceauth/
```

### Error Messages

| Error | Solution |
|-------|----------|
| `Camera error` | Check camera permissions and connections |
| `User already exists` | Use `delete-user` first or choose different ID |
| `No face detected` | Improve lighting and positioning |
| `Multiple faces` | Ensure only one person is visible |
| `Import error` | Reinstall dependencies |

## 🔒 Security Notes

### What's Stored
- ✅ Mathematical face embeddings (512 dimensions)
- ✅ Encrypted with AES-256
- ✅ Cannot reconstruct original images
- ❌ No photos or videos stored

### Best Practices
1. **Use strong master keys** for custom encryption
2. **Secure your device** with encryption and locks
3. **Regular backups** of enrollment data
4. **Limit access** to storage directories
5. **Clean up** unused enrollments

### Privacy
- **100% Local**: No network requests
- **No Cloud**: All data stays on device
- **No Tracking**: No telemetry or analytics
- **Open Source**: Full transparency

## 📚 Advanced Usage

### Batch Operations
```bash
# Backup before bulk operations
python main.py backup before_bulk.zip

# Process multiple users (script this)
for user in alice bob charlie; do
    python main.py enroll-face $user
done
```

### Integration
```python
# Custom storage location
from faceauth import FaceEnrollmentManager

manager = FaceEnrollmentManager(
    storage_dir="/secure/location",
    master_key="your-secure-key"
)

# Error handling
try:
    result = manager.enroll_user("john")
    if not result['success']:
        handle_enrollment_error(result['error'])
except Exception as e:
    handle_system_error(e)
```

### Monitoring
```python
# Get detailed statistics
stats = manager.get_storage_stats()
print(f"Storage usage: {stats['storage_size_bytes']} bytes")
print(f"Total users: {stats['total_users']}")

# Monitor enrollment quality
result = manager.enroll_user("alice")
if result['average_quality'] < 0.95:
    print("Warning: Low quality enrollment")
```

## 🆘 Support

- **Documentation**: README.md and code comments
- **Issues**: [GitHub Issues](https://github.com/your-username/faceauth/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-username/faceauth/discussions)

## 🔄 Updates

```bash
# Update to latest version
git pull origin main
pip install -r requirements.txt

# Check for breaking changes
python main.py system-check
```

---

**Happy face authentication!** 🎉
