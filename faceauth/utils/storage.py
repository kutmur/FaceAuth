"""
Storage utilities for FaceAuth system.
Handles local storage and retrieval of face embeddings and user data.
"""

import os
import json
import pickle
import time
from typing import Dict, List, Optional, Any
from pathlib import Path
import numpy as np
from .security import SecurityManager


class FaceDataStorage:
    """Manages local storage of face embeddings and user data."""
    
    def __init__(self, storage_dir: str = None, security_manager: SecurityManager = None):
        """
        Initialize storage manager.
        
        Args:
            storage_dir: Directory for storing face data. Defaults to ~/.faceauth/data
            security_manager: Security manager for encryption
        """
        if storage_dir is None:
            storage_dir = os.path.join(os.path.expanduser("~"), ".faceauth", "data")
        
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        self.security_manager = security_manager or SecurityManager()
        
        # Set restrictive permissions
        os.chmod(str(self.storage_dir), 0o700)
        
        # Metadata file for user information
        self.metadata_file = self.storage_dir / "users.metadata"
        
    def save_user_enrollment(self, user_id: str, embedding: np.ndarray, 
                           metadata: Dict[str, Any] = None) -> bool:
        """
        Save user face embedding and metadata.
        
        Args:
            user_id: Unique user identifier
            embedding: Face embedding vector
            metadata: Additional user metadata
            
        Returns:
            True if successful
        """
        try:
            # Generate secure filename
            filename = self.security_manager.generate_secure_filename(user_id)
            filepath = self.storage_dir / filename
            
            # Encrypt the embedding
            encrypted_embedding = self.security_manager.encrypt_embedding(embedding)
            
            # Prepare user data
            user_data = {
                'user_id_hash': self.security_manager.hash_user_id(user_id),
                'embedding': encrypted_embedding,
                'enrollment_time': time.time(),
                'metadata': metadata or {}
            }
            
            # Serialize and obfuscate data
            serialized_data = pickle.dumps(user_data)
            obfuscated_data = self.security_manager.obfuscate_data(serialized_data)
            
            # Write to file
            with open(filepath, 'wb') as f:
                f.write(obfuscated_data)
            
            # Set restrictive permissions
            os.chmod(str(filepath), 0o600)
            
            # Update metadata index
            self._update_user_metadata(user_id, filename, metadata)
            
            return True
            
        except Exception as e:
            print(f"Error saving user enrollment: {e}")
            return False
    
    def load_user_embedding(self, user_id: str) -> Optional[np.ndarray]:
        """
        Load user face embedding.
        
        Args:
            user_id: User identifier
            
        Returns:
            Face embedding if found, None otherwise
        """
        try:
            # Find user file
            filename = self._find_user_file(user_id)
            if not filename:
                return None
            
            filepath = self.storage_dir / filename
            
            # Read and deobfuscate data
            with open(filepath, 'rb') as f:
                obfuscated_data = f.read()
            
            serialized_data = self.security_manager.deobfuscate_data(obfuscated_data)
            user_data = pickle.loads(serialized_data)
            
            # Decrypt embedding
            encrypted_embedding = user_data['embedding']
            embedding = self.security_manager.decrypt_embedding(encrypted_embedding)
            
            return embedding
            
        except Exception as e:
            print(f"Error loading user embedding: {e}")
            return None
    
    def user_exists(self, user_id: str) -> bool:
        """
        Check if user is enrolled in the system.
        
        Args:
            user_id: User identifier
            
        Returns:
            True if user exists
        """
        return self._find_user_file(user_id) is not None
    
    def list_enrolled_users(self) -> List[str]:
        """
        Get list of enrolled user IDs.
        
        Returns:
            List of user IDs
        """
        try:
            if not self.metadata_file.exists():
                return []
            
            with open(self.metadata_file, 'r') as f:
                metadata = json.load(f)
            
            return list(metadata.get('users', {}).keys())
            
        except Exception:
            return []
    
    def delete_user_enrollment(self, user_id: str) -> bool:
        """
        Delete user enrollment data.
        
        Args:
            user_id: User identifier
            
        Returns:
            True if successful
        """
        try:
            filename = self._find_user_file(user_id)
            if not filename:
                return False
            
            filepath = self.storage_dir / filename
            
            # Secure delete the file
            from .security import secure_delete_file
            success = secure_delete_file(str(filepath))
            
            if success:
                # Remove from metadata
                self._remove_user_metadata(user_id)
            
            return success
            
        except Exception as e:
            print(f"Error deleting user enrollment: {e}")
            return False
    
    def get_user_metadata(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get user metadata.
        
        Args:
            user_id: User identifier
            
        Returns:
            User metadata if found
        """
        try:
            if not self.metadata_file.exists():
                return None
            
            with open(self.metadata_file, 'r') as f:
                metadata = json.load(f)
            
            users = metadata.get('users', {})
            user_info = users.get(user_id)
            
            if user_info:
                return user_info.get('metadata', {})
            
            return None
            
        except Exception:
            return None
    
    def _find_user_file(self, user_id: str) -> Optional[str]:
        """Find the storage file for a user."""
        try:
            if not self.metadata_file.exists():
                return None
            
            with open(self.metadata_file, 'r') as f:
                metadata = json.load(f)
            
            users = metadata.get('users', {})
            user_info = users.get(user_id)
            
            if user_info:
                filename = user_info['filename']
                if (self.storage_dir / filename).exists():
                    return filename
            
            return None
            
        except Exception:
            return None
    
    def _update_user_metadata(self, user_id: str, filename: str, 
                            user_metadata: Dict[str, Any] = None):
        """Update the user metadata index."""
        try:
            # Load existing metadata
            if self.metadata_file.exists():
                with open(self.metadata_file, 'r') as f:
                    metadata = json.load(f)
            else:
                metadata = {'users': {}, 'created': time.time()}
            
            # Update user info
            metadata['users'][user_id] = {
                'filename': filename,
                'enrollment_time': time.time(),
                'metadata': user_metadata or {}
            }
            
            metadata['last_updated'] = time.time()
            
            # Save metadata
            with open(self.metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            # Set restrictive permissions
            os.chmod(str(self.metadata_file), 0o600)
            
        except Exception as e:
            print(f"Error updating metadata: {e}")
    
    def _remove_user_metadata(self, user_id: str):
        """Remove user from metadata index."""
        try:
            if not self.metadata_file.exists():
                return
            
            with open(self.metadata_file, 'r') as f:
                metadata = json.load(f)
            
            users = metadata.get('users', {})
            if user_id in users:
                del users[user_id]
                metadata['last_updated'] = time.time()
                
                with open(self.metadata_file, 'w') as f:
                    json.dump(metadata, f, indent=2)
                    
        except Exception as e:
            print(f"Error removing user metadata: {e}")
    
    def get_storage_stats(self) -> Dict[str, Any]:
        """Get storage statistics."""
        try:
            stats = {
                'storage_dir': str(self.storage_dir),
                'total_users': len(self.list_enrolled_users()),
                'storage_size_bytes': 0,
                'files': []
            }
            
            # Calculate storage size
            for file_path in self.storage_dir.rglob('*'):
                if file_path.is_file():
                    size = file_path.stat().st_size
                    stats['storage_size_bytes'] += size
                    stats['files'].append({
                        'name': file_path.name,
                        'size_bytes': size,
                        'modified': file_path.stat().st_mtime
                    })
            
            return stats
            
        except Exception as e:
            return {'error': str(e)}


class BackupManager:
    """Manages backup and restore of face data."""
    
    def __init__(self, storage: FaceDataStorage):
        """Initialize backup manager."""
        self.storage = storage
    
    def create_backup(self, backup_path: str) -> bool:
        """
        Create encrypted backup of all face data.
        
        Args:
            backup_path: Path for backup file
            
        Returns:
            True if successful
        """
        try:
            import zipfile
            import tempfile
            
            backup_data = {
                'users': {},
                'created': time.time(),
                'version': '1.0'
            }
            
            # Collect all user data
            for user_id in self.storage.list_enrolled_users():
                embedding = self.storage.load_user_embedding(user_id)
                metadata = self.storage.get_user_metadata(user_id)
                
                if embedding is not None:
                    backup_data['users'][user_id] = {
                        'embedding': embedding.tolist(),  # Convert to list for JSON
                        'metadata': metadata
                    }
            
            # Create encrypted backup
            with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
                json.dump(backup_data, temp_file, indent=2)
                temp_path = temp_file.name
            
            # Encrypt and compress
            encrypted_data = self.storage.security_manager.encrypt_embedding(
                np.array(open(temp_path, 'rb').read())
            )
            
            with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                zipf.writestr('faceauth_backup.enc', encrypted_data)
            
            # Clean up temp file
            os.unlink(temp_path)
            
            return True
            
        except Exception as e:
            print(f"Error creating backup: {e}")
            return False
    
    def restore_backup(self, backup_path: str) -> bool:
        """
        Restore face data from encrypted backup.
        
        Args:
            backup_path: Path to backup file
            
        Returns:
            True if successful
        """
        try:
            import zipfile
            import tempfile
            
            # Extract and decrypt backup
            with zipfile.ZipFile(backup_path, 'r') as zipf:
                encrypted_data = zipf.read('faceauth_backup.enc')
            
            decrypted_bytes = self.storage.security_manager.decrypt_embedding(encrypted_data)
            
            # Load backup data
            with tempfile.NamedTemporaryFile(mode='w+b', delete=False) as temp_file:
                temp_file.write(decrypted_bytes.tobytes())
                temp_path = temp_file.name
            
            with open(temp_path, 'r') as f:
                backup_data = json.load(f)
            
            # Restore users
            success_count = 0
            for user_id, user_data in backup_data['users'].items():
                embedding = np.array(user_data['embedding'], dtype=np.float32)
                metadata = user_data.get('metadata', {})
                
                if self.storage.save_user_enrollment(user_id, embedding, metadata):
                    success_count += 1
            
            # Clean up temp file
            os.unlink(temp_path)
            
            print(f"Restored {success_count} users from backup")
            return success_count > 0
            
        except Exception as e:
            print(f"Error restoring backup: {e}")
            return False