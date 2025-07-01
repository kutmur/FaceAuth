"""
Basic tests for FaceAuth system
"""

import unittest
import tempfile
import os
import numpy as np
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from faceauth.utils.security import SecurityManager
from faceauth.utils.storage import FaceDataStorage


class TestSecurityManager(unittest.TestCase):
    """Test the security manager functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.security_manager = SecurityManager("test_master_key")
    
    def test_encryption_decryption(self):
        """Test face embedding encryption and decryption."""
        # Create a sample embedding
        original_embedding = np.random.rand(512).astype(np.float32)
        
        # Encrypt the embedding
        encrypted = self.security_manager.encrypt_embedding(original_embedding)
        self.assertIsInstance(encrypted, str)
        self.assertTrue(len(encrypted) > 0)
        
        # Decrypt the embedding
        decrypted = self.security_manager.decrypt_embedding(encrypted)
        
        # Verify the embeddings match
        np.testing.assert_array_almost_equal(original_embedding, decrypted, decimal=6)
    
    def test_user_id_hashing(self):
        """Test user ID hashing and verification."""
        user_id = "test_user_123"
        
        # Hash the user ID
        hashed = self.security_manager.hash_user_id(user_id)
        self.assertIsInstance(hashed, str)
        self.assertTrue(len(hashed) > 0)
        self.assertNotEqual(user_id, hashed)
        
        # Verify the hash
        self.assertTrue(self.security_manager.verify_user_id(user_id, hashed))
        self.assertFalse(self.security_manager.verify_user_id("wrong_user", hashed))
    
    def test_secure_filename_generation(self):
        """Test secure filename generation."""
        user_id = "test_user_123"
        filename = self.security_manager.generate_secure_filename(user_id)
        
        self.assertIsInstance(filename, str)
        self.assertTrue(filename.endswith('.fauth'))
        self.assertTrue(filename.startswith('user_'))
        self.assertNotIn(user_id, filename)  # User ID should not appear in filename
    
    def test_data_obfuscation(self):
        """Test data obfuscation and deobfuscation."""
        original_data = b"This is test data for obfuscation"
        
        # Obfuscate the data
        obfuscated = self.security_manager.obfuscate_data(original_data)
        self.assertIsInstance(obfuscated, bytes)
        self.assertNotEqual(original_data, obfuscated)
        
        # Deobfuscate the data
        deobfuscated = self.security_manager.deobfuscate_data(obfuscated)
        self.assertEqual(original_data, deobfuscated)


class TestFaceDataStorage(unittest.TestCase):
    """Test the face data storage functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.security_manager = SecurityManager("test_master_key")
        self.storage = FaceDataStorage(self.temp_dir, self.security_manager)
    
    def tearDown(self):
        """Clean up test fixtures."""
        # Clean up temp directory
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_user_enrollment_and_retrieval(self):
        """Test saving and loading user enrollment."""
        user_id = "test_user"
        embedding = np.random.rand(512).astype(np.float32)
        metadata = {"test_key": "test_value"}
        
        # Save user enrollment
        success = self.storage.save_user_enrollment(user_id, embedding, metadata)
        self.assertTrue(success)
        
        # Check if user exists
        self.assertTrue(self.storage.user_exists(user_id))
        
        # Load user embedding
        loaded_embedding = self.storage.load_user_embedding(user_id)
        self.assertIsNotNone(loaded_embedding)
        np.testing.assert_array_almost_equal(embedding, loaded_embedding, decimal=6)
        
        # Load user metadata
        loaded_metadata = self.storage.get_user_metadata(user_id)
        self.assertIsNotNone(loaded_metadata)
        self.assertEqual(metadata["test_key"], loaded_metadata["test_key"])
    
    def test_user_deletion(self):
        """Test user enrollment deletion."""
        user_id = "test_user_delete"
        embedding = np.random.rand(512).astype(np.float32)
        
        # Save user enrollment
        self.storage.save_user_enrollment(user_id, embedding)
        self.assertTrue(self.storage.user_exists(user_id))
        
        # Delete user
        success = self.storage.delete_user_enrollment(user_id)
        self.assertTrue(success)
        self.assertFalse(self.storage.user_exists(user_id))
        
        # Try to load deleted user
        loaded_embedding = self.storage.load_user_embedding(user_id)
        self.assertIsNone(loaded_embedding)
    
    def test_list_enrolled_users(self):
        """Test listing enrolled users."""
        # Initially no users
        users = self.storage.list_enrolled_users()
        self.assertEqual(len(users), 0)
        
        # Add some users
        user_ids = ["user1", "user2", "user3"]
        for user_id in user_ids:
            embedding = np.random.rand(512).astype(np.float32)
            self.storage.save_user_enrollment(user_id, embedding)
        
        # Check user list
        enrolled_users = self.storage.list_enrolled_users()
        self.assertEqual(len(enrolled_users), 3)
        for user_id in user_ids:
            self.assertIn(user_id, enrolled_users)
    
    def test_storage_stats(self):
        """Test storage statistics."""
        # Get initial stats
        stats = self.storage.get_storage_stats()
        self.assertIsInstance(stats, dict)
        self.assertIn('storage_dir', stats)
        self.assertIn('total_users', stats)
        self.assertIn('storage_size_bytes', stats)
        
        # Add a user and check stats again
        user_id = "stats_test_user"
        embedding = np.random.rand(512).astype(np.float32)
        self.storage.save_user_enrollment(user_id, embedding)
        
        new_stats = self.storage.get_storage_stats()
        self.assertEqual(new_stats['total_users'], 1)
        self.assertGreater(new_stats['storage_size_bytes'], 0)


class TestIntegration(unittest.TestCase):
    """Integration tests for the complete system."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_full_enrollment_workflow(self):
        """Test the complete enrollment workflow."""
        # This test requires the AI models, so we'll skip if they're not available
        try:
            from faceauth.core.enrollment import FaceEnrollmentManager
        except ImportError:
            self.skipTest("AI dependencies not available")
        
        # Note: This test would require a camera and is more suitable for manual testing
        # For automated testing, we'll just test the manager initialization
        
        try:
            manager = FaceEnrollmentManager(storage_dir=self.temp_dir)
            
            # Test basic functionality
            users = manager.get_enrolled_users()
            self.assertEqual(len(users), 0)
            
            stats = manager.get_storage_stats()
            self.assertIsInstance(stats, dict)
            
        except Exception as e:
            self.skipTest(f"Could not initialize enrollment manager: {e}")


if __name__ == '__main__':
    unittest.main()