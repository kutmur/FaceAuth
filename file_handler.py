"""
File Encryption Module for FaceAuth
===================================

This module provides secure file encryption and decryption functionality using
a key wrapping approach. Files are encrypted with a random AES-256 key, which
is then encrypted using a password-derived key, ensuring maximum security.

Security Architecture:
- File content encrypted with random AES-256-GCM key (File Key)
- File Key encrypted with password-derived key using PBKDF2
- Each file gets a unique random File Key
- Original File Key never stored in plaintext
- Compatible with existing crypto.py security patterns

File Format (.faceauth):
- Bytes 0-16: Salt for password derivation (16 bytes)
- Bytes 16-28: Nonce for File Key encryption (12 bytes)
- Bytes 28-44: Encrypted File Key (16 bytes)
- Bytes 44-60: Authentication tag for File Key (16 bytes)
- Bytes 60-72: Nonce for file content encryption (12 bytes)
- Bytes 72+: Encrypted file content + authentication tag
"""

import os
import struct
from pathlib import Path
from typing import bytes, Tuple
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

from crypto import CryptoError


class FileEncryptionError(Exception):
    """Custom exception for file encryption errors"""
    pass


def generate_file_key() -> bytes:
    """
    Generate a random 256-bit key for file encryption.
    
    Returns:
        32-byte random key
    """
    return os.urandom(32)


def derive_key_from_password(password: str, salt: bytes = None) -> Tuple[bytes, bytes]:
    """
    Derive a cryptographic key from password using PBKDF2.
    Uses same parameters as crypto.py for consistency.
    
    Args:
        password: User password
        salt: Optional salt (generates random if not provided)
        
    Returns:
        Tuple of (key, salt)
    """
    if salt is None:
        salt = os.urandom(16)  # 128-bit salt
    
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,  # 256-bit key
        salt=salt,
        iterations=100000,  # Same as crypto.py
        backend=default_backend()
    )
    
    key = kdf.derive(password.encode('utf-8'))
    return key, salt


def encrypt_file_key(file_key: bytes, password_key: bytes) -> bytes:
    """
    Encrypt the file key using the password-derived key.
    
    Args:
        file_key: The file encryption key to protect
        password_key: Key derived from user password
        
    Returns:
        nonce + encrypted_file_key + auth_tag
    """
    try:
        # Generate random nonce
        nonce = os.urandom(12)
        
        # Create cipher
        cipher = Cipher(
            algorithms.AES(password_key),
            modes.GCM(nonce),
            backend=default_backend()
        )
        encryptor = cipher.encryptor()
        
        # Encrypt the file key
        ciphertext = encryptor.update(file_key) + encryptor.finalize()
        
        # Return nonce + ciphertext + tag
        return nonce + ciphertext + encryptor.tag
        
    except Exception as e:
        raise FileEncryptionError(f"File key encryption failed: {str(e)}")


def decrypt_file_key(encrypted_file_key_data: bytes, password_key: bytes) -> bytes:
    """
    Decrypt the file key using the password-derived key.
    
    Args:
        encrypted_file_key_data: nonce + encrypted_file_key + auth_tag
        password_key: Key derived from user password
        
    Returns:
        Decrypted file key
    """
    try:
        # Extract components
        nonce = encrypted_file_key_data[:12]
        tag = encrypted_file_key_data[-16:]
        ciphertext = encrypted_file_key_data[12:-16]
        
        # Create cipher
        cipher = Cipher(
            algorithms.AES(password_key),
            modes.GCM(nonce, tag),
            backend=default_backend()
        )
        decryptor = cipher.decryptor()
        
        # Decrypt the file key
        file_key = decryptor.update(ciphertext) + decryptor.finalize()
        
        return file_key
        
    except Exception as e:
        raise FileEncryptionError(f"File key decryption failed: {str(e)}")


def encrypt_file_content(file_data: bytes, file_key: bytes) -> bytes:
    """
    Encrypt file content using AES-GCM.
    
    Args:
        file_data: Raw file content
        file_key: Encryption key for the file
        
    Returns:
        nonce + encrypted_content + auth_tag
    """
    try:
        # Generate random nonce
        nonce = os.urandom(12)
        
        # Create cipher
        cipher = Cipher(
            algorithms.AES(file_key),
            modes.GCM(nonce),
            backend=default_backend()
        )
        encryptor = cipher.encryptor()
        
        # Encrypt the content
        ciphertext = encryptor.update(file_data) + encryptor.finalize()
        
        # Return nonce + ciphertext + tag
        return nonce + ciphertext + encryptor.tag
        
    except Exception as e:
        raise FileEncryptionError(f"File content encryption failed: {str(e)}")


def decrypt_file_content(encrypted_content_data: bytes, file_key: bytes) -> bytes:
    """
    Decrypt file content using AES-GCM.
    
    Args:
        encrypted_content_data: nonce + encrypted_content + auth_tag
        file_key: Decryption key for the file
        
    Returns:
        Decrypted file content
    """
    try:
        # Extract components
        nonce = encrypted_content_data[:12]
        tag = encrypted_content_data[-16:]
        ciphertext = encrypted_content_data[12:-16]
        
        # Create cipher
        cipher = Cipher(
            algorithms.AES(file_key),
            modes.GCM(nonce, tag),
            backend=default_backend()
        )
        decryptor = cipher.decryptor()
        
        # Decrypt the content
        file_data = decryptor.update(ciphertext) + decryptor.finalize()
        
        return file_data
        
    except Exception as e:
        raise FileEncryptionError(f"File content decryption failed: {str(e)}")


def encrypt_file(file_path: str, password: str) -> str:
    """
    Encrypt a file using the secure key wrapping approach.
    
    Security Model:
    1. Generate random File Key for AES-256-GCM encryption
    2. Encrypt file content with File Key
    3. Derive password key using PBKDF2 with random salt
    4. Encrypt File Key with password key
    5. Package everything into .faceauth file
    
    Args:
        file_path: Path to the file to encrypt
        password: User password for key protection
        
    Returns:
        Path to the created encrypted file
        
    Raises:
        FileEncryptionError: If encryption fails
    """
    try:
        # Validate input file
        input_path = Path(file_path)
        if not input_path.exists():
            raise FileEncryptionError(f"File not found: {file_path}")
        
        if not input_path.is_file():
            raise FileEncryptionError(f"Path is not a file: {file_path}")
        
        # Read file content
        try:
            with open(input_path, 'rb') as f:
                file_data = f.read()
        except Exception as e:
            raise FileEncryptionError(f"Cannot read file: {str(e)}")
        
        if len(file_data) == 0:
            raise FileEncryptionError("Cannot encrypt empty file")
        
        # Step 1: Generate random File Key
        file_key = generate_file_key()
        
        # Step 2: Encrypt file content with File Key
        encrypted_content = encrypt_file_content(file_data, file_key)
        
        # Step 3: Derive password key
        password_key, salt = derive_key_from_password(password)
        
        # Step 4: Encrypt File Key with password key
        encrypted_file_key = encrypt_file_key(file_key, password_key)
        
        # Step 5: Package everything into .faceauth file format
        # Format: salt (16) + encrypted_file_key (28) + encrypted_content (variable)
        output_data = salt + encrypted_file_key + encrypted_content
        
        # Write to output file
        output_path = input_path.with_suffix(input_path.suffix + '.faceauth')
        try:
            with open(output_path, 'wb') as f:
                f.write(output_data)
        except Exception as e:
            raise FileEncryptionError(f"Cannot write encrypted file: {str(e)}")
        
        # Securely clear sensitive data from memory (best effort)
        file_key = os.urandom(32)  # Overwrite with random data
        password_key = os.urandom(32)  # Overwrite with random data
        
        return str(output_path)
        
    except FileEncryptionError:
        raise
    except Exception as e:
        raise FileEncryptionError(f"Unexpected encryption error: {str(e)}")


def decrypt_file(encrypted_file_path: str, password: str, output_path: str = None) -> str:
    """
    Decrypt a file encrypted with encrypt_file().
    
    Args:
        encrypted_file_path: Path to the .faceauth encrypted file
        password: User password for key derivation
        output_path: Optional output path (defaults to removing .faceauth extension)
        
    Returns:
        Path to the decrypted file
        
    Raises:
        FileEncryptionError: If decryption fails
    """
    try:
        # Validate input file
        input_path = Path(encrypted_file_path)
        if not input_path.exists():
            raise FileEncryptionError(f"Encrypted file not found: {encrypted_file_path}")
        
        if not input_path.is_file():
            raise FileEncryptionError(f"Path is not a file: {encrypted_file_path}")
        
        # Read encrypted file
        try:
            with open(input_path, 'rb') as f:
                encrypted_data = f.read()
        except Exception as e:
            raise FileEncryptionError(f"Cannot read encrypted file: {str(e)}")
        
        # Validate minimum file size
        min_size = 16 + 28 + 12 + 16  # salt + encrypted_file_key + content_nonce + content_tag
        if len(encrypted_data) < min_size:
            raise FileEncryptionError("Invalid encrypted file format (too small)")
        
        # Extract components
        salt = encrypted_data[:16]
        encrypted_file_key = encrypted_data[16:44]  # 12 + 16 + 16 = 44
        encrypted_content = encrypted_data[44:]
        
        # Derive password key using stored salt
        password_key, _ = derive_key_from_password(password, salt)
        
        # Decrypt File Key
        file_key = decrypt_file_key(encrypted_file_key, password_key)
        
        # Decrypt file content
        file_data = decrypt_file_content(encrypted_content, file_key)
        
        # Determine output path
        if output_path is None:
            if input_path.suffix == '.faceauth':
                output_path = input_path.with_suffix('')
            else:
                output_path = input_path.with_suffix('.decrypted')
        
        output_path = Path(output_path)
        
        # Write decrypted content
        try:
            with open(output_path, 'wb') as f:
                f.write(file_data)
        except Exception as e:
            raise FileEncryptionError(f"Cannot write decrypted file: {str(e)}")
        
        # Securely clear sensitive data from memory (best effort)
        file_key = os.urandom(32)  # Overwrite with random data
        password_key = os.urandom(32)  # Overwrite with random data
        
        return str(output_path)
        
    except FileEncryptionError:
        raise
    except Exception as e:
        raise FileEncryptionError(f"Unexpected decryption error: {str(e)}")


def get_encrypted_file_info(encrypted_file_path: str) -> dict:
    """
    Get information about an encrypted file without decrypting it.
    
    Args:
        encrypted_file_path: Path to the .faceauth file
        
    Returns:
        Dictionary with file information
    """
    try:
        input_path = Path(encrypted_file_path)
        if not input_path.exists():
            raise FileEncryptionError(f"File not found: {encrypted_file_path}")
        
        file_size = input_path.stat().st_size
        min_size = 16 + 28 + 12 + 16  # Minimum expected size
        
        return {
            'file_path': str(input_path),
            'file_size': file_size,
            'encrypted_content_size': file_size - 44,  # Subtract headers
            'is_valid_format': file_size >= min_size,
            'created': input_path.stat().st_ctime,
            'modified': input_path.stat().st_mtime
        }
        
    except Exception as e:
        raise FileEncryptionError(f"Cannot get file info: {str(e)}")


# Utility function for testing and validation
def validate_encryption_integrity(file_path: str, password: str) -> bool:
    """
    Test encrypt/decrypt round-trip to validate implementation.
    This is useful for testing but should not be used in production.
    
    Args:
        file_path: Path to test file
        password: Test password
        
    Returns:
        True if round-trip successful
    """
    try:
        # Read original content
        with open(file_path, 'rb') as f:
            original_data = f.read()
        
        # Encrypt
        encrypted_path = encrypt_file(file_path, password)
        
        # Decrypt
        decrypted_path = decrypt_file(encrypted_path, password)
        
        # Read decrypted content
        with open(decrypted_path, 'rb') as f:
            decrypted_data = f.read()
        
        # Compare
        integrity_check = original_data == decrypted_data
        
        # Cleanup test files
        os.remove(encrypted_path)
        os.remove(decrypted_path)
        
        return integrity_check
        
    except Exception:
        return False
