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
from typing import Tuple
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

from .crypto import CryptoError


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
        
    Raises:
        FileEncryptionError: If decryption fails (wrong password or corrupted data)
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
        # Check if it's an authentication failure (wrong password or corrupted file)
        if "authentication" in str(e).lower() or "tag" in str(e).lower():
            raise FileEncryptionError(
                "Authentication failed. This usually means either:\n"
                "• Incorrect password was provided\n"
                "• The encrypted file has been corrupted or tampered with"
            )
        else:
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


def encrypt_file_content_chunked(input_file_path: str, output_file, file_key: bytes, chunk_size: int = 8192) -> bytes:
    """
    Encrypt file content using AES-GCM with chunked processing for large files.
    
    Args:
        input_file_path: Path to input file
        output_file: Open file handle for output
        file_key: Encryption key for the file
        chunk_size: Size of chunks to process (default 8KB)
        
    Returns:
        nonce + auth_tag (header for later decryption)
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
        
        # Write nonce first
        output_file.write(nonce)
        
        # Process file in chunks
        with open(input_file_path, 'rb') as input_file:
            while True:
                chunk = input_file.read(chunk_size)
                if not chunk:
                    break
                encrypted_chunk = encryptor.update(chunk)
                output_file.write(encrypted_chunk)
        
        # Finalize and get tag
        encryptor.finalize()
        auth_tag = encryptor.tag
        
        # Write authentication tag at the end
        output_file.write(auth_tag)
        
        return nonce + auth_tag  # Return header info for verification
        
    except Exception as e:
        raise FileEncryptionError(f"Chunked file content encryption failed: {str(e)}")


def decrypt_file_content_chunked(input_file, output_file_path: str, file_key: bytes, encrypted_size: int, chunk_size: int = 8192) -> None:
    """
    Decrypt file content using AES-GCM with chunked processing for large files.
    
    Args:
        input_file: Open file handle positioned at encrypted content start
        output_file_path: Path where to write decrypted content
        file_key: Decryption key for the file
        encrypted_size: Size of encrypted content section
        chunk_size: Size of chunks to process (default 8KB)
        
    Raises:
        FileEncryptionError: If decryption fails
    """
    try:
        # Read nonce (first 12 bytes)
        nonce = input_file.read(12)
        if len(nonce) != 12:
            raise FileEncryptionError("Invalid encrypted file: missing or incomplete nonce")
        
        # Read authentication tag (last 16 bytes of encrypted section)
        # We need to read it first to initialize the decryptor
        current_pos = input_file.tell()
        input_file.seek(current_pos + encrypted_size - 28)  # -28 = -12 (nonce) - 16 (tag)
        auth_tag = input_file.read(16)
        if len(auth_tag) != 16:
            raise FileEncryptionError("Invalid encrypted file: missing or incomplete authentication tag")
        
        # Go back to start of encrypted content (after nonce)
        input_file.seek(current_pos)
        
        # Create cipher with tag
        cipher = Cipher(
            algorithms.AES(file_key),
            modes.GCM(nonce, auth_tag),
            backend=default_backend()
        )
        decryptor = cipher.decryptor()
        
        # Process file in chunks
        remaining_bytes = encrypted_size - 28  # Total encrypted content size minus nonce and tag
        
        with open(output_file_path, 'wb') as output_file:
            while remaining_bytes > 0:
                # Read chunk, but don't exceed remaining bytes
                chunk_to_read = min(chunk_size, remaining_bytes)
                encrypted_chunk = input_file.read(chunk_to_read)
                
                if not encrypted_chunk:
                    raise FileEncryptionError("Unexpected end of encrypted file")
                
                # Decrypt chunk
                decrypted_chunk = decryptor.update(encrypted_chunk)
                output_file.write(decrypted_chunk)
                
                remaining_bytes -= len(encrypted_chunk)
        
        # Finalize decryption (this verifies the authentication tag)
        decryptor.finalize()
        
    except Exception as e:
        # Check if it's an authentication failure
        if "authentication" in str(e).lower() or "tag" in str(e).lower():
            raise FileEncryptionError(
                "File content authentication failed. The encrypted file may be corrupted."
            )
        else:
            raise FileEncryptionError(f"Chunked file content decryption failed: {str(e)}")


def decrypt_file_content(encrypted_content_data: bytes, file_key: bytes) -> bytes:
    """
    Decrypt file content using AES-GCM.
    
    Args:
        encrypted_content_data: nonce + encrypted_content + auth_tag
        file_key: Decryption key for the file
        
    Returns:
        Decrypted file content
        
    Raises:
        FileEncryptionError: If decryption fails
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
        # Check if it's an authentication failure
        if "authentication" in str(e).lower() or "tag" in str(e).lower():
            raise FileEncryptionError(
                "File content authentication failed. The encrypted file may be corrupted."
            )
        else:
            raise FileEncryptionError(f"File content decryption failed: {str(e)}")


def encrypt_file(file_path: str, password: str, use_chunked_processing: bool = True, chunk_threshold: int = 50 * 1024 * 1024) -> str:
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
        use_chunked_processing: Whether to use chunked processing for large files
        chunk_threshold: File size threshold for chunked processing (default 50MB)
        
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
        
        # Check file size
        file_size = input_path.stat().st_size
        # Allow empty files to be encrypted. Empty content will be treated as an empty byte string.
        
        # Step 1: Generate random File Key
        file_key = generate_file_key()
        
        # Step 2: Derive password key
        password_key, salt = derive_key_from_password(password)
        
        # Step 3: Encrypt File Key with password key
        encrypted_file_key = encrypt_file_key(file_key, password_key)
        
        # Step 4: Determine processing method based on file size
        output_path = input_path.with_suffix(input_path.suffix + '.faceauth')
        
        if use_chunked_processing and file_size > chunk_threshold:
            # Large file: use chunked processing
            print(f"🔄 Processing large file ({file_size / (1024*1024):.1f} MB) using chunked encryption...")
            
            try:
                with open(output_path, 'wb') as output_file:
                    # Write file format header: salt + encrypted_file_key
                    output_file.write(salt + encrypted_file_key)
                    
                    # Encrypt content in chunks
                    encrypt_file_content_chunked(str(input_path), output_file, file_key)
                    
            except Exception as e:
                # Clean up partial file on error
                if output_path.exists():
                    output_path.unlink()
                raise FileEncryptionError(f"Chunked encryption failed: {str(e)}")
        else:
            # Small file: use in-memory processing
            try:
                with open(input_path, 'rb') as f:
                    file_data = f.read()
            except Exception as e:
                raise FileEncryptionError(f"Cannot read file: {str(e)}")
            
            # Encrypt file content in memory
            encrypted_content = encrypt_file_content(file_data, file_key)
            
            # Package everything into .faceauth file format
            output_data = salt + encrypted_file_key + encrypted_content
            
            # Write to output file
            try:
                with open(output_path, 'wb') as f:
                    f.write(output_data)
            except Exception as e:
                raise FileEncryptionError(f"Cannot write encrypted file: {str(e)}")
        
        # Securely clear sensitive data from memory (best effort)
        file_key = os.urandom(32)  # Overwrite with random data
        password_key = os.urandom(32)  # Overwrite with random data
        
        print(f"✅ File encrypted successfully: {output_path}")
        return str(output_path)
        
    except FileEncryptionError:
        raise
    except Exception as e:
        raise FileEncryptionError(f"Unexpected encryption error: {str(e)}")


def decrypt_file(encrypted_file_path: str, password: str, output_path: str = None, use_chunked_processing: bool = True, chunk_threshold: int = 50 * 1024 * 1024) -> str:
    """
    Decrypt a file encrypted with encrypt_file().
    
    This function reverses the key wrapping process:
    1. Parse the .faceauth file structure
    2. Derive password key from password + salt
    3. Decrypt the file key using password key
    4. Decrypt file content using file key
    5. Write decrypted content to output file
    
    Args:
        encrypted_file_path: Path to the .faceauth encrypted file
        password: User password for key derivation
        output_path: Optional output path (defaults to removing .faceauth extension)
        use_chunked_processing: Whether to use chunked processing for large files
        chunk_threshold: File size threshold for chunked processing (default 50MB)
        
    Returns:
        Path to the decrypted file
        
    Raises:
        FileEncryptionError: If decryption fails for any reason
    """
    try:
        # Validate input file
        input_path = Path(encrypted_file_path)
        if not input_path.exists():
            raise FileEncryptionError(f"Encrypted file not found: {encrypted_file_path}")
        
        if not input_path.is_file():
            raise FileEncryptionError(f"Path is not a file: {encrypted_file_path}")
        
        # Check file size for processing method
        file_size = input_path.stat().st_size
        
        # Validate minimum file size for .faceauth format
        min_size = 16 + 28 + 12 + 16  # salt + encrypted_file_key + content_nonce + content_tag
        if file_size < min_size:
            raise FileEncryptionError(
                "Invalid encrypted file format. This doesn't appear to be a valid .faceauth file.\n"
                "• File may be corrupted\n"
                "• File may not be encrypted with FaceAuth\n"
                "• File may be incomplete"
            )
        
        # Determine output path
        if output_path is None:
            if input_path.suffix == '.faceauth':
                # Remove .faceauth extension to restore original name
                output_path = input_path.with_suffix('')
            else:
                # Add .decrypted suffix if not standard .faceauth file
                output_path = input_path.with_suffix('.decrypted')
        
        output_path = Path(output_path)
        
        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        if use_chunked_processing and file_size > chunk_threshold:
            # Large file: use chunked processing
            print(f"🔄 Processing large file ({file_size / (1024*1024):.1f} MB) using chunked decryption...")
            
            try:
                with open(input_path, 'rb') as input_file:
                    # Read file format header
                    salt = input_file.read(16)
                    encrypted_file_key = input_file.read(28)
                    
                    if len(salt) != 16 or len(encrypted_file_key) != 28:
                        raise FileEncryptionError("Invalid file format: corrupted header")
                    
                    # Derive password key using stored salt
                    password_key, _ = derive_key_from_password(password, salt)
                    
                    # Decrypt File Key
                    try:
                        file_key = decrypt_file_key(encrypted_file_key, password_key)
                    except FileEncryptionError as e:
                        raise FileEncryptionError(
                            f"Failed to decrypt file key: {str(e)}\n\n"
                            "This is usually caused by:\n"
                            "• Incorrect password\n"
                            "• Corrupted .faceauth file\n"
                            "• File tampering"
                        )
                    
                    # Calculate encrypted content size
                    encrypted_content_size = file_size - 44  # Total size minus headers
                    
                    # Decrypt content in chunks
                    decrypt_file_content_chunked(input_file, str(output_path), file_key, encrypted_content_size)
                    
            except Exception as e:
                # Clean up partial file on error
                if output_path.exists():
                    output_path.unlink()
                raise FileEncryptionError(f"Chunked decryption failed: {str(e)}")
        else:
            # Small file: use in-memory processing  
            try:
                with open(input_path, 'rb') as f:
                    encrypted_data = f.read()
            except Exception as e:
                raise FileEncryptionError(f"Cannot read encrypted file: {str(e)}")
            
            # Extract components from .faceauth file structure
            salt = encrypted_data[:16]
            encrypted_file_key = encrypted_data[16:44]
            encrypted_content = encrypted_data[44:]
            
            # Validate extracted components
            if len(encrypted_file_key) != 28:
                raise FileEncryptionError("Invalid file format: corrupted file key section")
            
            if len(encrypted_content) < 28:
                raise FileEncryptionError("Invalid file format: corrupted content section")
            
            # Derive password key using stored salt
            password_key, _ = derive_key_from_password(password, salt)
            
            # Decrypt File Key
            try:
                file_key = decrypt_file_key(encrypted_file_key, password_key)
            except FileEncryptionError as e:
                raise FileEncryptionError(
                    f"Failed to decrypt file key: {str(e)}\n\n"
                    "This is usually caused by:\n"
                    "• Incorrect password\n"
                    "• Corrupted .faceauth file\n"
                    "• File tampering"
                )
            
            # Decrypt file content using the unwrapped file key
            try:
                file_data = decrypt_file_content(encrypted_content, file_key)
            except FileEncryptionError as e:
                raise FileEncryptionError(
                    f"Failed to decrypt file content: {str(e)}\n\n"
                    "The file key was decrypted successfully, but the file content is corrupted."
                )
            
            # Write decrypted content
            try:
                with open(output_path, 'wb') as f:
                    f.write(file_data)
            except Exception as e:
                raise FileEncryptionError(f"Cannot write decrypted file: {str(e)}")
        
        # Verify file was written correctly
        if not output_path.exists():
            raise FileEncryptionError("Failed to write decrypted file")
        
        # Securely clear sensitive data from memory (best effort)
        if 'file_key' in locals():
            file_key = os.urandom(32)  # Overwrite with random data
        if 'password_key' in locals():
            password_key = os.urandom(32)  # Overwrite with random data
        
        print(f"✅ File decrypted successfully: {output_path}")
        return str(output_path)
        
    except FileEncryptionError:
        # Re-raise FileEncryptionError as-is
        raise
    except Exception as e:
        # Wrap unexpected errors
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
