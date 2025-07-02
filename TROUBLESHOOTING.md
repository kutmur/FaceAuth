# FaceAuth Troubleshooting Guide

## Table of Contents

- [Common Issues](#common-issues)
- [Installation Problems](#installation-problems)
- [Camera Issues](#camera-issues)
- [Authentication Problems](#authentication-problems)
- [File Encryption Issues](#file-encryption-issues)
- [Performance Issues](#performance-issues)
- [Security Concerns](#security-concerns)
- [System Requirements](#system-requirements)
- [Debug Mode](#debug-mode)
- [Error Codes](#error-codes)
- [Getting Help](#getting-help)

## Common Issues

### 🚨 "No module named 'facenet_pytorch'"

**Problem**: Missing facial recognition dependencies
**Solution**:
```bash
pip install -r requirements.txt
# Or specifically:
pip install facenet-pytorch torch torchvision opencv-python
```

### 🚨 "Camera not accessible" / "VideoCapture failed"

**Problem**: Camera permission or hardware issues
**Solutions**:
1. **Check camera permissions** (Windows/macOS)
2. **Close other camera applications** (Zoom, Skype, etc.)
3. **Try different camera index**:
   ```bash
   python main.py system-check --camera-test
   ```
4. **Restart camera service** (Linux):
   ```bash
   sudo systemctl restart uvcvideo
   ```

### 🚨 "No face detected" during enrollment

**Problem**: Face detection failing
**Solutions**:
1. **Improve lighting** - use natural light or bright indoor lighting
2. **Position face clearly** - center your face in the camera view
3. **Remove obstructions** - hats, sunglasses, masks
4. **Clean camera lens**
5. **Adjust camera angle** - eye level works best
6. **Try different distance** - 18-24 inches from camera

### 🚨 Authentication failing for enrolled user

**Problem**: Face recognition not working
**Solutions**:
1. **Check lighting conditions** - similar to enrollment conditions
2. **Adjust similarity threshold**:
   ```bash
   python main.py verify-face username --threshold 0.5
   ```
3. **Re-enroll with better quality**:
   ```bash
   python main.py enroll-face username --timeout 60
   ```
4. **Check for significant appearance changes** (glasses, beard, etc.)

### 🚨 "Permission denied" errors

**Problem**: File/directory access issues
**Solutions**:
1. **Fix storage permissions**:
   ```bash
   python main.py security-audit --fix
   ```
2. **Run as administrator** (Windows) or with sudo (Linux/macOS)
3. **Change storage directory**:
   ```bash
   python main.py config-set storage_dir /path/with/permissions
   ```

## Installation Problems

### Missing Dependencies

**Check what's missing**:
```bash
python main.py system-check
```

**Common missing packages**:
```bash
# Core ML dependencies
pip install torch torchvision facenet-pytorch
pip install opencv-python numpy Pillow

# Crypto dependencies  
pip install cryptography

# CLI dependencies
pip install click

# Development dependencies (optional)
pip install pytest pytest-cov
```

### Version Conflicts

**Python version issues**:
- **Minimum**: Python 3.8+
- **Recommended**: Python 3.9 or 3.10
- **Check version**: `python --version`

**Package conflicts**:
```bash
# Create clean environment
python -m venv faceauth_env
source faceauth_env/bin/activate  # Linux/macOS
# or
faceauth_env\Scripts\activate  # Windows

pip install -r requirements.txt
```

### GPU Support Issues

**CUDA not available**:
```bash
# Check CUDA availability
python -c "import torch; print(torch.cuda.is_available())"

# Install CUDA-enabled PyTorch (optional)
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

## Camera Issues

### Camera Detection

**Test camera access**:
```bash
python main.py system-check --camera-test
```

**Manual camera test**:
```python
import cv2
cap = cv2.VideoCapture(0)  # Try 0, 1, 2...
if cap.isOpened():
    print("Camera working")
    ret, frame = cap.read()
    if ret:
        print(f"Frame size: {frame.shape}")
cap.release()
```

### Multiple Cameras

**List available cameras**:
```bash
python main.py system-check --list-cameras
```

**Use specific camera**:
```bash
python main.py enroll-face username --camera-index 1
```

### Camera Quality Issues

**Poor image quality**:
1. **Clean lens** - physically clean camera lens
2. **Check resolution** - ensure camera supports 640x480 minimum
3. **Lighting** - use bright, even lighting
4. **Focus** - ensure camera has auto-focus or is in focus
5. **Stable mount** - reduce camera shake

## Authentication Problems

### Similarity Threshold Issues

**Too strict (false negatives)**:
```bash
# Lower threshold for easier authentication
python main.py verify-face username --threshold 0.5
```

**Too loose (security concern)**:
```bash
# Raise threshold for better security
python main.py verify-face username --threshold 0.8
```

**Find optimal threshold**:
```bash
# Test different thresholds
python main.py auth-metrics --user username --test-thresholds
```

### Environmental Factors

**Different lighting**:
- Enroll in multiple lighting conditions
- Use consistent lighting for authentication
- Avoid backlighting and shadows

**Appearance changes**:
- **Minor changes**: System should adapt automatically
- **Major changes**: Re-enrollment may be needed
- **Temporary changes**: Use lower threshold temporarily

### Performance Issues

**Slow authentication**:
1. **GPU acceleration**:
   ```bash
   python main.py config-set device cuda  # If available
   ```
2. **Reduce timeout**:
   ```bash
   python main.py verify-face username --timeout 5
   ```
3. **Close other applications** using camera/CPU

## File Encryption Issues

### Encryption Failures

**File access errors**:
1. **Check file permissions** - ensure file is readable
2. **File in use** - close file in other applications
3. **Disk space** - ensure sufficient storage space
4. **Path issues** - use absolute paths or escape spaces

**Authentication during encryption**:
```bash
# Extend authentication timeout
python main.py encrypt-file file.pdf username --auth-timeout 30
```

### Decryption Problems

**Wrong user**:
- Only the user who encrypted can decrypt
- Verify user ID matches exactly

**Corrupted files**:
```bash
# Verify file integrity
python main.py file-info encrypted_file.faceauth
```

**KDF method issues**:
```bash
# Try different KDF method
python main.py encrypt-file file.pdf username --kdf-method pbkdf2
```

### Large File Handling

**Memory issues with large files**:
```bash
# Reduce chunk size
python main.py encrypt-file largefile.zip username --chunk-size 1048576
```

**Performance optimization**:
```bash
# Use faster KDF for large files
python main.py encrypt-file largefile.zip username --kdf-method pbkdf2
```

## Performance Issues

### Slow Enrollment

**Optimization strategies**:
1. **GPU acceleration** if available
2. **Better lighting** for faster face detection
3. **Stable positioning** to reduce retries
4. **Close unnecessary applications**

**Monitor performance**:
```bash
# Show detailed timing
python main.py enroll-face username --verbose --show-metrics
```

### Memory Usage

**High memory consumption**:
1. **Close other applications**
2. **Restart Python process** after multiple operations
3. **Use smaller image resolution** if possible

**Memory monitoring**:
```python
import psutil
import os
process = psutil.Process(os.getpid())
print(f"Memory usage: {process.memory_info().rss / 1024 / 1024:.1f} MB")
```

### Disk Space

**Storage optimization**:
```bash
# Check storage usage
python main.py storage-info

# Clean up old users
python main.py delete-user old_username

# Compact storage
python main.py storage-compact
```

## Security Concerns

### Data Security

**Verify encryption**:
```bash
# Run security audit
python main.py security-audit

# Check compliance
python main.py compliance-check
```

**Storage security**:
```bash
# Fix permissions issues
python main.py security-audit --fix

# Verify file permissions
ls -la ~/.faceauth/  # Linux/macOS
```

### Privacy Verification

**Privacy compliance**:
```bash
# Check privacy settings
python main.py privacy-check

# Export privacy report
python main.py privacy-check --export privacy_report.json
```

**Data rights**:
```bash
# Export user data
python main.py privacy-settings username --export-data user_data.json

# Delete user data
python main.py privacy-settings username --delete-data
```

## System Requirements

### Minimum Requirements

- **OS**: Windows 10, macOS 10.14, Ubuntu 18.04+
- **Python**: 3.8+
- **RAM**: 4GB (8GB recommended)
- **Storage**: 100MB free space
- **Camera**: Any USB/built-in camera (640x480 minimum)

### Recommended Specifications

- **OS**: Latest stable versions
- **Python**: 3.9 or 3.10
- **RAM**: 8GB+
- **Storage**: 1GB+ free space
- **Camera**: HD camera (1280x720+)
- **GPU**: CUDA-compatible GPU (optional but recommended)

### Network Requirements

- **None** - FaceAuth works completely offline
- No internet connection required
- No cloud services used

## Debug Mode

### Enable Debug Logging

**Command-line debug**:
```bash
python main.py --debug enroll-face username
python main.py --verbose verify-face username
```

**Configuration debug**:
```bash
python main.py config-set log_level DEBUG
```

**Python debug**:
```python
import logging
logging.basicConfig(level=logging.DEBUG)

from faceauth.core.enrollment import FaceEnrollmentManager
manager = FaceEnrollmentManager(debug=True)
```

### Log Files

**Location**:
- **Windows**: `%USERPROFILE%\.faceauth\logs\`
- **Linux/macOS**: `~/.faceauth/logs/`

**View recent logs**:
```bash
# System logs
tail -f ~/.faceauth/logs/system.log

# Audit logs (encrypted)
python main.py audit-logs --recent --decrypt
```

### Performance Profiling

**Time operations**:
```bash
time python main.py enroll-face username
time python main.py verify-face username
```

**Memory profiling**:
```python
import tracemalloc
tracemalloc.start()

# Your FaceAuth operations here

current, peak = tracemalloc.get_traced_memory()
print(f"Current memory: {current / 1024 / 1024:.1f} MB")
print(f"Peak memory: {peak / 1024 / 1024:.1f} MB")
```

## Error Codes

### Enrollment Errors

| Code | Description | Solution |
|------|-------------|----------|
| `CAMERA_ERROR` | Camera not accessible | Check camera permissions/connections |
| `NO_FACE_DETECTED` | No face found in camera | Improve lighting, positioning |
| `POOR_QUALITY` | Face quality too low | Better lighting, reduce motion |
| `TIMEOUT` | Enrollment timed out | Extend timeout, improve conditions |
| `USER_EXISTS` | User already enrolled | Delete existing user first |
| `STORAGE_ERROR` | Storage operation failed | Check permissions, disk space |

### Authentication Errors

| Code | Description | Solution |
|------|-------------|----------|
| `USER_NOT_FOUND` | User not enrolled | Enroll user first |
| `THRESHOLD_NOT_MET` | Similarity below threshold | Lower threshold or re-enroll |
| `TIMEOUT` | Authentication timed out | Improve conditions, extend timeout |
| `MAX_ATTEMPTS_EXCEEDED` | Too many failed attempts | Check user identity, improve conditions |
| `CAMERA_ERROR` | Camera not accessible | Check camera availability |

### Encryption Errors

| Code | Description | Solution |
|------|-------------|----------|
| `FILE_NOT_FOUND` | Input file doesn't exist | Check file path |
| `PERMISSION_DENIED` | File access denied | Check file permissions |
| `AUTHENTICATION_FAILED` | Face auth failed | Verify user identity |
| `INVALID_FILE` | File corrupted/invalid | Check file integrity |
| `STORAGE_FULL` | Insufficient disk space | Free up storage space |

## Getting Help

### Self-Help Resources

1. **System Check**: `python main.py system-check`
2. **Documentation**: Read `README.md` and `API_DOCUMENTATION.md`
3. **Demo**: Run `python comprehensive_demo.py`
4. **Tests**: Run test suite to verify installation

### Community Support

1. **GitHub Issues**: Report bugs and get help
2. **Documentation**: Check latest docs for updates
3. **Security**: Report security issues privately

### Professional Support

For enterprise or production deployments:
1. **Security Review**: Professional security assessment
2. **Integration Support**: Custom integration assistance  
3. **Performance Optimization**: System tuning and optimization
4. **Compliance Consulting**: Regulatory compliance assistance

### Reporting Issues

When reporting issues, please include:

1. **System Information**:
   ```bash
   python main.py system-check --export system_info.json
   ```

2. **Error Messages**: Complete error output

3. **Steps to Reproduce**: Exact commands and conditions

4. **Environment**: OS, Python version, hardware specs

5. **Logs**: Relevant log files (with sensitive data removed)

**Issue Template**:
```
**Problem Description**: Brief description of the issue

**System Information**:
- OS: [Windows 10/macOS/Ubuntu]
- Python: [3.9.x]
- FaceAuth Version: [1.0]
- Hardware: [Camera model, GPU if any]

**Steps to Reproduce**:
1. Command run: `python main.py ...`
2. Expected behavior: ...
3. Actual behavior: ...

**Error Messages**:
```
[Paste complete error output here]
```

**Additional Context**:
Any other relevant information
```

---

*FaceAuth Troubleshooting Guide v1.0 | Privacy-First Face Authentication*
