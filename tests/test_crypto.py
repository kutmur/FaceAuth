"""
Unit Tests for Crypto Module
============================

Tests for the cryptographic functions in crypto.py, focusing on:
- Encryption/decryption round-trip tests
- Error handling for wrong passwords
- Key derivation and security functions
- SecureEmbeddingStorage class functionality
"""

import pytest
import numpy as np
import os
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, mock_open

# Import the modules under test
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from crypto import (
    generate_key_from_password,
    encrypt_embedding,
    decrypt_embedding,
    encrypt_embedding_with_password,
    generate_user_hash,
    verify_embedding_integrity,
    SecureEmbeddingStorage,
    CryptoError
)


class TestCryptoBasics:
    """Test basic cryptographic operations."""
    
    def test_key_generation_from_password(self):
        """Test PBKDF2 key derivation from password."""
        password = "test_password_123"
        
        # Test with random salt
        key1, salt1 = generate_key_from_password(password)
        key2, salt2 = generate_key_from_password(password)
        
        # Keys should be 32 bytes (256 bits)
        assert len(key1) == 32
        assert len(key2) == 32
        
        # Different salts should produce different keys
        assert salt1 != salt2
        assert key1 != key2
        
        # Same password and salt should produce same key
        key3, _ = generate_key_from_password(password, salt1)
        assert key1 == key3
    
    def test_encrypt_decrypt_roundtrip(self):
        """Test that encryption followed by decryption returns original data."""
        # Create sample embedding (simulating DeepFace output)
        original_embedding = np.random.rand(512).astype(np.float32)
        password = "secure_password_456"
        
        # Encrypt the embedding
        encrypted_data = encrypt_embedding_with_password(original_embedding, password)
        
        # Verify encrypted data is different and non-empty
        assert len(encrypted_data) > 0
        assert isinstance(encrypted_data, bytes)
        
        # Decrypt the embedding
        decrypted_embedding = decrypt_embedding(encrypted_data, password)
        
        # Verify decrypted data matches original
        assert isinstance(decrypted_embedding, np.ndarray)
        assert decrypted_embedding.shape == original_embedding.shape
        assert np.allclose(original_embedding, decrypted_embedding, rtol=1e-6)
    
    def test_decryption_with_wrong_password(self):
        """Test that wrong password raises CryptoError."""
        original_embedding = np.random.rand(128).astype(np.float32)
        correct_password = "correct_password"
        wrong_password = "wrong_password"
        
        # Encrypt with correct password
        encrypted_data = encrypt_embedding_with_password(original_embedding, correct_password)
        
        # Try to decrypt with wrong password
        with pytest.raises(CryptoError, match="Decryption failed"):
            decrypt_embedding(encrypted_data, wrong_password)
    
    def test_user_hash_generation(self):
        """Test user ID hashing for filename generation."""
        user_id = "test_user_123"
        
        # Hash should be consistent
        hash1 = generate_user_hash(user_id)
        hash2 = generate_user_hash(user_id)
        assert hash1 == hash2
        
        # Different user IDs should produce different hashes
        different_hash = generate_user_hash("different_user")
        assert hash1 != different_hash
        
        # Hash should be valid hex string
        assert len(hash1) == 64  # SHA-256 produces 64 hex characters
        int(hash1, 16)  # Should not raise exception
    
    def test_embedding_integrity_verification(self):
        """Test embedding validation function."""
        # Valid embedding
        valid_embedding = np.random.rand(512).astype(np.float32)
        assert verify_embedding_integrity(valid_embedding) is True
        
        # Invalid cases
        assert verify_embedding_integrity("not_numpy_array") is False
        assert verify_embedding_integrity(np.array([1, 2, 3])) is False  # Too small
        assert verify_embedding_integrity(np.zeros(512)) is False  # All zeros
        assert verify_embedding_integrity(np.full(512, np.nan)) is False  # NaN values
        assert verify_embedding_integrity(np.full(512, np.inf)) is False  # Infinite values


class TestSecureEmbeddingStorage:
    """Test the SecureEmbeddingStorage class."""
    
    def setup_method(self):
        """Set up test environment with temporary directory."""
        self.test_dir = tempfile.mkdtemp()
        self.storage = SecureEmbeddingStorage(self.test_dir)
        self.test_embedding = np.random.rand(512).astype(np.float32)
        self.user_id = "test_user"
        self.password = "test_password"
    
    def teardown_method(self):
        """Clean up test environment."""
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_save_and_load_embedding(self):
        """Test saving and loading user embeddings."""
        # Save embedding
        filepath = self.storage.save_user_embedding(
            self.user_id, self.test_embedding, self.password
        )
        
        # Verify file was created
        assert os.path.exists(filepath)
        
        # Load embedding
        loaded_embedding = self.storage.load_user_embedding(self.user_id, self.password)
        
        # Verify loaded embedding matches original
        assert np.allclose(self.test_embedding, loaded_embedding, rtol=1e-6)
    
    def test_user_exists_check(self):
        """Test user existence checking."""
        # User should not exist initially
        assert not self.storage.user_exists(self.user_id)
        
        # Save embedding
        self.storage.save_user_embedding(self.user_id, self.test_embedding, self.password)
        
        # User should now exist
        assert self.storage.user_exists(self.user_id)
    
    def test_load_nonexistent_user(self):
        """Test loading embedding for user that doesn't exist."""
        with pytest.raises(CryptoError, match="No face data found"):
            self.storage.load_user_embedding("nonexistent_user", self.password)
    
    def test_load_with_wrong_password(self):
        """Test loading embedding with incorrect password."""
        # Save embedding
        self.storage.save_user_embedding(self.user_id, self.test_embedding, self.password)
        
        # Try to load with wrong password
        with pytest.raises(CryptoError, match="Decryption failed"):
            self.storage.load_user_embedding(self.user_id, "wrong_password")
    
    def test_save_invalid_embedding(self):
        """Test saving invalid embedding data."""
        invalid_embedding = np.zeros(512)  # All zeros - invalid
        
        with pytest.raises(CryptoError, match="Invalid embedding data"):
            self.storage.save_user_embedding(self.user_id, invalid_embedding, self.password)
    
    @patch('builtins.open', side_effect=PermissionError("Permission denied"))
    def test_file_permission_error(self, mock_open):
        """Test handling of file permission errors."""
        with pytest.raises(CryptoError):
            self.storage.save_user_embedding(self.user_id, self.test_embedding, self.password)


class TestCryptoErrorHandling:
    """Test error handling in crypto operations."""
    
    def test_corrupt_encrypted_data(self):
        """Test handling of corrupted encryption data."""
        embedding = np.random.rand(128).astype(np.float32)
        password = "test_password"
        
        # Encrypt normally
        encrypted_data = encrypt_embedding_with_password(embedding, password)
        
        # Corrupt the data
        corrupted_data = bytearray(encrypted_data)
        corrupted_data[50] = (corrupted_data[50] + 1) % 256  # Flip one bit
        
        # Decryption should fail
        with pytest.raises(CryptoError, match="Decryption failed"):
            decrypt_embedding(bytes(corrupted_data), password)
    
    def test_truncated_encrypted_data(self):
        """Test handling of truncated encryption data."""
        embedding = np.random.rand(128).astype(np.float32)
        password = "test_password"
        
        # Encrypt normally
        encrypted_data = encrypt_embedding_with_password(embedding, password)
        
        # Truncate the data
        truncated_data = encrypted_data[:len(encrypted_data)//2]
        
        # Decryption should fail
        with pytest.raises(CryptoError, match="Decryption failed"):
            decrypt_embedding(truncated_data, password)
    
    def test_empty_password(self):
        """Test handling of empty password."""
        embedding = np.random.rand(128).astype(np.float32)
        
        # Empty password should still work (though not recommended)
        encrypted_data = encrypt_embedding_with_password(embedding, "")
        decrypted_embedding = decrypt_embedding(encrypted_data, "")
        
        assert np.allclose(embedding, decrypted_embedding, rtol=1e-6)


class TestCryptoPerformance:
    """Test crypto operations performance and behavior."""
    
    def test_different_embedding_sizes(self):
        """Test encryption with different embedding sizes."""
        sizes = [128, 256, 512, 1024, 2048]
        password = "test_password"
        
        for size in sizes:
            embedding = np.random.rand(size).astype(np.float32)
            
            # Should work for all common embedding sizes
            encrypted_data = encrypt_embedding_with_password(embedding, password)
            decrypted_embedding = decrypt_embedding(encrypted_data, password)
            
            assert np.allclose(embedding, decrypted_embedding, rtol=1e-6)
    
    def test_multiple_users_same_password(self):
        """Test that same password produces different encrypted data for different users."""
        password = "shared_password"
        embedding = np.random.rand(512).astype(np.float32)
        
        # Encrypt same embedding with same password multiple times
        encrypted1 = encrypt_embedding_with_password(embedding, password)
        encrypted2 = encrypt_embedding_with_password(embedding, password)
        
        # Encrypted data should be different due to random salt and nonce
        assert encrypted1 != encrypted2
        
        # But both should decrypt to same embedding
        decrypted1 = decrypt_embedding(encrypted1, password)
        decrypted2 = decrypt_embedding(encrypted2, password)
        
        assert np.allclose(decrypted1, decrypted2, rtol=1e-6)
        assert np.allclose(embedding, decrypted1, rtol=1e-6)


if __name__ == "__main__":
    # Allow running tests directly
    pytest.main([__file__, "-v"])
