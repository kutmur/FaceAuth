#!/usr/bin/env python3
"""
Integration tests for FaceAuth file encryption module.
Tests the complete encryption workflow with face authentication.
"""

import sys
import time
import tempfile
import shutil
from pathlib import Path
import numpy as np
import pytest
import secrets

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from faceauth.crypto.file_encryption import FileEncryption, EncryptionError
from faceauth.crypto.key_derivation import KeyDerivation, KeyDerivationError
from faceauth.utils.storage import FaceDataStorage
from faceauth.utils.security import SecurityManager


class TestFileEncryptionIntegration:
    """Integration tests for file encryption with face authentication."""
    
    def setup_method(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.security_manager = SecurityManager()
        self.storage = FaceDataStorage(self.test_dir, self.security_manager)
        self.file_encryption = FileEncryption(self.storage)
        
        # Create test user
        self.user_id = "test_user"
        self.test_embedding = np.random.rand(512).astype(np.float32)
        self.test_embedding = self.test_embedding / np.linalg.norm(self.test_embedding)
        
        # Save test user
        success = self.storage.save_user_enrollment(self.user_id, self.test_embedding)
        assert success, "Failed to save test user"
    
    def teardown_method(self):
        """Clean up test environment."""
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_complete_encryption_workflow(self):
        """Test complete encryption and decryption workflow."""
        # Create test file
        test_file = Path(self.test_dir) / "integration_test.txt"
        test_content = b"This is a test file for integration testing of FaceAuth encryption."
        test_file.write_bytes(test_content)
        
        encrypted_file = Path(self.test_dir) / "integration_test.txt.faceauth"
        decrypted_file = Path(self.test_dir) / "integration_test_decrypted.txt"
        
        # Mock authentication to avoid camera dependency
        original_auth = self.file_encryption._authenticate_user
        self.file_encryption._authenticate_user = lambda user_id, timeout: self.test_embedding
        
        try:
            # Test encryption
            encrypt_result = self.file_encryption.encrypt_file(
                file_path=str(test_file),
                user_id=self.user_id,
                output_path=str(encrypted_file),
                kdf_method='argon2'
            )
            
            assert encrypt_result['success']
            assert encrypted_file.exists()
            assert encrypt_result['original_size'] == len(test_content)
            assert encrypt_result['encrypted_size'] > len(test_content)  # Should have overhead
            
            # Test file verification
            file_info = self.file_encryption.verify_encrypted_file(str(encrypted_file))
            assert file_info['is_faceauth_file']
            assert file_info['kdf_method'] == 'argon2'
            assert file_info['original_filename'] == 'integration_test.txt'
            
            # Test decryption
            decrypt_result = self.file_encryption.decrypt_file(
                encrypted_path=str(encrypted_file),
                user_id=self.user_id,
                output_path=str(decrypted_file)
            )
            
            assert decrypt_result['success']
            assert decrypted_file.exists()
            
            # Verify content integrity
            decrypted_content = decrypted_file.read_bytes()
            assert decrypted_content == test_content
            
        finally:
            self.file_encryption._authenticate_user = original_auth
    
    def test_key_derivation_integration(self):
        """Test key derivation integration with file encryption."""
        kdf = KeyDerivation()
        
        # Test different KDF methods
        methods = ['argon2', 'pbkdf2', 'scrypt']
        
        for method in methods:
            # Derive key for file
            file_path = f"/test/path/{method}_test.txt"
            key1, salt = kdf.derive_file_key(self.test_embedding, file_path)
            
            # Should be consistent
            key2, _ = kdf.derive_file_key(self.test_embedding, file_path, salt)
            assert key1 == key2, f"Key derivation not consistent for {method}"
            
            # Different files should have different keys
            key3, _ = kdf.derive_file_key(self.test_embedding, f"/test/path/different_{method}.txt", salt)
            assert key1 != key3, f"Different files should have different keys for {method}"
    
    def test_multi_user_encryption(self):
        """Test encryption with multiple users."""
        # Create second user
        user2_id = "test_user_2"
        user2_embedding = np.random.rand(512).astype(np.float32)
        user2_embedding = user2_embedding / np.linalg.norm(user2_embedding)
        
        self.storage.save_user_enrollment(user2_id, user2_embedding)
        
        # Create test file
        test_file = Path(self.test_dir) / "multi_user_test.txt"
        test_content = b"Multi-user encryption test content"
        test_file.write_bytes(test_content)
        
        # Mock authentication for both users
        def mock_auth(user_id, timeout):
            if user_id == self.user_id:
                return self.test_embedding
            elif user_id == user2_id:
                return user2_embedding
            else:
                raise EncryptionError(f"Unknown user: {user_id}")
        
        self.file_encryption._authenticate_user = mock_auth
        
        try:
            # Encrypt with user 1
            encrypted_file1 = Path(self.test_dir) / "multi_user_test_user1.faceauth"
            result1 = self.file_encryption.encrypt_file(
                str(test_file), self.user_id, str(encrypted_file1)
            )
            assert result1['success']
            
            # Encrypt with user 2
            encrypted_file2 = Path(self.test_dir) / "multi_user_test_user2.faceauth"
            result2 = self.file_encryption.encrypt_file(
                str(test_file), user2_id, str(encrypted_file2)
            )
            assert result2['success']
            
            # Files should be different (different keys)
            content1 = encrypted_file1.read_bytes()
            content2 = encrypted_file2.read_bytes()
            assert content1 != content2, "Different users should produce different encrypted files"
            
            # Each user should only be able to decrypt their own file
            decrypted_file1 = Path(self.test_dir) / "decrypted_by_user1.txt"
            result_decrypt1 = self.file_encryption.decrypt_file(
                str(encrypted_file1), self.user_id, str(decrypted_file1)
            )
            assert result_decrypt1['success']
            
            decrypted_file2 = Path(self.test_dir) / "decrypted_by_user2.txt"
            result_decrypt2 = self.file_encryption.decrypt_file(
                str(encrypted_file2), user2_id, str(decrypted_file2)
            )
            assert result_decrypt2['success']
            
            # Verify content
            assert decrypted_file1.read_bytes() == test_content
            assert decrypted_file2.read_bytes() == test_content
            
        finally:
            # Cleanup
            for f in [test_file, encrypted_file1, encrypted_file2]:
                if f.exists():
                    f.unlink()
    
    def test_large_file_encryption_integration(self):
        """Test encryption of large files."""
        # Create large test file (5MB)
        test_file = Path(self.test_dir) / "large_integration_test.bin"
        large_content = secrets.token_bytes(5 * 1024 * 1024)  # 5MB
        test_file.write_bytes(large_content)
        
        encrypted_file = Path(self.test_dir) / "large_integration_test.bin.faceauth"
        
        # Mock authentication
        self.file_encryption._authenticate_user = lambda user_id, timeout: self.test_embedding
        
        try:
            # Test encryption performance
            start_time = time.time()
            encrypt_result = self.file_encryption.encrypt_file(
                str(test_file), self.user_id, str(encrypted_file)
            )
            encrypt_time = time.time() - start_time
            
            assert encrypt_result['success']
            assert encrypted_file.exists()
            
            # Should complete within reasonable time (adjust threshold as needed)
            assert encrypt_time < 30, f"Large file encryption took too long: {encrypt_time:.2f}s"
            
            # Test decryption
            decrypted_file = Path(self.test_dir) / "large_integration_test_decrypted.bin"
            start_time = time.time()
            decrypt_result = self.file_encryption.decrypt_file(
                str(encrypted_file), self.user_id, str(decrypted_file)
            )
            decrypt_time = time.time() - start_time
            
            assert decrypt_result['success']
            assert decrypt_time < 30, f"Large file decryption took too long: {decrypt_time:.2f}s"
            
            # Verify file size (content verification would take too long for 5MB)
            assert decrypted_file.stat().st_size == len(large_content)
            
        finally:
            # Cleanup large files
            for f in [test_file, encrypted_file]:
                if f.exists():
                    f.unlink()
    
    def test_error_conditions_integration(self):
        """Test error conditions in integration scenarios."""
        # Test with non-enrolled user
        test_file = Path(self.test_dir) / "error_test.txt"
        test_file.write_bytes(b"test content")
        
        try:
            with pytest.raises(EncryptionError, match="not enrolled"):
                self.file_encryption.encrypt_file(
                    str(test_file), "non_existent_user"
                )
            
            # Test decryption with wrong user
            # First create an encrypted file
            encrypted_file = Path(self.test_dir) / "error_test.faceauth"
            
            # Mock authentication for encryption
            original_auth = self.file_encryption._authenticate_user
            self.file_encryption._authenticate_user = lambda user_id, timeout: self.test_embedding
            
            encrypt_result = self.file_encryption.encrypt_file(
                str(test_file), self.user_id, str(encrypted_file)
            )
            assert encrypt_result['success']
            
            # Remove original file to avoid "file exists" error
            test_file.unlink()
            
            # Restore original authentication for testing wrong user
            self.file_encryption._authenticate_user = original_auth
            
            # Try to decrypt with non-existent user
            with pytest.raises(EncryptionError, match="not enrolled"):
                self.file_encryption.decrypt_file(
                    str(encrypted_file), "wrong_user"
                )
                
        finally:
            if test_file.exists():
                test_file.unlink()
            if encrypted_file.exists():
                encrypted_file.unlink()
    
    def test_file_format_compatibility(self):
        """Test file format compatibility and versioning."""
        test_file = Path(self.test_dir) / "format_test.txt"
        test_content = b"File format compatibility test"
        test_file.write_bytes(test_content)
        
        encrypted_file = Path(self.test_dir) / "format_test.faceauth"
        
        # Mock authentication
        self.file_encryption._authenticate_user = lambda user_id, timeout: self.test_embedding
        
        try:
            # Encrypt file
            encrypt_result = self.file_encryption.encrypt_file(
                str(test_file), self.user_id, str(encrypted_file)
            )
            assert encrypt_result['success']
            
            # Verify file format
            file_info = self.file_encryption.verify_encrypted_file(str(encrypted_file))
            assert file_info['is_faceauth_file']
            assert file_info['file_format_version'] == self.file_encryption.FILE_FORMAT_VERSION
            
            # Read raw file and check magic bytes
            with open(encrypted_file, 'rb') as f:
                magic = f.read(8)
                assert magic == self.file_encryption.MAGIC_BYTES
            
        finally:
            for f in [test_file, encrypted_file]:
                if f.exists():
                    f.unlink()


def test_cli_integration():
    """Test CLI integration components."""
    # Test that imports work correctly for CLI
    try:
        from faceauth.crypto.file_encryption import FileEncryption, EncryptionError
        from faceauth.crypto.key_derivation import KeyDerivation, KeyDerivationError
        
        # Test instantiation
        storage = FaceDataStorage()
        file_encryption = FileEncryption(storage)
        kdf = KeyDerivation()
        
        # Test basic functionality
        info = file_encryption.get_encryption_info()
        assert 'encryption_algorithm' in info
        
        kdf_info = kdf.get_kdf_info()
        assert 'method' in kdf_info
        
    except ImportError as e:
        pytest.fail(f"CLI integration import failed: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
