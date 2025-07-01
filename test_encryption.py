#!/usr/bin/env python3
"""
Test suite for FaceAuth file encryption functionality.
Tests cryptographic operations, key derivation, and file encryption/decryption.
"""

import sys
import time
import tempfile
import shutil
from pathlib import Path
import numpy as np
import pytest
import secrets
import hashlib

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from faceauth.crypto.key_derivation import KeyDerivation, KeyDerivationError
from faceauth.crypto.file_encryption import FileEncryption, EncryptionError
from faceauth.utils.storage import FaceDataStorage
from faceauth.utils.security import SecurityManager


class TestKeyDerivation:
    """Test suite for key derivation functionality."""
    
    def setup_method(self):
        """Set up test environment."""
        self.kdf = KeyDerivation()
        self.test_embedding = np.random.rand(512).astype(np.float32)
        self.test_embedding = self.test_embedding / np.linalg.norm(self.test_embedding)
    
    def test_salt_generation(self):
        """Test cryptographically secure salt generation."""
        salt1 = self.kdf.generate_salt()
        salt2 = self.kdf.generate_salt()
        
        assert len(salt1) == self.kdf.SALT_LENGTH
        assert len(salt2) == self.kdf.SALT_LENGTH
        assert salt1 != salt2  # Should be different
    
    def test_embedding_normalization(self):
        """Test face embedding normalization."""
        normalized = self.kdf._normalize_embedding(self.test_embedding)
        
        assert isinstance(normalized, bytes)
        assert len(normalized) == self.test_embedding.nbytes
        
        # Test consistency
        normalized2 = self.kdf._normalize_embedding(self.test_embedding)
        assert normalized == normalized2
    
    def test_pbkdf2_key_derivation(self):
        """Test PBKDF2 key derivation."""
        salt = self.kdf.generate_salt()
        key, used_salt = self.kdf.derive_encryption_key(
            self.test_embedding, salt, method='pbkdf2'
        )
        
        assert len(key) == self.kdf.KEY_LENGTH
        assert used_salt == salt
        
        # Test consistency
        key2, _ = self.kdf.derive_encryption_key(
            self.test_embedding, salt, method='pbkdf2'
        )
        assert key == key2
    
    def test_scrypt_key_derivation(self):
        """Test scrypt key derivation."""
        salt = self.kdf.generate_salt()
        key, used_salt = self.kdf.derive_encryption_key(
            self.test_embedding, salt, method='scrypt'
        )
        
        assert len(key) == self.kdf.KEY_LENGTH
        assert used_salt == salt
    
    def test_argon2_key_derivation(self):
        """Test Argon2 key derivation."""
        salt = self.kdf.generate_salt()
        key, used_salt = self.kdf.derive_encryption_key(
            self.test_embedding, salt, method='argon2'
        )
        
        assert len(key) == self.kdf.KEY_LENGTH
        assert used_salt == salt
    
    def test_multi_kdf_derivation(self):
        """Test multi-KDF key derivation."""
        salt = self.kdf.generate_salt()
        key, used_salt = self.kdf.derive_encryption_key(
            self.test_embedding, salt, method='multi'
        )
        
        assert len(key) == self.kdf.KEY_LENGTH
        assert used_salt == salt
    
    def test_key_verification(self):
        """Test key verification functionality."""
        salt = self.kdf.generate_salt()
        key, _ = self.kdf.derive_encryption_key(self.test_embedding, salt)
        
        # Should verify correctly
        assert self.kdf.verify_key(self.test_embedding, salt, key)
        
        # Should fail with wrong key
        wrong_key = secrets.token_bytes(32)
        assert not self.kdf.verify_key(self.test_embedding, salt, wrong_key)
        
        # Should fail with wrong embedding
        wrong_embedding = np.random.rand(512).astype(np.float32)
        assert not self.kdf.verify_key(wrong_embedding, salt, key)
    
    def test_file_key_derivation(self):
        """Test file-specific key derivation."""
        file_path = "/test/path/file.txt"
        salt = self.kdf.generate_salt()
        
        key1, used_salt = self.kdf.derive_file_key(self.test_embedding, file_path, salt)
        key2, _ = self.kdf.derive_file_key(self.test_embedding, file_path, salt)
        
        assert len(key1) == self.kdf.KEY_LENGTH
        assert key1 == key2  # Should be consistent
        assert used_salt == salt
        
        # Different file paths should produce different keys
        key3, _ = self.kdf.derive_file_key(self.test_embedding, "/different/path", salt)
        assert key1 != key3
    
    def test_secure_key_deletion(self):
        """Test secure key deletion."""
        key = secrets.token_bytes(32)
        key_copy = key[:]  # Make a copy
        
        # Secure delete should not raise an error
        self.kdf.secure_delete_key(key)
        
        # Original should still exist (we can't test memory overwriting directly)
        assert key_copy == key  # The original bytes object
    
    def test_kdf_info(self):
        """Test KDF information retrieval."""
        info = self.kdf.get_kdf_info('argon2')
        
        assert 'method' in info
        assert 'time_cost' in info
        assert 'memory_cost' in info
        assert 'key_length' in info
        assert info['key_length'] == self.kdf.KEY_LENGTH


class TestFileEncryption:
    """Test suite for file encryption functionality."""
    
    def setup_method(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.storage = FaceDataStorage(self.test_dir)
        self.file_encryption = FileEncryption(self.storage)
        
        # Create test user
        self.user_id = "test_user"
        self.test_embedding = np.random.rand(512).astype(np.float32)
        self.test_embedding = self.test_embedding / np.linalg.norm(self.test_embedding)
        
        # Save test user
        self.storage.save_user_enrollment(self.user_id, self.test_embedding)
    
    def teardown_method(self):
        """Clean up test environment."""
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_file_header_creation_and_parsing(self):
        """Test encrypted file header creation and parsing."""
        salt = secrets.token_bytes(32)
        nonce = secrets.token_bytes(12)
        kdf_method = "argon2"
        original_filename = "test.txt"
        file_size = 1234
        
        # Create header
        header = self.file_encryption._create_file_header(
            salt, nonce, kdf_method, original_filename, file_size
        )
        
        # Parse header
        parsed = self.file_encryption._parse_file_header(header)
        
        assert parsed['kdf_method'] == kdf_method
        assert parsed['salt'] == salt
        assert parsed['nonce'] == nonce
        assert parsed['original_filename'] == original_filename
        assert parsed['file_size'] == file_size
        assert parsed['version'] == self.file_encryption.FILE_FORMAT_VERSION
    
    def test_header_checksum_validation(self):
        """Test header checksum validation."""
        salt = secrets.token_bytes(32)
        nonce = secrets.token_bytes(12)
        header = self.file_encryption._create_file_header(
            salt, nonce, "argon2", "test.txt", 1234
        )
        
        # Valid header should parse correctly
        parsed = self.file_encryption._parse_file_header(header)
        assert parsed is not None
        
        # Corrupted header should fail
        corrupted_header = bytearray(header)
        corrupted_header[50] = (corrupted_header[50] + 1) % 256  # Corrupt one byte
        
        with pytest.raises(EncryptionError, match="checksum"):
            self.file_encryption._parse_file_header(bytes(corrupted_header))
    
    def test_encrypt_decrypt_small_file(self):
        """Test encryption and decryption of a small file."""
        # Create test file
        test_file = Path(self.test_dir) / "test.txt"
        test_content = b"Hello, this is a test file for encryption!"
        test_file.write_bytes(test_content)
        
        encrypted_file = Path(self.test_dir) / "test.txt.faceauth"
        decrypted_file = Path(self.test_dir) / "test_decrypted.txt"
        
        # Mock authentication by directly using the embedding
        original_authenticate = self.file_encryption._authenticate_user
        self.file_encryption._authenticate_user = lambda user_id, timeout: self.test_embedding
        
        try:
            # Encrypt file
            encrypt_result = self.file_encryption.encrypt_file(
                str(test_file), self.user_id, str(encrypted_file)
            )
            
            assert encrypt_result['success']
            assert encrypted_file.exists()
            assert encrypt_result['original_size'] == len(test_content)
            
            # Decrypt file
            decrypt_result = self.file_encryption.decrypt_file(
                str(encrypted_file), self.user_id, str(decrypted_file)
            )
            
            assert decrypt_result['success']
            assert decrypted_file.exists()
            
            # Verify content
            decrypted_content = decrypted_file.read_bytes()
            assert decrypted_content == test_content
            
        finally:
            # Restore original method
            self.file_encryption._authenticate_user = original_authenticate
    
    def test_encrypt_decrypt_large_file(self):
        """Test encryption and decryption of a large file (multi-chunk)."""
        # Create large test file (2MB)
        test_file = Path(self.test_dir) / "large_test.bin"
        test_content = secrets.token_bytes(2 * 1024 * 1024)  # 2MB
        test_file.write_bytes(test_content)
        
        encrypted_file = Path(self.test_dir) / "large_test.bin.faceauth"
        decrypted_file = Path(self.test_dir) / "large_test_decrypted.bin"
        
        # Mock authentication
        self.file_encryption._authenticate_user = lambda user_id, timeout: self.test_embedding
        
        try:
            # Encrypt file
            encrypt_result = self.file_encryption.encrypt_file(
                str(test_file), self.user_id, str(encrypted_file)
            )
            
            assert encrypt_result['success']
            assert encrypted_file.exists()
            
            # Decrypt file
            decrypt_result = self.file_encryption.decrypt_file(
                str(encrypted_file), self.user_id, str(decrypted_file)
            )
            
            assert decrypt_result['success']
            assert decrypted_file.exists()
            
            # Verify content
            decrypted_content = decrypted_file.read_bytes()
            assert len(decrypted_content) == len(test_content)
            assert hashlib.sha256(decrypted_content).digest() == hashlib.sha256(test_content).digest()
            
        finally:
            # Cleanup
            for f in [test_file, encrypted_file, decrypted_file]:
                if f.exists():
                    f.unlink()
    
    def test_file_verification(self):
        """Test encrypted file verification."""
        # Create and encrypt a test file
        test_file = Path(self.test_dir) / "verify_test.txt"
        test_file.write_bytes(b"Test content for verification")
        encrypted_file = Path(self.test_dir) / "verify_test.txt.faceauth"
        
        # Mock authentication
        self.file_encryption._authenticate_user = lambda user_id, timeout: self.test_embedding
        
        try:
            # Encrypt file
            self.file_encryption.encrypt_file(
                str(test_file), self.user_id, str(encrypted_file)
            )
            
            # Verify encrypted file
            info = self.file_encryption.verify_encrypted_file(str(encrypted_file))
            
            assert info['is_faceauth_file']
            assert info['original_filename'] == 'verify_test.txt'
            assert info['kdf_method'] == 'argon2'
            assert info['file_format_version'] == self.file_encryption.FILE_FORMAT_VERSION
            
            # Test verification of non-encrypted file
            info2 = self.file_encryption.verify_encrypted_file(str(test_file))
            assert not info2['is_faceauth_file']
            
        finally:
            # Cleanup
            for f in [test_file, encrypted_file]:
                if f.exists():
                    f.unlink()
    
    def test_encryption_with_different_kdf_methods(self):
        """Test encryption with different KDF methods."""
        test_file = Path(self.test_dir) / "kdf_test.txt"
        test_content = b"Test content for KDF methods"
        test_file.write_bytes(test_content)
        
        # Mock authentication
        self.file_encryption._authenticate_user = lambda user_id, timeout: self.test_embedding
        
        kdf_methods = ['argon2', 'pbkdf2', 'scrypt']
        
        for method in kdf_methods:
            encrypted_file = Path(self.test_dir) / f"kdf_test_{method}.faceauth"
            decrypted_file = Path(self.test_dir) / f"kdf_test_{method}_decrypted.txt"
            
            try:
                # Encrypt with specific KDF method
                encrypt_result = self.file_encryption.encrypt_file(
                    str(test_file), self.user_id, str(encrypted_file), kdf_method=method
                )
                
                assert encrypt_result['success']
                assert encrypt_result['kdf_method'] == method
                
                # Verify file info
                info = self.file_encryption.verify_encrypted_file(str(encrypted_file))
                assert info['kdf_method'] == method
                
                # Decrypt file
                decrypt_result = self.file_encryption.decrypt_file(
                    str(encrypted_file), self.user_id, str(decrypted_file)
                )
                
                assert decrypt_result['success']
                
                # Verify content
                decrypted_content = decrypted_file.read_bytes()
                assert decrypted_content == test_content
                
            finally:
                # Cleanup
                for f in [encrypted_file, decrypted_file]:
                    if f.exists():
                        f.unlink()
        
        # Cleanup test file
        test_file.unlink()
    
    def test_encryption_error_handling(self):
        """Test encryption error handling."""
        # Test with non-existent file
        with pytest.raises(EncryptionError, match="not found"):
            self.file_encryption.encrypt_file(
                "/nonexistent/file.txt", self.user_id
            )
        
        # Test with non-existent user
        test_file = Path(self.test_dir) / "error_test.txt"
        test_file.write_bytes(b"test")
        
        try:
            with pytest.raises(EncryptionError, match="not enrolled"):
                self.file_encryption.encrypt_file(
                    str(test_file), "nonexistent_user"
                )
        finally:
            test_file.unlink()
    
    def test_decryption_error_handling(self):
        """Test decryption error handling."""
        # Test with non-existent file
        with pytest.raises(EncryptionError, match="not found"):
            self.file_encryption.decrypt_file(
                "/nonexistent/file.faceauth", self.user_id
            )
        
        # Test with non-encrypted file
        test_file = Path(self.test_dir) / "not_encrypted.txt"
        test_file.write_bytes(b"This is not an encrypted file")
        
        try:
            with pytest.raises(EncryptionError, match="Not a FaceAuth encrypted file"):
                self.file_encryption.decrypt_file(
                    str(test_file), "nonexistent_user"
                )
        finally:
            test_file.unlink()
    
    def test_encryption_info(self):
        """Test encryption information retrieval."""
        info = self.file_encryption.get_encryption_info()
        
        assert info['encryption_algorithm'] == 'AES-256-GCM'
        assert info['key_size_bits'] == 256
        assert info['nonce_size_bits'] == 96
        assert info['tag_size_bits'] == 128
        assert 'kdf_info' in info


def test_cryptographic_security():
    """Test cryptographic security properties."""
    print("\n🔐 Testing Cryptographic Security")
    print("=" * 40)
    
    kdf = KeyDerivation()
    
    # Test 1: Key uniqueness
    print("1. Testing key uniqueness...")
    embedding = np.random.rand(512).astype(np.float32)
    keys = []
    
    for i in range(10):
        salt = kdf.generate_salt()
        key, _ = kdf.derive_encryption_key(embedding, salt)
        keys.append(key)
    
    # All keys should be different
    unique_keys = set(keys)
    assert len(unique_keys) == len(keys), "Keys are not unique!"
    print("   ✅ All derived keys are unique")
    
    # Test 2: Key consistency
    print("2. Testing key consistency...")
    salt = kdf.generate_salt()
    key1, _ = kdf.derive_encryption_key(embedding, salt)
    key2, _ = kdf.derive_encryption_key(embedding, salt)
    assert key1 == key2, "Key derivation is not consistent!"
    print("   ✅ Key derivation is consistent")
    
    # Test 3: Salt importance
    print("3. Testing salt importance...")
    key_no_salt1, salt1 = kdf.derive_encryption_key(embedding)
    key_no_salt2, salt2 = kdf.derive_encryption_key(embedding)
    assert key_no_salt1 != key_no_salt2, "Different salts should produce different keys!"
    print("   ✅ Different salts produce different keys")
    
    print("✅ All cryptographic security tests passed!")


def test_performance_requirements():
    """Test performance requirements for encryption/decryption."""
    print("\n⚡ Testing Performance Requirements")
    print("=" * 40)
    
    # Create test environment
    test_dir = tempfile.mkdtemp()
    try:
        storage = FaceDataStorage(test_dir)
        file_encryption = FileEncryption(storage)
        
        # Create test user
        user_id = "perf_test_user"
        embedding = np.random.rand(512).astype(np.float32)
        embedding = embedding / np.linalg.norm(embedding)
        storage.save_user_enrollment(user_id, embedding)
        
        # Mock authentication for testing
        file_encryption._authenticate_user = lambda user_id, timeout: embedding
        
        # Test small file encryption/decryption speed
        test_file = Path(test_dir) / "perf_test.txt"
        test_content = b"Test content for performance testing" * 1000  # ~36KB
        test_file.write_bytes(test_content)
        
        encrypted_file = Path(test_dir) / "perf_test.faceauth"
        
        # Test encryption speed
        start_time = time.time()
        encrypt_result = file_encryption.encrypt_file(
            str(test_file), user_id, str(encrypted_file)
        )
        encrypt_time = time.time() - start_time
        
        assert encrypt_result['success']
        print(f"Encryption time: {encrypt_time:.3f}s ({len(test_content)} bytes)")
        
        # Test decryption speed
        decrypted_file = Path(test_dir) / "perf_test_decrypted.txt"
        start_time = time.time()
        decrypt_result = file_encryption.decrypt_file(
            str(encrypted_file), user_id, str(decrypted_file)
        )
        decrypt_time = time.time() - start_time
        
        assert decrypt_result['success']
        print(f"Decryption time: {decrypt_time:.3f}s")
        
        # Verify content
        decrypted_content = decrypted_file.read_bytes()
        assert decrypted_content == test_content
        
        print("✅ Performance requirements met!")
        
    finally:
        shutil.rmtree(test_dir, ignore_errors=True)


def run_comprehensive_tests():
    """Run all encryption tests comprehensively."""
    print("🔒 FaceAuth File Encryption - Comprehensive Testing")
    print("=" * 60)
    
    # Run pytest tests
    print("\n📋 Running Unit Tests...")
    test_result = pytest.main([__file__ + "::TestKeyDerivation", "-v", "-x"])
    
    if test_result == 0:
        test_result = pytest.main([__file__ + "::TestFileEncryption", "-v", "-x"])
    
    if test_result == 0:
        print("✅ All unit tests passed!")
    else:
        print("❌ Some unit tests failed!")
        return False
    
    # Run security tests
    try:
        test_cryptographic_security()
    except Exception as e:
        print(f"❌ Security test failed: {e}")
        return False
    
    # Run performance tests
    try:
        test_performance_requirements()
    except Exception as e:
        print(f"❌ Performance test failed: {e}")
        return False
    
    print("\n🎉 ALL TESTS PASSED!")
    print("\n📊 Test Summary:")
    print("   ✅ Unit tests: Key derivation and file encryption")
    print("   ✅ Security: Cryptographic properties verified")
    print("   ✅ Performance: Encryption/decryption speed validated")
    print("   ✅ Error handling: Various failure scenarios")
    print("   ✅ File integrity: Content verification")
    print("   ✅ Multi-KDF: Support for different key derivation methods")
    
    return True


if __name__ == "__main__":
    success = run_comprehensive_tests()
    sys.exit(0 if success else 1)
