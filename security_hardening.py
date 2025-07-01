"""
Security Hardening Recommendations for FaceAuth
==============================================

This document outlines practical security enhancements to further strengthen
the local security posture of the FaceAuth system.
"""

import os
import stat
import getpass
import secrets
import string
from pathlib import Path


def validate_password_strength(password: str) -> tuple[bool, str]:
    """
    Validate password strength according to security best practices.
    
    Args:
        password: Password to validate
        
    Returns:
        Tuple of (is_valid, feedback_message)
    """
    issues = []
    
    if len(password) < 12:
        issues.append("• Password should be at least 12 characters long")
    
    if not any(c.islower() for c in password):
        issues.append("• Password should contain lowercase letters")
    
    if not any(c.isupper() for c in password):
        issues.append("• Password should contain uppercase letters")
    
    if not any(c.isdigit() for c in password):
        issues.append("• Password should contain numbers")
    
    if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
        issues.append("• Password should contain special characters")
    
    if any(word in password.lower() for word in ["password", "face", "auth", "login"]):
        issues.append("• Password should not contain common words")
    
    if len(issues) == 0:
        return True, "✅ Strong password!"
    else:
        return False, "⚠️ Password strength issues:\n" + "\n".join(issues)


def secure_file_permissions(file_path: str) -> bool:
    """
    Set secure file permissions (owner read/write only).
    
    Args:
        file_path: Path to the file to secure
        
    Returns:
        True if permissions were set successfully
    """
    try:
        # Set permissions to 600 (owner read/write only)
        os.chmod(file_path, stat.S_IRUSR | stat.S_IWUSR)
        return True
    except Exception as e:
        print(f"⚠️ Could not set secure permissions on {file_path}: {e}")
        return False


def secure_directory_permissions(dir_path: str) -> bool:
    """
    Set secure directory permissions (owner access only).
    
    Args:
        dir_path: Path to the directory to secure
        
    Returns:
        True if permissions were set successfully
    """
    try:
        # Set permissions to 700 (owner read/write/execute only)
        os.chmod(dir_path, stat.S_IRWXU)
        return True
    except Exception as e:
        print(f"⚠️ Could not set secure permissions on {dir_path}: {e}")
        return False


def generate_secure_password(length: int = 16) -> str:
    """
    Generate a cryptographically secure password.
    
    Args:
        length: Desired password length
        
    Returns:
        Secure random password
    """
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    password = ''.join(secrets.choice(alphabet) for _ in range(length))
    return password


def secure_delete_file(file_path: str, passes: int = 3) -> bool:
    """
    Attempt to securely delete a file by overwriting it before deletion.
    Note: This is best-effort and may not be completely secure on all filesystems.
    
    Args:
        file_path: Path to file to securely delete
        passes: Number of overwrite passes
        
    Returns:
        True if file was securely deleted
    """
    try:
        file_path = Path(file_path)
        if not file_path.exists():
            return True
        
        file_size = file_path.stat().st_size
        
        # Overwrite file with random data multiple times
        with open(file_path, 'r+b') as f:
            for _ in range(passes):
                f.seek(0)
                f.write(os.urandom(file_size))
                f.flush()
                os.fsync(f.fileno())  # Force write to disk
        
        # Finally delete the file
        file_path.unlink()
        return True
        
    except Exception as e:
        print(f"⚠️ Could not securely delete {file_path}: {e}")
        return False


def audit_system_security() -> dict:
    """
    Perform basic security audit of the current system.
    
    Returns:
        Dictionary with security audit results
    """
    audit_results = {
        'platform': os.name,
        'face_data_dir_exists': False,
        'face_data_dir_permissions': None,
        'face_files': [],
        'recommendations': []
    }
    
    # Check face_data directory
    face_data_dir = Path('face_data')
    if face_data_dir.exists():
        audit_results['face_data_dir_exists'] = True
        
        # Check directory permissions
        dir_stat = face_data_dir.stat()
        dir_perms = oct(dir_stat.st_mode)[-3:]
        audit_results['face_data_dir_permissions'] = dir_perms
        
        if dir_perms != '700':
            audit_results['recommendations'].append(
                f"Directory permissions are {dir_perms}, recommend 700 (owner only)"
            )
        
        # Check face files
        for face_file in face_data_dir.glob('*_face.dat'):
            file_stat = face_file.stat()
            file_perms = oct(file_stat.st_mode)[-3:]
            
            audit_results['face_files'].append({
                'file': str(face_file),
                'permissions': file_perms,
                'size': file_stat.st_size
            })
            
            if file_perms != '600':
                audit_results['recommendations'].append(
                    f"File {face_file.name} has permissions {file_perms}, recommend 600"
                )
    
    return audit_results


# Security hardening recommendations for implementation:

HARDENING_RECOMMENDATIONS = """
🛡️ FaceAuth Security Hardening Recommendations
============================================

1. **File Permissions (High Priority)**
   - Automatically set face_data/ directory to 700 (owner only)
   - Set all .dat files to 600 (owner read/write only)
   - Set .faceauth files to 600 when created

2. **Password Security (Medium Priority)**
   - Implement password strength validation
   - Offer to generate secure passwords for users
   - Add password confirmation prompts

3. **Secure Deletion (Medium Priority)**
   - Implement secure deletion for temporary files
   - Offer secure deletion of original files after encryption
   - Clear sensitive variables from memory when possible

4. **Audit and Monitoring (Low Priority)**
   - Add system security audit command
   - Log security events (enrollment, authentication) with timestamps
   - Implement file integrity checking

5. **Platform-Specific Enhancements**
   - Linux/macOS: Use umask to set default secure permissions
   - Windows: Use NTFS file attributes for additional protection
   - All platforms: Check for disk encryption recommendations

Implementation Priority:
1. File permissions (can be implemented immediately)
2. Password validation (user experience improvement)
3. Secure deletion (advanced security feature)
4. Audit capabilities (operational security)
"""

if __name__ == "__main__":
    print(HARDENING_RECOMMENDATIONS)
    
    # Example usage
    print("\n🔍 Security Audit Results:")
    audit = audit_system_security()
    print(f"Platform: {audit['platform']}")
    print(f"Face data directory exists: {audit['face_data_dir_exists']}")
    
    if audit['recommendations']:
        print("\n⚠️ Security Recommendations:")
        for rec in audit['recommendations']:
            print(f"• {rec}")
    else:
        print("\n✅ No immediate security issues found")
