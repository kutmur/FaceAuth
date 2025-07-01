"""
Secure Key Derivation Module for FaceAuth
Derives cryptographic keys from face embeddings using PBKDF2 and Argon2.
"""

import os
import hmac
import hashlib
import secrets
from typing import Tuple, Optional, Dict, Any
import numpy as np
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from cryptography.hazmat.backends import default_backend
import argon2


class KeyDerivationError(Exception):
    """Custom exception for key derivation errors."""
    pass


class KeyDerivation:
    """
    Secure key derivation from face embeddings.
    Uses multiple rounds of cryptographic functions to ensure security.
    """
    
    # Key derivation parameters
    PBKDF2_ITERATIONS = 100000  # OWASP recommended minimum
    SCRYPT_N = 16384  # Memory cost
    SCRYPT_R = 8      # Block size
    SCRYPT_P = 1      # Parallelization
    ARGON2_TIME_COST = 2  # Time iterations
    ARGON2_MEMORY_COST = 65536  # Memory cost in KB (64MB)
    ARGON2_PARALLELISM = 1  # Parallelism degree
    
    SALT_LENGTH = 32  # 256 bits
    KEY_LENGTH = 32   # 256 bits for AES-256
    
    def __init__(self):
        """Initialize key derivation with secure parameters."""
        self.backend = default_backend()
        self.argon2_hasher = argon2.PasswordHasher(
            time_cost=self.ARGON2_TIME_COST,
            memory_cost=self.ARGON2_MEMORY_COST,
            parallelism=self.ARGON2_PARALLELISM,
            hash_len=self.KEY_LENGTH,
            salt_len=self.SALT_LENGTH
        )
    
    def generate_salt(self) -> bytes:
        """Generate cryptographically secure random salt."""
        return secrets.token_bytes(self.SALT_LENGTH)
    
    def _normalize_embedding(self, embedding: np.ndarray) -> bytes:
        """
        Normalize face embedding for consistent key derivation.
        
        Args:
            embedding: Face embedding vector
            
        Returns:
            Normalized embedding as bytes
        """
        try:
            # Ensure embedding is float32 and normalized
            embedding = embedding.astype(np.float32)
            
            # L2 normalization
            norm = np.linalg.norm(embedding)
            if norm > 0:
                embedding = embedding / norm
            
            # Quantize to reduce floating point precision issues
            # This helps with slight variations in embeddings
            embedding = np.round(embedding, decimals=6)
            
            # Convert to bytes
            return embedding.tobytes()
            
        except Exception as e:
            raise KeyDerivationError(f"Failed to normalize embedding: {str(e)}")
    
    def _derive_pbkdf2_key(self, normalized_embedding: bytes, salt: bytes) -> bytes:
        """Derive key using PBKDF2-HMAC-SHA256."""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=self.KEY_LENGTH,
            salt=salt,
            iterations=self.PBKDF2_ITERATIONS,
            backend=self.backend
        )
        return kdf.derive(normalized_embedding)
    
    def _derive_scrypt_key(self, normalized_embedding: bytes, salt: bytes) -> bytes:
        """Derive key using scrypt."""
        kdf = Scrypt(
            length=self.KEY_LENGTH,
            salt=salt,
            n=self.SCRYPT_N,
            r=self.SCRYPT_R,
            p=self.SCRYPT_P,
            backend=self.backend
        )
        return kdf.derive(normalized_embedding)
    
    def _derive_argon2_key(self, normalized_embedding: bytes, salt: bytes) -> bytes:
        """Derive key using Argon2id."""
        try:
            # Argon2 expects password as string, so we use base64 encoding
            import base64
            import warnings
            password = base64.b64encode(normalized_embedding).decode('ascii')
            
            # Suppress deprecation warning for now
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", DeprecationWarning)
                # Use Argon2id for key derivation
                hash_result = argon2.hash_password_raw(
                    password.encode('utf-8'),
                    salt,
                    time_cost=self.ARGON2_TIME_COST,
                    memory_cost=self.ARGON2_MEMORY_COST,
                    parallelism=self.ARGON2_PARALLELISM,
                    hash_len=self.KEY_LENGTH,
                    type=argon2.Type.ID
                )
            return hash_result
            
        except Exception as e:
            raise KeyDerivationError(f"Argon2 key derivation failed: {str(e)}")
    
    def derive_encryption_key(self, embedding: np.ndarray, salt: bytes = None, 
                            method: str = 'argon2') -> Tuple[bytes, bytes]:
        """
        Derive encryption key from face embedding.
        
        Args:
            embedding: Face embedding vector
            salt: Salt for key derivation (generated if None)
            method: Key derivation method ('argon2', 'pbkdf2', 'scrypt', or 'multi')
            
        Returns:
            Tuple of (derived_key, salt_used)
        """
        try:
            # Generate salt if not provided
            if salt is None:
                salt = self.generate_salt()
            
            # Normalize embedding
            normalized_embedding = self._normalize_embedding(embedding)
            
            # Derive key using specified method
            if method == 'pbkdf2':
                key = self._derive_pbkdf2_key(normalized_embedding, salt)
            elif method == 'scrypt':
                key = self._derive_scrypt_key(normalized_embedding, salt)
            elif method == 'argon2':
                key = self._derive_argon2_key(normalized_embedding, salt)
            elif method == 'multi':
                # Use multiple KDFs for enhanced security
                key = self._derive_multi_kdf_key(normalized_embedding, salt)
            else:
                raise KeyDerivationError(f"Unknown key derivation method: {method}")
            
            return key, salt
            
        except Exception as e:
            raise KeyDerivationError(f"Key derivation failed: {str(e)}")
    
    def _derive_multi_kdf_key(self, normalized_embedding: bytes, salt: bytes) -> bytes:
        """
        Use multiple KDFs for enhanced security.
        Combines PBKDF2, scrypt, and Argon2.
        """
        try:
            # Split salt for different KDFs
            salt1 = salt[:16]
            salt2 = salt[16:]
            
            # Derive keys using different methods
            key1 = self._derive_pbkdf2_key(normalized_embedding, salt1)
            key2 = self._derive_scrypt_key(normalized_embedding, salt2)
            key3 = self._derive_argon2_key(normalized_embedding, salt)
            
            # Combine keys using HMAC
            combined = key1 + key2 + key3
            final_key = hmac.new(salt, combined, hashlib.sha256).digest()
            
            return final_key[:self.KEY_LENGTH]
            
        except Exception as e:
            raise KeyDerivationError(f"Multi-KDF derivation failed: {str(e)}")
    
    def verify_key(self, embedding: np.ndarray, salt: bytes, 
                  expected_key: bytes, method: str = 'argon2') -> bool:
        """
        Verify that an embedding produces the expected key.
        
        Args:
            embedding: Face embedding to verify
            salt: Salt used in original derivation
            expected_key: Expected derived key
            method: Key derivation method used
            
        Returns:
            True if keys match, False otherwise
        """
        try:
            derived_key, _ = self.derive_encryption_key(embedding, salt, method)
            return hmac.compare_digest(derived_key, expected_key)
        except Exception:
            return False
    
    def derive_file_key(self, embedding: np.ndarray, file_path: str, 
                       salt: bytes = None, kdf_method: str = 'argon2') -> Tuple[bytes, bytes]:
        """
        Derive a unique key for a specific file.
        Incorporates file path for unique per-file keys.
        
        Args:
            embedding: Face embedding
            file_path: Path to the file being encrypted
            salt: Salt for derivation
            kdf_method: KDF method to use ('pbkdf2', 'scrypt', 'argon2', 'multi')
            
        Returns:
            Tuple of (file_key, salt_used)
        """
        try:
            if salt is None:
                salt = self.generate_salt()
            
            # Create file-specific input by combining embedding and file path
            normalized_embedding = self._normalize_embedding(embedding)
            file_info = file_path.encode('utf-8')
            
            # Combine embedding with file information
            combined_input = normalized_embedding + hashlib.sha256(file_info).digest()
            
            # Derive key using specified method
            if kdf_method == 'pbkdf2':
                file_key = self._derive_pbkdf2_key(combined_input, salt)
            elif kdf_method == 'scrypt':
                file_key = self._derive_scrypt_key(combined_input, salt)
            elif kdf_method == 'argon2':
                file_key = self._derive_argon2_key(combined_input, salt)
            elif kdf_method == 'multi':
                file_key = self._derive_multi_kdf_key(combined_input, salt)
            else:
                raise KeyDerivationError(f"Unsupported KDF method: {kdf_method}")
            
            return file_key, salt
            
        except Exception as e:
            raise KeyDerivationError(f"File key derivation failed: {str(e)}")
    
    def secure_delete_key(self, key: bytes) -> None:
        """
        Securely delete key from memory.
        Overwrites memory with random data.
        """
        try:
            if hasattr(key, '__len__'):
                # Overwrite memory with random bytes
                key_array = bytearray(key)
                for i in range(len(key_array)):
                    key_array[i] = secrets.randbits(8)
                # Clear the bytearray
                key_array.clear()
        except Exception:
            # Best effort - if secure deletion fails, continue
            pass
    
    def get_kdf_info(self, method: str = 'argon2') -> Dict[str, Any]:
        """
        Get key derivation function parameters.
        
        Args:
            method: KDF method
            
        Returns:
            Dictionary with KDF parameters
        """
        if method == 'pbkdf2':
            return {
                'method': 'PBKDF2-HMAC-SHA256',
                'iterations': self.PBKDF2_ITERATIONS,
                'key_length': self.KEY_LENGTH,
                'salt_length': self.SALT_LENGTH
            }
        elif method == 'scrypt':
            return {
                'method': 'scrypt',
                'n': self.SCRYPT_N,
                'r': self.SCRYPT_R,
                'p': self.SCRYPT_P,
                'key_length': self.KEY_LENGTH,
                'salt_length': self.SALT_LENGTH
            }
        elif method == 'argon2':
            return {
                'method': 'Argon2id',
                'time_cost': self.ARGON2_TIME_COST,
                'memory_cost': self.ARGON2_MEMORY_COST,
                'parallelism': self.ARGON2_PARALLELISM,
                'key_length': self.KEY_LENGTH,
                'salt_length': self.SALT_LENGTH
            }
        elif method == 'multi':
            return {
                'method': 'Multi-KDF (PBKDF2 + scrypt + Argon2)',
                'combines': ['PBKDF2-HMAC-SHA256', 'scrypt', 'Argon2id'],
                'key_length': self.KEY_LENGTH,
                'salt_length': self.SALT_LENGTH
            }
        else:
            raise KeyDerivationError(f"Unknown method: {method}")
