#!/usr/bin/env python3
"""
Debug script for encryption/decryption issues.
"""

import tempfile
import numpy as np
from pathlib import Path
from faceauth.utils.storage import FaceDataStorage
from faceauth.crypto.file_encryption import FileEncryption

def debug_encryption():
    # Create test environment
    test_dir = tempfile.mkdtemp()
    storage = FaceDataStorage(test_dir)
    file_encryption = FileEncryption(storage)
    
    # Create test user
    user_id = "debug_user"
    embedding = np.random.rand(512).astype(np.float32)
    embedding = embedding / np.linalg.norm(embedding)
    storage.save_user_enrollment(user_id, embedding)
    
    # Create test file
    test_file = Path(test_dir) / "debug.txt"
    test_content = b"Debug test content"
    test_file.write_bytes(test_content)
    
    print(f"Test directory: {test_dir}")
    print(f"Test content: {test_content}")
    print(f"Embedding shape: {embedding.shape}")
    
    # Mock authentication
    file_encryption._authenticate_user = lambda user_id, timeout: embedding
    
    try:
        # Encrypt with default method (argon2)
        encrypted_file = Path(test_dir) / "debug.txt.faceauth"
        print("\n=== ENCRYPTION ===")
        encrypt_result = file_encryption.encrypt_file(
            str(test_file), user_id, str(encrypted_file)
        )
        print(f"Encryption result: {encrypt_result}")
        
        # Examine the encrypted file header
        print("\n=== HEADER ANALYSIS ===")
        with open(encrypted_file, 'rb') as f:
            header_bytes = f.read(512)
        
        header_info = file_encryption._parse_file_header(header_bytes)
        print(f"Header info: {header_info}")
        
        # Try to decrypt
        print("\n=== DECRYPTION ===")
        decrypted_file = Path(test_dir) / "debug_decrypted.txt"
        decrypt_result = file_encryption.decrypt_file(
            str(encrypted_file), user_id, str(decrypted_file)
        )
        print(f"Decryption result: {decrypt_result}")
        
        # Check content
        decrypted_content = decrypted_file.read_bytes()
        print(f"Decrypted content: {decrypted_content}")
        print(f"Content matches: {test_content == decrypted_content}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Cleanup
        import shutil
        shutil.rmtree(test_dir, ignore_errors=True)

if __name__ == "__main__":
    debug_encryption()
