# FaceAuth Troubleshooting Guide

Comprehensive troubleshooting guide for common issues, error messages, and solutions.

## Table of Contents
- [Quick Diagnostics](#quick-diagnostics)
- [Installation Issues](#installation-issues)
- [Camera Problems](#camera-problems)
- [Authentication Issues](#authentication-issues)
- [File Encryption Problems](#file-encryption-problems)
- [Performance Issues](#performance-issues)
- [Privacy & Security Concerns](#privacy--security-concerns)
- [Error Messages Reference](#error-messages-reference)
- [Advanced Troubleshooting](#advanced-troubleshooting)

## Quick Diagnostics

### System Health Check

Run the comprehensive system check first:

```bash
# Run full system diagnostics
python main.py system-check

# Run with verbose output
python main.py system-check --verbose

# Run specific component checks
python main.py system-check --component camera
python main.py system-check --component security
python main.py system-check --component storage
```

### Common Quick Fixes

```bash
# Reset configuration to defaults
python main.py config-reset

# Clear temporary files
python main.py cleanup --temp-files

# Reset camera settings
python main.py config-reset camera

# Check and fix file permissions
python main.py security-audit --fix
```

### Emergency Recovery

```bash
# Emergency user recovery
python main.py emergency-recovery --user username

# Reset entire system (WARNING: Deletes all data)
python main.py factory-reset --confirm

# Backup before troubleshooting
python main.py backup emergency_backup.zip
```

## Installation Issues

### Issue: "Module not found" errors during installation

**Symptoms:**
```
ImportError: No module named 'cv2'
ImportError: No module named 'torch'
ModuleNotFoundError: No module named 'facenet_pytorch'
```

**Solutions:**

1. **Check Python version:**
```bash
python --version  # Should be 3.8 or higher
```

2. **Verify virtual environment:**
```bash
# Create new virtual environment
python -m venv faceauth_env

# Activate it
# Windows:
faceauth_env\Scripts\activate
# macOS/Linux:
source faceauth_env/bin/activate

# Upgrade pip
python -m pip install --upgrade pip
```

3. **Install dependencies step by step:**
```bash
# Install core dependencies first
pip install numpy opencv-python

# Install PyTorch (CPU version)
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu

# Install remaining dependencies
pip install -r requirements.txt
```

4. **Platform-specific fixes:**

**Windows:**
```powershell
# Install Visual C++ Redistributable
# Download from Microsoft website

# Install dependencies with Windows-specific options
pip install opencv-python-headless  # If GUI issues occur
```

**macOS:**
```bash
# Install Xcode Command Line Tools
xcode-select --install

# Install Homebrew dependencies
brew install cmake

# Install with conda if pip fails
conda install opencv pytorch
```

**Linux (Ubuntu/Debian):**
```bash
# Install system dependencies
sudo apt update
sudo apt install python3-dev build-essential cmake
sudo apt install libopencv-dev python3-opencv

# Install with apt if pip fails
sudo apt install python3-torch python3-torchvision
```

### Issue: Permission denied during installation

**Solutions:**

1. **Use user installation:**
```bash
pip install --user -r requirements.txt
```

2. **Fix directory permissions:**
```bash
# Linux/macOS
chmod 755 ~/.local/
chmod -R 755 ~/.local/lib/python*/

# Windows (run as administrator)
icacls "%USERPROFILE%" /grant %USERNAME%:F /T
```

### Issue: SSL certificate errors

**Solutions:**

1. **Update certificates:**
```bash
# Update pip and certificates
pip install --upgrade pip certifi

# Use trusted hosts
pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org -r requirements.txt
```

2. **Corporate firewall workaround:**
```bash
# Use corporate proxy
pip install --proxy http://proxy.company.com:8080 -r requirements.txt

# Download and install offline
pip download -r requirements.txt
pip install --find-links . --no-index -r requirements.txt
```

## Camera Problems

### Issue: Camera not detected

**Symptoms:**
```
CameraError: No camera devices found
CameraError: Camera device 0 not available
```

**Diagnostics:**

1. **List available cameras:**
```bash
python main.py list-cameras
```

2. **Test camera access:**
```bash
python main.py test-camera
python main.py test-camera --device 1  # Try different devices
```

**Solutions:**

1. **Check camera connections:**
   - Ensure USB camera is properly connected
   - Try different USB ports
   - Check if camera is being used by another application
   - Restart computer if camera is frozen

2. **Fix camera permissions:**

**Windows:**
```powershell
# Check camera privacy settings
# Settings → Privacy → Camera → Allow apps to access camera
```

**macOS:**
```bash
# Grant camera permission to Terminal
# System Preferences → Security & Privacy → Privacy → Camera
```

**Linux:**
```bash
# Add user to video group
sudo usermod -a -G video $USER

# Check camera devices
ls -la /dev/video*

# Fix permissions
sudo chmod 666 /dev/video0
```

3. **Configure camera device:**
```bash
# Set specific camera device
python main.py config-set camera_device 1

# Try different resolutions
python main.py config-set camera_resolution "640x480"
python main.py config-set camera_resolution "320x240"
```

### Issue: Poor camera quality

**Symptoms:**
- Blurry images
- Low light detection
- Inconsistent face detection

**Solutions:**

1. **Improve lighting:**
   - Use natural daylight or bright artificial light
   - Avoid backlighting
   - Use diffused lighting to reduce shadows

2. **Adjust camera settings:**
```bash
# Increase resolution
python main.py config-set camera_resolution "1280x720"

# Adjust frame rate
python main.py config-set camera_fps 15

# Enable auto-focus
python main.py config-set camera_autofocus true
```

3. **Camera positioning:**
   - Position camera at eye level
   - Maintain 18-24 inches distance
   - Ensure stable camera mount
   - Clean camera lens

### Issue: Camera lag or freezing

**Solutions:**

1. **Reduce camera load:**
```bash
# Lower resolution
python main.py config-set camera_resolution "320x240"

# Reduce frame rate
python main.py config-set camera_fps 15

# Use CPU-only processing
python main.py config-set device cpu
```

2. **Close other camera applications:**
```bash
# Windows: Check Task Manager
# macOS: Check Activity Monitor
# Linux: 
lsof /dev/video0  # Check what's using camera
```

3. **Reset camera driver:**
```bash
# Windows
# Device Manager → Cameras → Uninstall and scan for changes

# Linux
sudo modprobe -r uvcvideo
sudo modprobe uvcvideo
```

## Authentication Issues

### Issue: Authentication always fails

**Symptoms:**
```
AuthenticationError: Face not recognized
AuthenticationError: Similarity score too low: 0.45 (threshold: 0.6)
```

**Diagnostics:**

1. **Check user enrollment:**
```bash
python main.py verify-enrollment username
python main.py user-info username
```

2. **Test with verbose output:**
```bash
python main.py verify-face username --verbose --debug
```

**Solutions:**

1. **Adjust similarity threshold:**
```bash
# Lower threshold (more lenient)
python main.py config-set similarity_threshold 0.4

# User-specific threshold
python main.py user-config username --set threshold 0.5
```

2. **Re-enroll with better samples:**
```bash
# Delete and re-enroll user
python main.py delete-user username
python main.py enroll-face username --samples 15 --quality-threshold 0.8
```

3. **Improve authentication conditions:**
   - Use same lighting as enrollment
   - Maintain consistent face position
   - Ensure face is visible and unobstructed
   - Look directly at camera

### Issue: Authentication too sensitive (false positives)

**Solutions:**

1. **Increase similarity threshold:**
```bash
python main.py config-set similarity_threshold 0.8
```

2. **Use stricter enrollment:**
```bash
python main.py enroll-face username --quality-threshold 0.9 --samples 20
```

3. **Enable additional security:**
```bash
python main.py config-set require_liveness_detection true
python main.py config-set max_authentication_attempts 3
```

### Issue: Slow authentication

**Solutions:**

1. **Enable performance optimizations:**
```bash
# Use GPU if available
python main.py config-set use_gpu true

# Reduce image processing
python main.py config-set fast_mode true

# Lower resolution for speed
python main.py config-set auth_resolution "320x240"
```

2. **Check system resources:**
```bash
# Monitor performance
python main.py performance-monitor

# Check memory usage
python main.py memory-monitor
```

## File Encryption Problems

### Issue: File encryption fails

**Symptoms:**
```
EncryptionError: Failed to encrypt file
PermissionError: Access denied
FileNotFoundError: File not found
```

**Solutions:**

1. **Check file permissions:**
```bash
# Windows
icacls filename.txt

# Linux/macOS
ls -la filename.txt
chmod 644 filename.txt  # Make readable
```

2. **Verify disk space:**
```bash
# Check available space
df -h  # Linux/macOS
dir   # Windows

# Clean up temp files
python main.py cleanup --temp-files
```

3. **Test with simple file:**
```bash
echo "test content" > test.txt
python main.py encrypt-file test.txt username
```

### Issue: File decryption fails

**Symptoms:**
```
DecryptionError: Invalid encryption format
DecryptionError: Authentication failed
IntegrityError: File may be corrupted
```

**Solutions:**

1. **Verify file integrity:**
```bash
python main.py verify-file encrypted_file.enc
```

2. **Check user authentication:**
```bash
# Test authentication separately
python main.py verify-face username

# Use emergency recovery
python main.py emergency-decrypt encrypted_file.enc --user username
```

3. **Corruption recovery:**
```bash
# Attempt repair
python main.py repair-file encrypted_file.enc username

# Partial recovery
python main.py emergency-decrypt encrypted_file.enc --partial-recovery
```

### Issue: Encrypted files are corrupted

**Solutions:**

1. **Check storage integrity:**
```bash
# File system check
# Windows: chkdsk C: /f
# Linux: fsck /dev/sda1
# macOS: diskutil verifyVolume /

# Verify FaceAuth storage
python main.py storage-integrity-check
```

2. **Restore from backup:**
```bash
# List available backups
python main.py list-backups

# Restore specific files
python main.py restore backup.zip --files "*.encrypted"
```

## Performance Issues

### Issue: Slow face detection/recognition

**Solutions:**

1. **Hardware optimization:**
```bash
# Enable GPU acceleration
python main.py config-set use_gpu true

# Optimize for your hardware
python main.py config-set performance_profile fast

# Reduce processing load
python main.py config-set batch_size 1
```

2. **Model optimization:**
```bash
# Use faster model
python main.py config-set model_type lightweight

# Reduce precision
python main.py config-set precision_mode fast
```

### Issue: High memory usage

**Solutions:**

1. **Memory optimization:**
```bash
# Enable memory-efficient mode
python main.py config-set memory_efficient true

# Reduce batch processing
python main.py config-set max_batch_size 1

# Clear memory caches
python main.py cleanup --memory-cache
```

2. **Monitor memory usage:**
```bash
python main.py memory-monitor --duration 60
```

### Issue: High CPU usage

**Solutions:**

1. **CPU optimization:**
```bash
# Limit CPU threads
python main.py config-set max_threads 2

# Reduce processing frequency
python main.py config-set processing_interval 100ms

# Use CPU-efficient algorithms
python main.py config-set algorithm_profile cpu_optimized
```

## Privacy & Security Concerns

### Issue: Data privacy concerns

**Solutions:**

1. **Verify local-only operation:**
```bash
# Check network activity (should be none)
python main.py network-monitor

# Verify no external connections
netstat -an | grep python  # Should show no external connections
```

2. **Review data storage:**
```bash
# Show what data is stored
python main.py privacy-audit

# Export user data for review
python main.py privacy-settings username --export-data review.json
```

3. **Enhanced privacy settings:**
```bash
# Enable strongest privacy settings
python main.py config-set privacy_level maximum

# Set automatic data deletion
python main.py config-set auto_delete_after_days 90
```

### Issue: Security audit failures

**Solutions:**

1. **Fix common security issues:**
```bash
# Run security audit with auto-fix
python main.py security-audit --fix

# Fix file permissions
python main.py fix-permissions

# Update security settings
python main.py config-set security_level high
```

2. **Manual security fixes:**
```bash
# Linux/macOS: Fix directory permissions
chmod 700 ~/.faceauth
chmod 600 ~/.faceauth/users/*/
chmod 600 ~/.faceauth/logs/*

# Windows: Fix folder permissions
icacls "%USERPROFILE%\.faceauth" /inheritance:r /grant:r "%USERNAME%":F
```

## Error Messages Reference

### Common Error Codes

#### CAMERA_001: Camera Not Found
**Full Error:** `CameraError: No camera devices found (CAMERA_001)`

**Cause:** No camera hardware detected
**Solution:** Check camera connection, install drivers, check permissions

#### AUTH_002: Authentication Failed
**Full Error:** `AuthenticationError: Face recognition failed (AUTH_002)`

**Cause:** Face not recognized or poor quality
**Solution:** Improve lighting, re-enroll user, adjust threshold

#### ENCRYPT_003: Encryption Failed
**Full Error:** `EncryptionError: File encryption failed (ENCRYPT_003)`

**Cause:** File access issues or insufficient disk space
**Solution:** Check file permissions, free disk space

#### STORAGE_004: Storage Access Denied
**Full Error:** `StorageError: Cannot access storage directory (STORAGE_004)`

**Cause:** Insufficient permissions or directory doesn't exist
**Solution:** Create directory, fix permissions

#### CONFIG_005: Invalid Configuration
**Full Error:** `ConfigError: Configuration value invalid (CONFIG_005)`

**Cause:** Invalid configuration setting
**Solution:** Reset configuration or set valid values

### Warning Messages

#### WARN_LOW_QUALITY: Poor Image Quality
**Message:** `Warning: Image quality below recommended threshold`
**Action:** Improve lighting, clean camera lens, check focus

#### WARN_MULTIPLE_FACES: Multiple Faces Detected
**Message:** `Warning: Multiple faces detected in frame`
**Action:** Ensure only one person in camera view

#### WARN_PARTIAL_FACE: Face Partially Visible
**Message:** `Warning: Face partially obscured or outside frame`
**Action:** Position face fully in camera view

## Advanced Troubleshooting

### Debug Mode

Enable comprehensive debugging:

```bash
# Enable debug logging
python main.py config-set log_level DEBUG

# Run with debug output
python main.py --debug verify-face username

# Check debug logs
tail -f ~/.faceauth/logs/debug.log
```

### Performance Profiling

```bash
# Profile authentication performance
python main.py profile-auth --iterations 10

# Profile memory usage
python main.py profile-memory --duration 60

# Generate performance report
python main.py performance-report --output report.json
```

### System Information Collection

```bash
# Collect system information for support
python main.py collect-system-info --output system_info.txt

# Generate diagnostic report
python main.py diagnostic-report --output diagnostic.zip
```

### Database Recovery

```bash
# Verify database integrity
python main.py verify-database

# Repair database corruption
python main.py repair-database --backup

# Rebuild database from backups
python main.py rebuild-database --from-backup backup.zip
```

### Network Diagnostics

```bash
# Verify no network traffic (should be silent)
python main.py network-trace --duration 30

# Check for external connections
python main.py connection-audit
```

### Advanced Configuration Reset

```bash
# Reset specific components
python main.py reset-component camera
python main.py reset-component authentication
python main.py reset-component encryption

# Selective reset with backup
python main.py selective-reset --backup --components "camera,auth"
```

## Getting Additional Help

### Log Analysis

```bash
# View recent errors
python main.py logs --level ERROR --recent 24h

# Search logs for specific issues
python main.py logs --search "CameraError"

# Export logs for support
python main.py export-logs --output support_logs.zip
```

### Support Information

When seeking help, provide:

1. **System Information:**
```bash
python main.py system-info --export system.json
```

2. **Error Logs:**
```bash
python main.py logs --level ERROR --export error_logs.txt
```

3. **Configuration:**
```bash
python main.py config-show --export config.json
```

### Community Support

- **GitHub Issues**: [Report bugs and issues](https://github.com/your-username/faceauth/issues)
- **GitHub Discussions**: [Ask questions and get help](https://github.com/your-username/faceauth/discussions)
- **Documentation**: [Read comprehensive docs](https://github.com/your-username/faceauth/docs)

### Professional Support

For enterprise deployments or complex issues:
- Enterprise support available
- Custom consultation services
- Training and implementation assistance

## Prevention Tips

### Best Practices
1. **Regular Backups**: Create encrypted backups weekly
2. **System Updates**: Keep dependencies updated
3. **Security Audits**: Run monthly security checks
4. **Monitor Performance**: Track authentication metrics
5. **Clean Environment**: Maintain good camera conditions

### Maintenance Schedule
- **Daily**: Check for errors in logs
- **Weekly**: Run system health check
- **Monthly**: Security audit and backup verification
- **Quarterly**: Full system cleanup and optimization

This troubleshooting guide covers the most common issues and their solutions. For issues not covered here, please consult the community support channels or submit a detailed bug report.
