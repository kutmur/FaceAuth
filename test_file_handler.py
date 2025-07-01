#!/usr/bin/env python3
"""
File Handler Test Script for FaceAuth
=====================================

This script tests the file encryption functionality of the FaceAuth system.
It creates sample files and tests the encryption/decryption workflow.
"""

import sys
import tempfile
import os
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

def test_file_encryption():
    """Test the file encryption functionality"""
    print("🧪 Testing FaceAuth File Encryption")
    print("=" * 50)
    
    try:
        from file_handler import encrypt_file, decrypt_file, validate_encryption_integrity
        
        # Create a test file
        test_content = b"This is a secret document.\nIt contains sensitive information.\nFaceAuth will protect it!"
        
        with tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.txt') as f:
            f.write(test_content)
            test_file_path = f.name
        
        print(f"📁 Created test file: {test_file_path}")
        print(f"📊 Content size: {len(test_content)} bytes")
        
        # Test password
        test_password = "SecurePassword123!"
        
        # Test encryption
        print("\n🔒 Testing encryption...")
        encrypted_path = encrypt_file(test_file_path, test_password)
        print(f"✅ Encrypted to: {encrypted_path}")
        
        # Check encrypted file size
        encrypted_size = Path(encrypted_path).stat().st_size
        print(f"📊 Encrypted size: {encrypted_size} bytes")
        print(f"📊 Overhead: {encrypted_size - len(test_content)} bytes")
        
        # Test decryption
        print("\n🔓 Testing decryption...")
        decrypted_path = decrypt_file(encrypted_path, test_password)
        print(f"✅ Decrypted to: {decrypted_path}")
        
        # Verify content
        with open(decrypted_path, 'rb') as f:
            decrypted_content = f.read()
        
        if decrypted_content == test_content:
            print("✅ Content verification: PASSED")
        else:
            print("❌ Content verification: FAILED")
            return False
        
        # Test integrity validation
        print("\n🔍 Testing integrity validation...")
        os.remove(encrypted_path)  # Clean up first
        os.remove(decrypted_path)  # Clean up first
        
        integrity_ok = validate_encryption_integrity(test_file_path, test_password)
        if integrity_ok:
            print("✅ Integrity validation: PASSED")
        else:
            print("❌ Integrity validation: FAILED")
            return False
        
        # Clean up
        os.remove(test_file_path)
        
        print("\n🎉 All tests PASSED!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test FAILED: {e}")
        return False

def create_sample_file():
    """Create a sample file for manual testing"""
    sample_content = """🔐 FaceAuth Sample Document
===========================

This is a sample document to test the FaceAuth file encryption system.

🛡️ Security Features:
• AES-256-GCM encryption
• PBKDF2 key derivation (100,000 iterations)
• Unique random keys per file
• Secure key wrapping architecture

📋 Test Instructions:
1. Run: python main.py enroll-face
2. Run: python main.py encrypt-file sample_document.txt
3. Verify face authentication works
4. Enter a secure password
5. Check that sample_document.txt.faceauth is created

🔓 To decrypt:
1. Run: python main.py decrypt-file sample_document.txt.faceauth
2. Verify face authentication again
3. Enter the same password
4. Check that the file is restored

⚠️ Security Notes:
• Keep your password secure - it cannot be recovered
• The .faceauth file contains your encrypted data
• Face authentication is required for both encryption and decryption
• Original files remain unchanged during encryption

📧 Created by FaceAuth System
🔗 Local, privacy-first file encryption
"""
    
    sample_path = Path("sample_document.txt")
    with open(sample_path, 'w', encoding='utf-8') as f:
        f.write(sample_content)
    
    print(f"📄 Created sample file: {sample_path}")
    print(f"📊 Size: {sample_path.stat().st_size} bytes")
    print("\n💡 Usage:")
    print(f"  python main.py encrypt-file {sample_path}")
    
    return str(sample_path)

if __name__ == "__main__":
    print("FaceAuth File Handler Test Suite")
    print("=" * 40)
    
    if len(sys.argv) > 1 and sys.argv[1] == "create-sample":
        create_sample_file()
    else:
        test_file_encryption()
