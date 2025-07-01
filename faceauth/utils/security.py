"""
Security utilities for FaceAuth system.
Provides encryption, hashing, and secure storage mechanisms.
"""

import os
import hashlib
import base64
from typing import Union, Tuple
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import bcrypt
import numpy as np


class SecurityManager:
    """Handles encryption, decryption, and secure storage of face embeddings."""
    
    def __init__(self, master_key: str = None):
        """
        Initialize security manager with optional master key.
        
        Args:
            master_key: Master password for encryption. If None, uses system-generated key.
        """
        self.master_key = master_key
        self._fernet = None
        
    def _get_or_create_key(self) -> bytes:
        """Get or create encryption key from master password."""
        if self.master_key:
            # Derive key from master password
            password = self.master_key.encode()
            salt = b'faceauth_salt_2025'  # In production, use random salt per user
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(password))
        else:
            # Use system-generated key (stored in secure location)
            key_file = os.path.join(os.path.expanduser("~"), ".faceauth", "key.bin")
            os.makedirs(os.path.dirname(key_file), exist_ok=True)
            
            if os.path.exists(key_file):
                with open(key_file, 'rb') as f:
                    key = f.read()
            else:
                key = Fernet.generate_key()
                with open(key_file, 'wb') as f:
                    f.write(key)
                # Set restrictive permissions on Windows
                os.chmod(key_file, 0o600)
                
        return key
    
    def _get_fernet(self) -> Fernet:
        """Get Fernet encryption instance."""
        if self._fernet is None:
            key = self._get_or_create_key()
            self._fernet = Fernet(key)
        return self._fernet
    
    def encrypt_embedding(self, embedding: np.ndarray) -> str:
        """
        Encrypt face embedding for secure storage.
        
        Args:
            embedding: Face embedding as numpy array
            
        Returns:
            Encrypted embedding as base64 string
        """
        # Convert numpy array to bytes
        embedding_bytes = embedding.astype(np.float32).tobytes()
        
        # Encrypt the data
        fernet = self._get_fernet()
        encrypted_data = fernet.encrypt(embedding_bytes)
        
        # Return as base64 string for storage
        return base64.b64encode(encrypted_data).decode('utf-8')
    
    def decrypt_embedding(self, encrypted_embedding: str) -> np.ndarray:
        """
        Decrypt face embedding from storage.
        
        Args:
            encrypted_embedding: Encrypted embedding as base64 string
            
        Returns:
            Decrypted embedding as numpy array
        """
        # Decode from base64
        encrypted_data = base64.b64decode(encrypted_embedding.encode('utf-8'))
        
        # Decrypt the data
        fernet = self._get_fernet()
        embedding_bytes = fernet.decrypt(encrypted_data)
        
        # Convert back to numpy array
        embedding = np.frombuffer(embedding_bytes, dtype=np.float32)
        return embedding
    
    def hash_user_id(self, user_id: str) -> str:
        """
        Create secure hash of user ID for storage.
        
        Args:
            user_id: User identifier
            
        Returns:
            Hashed user ID
        """
        # Use bcrypt for secure hashing
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(user_id.encode('utf-8'), salt)
        return base64.b64encode(hashed).decode('utf-8')
    
    def verify_user_id(self, user_id: str, hashed_user_id: str) -> bool:
        """
        Verify user ID against stored hash.
        
        Args:
            user_id: User identifier to verify
            hashed_user_id: Stored hash to check against
            
        Returns:
            True if user ID matches hash
        """
        try:
            hashed_bytes = base64.b64decode(hashed_user_id.encode('utf-8'))
            return bcrypt.checkpw(user_id.encode('utf-8'), hashed_bytes)
        except Exception:
            return False
    
    def generate_secure_filename(self, user_id: str) -> str:
        """
        Generate secure filename for user data.
        
        Args:
            user_id: User identifier
            
        Returns:
            Secure filename
        """
        # Create SHA256 hash of user ID
        hash_obj = hashlib.sha256(user_id.encode('utf-8'))
        return f"user_{hash_obj.hexdigest()[:16]}.fauth"
    
    def obfuscate_data(self, data: bytes) -> bytes:
        """
        Additional obfuscation layer for stored data.
        
        Args:
            data: Data to obfuscate
            
        Returns:
            Obfuscated data
        """
        # Simple XOR obfuscation with rotating key
        key = b"FaceAuth2025SecureKey"
        obfuscated = bytearray()
        
        for i, byte in enumerate(data):
            obfuscated.append(byte ^ key[i % len(key)])
            
        return bytes(obfuscated)
    
    def deobfuscate_data(self, obfuscated_data: bytes) -> bytes:
        """
        Remove obfuscation layer from stored data.
        
        Args:
            obfuscated_data: Obfuscated data
            
        Returns:
            Original data
        """
        # XOR with same key to reverse obfuscation
        return self.obfuscate_data(obfuscated_data)


def generate_salt() -> str:
    """Generate a random salt for password hashing."""
    return base64.b64encode(os.urandom(32)).decode('utf-8')


def secure_delete_file(filepath: str) -> bool:
    """
    Securely delete a file by overwriting it before deletion.
    
    Args:
        filepath: Path to file to delete
        
    Returns:
        True if successful
    """
    try:
        if os.path.exists(filepath):
            # Get file size
            filesize = os.path.getsize(filepath)
            
            # Overwrite with random data multiple times
            with open(filepath, 'rb+') as f:
                for _ in range(3):
                    f.seek(0)
                    f.write(os.urandom(filesize))
                    f.flush()
                    os.fsync(f.fileno())
            
            # Finally delete the file
            os.remove(filepath)
            return True
    except Exception:
        return False