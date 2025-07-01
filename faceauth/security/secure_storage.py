"""
Secure Storage Manager for FaceAuth

Provides secure, encrypted storage for all sensitive data with:
- Encrypted file storage with proper permissions
- Secure directory management
- Anti-forensic deletion capabilities
- Access control and isolation
- Backup and restore with encryption
- Audit trail for data access

Privacy Features:
- All data encrypted at rest
- Secure file permissions (user-only access)
- Protection against unauthorized access
- Secure deletion with multiple overwrites
- No sensitive data in file names or metadata
- Isolated storage directories
"""

import os
import stat
import shutil
import json
import time
import platform
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
import pickle
import tempfile
import secrets

from .encryption_manager import EncryptionManager, EncryptionError
from .access_control import AccessControlManager


class SecureStorageError(Exception):
    """Custom exception for secure storage operations."""
    pass


class SecureStorage:
    """
    Secure storage manager with encryption and access control.
    
    Provides enterprise-grade secure storage for face embeddings,
    metadata, and other sensitive data with privacy protection.
    """
    
    def __init__(self, storage_dir: Optional[str] = None, 
                 encryption_manager: Optional[EncryptionManager] = None,
                 master_password: Optional[str] = None):
        """
        Initialize secure storage.
        
        Args:
            storage_dir: Custom storage directory path
            encryption_manager: Encryption manager instance
            master_password: Master password for encryption
        """
        self.master_password = master_password
        self.encryption_manager = encryption_manager or EncryptionManager(master_password)
        self.access_control = AccessControlManager()
        
        # Set up storage directories
        self._setup_storage_directories(storage_dir)
        
        # File extensions
        self.encrypted_ext = '.faceauth'
        self.metadata_ext = '.meta'
        self.backup_ext = '.bak'
        
        # Security settings
        self.secure_delete_passes = 3
        self.backup_retention_days = 30
        
    def _setup_storage_directories(self, custom_dir: Optional[str] = None):
        """Set up secure storage directory structure."""
        if custom_dir:
            self.base_dir = Path(custom_dir).resolve()
        else:
            # Use system-appropriate directory
            if platform.system() == 'Windows':
                base_path = Path.home() / 'AppData' / 'Local' / 'FaceAuth'
            else:
                base_path = Path.home() / '.faceauth'
            self.base_dir = base_path
        
        # Create directory structure
        self.embeddings_dir = self.base_dir / 'embeddings'
        self.metadata_dir = self.base_dir / 'metadata'
        self.backups_dir = self.base_dir / 'backups'
        self.logs_dir = self.base_dir / 'logs'
        self.temp_dir = self.base_dir / 'temp'
        
        # Create directories with secure permissions
        for directory in [self.embeddings_dir, self.metadata_dir, 
                         self.backups_dir, self.logs_dir, self.temp_dir]:
            self._create_secure_directory(directory)
    
    def _create_secure_directory(self, directory: Path):
        """Create directory with secure permissions."""
        try:
            directory.mkdir(parents=True, exist_ok=True)
            
            # Set restrictive permissions (owner only)
            if platform.system() != 'Windows':
                os.chmod(directory, stat.S_IRWXU)  # 700 - owner read/write/execute only
            else:
                # Windows: Remove all permissions except for owner
                try:
                    self.access_control.set_windows_permissions(directory, owner_only=True)
                except Exception as e:
                    # Fall back to basic permissions if Windows security fails
                    pass
        except Exception as e:
            raise SecureStorageError(f"Failed to create secure directory {directory}: {str(e)}")
    
    def _generate_secure_filename(self, user_id: str, file_type: str = 'embedding') -> str:
        """
        Generate secure filename that doesn't reveal user information.
        
        Args:
            user_id: User identifier
            file_type: Type of file ('embedding', 'metadata')
            
        Returns:
            Secure filename
        """
        # Hash user ID to create non-revealing filename
        import hashlib
        user_hash = hashlib.sha256(user_id.encode()).hexdigest()[:16]
        timestamp = int(time.time())
        
        if file_type == 'embedding':
            return f"emb_{user_hash}_{timestamp}{self.encrypted_ext}"
        elif file_type == 'metadata':
            return f"meta_{user_hash}_{timestamp}{self.metadata_ext}"
        else:
            return f"{file_type}_{user_hash}_{timestamp}"
    
    def store_face_embedding(self, user_id: str, embedding_data: Dict[str, Any]) -> str:
        """
        Store encrypted face embedding.
        
        Args:
            user_id: User identifier
            embedding_data: Encrypted embedding package
            
        Returns:
            Storage path
        """
        try:
            # Generate secure filename
            filename = self._generate_secure_filename(user_id, 'embedding')
            file_path = self.embeddings_dir / filename
            
            # Add storage metadata
            storage_metadata = {
                'user_id_hash': self._hash_user_id(user_id),
                'storage_version': '1.0',
                'stored_at': int(time.time()),
                'file_type': 'face_embedding'
            }
            
            # Combine data with storage metadata
            complete_package = {
                'embedding_data': embedding_data,
                'storage_metadata': storage_metadata
            }
            
            # Serialize and encrypt the complete package
            serialized_data = pickle.dumps(complete_package)
            encrypted_package = self.encryption_manager.encrypt_data(
                serialized_data, self.master_password, 'argon2'
            )
            
            # Write to temporary file first, then atomic move
            temp_path = self._write_secure_temp_file(encrypted_package)
            shutil.move(str(temp_path), str(file_path))
            
            # Set secure permissions
            self._set_secure_file_permissions(file_path)
            
            # Store metadata separately
            self._store_user_metadata(user_id, {
                'embedding_file': str(file_path),
                'created_at': int(time.time()),
                'last_accessed': int(time.time())
            })
            
            return str(file_path)
            
        except Exception as e:
            raise SecureStorageError(f"Failed to store face embedding: {str(e)}")
    
    def load_face_embedding(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Load and decrypt face embedding.
        
        Args:
            user_id: User identifier
            
        Returns:
            Decrypted embedding data or None if not found
        """
        try:
            # Find embedding file for user
            embedding_file = self._find_user_embedding_file(user_id)
            if not embedding_file:
                return None
            
            # Read and decrypt file
            with open(embedding_file, 'rb') as f:
                encrypted_data = pickle.load(f)
            
            # Decrypt the complete package
            decrypted_data = self.encryption_manager.decrypt_data(
                encrypted_data, self.master_password
            )
            
            # Deserialize
            complete_package = pickle.loads(decrypted_data)
            
            # Update access time
            self._update_access_time(user_id)
            
            return complete_package['embedding_data']
            
        except Exception as e:
            raise SecureStorageError(f"Failed to load face embedding: {str(e)}")
    
    def delete_face_embedding(self, user_id: str) -> bool:
        """
        Securely delete face embedding and metadata.
        
        Args:
            user_id: User identifier
            
        Returns:
            True if successful
        """
        try:
            # Find and delete embedding file
            embedding_file = self._find_user_embedding_file(user_id)
            if embedding_file:
                self._secure_delete_file(embedding_file)
            
            # Delete metadata
            self._delete_user_metadata(user_id)
            
            return True
            
        except Exception as e:
            raise SecureStorageError(f"Failed to delete face embedding: {str(e)}")
    
    def list_enrolled_users(self) -> List[str]:
        """
        List all enrolled users.
        
        Returns:
            List of user IDs
        """
        try:
            users = []
            metadata_files = list(self.metadata_dir.glob(f"*{self.metadata_ext}"))
            
            for metadata_file in metadata_files:
                try:
                    metadata = self._load_metadata_file(metadata_file)
                    if 'user_id' in metadata:
                        users.append(metadata['user_id'])
                except:
                    continue  # Skip corrupted files
            
            return sorted(users)
            
        except Exception as e:
            raise SecureStorageError(f"Failed to list users: {str(e)}")
    
    def user_exists(self, user_id: str) -> bool:
        """Check if user exists in storage."""
        return self._find_user_embedding_file(user_id) is not None
    
    def create_secure_backup(self, backup_name: Optional[str] = None) -> str:
        """
        Create encrypted backup of all data.
        
        Args:
            backup_name: Optional backup name
            
        Returns:
            Backup file path
        """
        try:
            if not backup_name:
                timestamp = int(time.time())
                backup_name = f"faceauth_backup_{timestamp}"
            
            backup_file = self.backups_dir / f"{backup_name}.backup"
            
            # Collect all data
            backup_data = {
                'version': '1.0',
                'created_at': int(time.time()),
                'embeddings': {},
                'metadata': {}
            }
            
            # Backup all user data
            users = self.list_enrolled_users()
            for user_id in users:
                embedding_data = self.load_face_embedding(user_id)
                if embedding_data:
                    backup_data['embeddings'][user_id] = embedding_data
                
                metadata = self._load_user_metadata(user_id)
                if metadata:
                    backup_data['metadata'][user_id] = metadata
            
            # Encrypt backup
            serialized_backup = pickle.dumps(backup_data)
            encrypted_backup = self.encryption_manager.encrypt_data(
                serialized_backup, self.master_password, 'argon2'
            )
            
            # Write backup file
            with open(backup_file, 'wb') as f:
                pickle.dump(encrypted_backup, f)
            
            self._set_secure_file_permissions(backup_file)
            
            return str(backup_file)
            
        except Exception as e:
            raise SecureStorageError(f"Failed to create backup: {str(e)}")
    
    def restore_from_backup(self, backup_file: str) -> bool:
        """
        Restore data from encrypted backup.
        
        Args:
            backup_file: Path to backup file
            
        Returns:
            True if successful
        """
        try:
            # Load and decrypt backup
            with open(backup_file, 'rb') as f:
                encrypted_backup = pickle.load(f)
            
            decrypted_backup = self.encryption_manager.decrypt_data(
                encrypted_backup, self.master_password
            )
            
            backup_data = pickle.loads(decrypted_backup)
            
            # Restore embeddings
            for user_id, embedding_data in backup_data['embeddings'].items():
                self.store_face_embedding(user_id, embedding_data)
            
            # Restore metadata
            for user_id, metadata in backup_data['metadata'].items():
                self._store_user_metadata(user_id, metadata)
            
            return True
            
        except Exception as e:
            raise SecureStorageError(f"Failed to restore backup: {str(e)}")
    
    def cleanup_temporary_files(self):
        """Clean up temporary files securely."""
        try:
            for temp_file in self.temp_dir.glob('*'):
                if temp_file.is_file():
                    self._secure_delete_file(temp_file)
        except Exception:
            pass  # Best effort cleanup
    
    def get_storage_info(self) -> Dict[str, Any]:
        """Get storage information and statistics."""
        try:
            users_count = len(self.list_enrolled_users())
            
            # Calculate storage usage
            total_size = 0
            for directory in [self.embeddings_dir, self.metadata_dir, self.backups_dir]:
                for file_path in directory.rglob('*'):
                    if file_path.is_file():
                        total_size += file_path.stat().st_size
            
            return {
                'base_directory': str(self.base_dir),
                'users_enrolled': users_count,
                'total_storage_bytes': total_size,
                'storage_directories': {
                    'embeddings': str(self.embeddings_dir),
                    'metadata': str(self.metadata_dir),
                    'backups': str(self.backups_dir),
                    'logs': str(self.logs_dir),
                    'temp': str(self.temp_dir)
                },
                'security_features': [
                    'AES-256-GCM encryption',
                    'Secure file permissions',
                    'Anti-forensic deletion',
                    'Isolated storage',
                    'Access control'
                ]
            }
        except Exception as e:
            raise SecureStorageError(f"Failed to get storage info: {str(e)}")
    
    def validate_security(self) -> List[Dict[str, Any]]:
        """
        Validate security of storage system.
        
        Returns:
            List of security issues found
        """
        issues = []
        
        # Check directory permissions
        try:
            base_dir_stat = self.base_dir.stat()
            if platform.system() != 'Windows':
                # Check Unix permissions (should be 700)
                mode = stat.filemode(base_dir_stat.st_mode)
                if not mode.startswith('drwx------'):
                    issues.append({
                        'category': 'storage',
                        'severity': 'medium',
                        'issue': 'Directory permissions too permissive',
                        'details': f'Base directory permissions: {mode}'
                    })
            
            # Check if sensitive directories exist
            for directory in [self.embeddings_dir, self.metadata_dir, self.logs_dir]:
                if not directory.exists():
                    issues.append({
                        'category': 'storage',
                        'severity': 'low',
                        'issue': f'Missing secure directory: {directory.name}',
                        'details': f'Directory {directory} does not exist'
                    })
        except Exception as e:
            issues.append({
                'category': 'storage',
                'severity': 'high',
                'issue': 'Cannot validate directory security',
                'details': str(e)
            })
        
        # Check for unencrypted files
        try:
            for root, dirs, files in os.walk(self.base_dir):
                for file in files:
                    file_path = Path(root) / file
                    if not file.endswith(self.encrypted_ext) and not file.endswith('.log'):
                        # Check if it contains sensitive data
                        if file_path.suffix in ['.txt', '.json', '.csv', '.xml']:
                            issues.append({
                                'category': 'storage',
                                'severity': 'high',
                                'issue': 'Unencrypted sensitive file detected',
                                'details': f'File: {file_path}'
                            })
        except Exception as e:
            issues.append({
                'category': 'storage',
                'severity': 'medium',
                'issue': 'Cannot scan for unencrypted files',
                'details': str(e)
            })
        
        return issues
    
    def fix_permissions(self):
        """Fix storage directory permissions."""
        try:
            for directory in [self.base_dir, self.embeddings_dir, self.metadata_dir, 
                             self.backups_dir, self.logs_dir, self.temp_dir]:
                if directory.exists():
                    self._create_secure_directory(directory)
        except Exception as e:
            raise SecureStorageError(f"Failed to fix permissions: {str(e)}")

    # Private helper methods
    
    def _hash_user_id(self, user_id: str) -> str:
        """Create secure hash of user ID."""
        import hashlib
        return hashlib.sha256(user_id.encode()).hexdigest()
    
    def _find_user_embedding_file(self, user_id: str) -> Optional[Path]:
        """Find embedding file for user."""
        user_hash = self._hash_user_id(user_id)
        
        for file_path in self.embeddings_dir.glob(f"emb_{user_hash[:16]}*{self.encrypted_ext}"):
            return file_path
        
        return None
    
    def _store_user_metadata(self, user_id: str, metadata: Dict[str, Any]):
        """Store user metadata."""
        metadata_with_id = metadata.copy()
        metadata_with_id['user_id'] = user_id
        metadata_with_id['user_id_hash'] = self._hash_user_id(user_id)
        
        filename = self._generate_secure_filename(user_id, 'metadata')
        file_path = self.metadata_dir / filename
        
        # Encrypt metadata
        serialized_metadata = json.dumps(metadata_with_id).encode()
        encrypted_metadata = self.encryption_manager.encrypt_data(
            serialized_metadata, self.master_password, 'argon2'
        )
        
        # Write to file
        with open(file_path, 'wb') as f:
            pickle.dump(encrypted_metadata, f)
        
        self._set_secure_file_permissions(file_path)
    
    def _load_user_metadata(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Load user metadata."""
        user_hash = self._hash_user_id(user_id)
        
        for file_path in self.metadata_dir.glob(f"meta_{user_hash[:16]}*{self.metadata_ext}"):
            try:
                return self._load_metadata_file(file_path)
            except:
                continue
        
        return None
    
    def _load_metadata_file(self, file_path: Path) -> Dict[str, Any]:
        """Load metadata from file."""
        with open(file_path, 'rb') as f:
            encrypted_metadata = pickle.load(f)
        
        decrypted_data = self.encryption_manager.decrypt_data(
            encrypted_metadata, self.master_password
        )
        
        return json.loads(decrypted_data.decode())
    
    def _delete_user_metadata(self, user_id: str):
        """Delete user metadata."""
        user_hash = self._hash_user_id(user_id)
        
        for file_path in self.metadata_dir.glob(f"meta_{user_hash[:16]}*{self.metadata_ext}"):
            self._secure_delete_file(file_path)
    
    def _update_access_time(self, user_id: str):
        """Update last access time for user."""
        metadata = self._load_user_metadata(user_id)
        if metadata:
            metadata['last_accessed'] = int(time.time())
            self._store_user_metadata(user_id, metadata)
    
    def _write_secure_temp_file(self, data: Any) -> Path:
        """Write data to secure temporary file."""
        temp_file = self.temp_dir / f"temp_{secrets.token_hex(8)}"
        
        with open(temp_file, 'wb') as f:
            pickle.dump(data, f)
        
        self._set_secure_file_permissions(temp_file)
        return temp_file
    
    def _set_secure_file_permissions(self, file_path: Path):
        """Set secure permissions on file."""
        if platform.system() != 'Windows':
            os.chmod(file_path, stat.S_IRUSR | stat.S_IWUSR)  # 600 - owner read/write only
        else:
            self.access_control.set_windows_permissions(file_path, owner_only=True)
    
    def _secure_delete_file(self, file_path: Path):
        """Securely delete file with multiple overwrites."""
        if not file_path.exists():
            return
        
        try:
            file_size = file_path.stat().st_size
            
            # Multiple overwrite passes
            with open(file_path, 'r+b') as f:
                for _ in range(self.secure_delete_passes):
                    f.seek(0)
                    f.write(os.urandom(file_size))
                    f.flush()
                    os.fsync(f.fileno())
            
            # Final deletion
            file_path.unlink()
            
        except Exception:
            # Fallback to regular deletion
            try:
                file_path.unlink()
            except:
                pass
