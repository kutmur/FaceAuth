# FaceAuth - Developer Instructions

## 🚀 Quick Start Guide

### 1. Setup Environment

**Option A: Automatic Setup (Recommended)**
```bash
python setup.py
```

**Option B: Manual Setup**
```bash
# Install dependencies
pip install -r requirements.txt

# Create directories
mkdir -p face_data logs
```

### 2. Test Installation

```bash
# Check system info
python main.py info

# Test crypto module
python test_crypto.py
```

### 3. Enroll Your First Face

```bash
# Basic enrollment
python main.py enroll-face

# With specific user ID
python main.py enroll-face --user-id your_name

# Using ArcFace model (higher accuracy)
python main.py enroll-face --user-id your_name --model ArcFace
```

### 4. Programmatic Usage

```bash
# Run examples
python examples.py

# Or import in your code
from enrollment import enroll_new_user
result = enroll_new_user(user_id="test_user")
```

## 📋 Enrollment Process

### What to Expect

1. **Camera Access**: System will request webcam permission
2. **Positioning**: Green rectangle shows optimal face area
3. **Real-time Feedback**: 
   - ✅ "Face detected" - you're positioned correctly
   - ❌ "Multiple faces" - ensure only one person visible
   - ❌ "No face detected" - move into camera view
   - ❌ "Face too small" - move closer to camera

4. **Capture**: Press SPACE when you see ✅ message
5. **Countdown**: 3-second countdown before capture
6. **Processing**: AI generates face embedding (~5-10 seconds)
7. **Encryption**: Data encrypted with your password
8. **Storage**: Saved to `face_data/[user_id]_face.dat`

### Controls During Enrollment

- **SPACE**: Capture face (when ✅ face detected)
- **ESC**: Cancel enrollment
- **Close window**: Cancel enrollment

### Troubleshooting

**Camera Issues:**
```bash
# Linux - check camera devices
ls /dev/video*

# Install v4l-utils if needed
sudo apt-get install v4l-utils
```

**Face Detection Issues:**
- Ensure good lighting (avoid backlighting)
- Remove glasses/sunglasses if possible
- Ensure only one person in frame
- Face should fill about 30-50% of the rectangle
- Look directly at the camera

**Import Errors:**
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Check Python version (requires 3.8+)
python --version
```

## 🔒 Security Notes

### Password Requirements
- Minimum 8 characters
- Used for encryption only (never stored)
- Cannot be recovered if forgotten
- Required for any future access to face data

### File Security
- Face data stored in `face_data/` directory
- Files named `[user_id]_face.dat`
- AES-256 encrypted
- Cannot reconstruct original face images
- Safe to backup (still encrypted)

### What's Stored
- Mathematical face embedding (vector of numbers)
- NOT the actual face image
- NOT the password
- Embedding dimensions: 128-2048 numbers depending on model

## 🧪 Testing & Development

### Run Crypto Tests
```bash
python test_crypto.py
```

### Run Examples
```bash
python examples.py
```

### Development Mode
```bash
# Install in development mode
pip install -e .

# Run with debugging
python main.py enroll-face --debug
```

### Supported Models

| Model | Speed | Accuracy | Embedding Size |
|-------|-------|----------|----------------|
| Facenet | Fast | Good | 128 |
| Facenet512 | Medium | Better | 512 |
| ArcFace | Slow | Best | 512 |
| VGG-Face | Medium | Good | 2048 |

## 📁 File Structure

```
FaceAuth/
├── main.py              # CLI interface
├── enrollment.py        # Face enrollment module
├── crypto.py           # Security functions
├── setup.py            # Installation script
├── examples.py         # Usage examples
├── test_crypto.py      # Crypto tests
├── requirements.txt    # Dependencies
├── README.md          # Documentation
├── .gitignore         # Git ignore rules
└── face_data/         # Encrypted face data (created after use)
```

## 🔧 Configuration

### Environment Variables

```bash
# Optional: Set custom face data directory
export FACEAUTH_DATA_DIR="/path/to/secure/location"

# Optional: Set default model
export FACEAUTH_DEFAULT_MODEL="ArcFace"
```

### Custom Model Selection

```python
from enrollment import FaceEnroller

# Create with custom settings
enroller = FaceEnroller(
    model_name="ArcFace",     # Model choice
    data_dir="custom_dir"    # Custom directory
)

# Adjust detection settings
enroller.min_confidence = 0.8    # Higher confidence
enroller.capture_delay = 5       # Longer delay
```

## 🚨 Important Notes

### Security Best Practices
1. **Backup**: Keep encrypted face data files safe
2. **Password**: Use strong, unique password
3. **Environment**: Run in secure environment
4. **Updates**: Keep dependencies updated

### Privacy Guarantees
- No network communication
- No cloud storage
- No telemetry/tracking
- Face data never leaves your machine
- Original images not stored anywhere

### Limitations
- Requires good lighting
- Works best with frontal face view
- Single user per enrollment session
- Webcam required for enrollment

## 🆘 Support

### Common Error Messages

**"Cannot access webcam"**
- Check camera permissions
- Ensure no other app is using camera
- Try different camera index

**"No face detected"**
- Improve lighting
- Position face in center
- Remove obstructions

**"Multiple faces detected"**
- Ensure only one person visible
- Cover mirrors/reflections

**"Import errors"**
- Install dependencies: `pip install -r requirements.txt`
- Check Python version: `python --version`

### Getting Help
1. Check this instruction file
2. Run `python main.py --help`
3. Test with `python test_crypto.py`
4. Try examples with `python examples.py`

---

**Happy face enrolling! 🎉**
