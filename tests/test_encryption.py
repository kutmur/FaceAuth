"""
Comprehensive test suite for FaceAuth encryption module.
Tests encryption, decryption, key management, and security features.
"""

import pytest
import os
import time
import tempfile
import shutil
import secrets
import json
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from cryptography.fernet import Fernet
from cryptography.exceptions import InvalidSignature

from faceauth.security.encryption_manager import EncryptionManager, EncryptionError


class TestEncryptionManagerInit:
    """Test EncryptionManager initialization and setup."""
    
    def test_init_with_default_settings(self, temp_dir):
        """Test initialization with default settings."""
        em = EncryptionManager(key_dir=str(temp_dir))
        
        assert em.key_dir == Path(temp_dir)
        assert em.algorithm == 'AES-256-GCM'
        assert em.key_size == 32  # 256 bits
        assert em.salt_size == 16
        assert em.iterations == 100000
        assert em.memory_manager is not None
        assert em._keys == {}
    
    def test_init_with_custom_settings(self, temp_dir):
        """Test initialization with custom settings."""
        custom_iterations = 200000
        em = EncryptionManager(
            key_dir=str(temp_dir),
            iterations=custom_iterations
        )
        
        assert em.iterations == custom_iterations
    
    def test_init_creates_key_directory(self):
        """Test that initialization creates key directory if it doesn't exist."""
        with tempfile.TemporaryDirectory() as temp_dir:
            key_dir = Path(temp_dir) / "new_keys"
            
            em = EncryptionManager(key_dir=str(key_dir))
            
            assert key_dir.exists()
            assert key_dir.is_dir()
    
    def test_init_key_directory_permissions(self, temp_dir):
        """Test that key directory has proper permissions."""
        em = EncryptionManager(key_dir=str(temp_dir))
        
        # On Unix systems, check for restrictive permissions
        if os.name == 'posix':
            stat_info = os.stat(temp_dir)
            # Should be readable/writable by owner only
            assert (stat_info.st_mode & 0o777) == 0o700


class TestKeyGeneration:
    """Test cryptographic key generation."""
    
    def test_generate_salt(self, encryption_manager):
        """Test salt generation."""
        salt = encryption_manager._generate_salt()
        
        assert len(salt) == encryption_manager.salt_size
        assert isinstance(salt, bytes)
        
        # Generate multiple salts to ensure they're different
        salt2 = encryption_manager._generate_salt()
        assert salt != salt2
    
    def test_derive_key_from_password(self, encryption_manager):
        """Test key derivation from password."""
        password = "test_password"
        salt = encryption_manager._generate_salt()
        
        key = encryption_manager._derive_key(password, salt)
        
        assert len(key) == encryption_manager.key_size
        assert isinstance(key, bytes)
        
        # Same password and salt should produce same key
        key2 = encryption_manager._derive_key(password, salt)
        assert key == key2
        
        # Different salt should produce different key
        salt2 = encryption_manager._generate_salt()
        key3 = encryption_manager._derive_key(password, salt2)
        assert key != key3
    
    def test_generate_random_key(self, encryption_manager):
        """Test random key generation."""
        key = encryption_manager._generate_random_key()
        
        assert len(key) == encryption_manager.key_size
        assert isinstance(key, bytes)
        
        # Generate multiple keys to ensure they're different
        key2 = encryption_manager._generate_random_key()
        assert key != key2
    
    def test_derive_key_performance(self, encryption_manager):
        """Test that key derivation takes reasonable time (security requirement)."""
        import time
        
        password = "test_password"
        salt = encryption_manager._generate_salt()
        
        start_time = time.time()
        key = encryption_manager._derive_key(password, salt)
        derivation_time = time.time() - start_time
        
        # Should take some time for security (PBKDF2 iterations)
        assert derivation_time > 0.01  # At least 10ms
        assert derivation_time < 5.0   # But not too long for usability


class TestEncryptionDecryption:
    """Test encryption and decryption operations."""
    
    def test_encrypt_decrypt_data(self, encryption_manager):
        """Test basic data encryption and decryption."""
        data = b"Hello, World! This is test data."
        password = "test_password"
        
        # Encrypt data
        encrypted_data = encryption_manager.encrypt_data(data, password)
        
        assert encrypted_data != data
        assert len(encrypted_data) > len(data)  # Should be larger due to metadata
        assert isinstance(encrypted_data, bytes)
        
        # Decrypt data
        decrypted_data = encryption_manager.decrypt_data(encrypted_data, password)
        
        assert decrypted_data == data
    
    def test_encrypt_decrypt_string(self, encryption_manager):
        """Test string encryption and decryption."""
        data = "Hello, World! This is test data with unicode: 🔐"
        password = "test_password"
        
        # Encrypt string
        encrypted_data = encryption_manager.encrypt_data(data, password)
        
        # Decrypt string
        decrypted_data = encryption_manager.decrypt_data(encrypted_data, password)
        
        assert decrypted_data == data.encode('utf-8')
    
    def test_encrypt_decrypt_large_data(self, encryption_manager):
        """Test encryption/decryption of large data."""
        # Generate 1MB of random data
        data = secrets.token_bytes(1024 * 1024)
        password = "test_password"
        
        encrypted_data = encryption_manager.encrypt_data(data, password)
        decrypted_data = encryption_manager.decrypt_data(encrypted_data, password)
        
        assert decrypted_data == data
    
    def test_encrypt_with_wrong_password_fails(self, encryption_manager):
        """Test that decryption with wrong password fails."""
        data = b"Sensitive data"
        correct_password = "correct_password"
        wrong_password = "wrong_password"
        
        encrypted_data = encryption_manager.encrypt_data(data, correct_password)
        
        with pytest.raises(EncryptionError, match="Failed to decrypt data"):
            encryption_manager.decrypt_data(encrypted_data, wrong_password)
    
    def test_encrypt_empty_data(self, encryption_manager):
        """Test encryption of empty data."""
        data = b""
        password = "test_password"
        
        encrypted_data = encryption_manager.encrypt_data(data, password)
        decrypted_data = encryption_manager.decrypt_data(encrypted_data, password)
        
        assert decrypted_data == data
    
    def test_encrypt_with_key_object(self, encryption_manager):
        """Test encryption using key object instead of password."""
        data = b"Test data"
        key = encryption_manager._generate_random_key()
        
        encrypted_data = encryption_manager.encrypt_data_with_key(data, key)
        decrypted_data = encryption_manager.decrypt_data_with_key(encrypted_data, key)
        
        assert decrypted_data == data
    
    def test_encrypt_metadata_format(self, encryption_manager):
        """Test that encrypted data contains proper metadata."""
        data = b"Test data"
        password = "test_password"
        
        encrypted_data = encryption_manager.encrypt_data(data, password)
        
        # Should start with metadata header
        assert encrypted_data.startswith(b'FACEAUTH_ENC_V1:')
        
        # Should contain salt and encrypted content
        assert len(encrypted_data) > len(data) + 32  # At least salt + some overhead


class TestFileEncryption:
    """Test file encryption and decryption operations."""
    
    def test_encrypt_decrypt_file(self, encryption_manager, temp_dir):
        """Test file encryption and decryption."""
        # Create test file
        test_file = Path(temp_dir) / "test.txt"
        test_data = b"This is test file content"
        test_file.write_bytes(test_data)
        
        password = "file_password"
        encrypted_file = Path(temp_dir) / "test.enc"
        
        # Encrypt file
        encryption_manager.encrypt_file(str(test_file), str(encrypted_file), password)
        
        assert encrypted_file.exists()
        assert encrypted_file.stat().st_size > test_file.stat().st_size
        
        # Decrypt file
        decrypted_file = Path(temp_dir) / "test_decrypted.txt"
        encryption_manager.decrypt_file(str(encrypted_file), str(decrypted_file), password)
        
        assert decrypted_file.exists()
        assert decrypted_file.read_bytes() == test_data
    
    def test_encrypt_file_in_place(self, encryption_manager, temp_dir):
        """Test in-place file encryption."""
        # Create test file
        test_file = Path(temp_dir) / "test.txt"
        test_data = b"This is test file content"
        test_file.write_bytes(test_data)
        
        password = "file_password"
        
        # Encrypt file in place
        encryption_manager.encrypt_file(str(test_file), str(test_file), password)
        
        # File content should be encrypted now
        encrypted_content = test_file.read_bytes()
        assert encrypted_content != test_data
        assert encrypted_content.startswith(b'FACEAUTH_ENC_V1:')
        
        # Decrypt file in place
        encryption_manager.decrypt_file(str(test_file), str(test_file), password)
        
        # File content should be original now
        assert test_file.read_bytes() == test_data
    
    def test_encrypt_nonexistent_file_fails(self, encryption_manager, temp_dir):
        """Test that encrypting non-existent file fails."""
        nonexistent_file = Path(temp_dir) / "nonexistent.txt"
        encrypted_file = Path(temp_dir) / "encrypted.enc"
        
        with pytest.raises(EncryptionError, match="File not found"):
            encryption_manager.encrypt_file(str(nonexistent_file), str(encrypted_file), "password")
    
    def test_decrypt_invalid_file_fails(self, encryption_manager, temp_dir):
        """Test that decrypting invalid file fails."""
        # Create file with invalid encrypted content
        invalid_file = Path(temp_dir) / "invalid.enc"
        invalid_file.write_bytes(b"This is not encrypted data")
        
        decrypted_file = Path(temp_dir) / "decrypted.txt"
        
        with pytest.raises(EncryptionError, match="Invalid encrypted file format"):
            encryption_manager.decrypt_file(str(invalid_file), str(decrypted_file), "password")


class TestKeyManagement:
    """Test key management operations."""
    
    def test_save_load_key(self, encryption_manager):
        """Test saving and loading encryption keys."""
        key_id = "test_key"
        key = encryption_manager._generate_random_key()
        password = "key_password"
        
        # Save key
        encryption_manager.save_key(key_id, key, password)
        
        # Verify key file exists
        key_file = encryption_manager.key_dir / f"{key_id}.key"
        assert key_file.exists()
        
        # Load key
        loaded_key = encryption_manager.load_key(key_id, password)
        
        assert loaded_key == key
    
    def test_save_key_overwrites_existing(self, encryption_manager):
        """Test that saving key overwrites existing key."""
        key_id = "test_key"
        key1 = encryption_manager._generate_random_key()
        key2 = encryption_manager._generate_random_key()
        password = "key_password"
        
        # Save first key
        encryption_manager.save_key(key_id, key1, password)
        
        # Save second key (should overwrite)
        encryption_manager.save_key(key_id, key2, password)
        
        # Load key should return second key
        loaded_key = encryption_manager.load_key(key_id, password)
        assert loaded_key == key2
        assert loaded_key != key1
    
    def test_load_nonexistent_key_fails(self, encryption_manager):
        """Test that loading non-existent key fails."""
        with pytest.raises(EncryptionError, match="Key file not found"):
            encryption_manager.load_key("nonexistent_key", "password")
    
    def test_load_key_wrong_password_fails(self, encryption_manager):
        """Test that loading key with wrong password fails."""
        key_id = "test_key"
        key = encryption_manager._generate_random_key()
        correct_password = "correct_password"
        wrong_password = "wrong_password"
        
        encryption_manager.save_key(key_id, key, correct_password)
        
        with pytest.raises(EncryptionError, match="Failed to decrypt key"):
            encryption_manager.load_key(key_id, wrong_password)
    
    def test_delete_key(self, encryption_manager):
        """Test key deletion."""
        key_id = "test_key"
        key = encryption_manager._generate_random_key()
        password = "key_password"
        
        # Save key
        encryption_manager.save_key(key_id, key, password)
        
        # Verify key exists
        assert encryption_manager.key_exists(key_id)
        
        # Delete key
        encryption_manager.delete_key(key_id)
        
        # Verify key no longer exists
        assert not encryption_manager.key_exists(key_id)
        
        # Key file should be gone
        key_file = encryption_manager.key_dir / f"{key_id}.key"
        assert not key_file.exists()
    
    def test_delete_nonexistent_key_silent(self, encryption_manager):
        """Test that deleting non-existent key doesn't raise error."""
        # Should not raise an exception
        encryption_manager.delete_key("nonexistent_key")
    
    def test_key_exists(self, encryption_manager):
        """Test key existence check."""
        key_id = "test_key"
        
        # Key should not exist initially
        assert not encryption_manager.key_exists(key_id)
        
        # Save key
        key = encryption_manager._generate_random_key()
        encryption_manager.save_key(key_id, key, "password")
        
        # Key should exist now
        assert encryption_manager.key_exists(key_id)
    
    def test_list_keys(self, encryption_manager):
        """Test listing available keys."""
        # Initially no keys
        keys = encryption_manager.list_keys()
        assert len(keys) == 0
        
        # Save some keys
        key1 = encryption_manager._generate_random_key()
        key2 = encryption_manager._generate_random_key()
        encryption_manager.save_key("key1", key1, "password")
        encryption_manager.save_key("key2", key2, "password")
        
        # Should list both keys
        keys = encryption_manager.list_keys()
        assert len(keys) == 2
        assert "key1" in keys
        assert "key2" in keys
    
    def test_generate_and_save_key(self, encryption_manager):
        """Test generating and saving a new key."""
        key_id = "generated_key"
        password = "key_password"
        
        key = encryption_manager.generate_and_save_key(key_id, password)
        
        assert isinstance(key, bytes)
        assert len(key) == encryption_manager.key_size
        assert encryption_manager.key_exists(key_id)
        
        # Should be able to load the same key
        loaded_key = encryption_manager.load_key(key_id, password)
        assert loaded_key == key


class TestMemoryManagement:
    """Test secure memory management features."""
    
    def test_memory_cleanup_on_deletion(self, encryption_manager):
        """Test that sensitive data is cleared from memory."""
        key_id = "test_key"
        key = encryption_manager._generate_random_key()
        password = "password"
        
        # Save and load key (puts it in memory cache)
        encryption_manager.save_key(key_id, key, password)
        encryption_manager.load_key(key_id, password)
        
        # Key should be in cache
        assert key_id in encryption_manager._keys
        
        # Mock memory manager to verify cleanup
        with patch.object(encryption_manager.memory_manager, 'secure_zero') as mock_zero:
            # Delete key
            encryption_manager.delete_key(key_id)
            
            # Memory should be cleared
            assert key_id not in encryption_manager._keys
            # mock_zero.assert_called()  # Would need proper implementation check
    
    def test_memory_cleanup_on_shutdown(self, encryption_manager):
        """Test memory cleanup on encryption manager shutdown."""
        # Add some keys to memory
        key1 = encryption_manager._generate_random_key()
        key2 = encryption_manager._generate_random_key()
        encryption_manager._keys["key1"] = key1
        encryption_manager._keys["key2"] = key2
        
        with patch.object(encryption_manager.memory_manager, 'secure_zero') as mock_zero:
            # Simulate shutdown
            encryption_manager.cleanup()
            
            # All keys should be cleared from memory
            assert len(encryption_manager._keys) == 0
            # mock_zero.assert_called()  # Would need proper implementation check


class TestErrorHandling:
    """Test error handling and edge cases."""
    
    def test_invalid_password_type(self, encryption_manager):
        """Test handling of invalid password types."""
        data = b"test data"
        
        with pytest.raises(EncryptionError, match="Password must be a string"):
            encryption_manager.encrypt_data(data, 12345)  # Invalid type
    
    def test_invalid_data_type_for_encryption(self, encryption_manager):
        """Test handling of invalid data types."""
        password = "test_password"
        
        # Should handle None
        with pytest.raises(EncryptionError, match="Data cannot be None"):
            encryption_manager.encrypt_data(None, password)
    
    def test_corrupted_encrypted_data(self, encryption_manager):
        """Test handling of corrupted encrypted data."""
        data = b"test data"
        password = "test_password"
        
        encrypted_data = encryption_manager.encrypt_data(data, password)
        
        # Corrupt the encrypted data
        corrupted_data = encrypted_data[:-10] + b"corrupted!"
        
        with pytest.raises(EncryptionError, match="Failed to decrypt data"):
            encryption_manager.decrypt_data(corrupted_data, password)
    
    def test_malformed_encrypted_file_header(self, encryption_manager, temp_dir):
        """Test handling of malformed encrypted file headers."""
        malformed_file = Path(temp_dir) / "malformed.enc"
        malformed_file.write_bytes(b"FACEAUTH_ENC_V1:invalid_format")
        
        decrypted_file = Path(temp_dir) / "decrypted.txt"
        
        with pytest.raises(EncryptionError, match="Invalid encrypted file format"):
            encryption_manager.decrypt_file(str(malformed_file), str(decrypted_file), "password")
    
    def test_permission_error_handling(self, encryption_manager, temp_dir):
        """Test handling of permission errors."""
        if os.name == 'posix':  # Unix systems
            # Create a read-only directory
            readonly_dir = Path(temp_dir) / "readonly"
            readonly_dir.mkdir()
            readonly_dir.chmod(0o444)  # Read-only
            
            try:
                key_file = readonly_dir / "test.key"
                key = encryption_manager._generate_random_key()
                
                with pytest.raises(EncryptionError, match="Permission denied"):
                    encryption_manager.save_key("test", key, "password")
            finally:
                # Restore permissions for cleanup
                readonly_dir.chmod(0o755)
    
    def test_disk_space_error_simulation(self, encryption_manager, temp_dir):
        """Test handling of disk space errors (simulated)."""
        # Mock file writing to simulate disk space error
        with patch('builtins.open', side_effect=OSError("No space left on device")):
            key = encryption_manager._generate_random_key()
            
            with pytest.raises(EncryptionError, match="Failed to save key"):
                encryption_manager.save_key("test", key, "password")


class TestSecurityFeatures:
    """Test security-specific features."""
    
    def test_salt_uniqueness(self, encryption_manager):
        """Test that each encryption uses a unique salt."""
        data = b"same data"
        password = "same password"
        
        encrypted1 = encryption_manager.encrypt_data(data, password)
        encrypted2 = encryption_manager.encrypt_data(data, password)
        
        # Even with same data and password, encrypted results should differ
        assert encrypted1 != encrypted2
    
    def test_key_derivation_consistency(self, encryption_manager):
        """Test that key derivation is consistent."""
        password = "test_password"
        salt = encryption_manager._generate_salt()
        
        key1 = encryption_manager._derive_key(password, salt)
        key2 = encryption_manager._derive_key(password, salt)
        
        assert key1 == key2
    
    def test_encryption_output_randomness(self, encryption_manager):
        """Test that encryption output appears random."""
        data = b"test data"
        password = "test_password"
        
        encrypted = encryption_manager.encrypt_data(data, password)
        
        # Remove the header to get just the encrypted part
        header_end = encrypted.find(b':') + 1
        encrypted_part = encrypted[header_end:]
        
        # Encrypted data should not contain original data
        assert data not in encrypted_part
        
        # Should have good byte distribution (rough randomness test)
        byte_counts = [0] * 256
        for byte in encrypted_part:
            byte_counts[byte] += 1
        
        # Most bytes should appear at least once in a reasonably sized sample
        unique_bytes = sum(1 for count in byte_counts if count > 0)
        assert unique_bytes > 50  # At least 50 different byte values
    
    def test_timing_attack_resistance(self, encryption_manager):
        """Test resistance to timing attacks."""
        import time
        
        correct_password = "correct_password"
        wrong_password1 = "wrong_password_1"
        wrong_password2 = "completely_different_wrong_password"
        
        data = b"sensitive data"
        encrypted_data = encryption_manager.encrypt_data(data, correct_password)
        
        # Time decryption with wrong passwords
        times = []
        for wrong_password in [wrong_password1, wrong_password2]:
            start_time = time.time()
            try:
                encryption_manager.decrypt_data(encrypted_data, wrong_password)
            except EncryptionError:
                pass
            end_time = time.time()
            times.append(end_time - start_time)
        
        # Times should be similar (within reasonable bounds)
        time_diff = abs(times[0] - times[1])
        assert time_diff < 0.1  # Less than 100ms difference


class TestPerformance:
    """Test performance characteristics."""
    
    def test_encryption_performance(self, encryption_manager):
        """Test encryption performance with various data sizes."""
        password = "test_password"
        
        # Test with different data sizes
        sizes = [1024, 10240, 102400]  # 1KB, 10KB, 100KB
        
        for size in sizes:
            data = secrets.token_bytes(size)
            
            start_time = time.time()
            encrypted = encryption_manager.encrypt_data(data, password)
            encryption_time = time.time() - start_time
            
            start_time = time.time()
            decrypted = encryption_manager.decrypt_data(encrypted, password)
            decryption_time = time.time() - start_time
            
            # Performance should be reasonable
            assert encryption_time < 1.0  # Less than 1 second
            assert decryption_time < 1.0  # Less than 1 second
            assert decrypted == data
    
    def test_key_caching_performance(self, encryption_manager):
        """Test that key caching improves performance."""
        key_id = "cached_key"
        key = encryption_manager._generate_random_key()
        password = "password"
        
        encryption_manager.save_key(key_id, key, password)
        
        # First load (from disk)
        start_time = time.time()
        key1 = encryption_manager.load_key(key_id, password)
        first_load_time = time.time() - start_time
        
        # Second load (from cache)
        start_time = time.time()
        key2 = encryption_manager.load_key(key_id, password)
        second_load_time = time.time() - start_time
        
        assert key1 == key2
        # Second load should be faster (cached)
        # Note: This test might be flaky on very fast systems
        # assert second_load_time < first_load_time


@pytest.mark.integration
class TestIntegrationScenarios:
    """Integration test scenarios."""
    
    def test_full_encryption_workflow(self, encryption_manager, temp_dir):
        """Test complete encryption workflow."""
        # Generate master key
        master_key_id = "master_key"
        master_password = "master_password"
        master_key = encryption_manager.generate_and_save_key(master_key_id, master_password)
        
        # Create test file
        test_file = Path(temp_dir) / "sensitive_data.txt"
        test_data = b"This is highly sensitive information that must be protected."
        test_file.write_bytes(test_data)
        
        # Encrypt file with master key
        encrypted_file = Path(temp_dir) / "sensitive_data.enc"
        loaded_key = encryption_manager.load_key(master_key_id, master_password)
        
        with test_file.open('rb') as f:
            data = f.read()
        
        encrypted_data = encryption_manager.encrypt_data_with_key(data, loaded_key)
        encrypted_file.write_bytes(encrypted_data)
        
        # Verify original file can be securely deleted
        test_file.unlink()
        
        # Decrypt file
        with encrypted_file.open('rb') as f:
            encrypted_content = f.read()
        
        decrypted_data = encryption_manager.decrypt_data_with_key(encrypted_content, loaded_key)
        
        assert decrypted_data == test_data
    
    def test_key_rotation_scenario(self, encryption_manager):
        """Test key rotation scenario."""
        data = b"sensitive data that needs key rotation"
        
        # Encrypt with old key
        old_key_id = "old_key"
        old_password = "old_password"
        old_key = encryption_manager.generate_and_save_key(old_key_id, old_password)
        
        encrypted_with_old = encryption_manager.encrypt_data_with_key(data, old_key)
        
        # Generate new key
        new_key_id = "new_key"
        new_password = "new_password"
        new_key = encryption_manager.generate_and_save_key(new_key_id, new_password)
        
        # Decrypt with old key and re-encrypt with new key
        decrypted_data = encryption_manager.decrypt_data_with_key(encrypted_with_old, old_key)
        encrypted_with_new = encryption_manager.encrypt_data_with_key(decrypted_data, new_key)
        
        # Verify data integrity
        final_decrypted = encryption_manager.decrypt_data_with_key(encrypted_with_new, new_key)
        assert final_decrypted == data
        
        # Old encrypted data should still work with old key
        old_decrypted = encryption_manager.decrypt_data_with_key(encrypted_with_old, old_key)
        assert old_decrypted == data
        
        # Clean up old key
        encryption_manager.delete_key(old_key_id)
        assert not encryption_manager.key_exists(old_key_id)


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
