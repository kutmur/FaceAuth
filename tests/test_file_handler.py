"""
Unit Tests for File Handler Module
==================================

Tests for file encryption/decryption functionality in file_handler.py, focusing on:
- File encryption/decryption round-trip tests
- Error handling for wrong passwords and corrupted files
- File format validation and security
- Integration with crypto module
"""

import pytest
import os
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, mock_open, MagicMock

# Import the modules under test
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from file_handler import (
    generate_file_key,
    derive_key_from_password,
    encrypt_file_key,
    decrypt_file_key,
    encrypt_file,
    decrypt_file,
    get_encrypted_file_info,
    validate_encryption_integrity,
    FileEncryptionError
)


class TestFileEncryptionBasics:
    """Test basic file encryption operations."""
    
    def test_file_key_generation(self):
        """Test generation of random file keys."""
        key1 = generate_file_key()
        key2 = generate_file_key()
        
        # Keys should be 32 bytes (256 bits)
        assert len(key1) == 32
        assert len(key2) == 32
        assert isinstance(key1, bytes)
        assert isinstance(key2, bytes)
        
        # Keys should be different
        assert key1 != key2
    
    def test_password_key_derivation(self):
        """Test key derivation from password."""
        password = "test_password_123"
        
        # Test with random salt
        key1, salt1 = derive_key_from_password(password)
        key2, salt2 = derive_key_from_password(password)
        
        # Keys should be 32 bytes
        assert len(key1) == 32
        assert len(salt1) == 16
        
        # Different salts should produce different keys
        assert salt1 != salt2
        assert key1 != key2
        
        # Same password and salt should produce same key
        key3, _ = derive_key_from_password(password, salt1)
        assert key1 == key3
    
    def test_file_key_encryption_decryption(self):
        """Test file key encryption/decryption with password-derived key."""
        file_key = generate_file_key()
        password_key = os.urandom(32)
        
        # Encrypt file key
        encrypted_file_key_data = encrypt_file_key(file_key, password_key)
        
        # Verify structure
        assert len(encrypted_file_key_data) == 12 + 32 + 16  # nonce + ciphertext + tag
        
        # Decrypt file key
        decrypted_file_key = decrypt_file_key(encrypted_file_key_data, password_key)
        
        # Verify decrypted key matches original
        assert decrypted_file_key == file_key


class TestFileEncryptionRoundTrip:
    """Test complete file encryption/decryption workflows."""
    
    def setup_method(self):
        """Set up test environment with temporary directory."""
        self.test_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.test_dir, "test_file.txt")
        self.encrypted_file = self.test_file + ".faceauth"
        self.password = "secure_password_123"
        
        # Create test file content
        self.test_content = b"This is secret test content that should be encrypted safely!"
        with open(self.test_file, 'wb') as f:
            f.write(self.test_content)
    
    def teardown_method(self):
        """Clean up test environment."""
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_encrypt_decrypt_file_roundtrip(self):
        """Test complete file encryption and decryption process."""
        # Encrypt the file
        encrypted_file_path = encrypt_file(self.test_file, self.password)
        
        # Verify encryption result
        assert os.path.exists(encrypted_file_path)
        assert encrypted_file_path.endswith('.faceauth')
        
        # Verify original file still exists
        assert os.path.exists(self.test_file)
        
        # Decrypt the file
        decrypted_file = os.path.join(self.test_dir, "decrypted_file.txt")
        decrypted_file_path = decrypt_file(encrypted_file_path, self.password, decrypted_file)
        
        # Verify decryption result
        assert os.path.exists(decrypted_file_path)
        
        # Verify content matches original
        with open(decrypted_file_path, 'rb') as f:
            decrypted_content = f.read()
        
        assert decrypted_content == self.test_content
    
    def test_decrypt_with_wrong_password(self):
        """Test decryption failure with wrong password."""
        # Encrypt the file
        encrypted_file_path = encrypt_file(self.test_file, self.password)
        assert os.path.exists(encrypted_file_path)
        
        # Try to decrypt with wrong password
        decrypted_file = os.path.join(self.test_dir, "decrypted_file.txt")
        
        with pytest.raises(FileEncryptionError, match="Failed to decrypt file key"):
            decrypt_file(encrypted_file_path, "wrong_password", decrypted_file)
        
        # Verify decrypted file was not created
        assert not os.path.exists(decrypted_file)
    
    def test_encrypt_nonexistent_file(self):
        """Test encryption of non-existent file."""
        nonexistent_file = os.path.join(self.test_dir, "nonexistent.txt")
        
        with pytest.raises(FileEncryptionError, match="File not found"):
            encrypt_file(nonexistent_file, self.password)
    
    def test_decrypt_nonexistent_file(self):
        """Test decryption of non-existent encrypted file."""
        nonexistent_file = os.path.join(self.test_dir, "nonexistent.faceauth")
        output_file = os.path.join(self.test_dir, "output.txt")
        
        with pytest.raises(FileEncryptionError, match="Encrypted file not found"):
            decrypt_file(nonexistent_file, self.password, output_file)
    
    def test_encrypt_empty_file(self):
        """Test encryption of empty file."""
        empty_file = os.path.join(self.test_dir, "empty.txt")
        with open(empty_file, 'wb') as f:
            f.write(b"")
        
        # Encrypt empty file
        encrypted_file_path = encrypt_file(empty_file, self.password)
        assert os.path.exists(encrypted_file_path)
        
        # Decrypt empty file
        decrypted_file = os.path.join(self.test_dir, "decrypted_empty.txt")
        decrypted_file_path = decrypt_file(encrypted_file_path, self.password, decrypted_file)
        
        assert os.path.exists(decrypted_file_path)
        
        # Verify content is empty
        with open(decrypted_file_path, 'rb') as f:
            content = f.read()
        assert content == b""
    
    def test_large_file_encryption(self):
        """Test encryption of larger file."""
        # Create a larger test file (1MB)
        large_file = os.path.join(self.test_dir, "large_file.txt")
        large_content = b"X" * (1024 * 1024)  # 1MB of X's
        
        with open(large_file, 'wb') as f:
            f.write(large_content)
        
        # Encrypt large file
        encrypted_file_path = encrypt_file(large_file, self.password)
        assert os.path.exists(encrypted_file_path)
        
        # Decrypt large file
        decrypted_file = os.path.join(self.test_dir, "decrypted_large.txt")
        decrypted_file_path = decrypt_file(encrypted_file_path, self.password, decrypted_file)
        
        assert os.path.exists(decrypted_file_path)
        
        # Verify content matches
        with open(decrypted_file_path, 'rb') as f:
            decrypted_content = f.read()
        
        assert decrypted_content == large_content


class TestFileCorruption:
    """Test handling of corrupted encrypted files."""
    
    def setup_method(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.test_dir, "test.txt")
        self.password = "test_password"
        
        # Create test file
        with open(self.test_file, 'wb') as f:
            f.write(b"Test content for corruption testing")
    
    def teardown_method(self):
        """Clean up test environment."""
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_corrupted_file_header(self):
        """Test handling of corrupted file header."""
        # Encrypt file first
        encrypted_file_path = encrypt_file(self.test_file, self.password)
        
        # Corrupt the header
        with open(encrypted_file_path, 'r+b') as f:
            f.seek(0)
            f.write(b"CORRUPTED_HEADER")
        
        # Try to decrypt
        output_file = os.path.join(self.test_dir, "output.txt")
        
        with pytest.raises(FileEncryptionError, match="Failed to decrypt file key"):
            decrypt_file(encrypted_file_path, self.password, output_file)
    
    def test_truncated_encrypted_file(self):
        """Test handling of truncated encrypted file."""
        # Encrypt file first
        encrypted_file_path = encrypt_file(self.test_file, self.password)
        
        # Truncate the file
        with open(encrypted_file_path, 'r+b') as f:
            f.truncate(50)  # Cut to 50 bytes
        
        # Try to decrypt
        output_file = os.path.join(self.test_dir, "output.txt")
        
        with pytest.raises(FileEncryptionError, match="Invalid encrypted file format"):
            decrypt_file(encrypted_file_path, self.password, output_file)


class TestFilePermissions:
    """Test file permission handling."""
    
    def setup_method(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.test_dir, "test.txt")
        self.password = "test_password"
        
        # Create test file
        with open(self.test_file, 'wb') as f:
            f.write(b"Test content")
    
    def teardown_method(self):
        """Clean up test environment."""
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    @patch('builtins.open', side_effect=PermissionError("Permission denied"))
    def test_file_permission_error_encrypt(self, mock_open):
        """Test handling of permission errors during encryption."""
        with pytest.raises(FileEncryptionError, match="Cannot read source file"):
            encrypt_file(self.test_file, self.password)
    
    @patch('builtins.open', side_effect=PermissionError("Permission denied"))
    def test_file_permission_error_decrypt(self, mock_open):
        """Test handling of permission errors during decryption."""
        encrypted_file = self.test_file + ".faceauth"
        output_file = os.path.join(self.test_dir, "output.txt")
        
        with pytest.raises(FileEncryptionError, match="Cannot read encrypted file"):
            decrypt_file(encrypted_file, self.password, output_file)


class TestFilePathHandling:
    """Test various file path scenarios."""
    
    def setup_method(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.password = "test_password"
    
    def teardown_method(self):
        """Clean up test environment."""
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_file_with_spaces_in_name(self):
        """Test encryption/decryption of files with spaces in name."""
        test_file = os.path.join(self.test_dir, "file with spaces.txt")
        content = b"Content in file with spaces"
        
        with open(test_file, 'wb') as f:
            f.write(content)
        
        # Encrypt
        encrypted_file_path = encrypt_file(test_file, self.password)
        assert os.path.exists(encrypted_file_path)
        
        # Decrypt
        output_file = os.path.join(self.test_dir, "output with spaces.txt")
        decrypted_file_path = decrypt_file(encrypted_file_path, self.password, output_file)
        
        assert os.path.exists(decrypted_file_path)
        
        # Verify content
        with open(decrypted_file_path, 'rb') as f:
            decrypted_content = f.read()
        assert decrypted_content == content
    
    def test_file_with_unicode_name(self):
        """Test encryption/decryption of files with unicode characters."""
        test_file = os.path.join(self.test_dir, "файл_тест_🔐.txt")
        content = b"Unicode filename test content"
        
        with open(test_file, 'wb') as f:
            f.write(content)
        
        # Encrypt
        encrypted_file_path = encrypt_file(test_file, self.password)
        assert os.path.exists(encrypted_file_path)
        
        # Decrypt
        output_file = os.path.join(self.test_dir, "output_unicode.txt")
        decrypted_file_path = decrypt_file(encrypted_file_path, self.password, output_file)
        
        assert os.path.exists(decrypted_file_path)
        
        # Verify content
        with open(decrypted_file_path, 'rb') as f:
            decrypted_content = f.read()
        assert decrypted_content == content
    
    def test_get_encrypted_file_info(self):
        """Test getting info about encrypted files."""
        # Encrypt a file first
        encrypted_file_path = encrypt_file(self.test_file, self.password)
        
        # Get file info
        info = get_encrypted_file_info(encrypted_file_path)
        
        assert info['file_path'] == encrypted_file_path
        assert info['file_size'] > 0
        assert info['is_valid_format'] is True
        assert 'created' in info
        assert 'modified' in info
    
    def test_validate_encryption_integrity(self):
        """Test the integrity validation utility function."""
        # Should pass for valid file
        is_valid = validate_encryption_integrity(self.test_file, self.password)
        assert is_valid is True


if __name__ == "__main__":
    # Allow running tests directly
    pytest.main([__file__, "-v"])
