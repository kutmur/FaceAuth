#!/usr/bin/env python3
"""
Simple FaceAuth Decryption Test
Tests the core decryption functionality.
"""

import tempfile
import os
import sys
from pathlib import Path
import numpy as np

# Add the current directory to Python path
sys.path.insert(0, '.')

from faceauth.utils.storage import FaceDataStorage
from faceauth.utils.security import SecurityManager
from faceauth.crypto.file_encryption import FileEncryption, EncryptionError


def test_decryption():
    """Test the core decryption functionality."""
    print("🧪 FaceAuth Decryption Test")
    print("=" * 30)
    
    # Create temporary directory
    test_dir = tempfile.mkdtemp(prefix='faceauth_test_')
    
    try:
        # Initialize system
        security_manager = SecurityManager()
        storage = FaceDataStorage(test_dir, security_manager)
        file_encryption = FileEncryption(storage)
        
        # Create test user
        user_id = "test_user"
        test_embedding = np.random.rand(512).astype(np.float32)
        test_embedding = test_embedding / np.linalg.norm(test_embedding)
        storage.save_user_enrollment(user_id, test_embedding)
        
        # Create test file
        test_file = Path(test_dir) / "test.txt"
        test_content = "This is a secret test file for FaceAuth decryption!"
        test_file.write_text(test_content, encoding='utf-8')
        
        print(f"✅ Created test file: {test_file.name}")
        print(f"   Content: '{test_content}'")
        
        # Mock authentication
        file_encryption._authenticate_user = lambda user_id, timeout: test_embedding
        
        # Encrypt file
        encrypted_file = Path(test_dir) / "test.txt.faceauth"
        encrypt_result = file_encryption.encrypt_file(
            str(test_file), user_id, str(encrypted_file)
        )
        
        if not encrypt_result['success']:
            print("❌ Encryption failed!")
            return False
        
        print(f"✅ Encryption successful")
        print(f"   Original: {encrypt_result['original_size']} bytes")
        print(f"   Encrypted: {encrypt_result['encrypted_size']} bytes")
        
        # Remove original file
        test_file.unlink()
        
        # Test decryption
        decrypted_file = Path(test_dir) / "decrypted.txt"
        decrypt_result = file_encryption.decrypt_file(
            str(encrypted_file), user_id, str(decrypted_file)
        )
        
        if not decrypt_result['success']:
            print("❌ Decryption failed!")
            return False
        
        print(f"✅ Decryption successful")
        print(f"   Output: {decrypt_result['output_file']}")
        print(f"   Size: {decrypt_result['file_size']} bytes")
        
        # Verify content
        decrypted_content = decrypted_file.read_text(encoding='utf-8')
        if decrypted_content == test_content:
            print("✅ Content integrity verified!")
            print("🎉 All tests passed!")
            return True
        else:
            print("❌ Content mismatch!")
            print(f"   Expected: '{test_content}'")
            print(f"   Got: '{decrypted_content}'")
            return False
        
    except Exception as e:
        print(f"❌ Test error: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # Cleanup
        import shutil
        try:
            shutil.rmtree(test_dir)
        except Exception:
            pass


if __name__ == "__main__":
    success = test_decryption()
    sys.exit(0 if success else 1)
