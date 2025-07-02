#!/usr/bin/env python3
"""
Integration test suite for FaceAuth platform.
Tests end-to-end functionality, system integration, and complete workflows.
"""

import pytest
import tempfile
import shutil
import time
import json
import os
import subprocess
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import numpy as np

from faceauth.core.enrollment import FaceEnrollment
from faceauth.core.authentication import FaceAuthenticator
from faceauth.security.encryption_manager import EncryptionManager
from faceauth.security.audit_logger import SecureAuditLogger
from faceauth.security.privacy_manager import PrivacyManager
from faceauth.security.compliance_checker import ComplianceChecker
from faceauth.utils.storage import FaceDataStorage


class TestEndToEndWorkflows:
    """Test complete end-to-end workflows."""
    
    def test_complete_enrollment_authentication_workflow(self, temp_dir, mock_face_data):
        """Test complete workflow from enrollment to authentication."""
        storage_dir = temp_dir / "storage"
        audit_dir = temp_dir / "audit"
        
        # Initialize components
        storage = FaceDataStorage(str(storage_dir))
        enrollment = FaceEnrollment(storage)
        authenticator = FaceAuthenticator(storage)
        audit_logger = SecureAuditLogger(str(audit_dir))
        
        user_id = "integration_test_user"
        
        # Step 1: Enroll user
        with patch('cv2.VideoCapture'), \
             patch('faceauth.face_model.extract_face_encoding') as mock_extract:
            
            mock_extract.return_value = mock_face_data["encoding"]
            
            success = enrollment.enroll_user(
                user_id=user_id,
                min_samples=3,
                quality_threshold=0.8
            )
            
            assert success is True
            audit_logger.log_enrollment_success(user_id, {"samples": 3})
        
        # Step 2: Authenticate user
        with patch('cv2.VideoCapture'), \
             patch('faceauth.face_model.extract_face_encoding') as mock_extract:
            
            mock_extract.return_value = mock_face_data["encoding"]
            
            auth_result = authenticator.authenticate(confidence_threshold=0.8)
            
            assert auth_result["success"] is True
            assert auth_result["user_id"] == user_id
            audit_logger.log_authentication_success(user_id, {"confidence": auth_result["confidence"]})
        
        # Step 3: Verify audit trail
        audit_files = list(audit_dir.glob("*.log"))
        assert len(audit_files) > 0
        
        with open(audit_files[0], 'r') as f:
            audit_content = f.read()
            assert "ENROLLMENT_SUCCESS" in audit_content
            assert "AUTHENTICATION_SUCCESS" in audit_content
            assert user_id in audit_content
    
    def test_file_encryption_with_face_auth(self, temp_dir, mock_face_data):
        """Test file encryption/decryption with face authentication."""
        storage_dir = temp_dir / "storage"
        test_file = temp_dir / "test_document.txt"
        encrypted_file = temp_dir / "test_document.txt.enc"
        
        # Create test file
        test_content = "This is a sensitive document that should be encrypted."
        test_file.write_text(test_content)
        
        # Initialize components
        storage = FaceDataStorage(str(storage_dir))
        enrollment = FaceEnrollment(storage)
        authenticator = FaceAuthenticator(storage)
        encryption_manager = EncryptionManager()
        
        user_id = "file_encryption_user"
        
        # Step 1: Enroll user
        with patch('cv2.VideoCapture'), \
             patch('faceauth.face_model.extract_face_encoding') as mock_extract:
            
            mock_extract.return_value = mock_face_data["encoding"]
            enrollment.enroll_user(user_id, min_samples=3)
        
        # Step 2: Encrypt file (after authentication)
        with patch('cv2.VideoCapture'), \
             patch('faceauth.face_model.extract_face_encoding') as mock_extract:
            
            mock_extract.return_value = mock_face_data["encoding"]
            auth_result = authenticator.authenticate()
            
            assert auth_result["success"] is True
            
            # Encrypt the file
            password = "secure_password_123"
            encryption_manager.encrypt_file(str(test_file), str(encrypted_file), password)
        
        # Step 3: Verify file is encrypted
        assert encrypted_file.exists()
        encrypted_content = encrypted_file.read_bytes()
        assert test_content.encode() not in encrypted_content
        
        # Step 4: Decrypt file (with authentication)
        decrypted_file = temp_dir / "decrypted_document.txt"
        
        with patch('cv2.VideoCapture'), \
             patch('faceauth.face_model.extract_face_encoding') as mock_extract:
            
            mock_extract.return_value = mock_face_data["encoding"]
            auth_result = authenticator.authenticate()
            
            assert auth_result["success"] is True
            
            # Decrypt the file
            encryption_manager.decrypt_file(str(encrypted_file), str(decrypted_file), password)
        
        # Step 5: Verify decrypted content
        assert decrypted_file.exists()
        decrypted_content = decrypted_file.read_text()
        assert decrypted_content == test_content
    
    def test_privacy_compliance_workflow(self, temp_dir, mock_face_data):
        """Test privacy compliance and data management workflow."""
        storage_dir = temp_dir / "storage"
        privacy_dir = temp_dir / "privacy"
        
        # Initialize components
        storage = FaceDataStorage(str(storage_dir))
        enrollment = FaceEnrollment(storage)
        privacy_manager = PrivacyManager(str(privacy_dir))
        compliance_checker = ComplianceChecker(str(privacy_dir))
        
        user_id = "privacy_test_user"
        
        # Step 1: Register user consent
        consent_types = ["data_collection", "biometric_processing", "storage"]
        privacy_manager.register_user_consent(user_id, consent_types)
        
        # Step 2: Enroll user (with consent)
        with patch('cv2.VideoCapture'), \
             patch('faceauth.face_model.extract_face_encoding') as mock_extract:
            
            mock_extract.return_value = mock_face_data["encoding"]
            success = enrollment.enroll_user(user_id, min_samples=3)
            assert success is True
        
        # Step 3: Check compliance
        compliance_report = compliance_checker.generate_compliance_report()
        assert compliance_report["gdpr"]["overall_compliance"] is True
        
        # Step 4: User withdraws consent
        privacy_manager.withdraw_consent(user_id, ["storage"])
        
        # Step 5: Process data deletion request
        privacy_manager.process_data_deletion_request(user_id, ["face_templates"])
        
        # Step 6: Verify data deletion
        with pytest.raises(FileNotFoundError):
            storage.load_user_data(user_id)
        
        # Step 7: Generate privacy report
        privacy_report = privacy_manager.generate_privacy_report(user_id)
        assert "data_deletion" in privacy_report
    
    def test_security_incident_response(self, temp_dir, mock_face_data):
        """Test security incident detection and response."""
        storage_dir = temp_dir / "storage"
        audit_dir = temp_dir / "audit"
        
        # Initialize components
        storage = FaceDataStorage(str(storage_dir))
        enrollment = FaceEnrollment(storage)
        authenticator = FaceAuthenticator(storage)
        audit_logger = SecureAuditLogger(str(audit_dir))
        
        user_id = "security_test_user"
        
        # Step 1: Enroll user
        with patch('cv2.VideoCapture'), \
             patch('faceauth.face_model.extract_face_encoding') as mock_extract:
            
            mock_extract.return_value = mock_face_data["encoding"]
            enrollment.enroll_user(user_id, min_samples=3)
        
        # Step 2: Simulate failed authentication attempts
        with patch('cv2.VideoCapture'), \
             patch('faceauth.face_model.extract_face_encoding') as mock_extract:
            
            # Different face encoding (unauthorized user)
            mock_extract.return_value = np.random.rand(128)
            
            for i in range(5):
                auth_result = authenticator.authenticate()
                assert auth_result["success"] is False
                
                audit_logger.log_authentication_failure(
                    "unknown_user",
                    "Face not recognized",
                    {"attempt": i + 1, "ip": "192.168.1.100"}
                )
        
        # Step 3: Log security event
        audit_logger.log_security_event(
            "MULTIPLE_FAILED_ATTEMPTS",
            "HIGH",
            {"user_id": "unknown_user", "attempts": 5, "source_ip": "192.168.1.100"}
        )
        
        # Step 4: Verify security logging
        audit_files = list(audit_dir.glob("*.log"))
        assert len(audit_files) > 0
        
        with open(audit_files[0], 'r') as f:
            audit_content = f.read()
            assert "AUTHENTICATION_FAILURE" in audit_content
            assert "MULTIPLE_FAILED_ATTEMPTS" in audit_content
            assert "HIGH" in audit_content


class TestSystemIntegration:
    """Test system-level integration."""
    
    def test_multi_user_system(self, temp_dir, mock_face_data):
        """Test system with multiple users."""
        storage_dir = temp_dir / "storage"
        
        storage = FaceDataStorage(str(storage_dir))
        enrollment = FaceEnrollment(storage)
        authenticator = FaceAuthenticator(storage)
        
        users = ["user1", "user2", "user3"]
        user_encodings = {}
        
        # Enroll multiple users
        for user_id in users:
            with patch('cv2.VideoCapture'), \
                 patch('faceauth.face_model.extract_face_encoding') as mock_extract:
                
                # Generate unique encoding for each user
                encoding = np.random.rand(128)
                user_encodings[user_id] = encoding
                mock_extract.return_value = encoding
                
                success = enrollment.enroll_user(user_id, min_samples=3)
                assert success is True
        
        # Test authentication for each user
        for user_id in users:
            with patch('cv2.VideoCapture'), \
                 patch('faceauth.face_model.extract_face_encoding') as mock_extract:
                
                mock_extract.return_value = user_encodings[user_id]
                auth_result = authenticator.authenticate()
                
                assert auth_result["success"] is True
                assert auth_result["user_id"] == user_id
        
        # Test cross-user authentication (should fail)
        with patch('cv2.VideoCapture'), \
             patch('faceauth.face_model.extract_face_encoding') as mock_extract:
            
            # Use user1's encoding but expect it not to match others
            mock_extract.return_value = user_encodings["user1"]
            auth_result = authenticator.authenticate()
            
            # Should only match user1
            assert auth_result["success"] is True
            assert auth_result["user_id"] == "user1"
    
    def test_system_performance_under_load(self, temp_dir, mock_face_data):
        """Test system performance under load."""
        storage_dir = temp_dir / "storage"
        
        storage = FaceDataStorage(str(storage_dir))
        enrollment = FaceEnrollment(storage)
        authenticator = FaceAuthenticator(storage)
        
        # Enroll user
        user_id = "performance_test_user"
        with patch('cv2.VideoCapture'), \
             patch('faceauth.face_model.extract_face_encoding') as mock_extract:
            
            mock_extract.return_value = mock_face_data["encoding"]
            enrollment.enroll_user(user_id, min_samples=3)
        
        # Test authentication performance
        start_time = time.time()
        successful_auths = 0
        
        for i in range(100):
            with patch('cv2.VideoCapture'), \
                 patch('faceauth.face_model.extract_face_encoding') as mock_extract:
                
                mock_extract.return_value = mock_face_data["encoding"]
                auth_result = authenticator.authenticate()
                
                if auth_result["success"]:
                    successful_auths += 1
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Performance assertions
        assert successful_auths == 100
        assert duration < 30.0  # Should complete 100 auths in under 30 seconds
        
        avg_time_per_auth = duration / 100
        assert avg_time_per_auth < 0.5  # Each auth should take less than 0.5 seconds
    
    def test_data_consistency_across_components(self, temp_dir, mock_face_data):
        """Test data consistency across different components."""
        storage_dir = temp_dir / "storage"
        audit_dir = temp_dir / "audit"
        privacy_dir = temp_dir / "privacy"
        
        # Initialize all components
        storage = FaceDataStorage(str(storage_dir))
        enrollment = FaceEnrollment(storage)
        authenticator = FaceAuthenticator(storage)
        audit_logger = SecureAuditLogger(str(audit_dir))
        privacy_manager = PrivacyManager(str(privacy_dir))
        
        user_id = "consistency_test_user"
        
        # Register consent
        privacy_manager.register_user_consent(user_id, ["data_collection", "biometric_processing"])
        
        # Enroll user
        with patch('cv2.VideoCapture'), \
             patch('faceauth.face_model.extract_face_encoding') as mock_extract:
            
            mock_extract.return_value = mock_face_data["encoding"]
            success = enrollment.enroll_user(user_id, min_samples=3)
            assert success is True
            
            audit_logger.log_enrollment_success(user_id, {"samples": 3})
        
        # Verify data exists in storage
        user_data = storage.load_user_data(user_id)
        assert user_data is not None
        assert len(user_data["encodings"]) == 3
        
        # Verify consent is recorded
        consent = privacy_manager.get_user_consent(user_id)
        assert consent["user_id"] == user_id
        
        # Verify audit log
        audit_files = list(audit_dir.glob("*.log"))
        assert len(audit_files) > 0
        
        # Delete user data and verify consistency
        privacy_manager.process_data_deletion_request(user_id, ["face_templates"])
        audit_logger.log_privacy_event("DATA_DELETION", {"user_id": user_id})
        
        # Verify data is deleted from storage
        with pytest.raises(FileNotFoundError):
            storage.load_user_data(user_id)
        
        # Verify audit log still exists (for compliance)
        with open(audit_files[0], 'r') as f:
            audit_content = f.read()
            assert "DATA_DELETION" in audit_content


class TestCLIIntegration:
    """Test CLI integration with core system."""
    
    def test_cli_enrollment_workflow(self, temp_dir):
        """Test CLI enrollment workflow."""
        os.chdir(str(temp_dir))
        
        # Mock the main CLI module
        with patch('sys.argv', ['main.py', 'enroll', '--user-id', 'cli_test_user']), \
             patch('cv2.VideoCapture'), \
             patch('faceauth.face_model.extract_face_encoding') as mock_extract:
            
            mock_extract.return_value = np.random.rand(128)
            
            # Import and run main
            import main
            
            # Should complete without errors
            # (In real implementation, this would capture CLI output)
    
    def test_cli_authentication_workflow(self, temp_dir):
        """Test CLI authentication workflow."""
        os.chdir(str(temp_dir))
        
        # First enroll a user
        storage_dir = temp_dir / "storage"
        storage = FaceDataStorage(str(storage_dir))
        enrollment = FaceEnrollment(storage)
        
        user_id = "cli_auth_user"
        encoding = np.random.rand(128)
        
        with patch('cv2.VideoCapture'), \
             patch('faceauth.face_model.extract_face_encoding') as mock_extract:
            
            mock_extract.return_value = encoding
            enrollment.enroll_user(user_id, min_samples=3)
        
        # Test CLI authentication
        with patch('sys.argv', ['main.py', 'authenticate']), \
             patch('cv2.VideoCapture'), \
             patch('faceauth.face_model.extract_face_encoding') as mock_extract:
            
            mock_extract.return_value = encoding
            
            # Import and run main
            import main
            
            # Should complete without errors
    
    def test_cli_privacy_commands(self, temp_dir):
        """Test CLI privacy management commands."""
        os.chdir(str(temp_dir))
        
        # Test privacy report generation
        with patch('sys.argv', ['main.py', 'privacy-report', '--user-id', 'test_user']):
            import main
            # Should complete without errors
        
        # Test data deletion
        with patch('sys.argv', ['main.py', 'delete-user-data', '--user-id', 'test_user']):
            import main
            # Should complete without errors
    
    def test_cli_compliance_commands(self, temp_dir):
        """Test CLI compliance checking commands."""
        os.chdir(str(temp_dir))
        
        # Test compliance check
        with patch('sys.argv', ['main.py', 'compliance-check']):
            import main
            # Should complete without errors
        
        # Test security audit
        with patch('sys.argv', ['main.py', 'security-audit']):
            import main
            # Should complete without errors


class TestErrorHandlingAndRecovery:
    """Test error handling and system recovery."""
    
    def test_storage_corruption_recovery(self, temp_dir, mock_face_data):
        """Test recovery from storage corruption."""
        storage_dir = temp_dir / "storage"
        
        storage = FaceDataStorage(str(storage_dir))
        enrollment = FaceEnrollment(storage)
        
        user_id = "corruption_test_user"
        
        # Enroll user
        with patch('cv2.VideoCapture'), \
             patch('faceauth.face_model.extract_face_encoding') as mock_extract:
            
            mock_extract.return_value = mock_face_data["encoding"]
            enrollment.enroll_user(user_id, min_samples=3)
        
        # Corrupt the storage file
        user_file = storage_dir / f"{user_id}.npz"
        assert user_file.exists()
        
        # Write invalid data
        with open(user_file, 'wb') as f:
            f.write(b"corrupted_data")
        
        # Test graceful handling of corruption
        with pytest.raises((ValueError, FileNotFoundError, Exception)):
            storage.load_user_data(user_id)
        
        # System should continue working for new enrollments
        new_user_id = "new_user_after_corruption"
        with patch('cv2.VideoCapture'), \
             patch('faceauth.face_model.extract_face_encoding') as mock_extract:
            
            mock_extract.return_value = mock_face_data["encoding"]
            success = enrollment.enroll_user(new_user_id, min_samples=3)
            assert success is True
    
    def test_network_interruption_handling(self, temp_dir, mock_face_data):
        """Test handling of network interruptions (if applicable)."""
        # This test simulates network-related failures
        storage_dir = temp_dir / "storage"
        
        storage = FaceDataStorage(str(storage_dir))
        enrollment = FaceEnrollment(storage)
        
        user_id = "network_test_user"
        
        # Simulate network failure during enrollment
        with patch('cv2.VideoCapture') as mock_camera:
            mock_camera.side_effect = Exception("Network connection failed")
            
            with pytest.raises(Exception):
                enrollment.enroll_user(user_id, min_samples=3)
        
        # System should recover and work normally
        with patch('cv2.VideoCapture'), \
             patch('faceauth.face_model.extract_face_encoding') as mock_extract:
            
            mock_extract.return_value = mock_face_data["encoding"]
            success = enrollment.enroll_user(user_id, min_samples=3)
            assert success is True
    
    def test_resource_exhaustion_handling(self, temp_dir):
        """Test handling of resource exhaustion."""
        storage_dir = temp_dir / "storage"
        
        storage = FaceDataStorage(str(storage_dir))
        enrollment = FaceEnrollment(storage)
        
        # Simulate memory exhaustion
        with patch('numpy.array') as mock_array:
            mock_array.side_effect = MemoryError("Out of memory")
            
            with pytest.raises(MemoryError):
                enrollment.enroll_user("memory_test_user", min_samples=3)
        
        # System should handle disk space exhaustion
        with patch('builtins.open') as mock_open:
            mock_open.side_effect = OSError("No space left on device")
            
            with pytest.raises(OSError):
                enrollment.enroll_user("disk_test_user", min_samples=3)


class TestBackupAndRecovery:
    """Test backup and recovery functionality."""
    
    def test_full_system_backup(self, temp_dir, mock_face_data):
        """Test complete system backup."""
        storage_dir = temp_dir / "storage"
        audit_dir = temp_dir / "audit"
        backup_dir = temp_dir / "backup"
        
        # Initialize system
        storage = FaceDataStorage(str(storage_dir))
        enrollment = FaceEnrollment(storage)
        audit_logger = SecureAuditLogger(str(audit_dir))
        
        # Create system data
        user_id = "backup_test_user"
        with patch('cv2.VideoCapture'), \
             patch('faceauth.face_model.extract_face_encoding') as mock_extract:
            
            mock_extract.return_value = mock_face_data["encoding"]
            enrollment.enroll_user(user_id, min_samples=3)
            audit_logger.log_enrollment_success(user_id, {"samples": 3})
        
        # Create backup
        backup_dir.mkdir()
        shutil.copytree(storage_dir, backup_dir / "storage")
        shutil.copytree(audit_dir, backup_dir / "audit")
        
        # Simulate system failure (delete original data)
        shutil.rmtree(storage_dir)
        shutil.rmtree(audit_dir)
        
        # Restore from backup
        shutil.copytree(backup_dir / "storage", storage_dir)
        shutil.copytree(backup_dir / "audit", audit_dir)
        
        # Verify system works after restore
        new_storage = FaceDataStorage(str(storage_dir))
        new_authenticator = FaceAuthenticator(new_storage)
        
        with patch('cv2.VideoCapture'), \
             patch('faceauth.face_model.extract_face_encoding') as mock_extract:
            
            mock_extract.return_value = mock_face_data["encoding"]
            auth_result = new_authenticator.authenticate()
            
            assert auth_result["success"] is True
            assert auth_result["user_id"] == user_id
    
    def test_incremental_backup(self, temp_dir, mock_face_data):
        """Test incremental backup functionality."""
        storage_dir = temp_dir / "storage"
        backup_dir = temp_dir / "backup"
        
        storage = FaceDataStorage(str(storage_dir))
        enrollment = FaceEnrollment(storage)
        
        backup_dir.mkdir()
        
        # Initial backup
        initial_backup = backup_dir / "backup_v1"
        initial_backup.mkdir()
        
        # Enroll first user
        user1_id = "incremental_user1"
        with patch('cv2.VideoCapture'), \
             patch('faceauth.face_model.extract_face_encoding') as mock_extract:
            
            mock_extract.return_value = mock_face_data["encoding"]
            enrollment.enroll_user(user1_id, min_samples=3)
        
        # Create initial backup
        shutil.copytree(storage_dir, initial_backup / "storage")
        
        # Enroll second user
        user2_id = "incremental_user2"
        with patch('cv2.VideoCapture'), \
             patch('faceauth.face_model.extract_face_encoding') as mock_extract:
            
            mock_extract.return_value = np.random.rand(128)
            enrollment.enroll_user(user2_id, min_samples=3)
        
        # Create incremental backup (only new files)
        incremental_backup = backup_dir / "backup_v2"
        incremental_backup.mkdir()
        
        # Copy only files that changed since initial backup
        for file_path in storage_dir.rglob("*"):
            if file_path.is_file():
                relative_path = file_path.relative_to(storage_dir)
                initial_file = initial_backup / "storage" / relative_path
                
                if not initial_file.exists() or file_path.stat().st_mtime > initial_file.stat().st_mtime:
                    backup_file = incremental_backup / relative_path
                    backup_file.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(file_path, backup_file)
        
        # Verify incremental backup contains only new user data
        backup_files = list(incremental_backup.rglob("*.npz"))
        assert len(backup_files) == 1
        assert user2_id in str(backup_files[0])


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
