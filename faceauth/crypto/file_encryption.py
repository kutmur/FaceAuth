"""
File Encryption Module for FaceAuth
Provides secure AES-GCM encryption for arbitrary files with face authentication.
"""

import os
import mmap
import secrets
import hashlib
import struct
from typing import Dict, Any, Optional, Tuple, BinaryIO
from pathlib import Path
import numpy as np
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend

from .key_derivation import KeyDerivation, KeyDerivationError
from ..core.authentication import FaceAuthenticator, AuthenticationError
from ..utils.storage import FaceDataStorage


class EncryptionError(Exception):
    """Custom exception for encryption/decryption errors."""
    pass


class SecureFileHandler:
    """Handles secure file operations with proper cleanup."""
    
    def __init__(self, file_path: str, mode: str = 'rb'):
        """Initialize secure file handler."""
        self.file_path = Path(file_path)
        self.mode = mode
        self.file_handle = None
        self.temp_files = []
    
    def __enter__(self):
        """Enter context manager."""
        self.file_handle = open(self.file_path, self.mode)
        return self.file_handle
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context manager with secure cleanup."""
        if self.file_handle:
            self.file_handle.close()
        
        # Clean up temporary files
        for temp_file in self.temp_files:
            try:
                if temp_file.exists():
                    # Overwrite with random data before deletion
                    with open(temp_file, 'r+b') as f:
                        size = f.seek(0, 2)  # Get file size
                        f.seek(0)
                        f.write(secrets.token_bytes(size))
                        f.flush()
                        os.fsync(f.fileno())
                    temp_file.unlink()
            except Exception:
                pass  # Best effort cleanup


class FileEncryption:
    """
    Military-grade file encryption controlled by face authentication.
    Uses AES-GCM with authenticated encryption and secure key derivation.
    """
    
    # Encryption parameters
    AES_KEY_SIZE = 32  # 256 bits
    NONCE_SIZE = 12    # 96 bits for GCM
    TAG_SIZE = 16      # 128 bits authentication tag
    CHUNK_SIZE = 1024 * 1024  # 1MB chunks for streaming
    
    # File format version
    FILE_FORMAT_VERSION = 1
    
    # Magic bytes to identify encrypted files
    MAGIC_BYTES = b'FACEAUTH'
    
    def __init__(self, storage: FaceDataStorage = None):
        """
        Initialize file encryption system.
        
        Args:
            storage: Face data storage instance
        """
        self.storage = storage or FaceDataStorage()
        self.key_derivation = KeyDerivation()
        self.authenticator = FaceAuthenticator(self.storage)
        
    def _create_file_header(self, salt: bytes, nonce: bytes, kdf_method: str, 
                          original_filename: str, file_size: int) -> bytes:
        """
        Create encrypted file header with metadata.
        
        Returns:
            Header bytes
        """
        header = {
            'magic': self.MAGIC_BYTES,
            'version': struct.pack('<I', self.FILE_FORMAT_VERSION),
            'kdf_method': kdf_method.encode('utf-8')[:16].ljust(16, b'\x00'),
            'salt': salt,
            'nonce': nonce,
            'original_filename': original_filename.encode('utf-8')[:256].ljust(256, b'\x00'),
            'file_size': struct.pack('<Q', file_size),
            'header_checksum': b'\x00' * 32  # Placeholder for SHA-256
        }
        
        # Calculate header checksum (excluding the checksum field itself)
        header_data = (header['magic'] + header['version'] + 
                      header['kdf_method'] + header['salt'] + 
                      header['nonce'] + header['original_filename'] + 
                      header['file_size'])
        
        checksum = hashlib.sha256(header_data).digest()
        header['header_checksum'] = checksum
        
        return header_data + checksum
    
    def _parse_file_header(self, header_bytes: bytes) -> Dict[str, Any]:
        """
        Parse encrypted file header.
        
        Args:
            header_bytes: Header bytes from file
            
        Returns:
            Dictionary with header information
        """
        if len(header_bytes) < 8:
            raise EncryptionError("Invalid file header - too short")
        
        # Check magic bytes
        magic = header_bytes[:8]
        if magic != self.MAGIC_BYTES:
            raise EncryptionError("Not a FaceAuth encrypted file")
        
        offset = 8
        
        # Parse version
        version = struct.unpack('<I', header_bytes[offset:offset+4])[0]
        offset += 4
        
        if version != self.FILE_FORMAT_VERSION:
            raise EncryptionError(f"Unsupported file format version: {version}")
        
        # Parse KDF method
        kdf_method = header_bytes[offset:offset+16].rstrip(b'\x00').decode('utf-8')
        offset += 16
        
        # Parse salt
        salt = header_bytes[offset:offset+32]
        offset += 32
        
        # Parse nonce
        nonce = header_bytes[offset:offset+12]
        offset += 12
        
        # Parse original filename
        original_filename = header_bytes[offset:offset+256].rstrip(b'\x00').decode('utf-8')
        offset += 256
        
        # Parse file size
        file_size = struct.unpack('<Q', header_bytes[offset:offset+8])[0]
        offset += 8
        
        # Parse and verify header checksum
        stored_checksum = header_bytes[offset:offset+32]
        calculated_checksum = hashlib.sha256(header_bytes[:offset]).digest()
        
        if not secrets.compare_digest(stored_checksum, calculated_checksum):
            raise EncryptionError("Header checksum verification failed")
        
        return {
            'version': version,
            'kdf_method': kdf_method,
            'salt': salt,
            'nonce': nonce,
            'original_filename': original_filename,
            'file_size': file_size,
            'header_size': offset + 32
        }
    
    def _authenticate_user(self, user_id: str, timeout: int = 10) -> np.ndarray:
        """
        Authenticate user and return face embedding.
        
        Args:
            user_id: User ID to authenticate
            timeout: Authentication timeout
            
        Returns:
            Face embedding if authentication successful
            
        Raises:
            EncryptionError: If authentication fails
        """
        try:
            # First check if user exists
            if not self.storage.user_exists(user_id):
                raise EncryptionError(f"User '{user_id}' not enrolled")
            
            print(f"🔐 Face authentication required for user: {user_id}")
            print("📷 Please look at the camera for authentication...")
            
            # Perform face authentication
            result = self.authenticator.authenticate_realtime(user_id, timeout=timeout)
            
            if not result['success']:
                error_msg = result.get('error', 'Authentication failed')
                raise EncryptionError(f"Face authentication failed: {error_msg}")
            
            print(f"✅ Authentication successful! (Similarity: {result['similarity']:.3f})")
            
            # Get the stored embedding for key derivation
            embedding = self.storage.load_user_embedding(user_id)
            if embedding is None:
                raise EncryptionError("Failed to load user embedding")
            
            return embedding
            
        except AuthenticationError as e:
            raise EncryptionError(f"Authentication error: {str(e)}")
        except Exception as e:
            raise EncryptionError(f"Authentication failed: {str(e)}")
    
    def encrypt_file(self, file_path: str, user_id: str, output_path: str = None,
                    kdf_method: str = 'argon2', auth_timeout: int = 10,
                    overwrite: bool = False) -> Dict[str, Any]:
        """
        Encrypt a file with face authentication.
        
        Args:
            file_path: Path to file to encrypt
            user_id: User ID for authentication
            output_path: Output path for encrypted file (optional)
            kdf_method: Key derivation method
            auth_timeout: Authentication timeout in seconds
            overwrite: Whether to overwrite existing files
            
        Returns:
            Dictionary with encryption results
        """
        start_time = __import__('time').time()
        
        try:
            # Validate input file
            input_file = Path(file_path)
            if not input_file.exists():
                raise EncryptionError(f"Input file not found: {file_path}")
            
            if not input_file.is_file():
                raise EncryptionError(f"Path is not a file: {file_path}")
            
            # Determine output path
            if output_path is None:
                output_path = str(input_file.with_suffix(input_file.suffix + '.faceauth'))
            
            output_file = Path(output_path)
            
            # Check if output file exists
            if output_file.exists() and not overwrite:
                raise EncryptionError(f"Output file already exists: {output_path}")
            
            # Get file information
            file_size = input_file.stat().st_size
            original_filename = input_file.name
            
            print(f"🔒 Encrypting file: {original_filename} ({file_size:,} bytes)")
            
            # Authenticate user
            embedding = self._authenticate_user(user_id, auth_timeout)
            
            # Derive encryption key (use filename only, not full path)
            print("🔑 Deriving encryption key...")
            encryption_key, salt = self.key_derivation.derive_file_key(
                embedding, original_filename, kdf_method=kdf_method
            )
            
            # Generate nonce for AES-GCM
            nonce = secrets.token_bytes(self.NONCE_SIZE)
            
            # Initialize AES-GCM
            aesgcm = AESGCM(encryption_key)
            
            # Create file header
            header = self._create_file_header(
                salt, nonce, kdf_method, original_filename, file_size
            )
            
            print("📝 Encrypting file data...")
            
            # Encrypt file in chunks
            with SecureFileHandler(input_file, 'rb') as infile, \
                 SecureFileHandler(output_file, 'wb') as outfile:
                
                # Write header
                outfile.write(header)
                
                # Encrypt file data in chunks
                chunk_num = 0
                total_chunks = (file_size + self.CHUNK_SIZE - 1) // self.CHUNK_SIZE
                
                while True:
                    chunk = infile.read(self.CHUNK_SIZE)
                    if not chunk:
                        break
                    
                    # Create unique nonce for each chunk
                    chunk_nonce = nonce + struct.pack('<I', chunk_num)
                    chunk_nonce = chunk_nonce[:self.NONCE_SIZE]  # Ensure correct size
                    
                    # Encrypt chunk with authentication
                    encrypted_chunk = aesgcm.encrypt(chunk_nonce, chunk, None)
                    
                    # Write chunk size and encrypted data
                    outfile.write(struct.pack('<I', len(encrypted_chunk)))
                    outfile.write(encrypted_chunk)
                    
                    chunk_num += 1
                    
                    # Progress indication
                    if chunk_num % 10 == 0 or chunk_num == total_chunks:
                        progress = (chunk_num / total_chunks) * 100
                        print(f"Progress: {progress:.1f}% ({chunk_num}/{total_chunks} chunks)")
            
            # Secure deletion of encryption key
            self.key_derivation.secure_delete_key(encryption_key)
            
            duration = __import__('time').time() - start_time
            encrypted_size = output_file.stat().st_size
            
            print(f"✅ File encrypted successfully!")
            print(f"   Output: {output_path}")
            print(f"   Size: {file_size:,} → {encrypted_size:,} bytes")
            print(f"   Duration: {duration:.2f}s")
            
            return {
                'success': True,
                'input_file': str(input_file),
                'output_file': str(output_file),
                'original_size': file_size,
                'encrypted_size': encrypted_size,
                'duration': duration,
                'kdf_method': kdf_method,
                'user_id': user_id
            }
            
        except Exception as e:
            # Clean up on error
            if 'output_file' in locals() and output_file.exists():
                try:
                    output_file.unlink()
                except Exception:
                    pass
            
            raise EncryptionError(f"Encryption failed: {str(e)}")
    
    def decrypt_file(self, encrypted_path: str, user_id: str, output_path: str = None,
                    auth_timeout: int = 10, overwrite: bool = False) -> Dict[str, Any]:
        """
        Decrypt a FaceAuth encrypted file.
        
        Args:
            encrypted_path: Path to encrypted file
            user_id: User ID for authentication
            output_path: Output path for decrypted file (optional)
            auth_timeout: Authentication timeout in seconds
            overwrite: Whether to overwrite existing files
            
        Returns:
            Dictionary with decryption results
        """
        start_time = __import__('time').time()
        
        try:
            # Validate encrypted file
            encrypted_file = Path(encrypted_path)
            if not encrypted_file.exists():
                raise EncryptionError(f"Encrypted file not found: {encrypted_path}")
            
            print(f"🔓 Decrypting file: {encrypted_file.name}")
            
            # Read and parse header
            with SecureFileHandler(encrypted_file, 'rb') as infile:
                # Read enough bytes for header
                header_bytes = infile.read(512)  # Should be enough for full header
                
            header_info = self._parse_file_header(header_bytes)
            
            # Determine output path
            if output_path is None:
                original_name = header_info['original_filename']
                output_path = str(encrypted_file.parent / original_name)
            
            output_file = Path(output_path)
            
            # Check if output file exists
            if output_file.exists() and not overwrite:
                raise EncryptionError(f"Output file already exists: {output_path}")
            
            print(f"📄 Original file: {header_info['original_filename']}")
            print(f"📊 File size: {header_info['file_size']:,} bytes")
            
            # Authenticate user
            embedding = self._authenticate_user(user_id, auth_timeout)
            
            # Derive decryption key (use original filename, not encrypted file path)
            print("🔑 Deriving decryption key...")
            decryption_key, _ = self.key_derivation.derive_file_key(
                embedding, header_info['original_filename'], salt=header_info['salt'], kdf_method=header_info['kdf_method']
            )
            
            # Initialize AES-GCM
            aesgcm = AESGCM(decryption_key)
            
            print("📝 Decrypting file data...")
            
            # Decrypt file
            with SecureFileHandler(encrypted_file, 'rb') as infile, \
                 SecureFileHandler(output_file, 'wb') as outfile:
                
                # Skip header
                infile.seek(header_info['header_size'])
                
                chunk_num = 0
                decrypted_size = 0
                expected_size = header_info['file_size']
                
                while decrypted_size < expected_size:
                    # Read chunk size
                    chunk_size_bytes = infile.read(4)
                    if len(chunk_size_bytes) != 4:
                        break
                    
                    chunk_size = struct.unpack('<I', chunk_size_bytes)[0]
                    
                    # Read encrypted chunk
                    encrypted_chunk = infile.read(chunk_size)
                    if len(encrypted_chunk) != chunk_size:
                        raise EncryptionError("Unexpected end of file")
                    
                    # Create chunk nonce
                    chunk_nonce = header_info['nonce'] + struct.pack('<I', chunk_num)
                    chunk_nonce = chunk_nonce[:self.NONCE_SIZE]
                    
                    # Decrypt chunk
                    try:
                        decrypted_chunk = aesgcm.decrypt(chunk_nonce, encrypted_chunk, None)
                    except Exception as e:
                        raise EncryptionError(f"Decryption failed - invalid key or corrupted data: {str(e)}")
                    
                    # Write decrypted data (trim if last chunk)
                    remaining = expected_size - decrypted_size
                    if len(decrypted_chunk) > remaining:
                        decrypted_chunk = decrypted_chunk[:remaining]
                    
                    outfile.write(decrypted_chunk)
                    decrypted_size += len(decrypted_chunk)
                    chunk_num += 1
                    
                    # Progress indication
                    if chunk_num % 10 == 0:
                        progress = (decrypted_size / expected_size) * 100
                        print(f"Progress: {progress:.1f}%")
            
            # Verify file size
            actual_size = output_file.stat().st_size
            if actual_size != expected_size:
                raise EncryptionError(f"File size mismatch: expected {expected_size}, got {actual_size}")
            
            # Secure deletion of decryption key
            self.key_derivation.secure_delete_key(decryption_key)
            
            duration = __import__('time').time() - start_time
            
            print(f"✅ File decrypted successfully!")
            print(f"   Output: {output_path}")
            print(f"   Size: {actual_size:,} bytes")
            print(f"   Duration: {duration:.2f}s")
            
            return {
                'success': True,
                'encrypted_file': str(encrypted_file),
                'output_file': str(output_file),
                'file_size': actual_size,
                'duration': duration,
                'original_filename': header_info['original_filename']
            }
            
        except Exception as e:
            # Clean up on error
            if 'output_file' in locals() and output_file.exists():
                try:
                    output_file.unlink()
                except Exception:
                    pass
            
            raise EncryptionError(f"Decryption failed: {str(e)}")
    
    def verify_encrypted_file(self, encrypted_path: str) -> Dict[str, Any]:
        """
        Verify and get information about an encrypted file.
        
        Args:
            encrypted_path: Path to encrypted file
            
        Returns:
            Dictionary with file information
        """
        try:
            encrypted_file = Path(encrypted_path)
            if not encrypted_file.exists():
                raise EncryptionError(f"File not found: {encrypted_path}")
            
            # Read and parse header
            with SecureFileHandler(encrypted_file, 'rb') as infile:
                header_bytes = infile.read(512)
            
            header_info = self._parse_file_header(header_bytes)
            file_size = encrypted_file.stat().st_size
            
            return {
                'is_faceauth_file': True,
                'file_format_version': header_info['version'],
                'kdf_method': header_info['kdf_method'],
                'original_filename': header_info['original_filename'],
                'original_size': header_info['file_size'],
                'encrypted_size': file_size,
                'overhead_bytes': file_size - header_info['file_size'],
                'header_size': header_info['header_size']
            }
            
        except EncryptionError:
            return {'is_faceauth_file': False, 'error': 'Not a valid FaceAuth encrypted file'}
        except Exception as e:
            return {'is_faceauth_file': False, 'error': str(e)}
    
    def get_encryption_info(self, kdf_method: str = 'argon2') -> Dict[str, Any]:
        """
        Get information about encryption parameters.
        
        Args:
            kdf_method: Key derivation method
            
        Returns:
            Dictionary with encryption information
        """
        kdf_info = self.key_derivation.get_kdf_info(kdf_method)
        
        return {
            'encryption_algorithm': 'AES-256-GCM',
            'key_size_bits': self.AES_KEY_SIZE * 8,
            'nonce_size_bits': self.NONCE_SIZE * 8,
            'tag_size_bits': self.TAG_SIZE * 8,
            'chunk_size_bytes': self.CHUNK_SIZE,
            'file_format_version': self.FILE_FORMAT_VERSION,
            'kdf_info': kdf_info
        }
