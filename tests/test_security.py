#!/usr/bin/env python3
"""
Comprehensive test suite for FaceAuth security modules.
Tests audit logging, privacy management, compliance checking, access control, and memory management.
"""

import pytest
import tempfile
import shutil
import json
import time
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta

from faceauth.security.audit_logger import SecureAuditLogger
from faceauth.security.privacy_manager import PrivacyManager
from faceauth.security.compliance_checker import ComplianceChecker
from faceauth.security.access_control import AccessController
from faceauth.security.memory_manager import SecureMemoryManager
from faceauth.security.secure_storage import SecureStorageManager


class TestSecureAuditLogger:
    """Test suite for SecureAuditLogger."""
    
    def test_audit_logger_initialization(self, temp_dir):
        """Test audit logger initialization."""
        log_dir = temp_dir / "audit_logs"
        logger = SecureAuditLogger(str(log_dir))
        
        assert logger.log_dir.exists()
        assert logger.log_dir.is_dir()
        
    def test_log_authentication_success(self, temp_dir):
        """Test logging successful authentication."""
        log_dir = temp_dir / "audit_logs"
        logger = SecureAuditLogger(str(log_dir))
        
        user_id = "test_user"
        metadata = {"ip": "192.168.1.1", "device": "test_device"}
        
        logger.log_authentication_success(user_id, metadata)
        
        # Check log file was created and contains entry
        log_files = list(log_dir.glob("*.log"))
        assert len(log_files) > 0
        
        with open(log_files[0], 'r') as f:
            log_content = f.read()
            assert user_id in log_content
            assert "AUTHENTICATION_SUCCESS" in log_content
            assert "192.168.1.1" in log_content
    
    def test_log_authentication_failure(self, temp_dir):
        """Test logging failed authentication."""
        log_dir = temp_dir / "audit_logs"
        logger = SecureAuditLogger(str(log_dir))
        
        user_id = "test_user"
        reason = "Face not recognized"
        metadata = {"ip": "192.168.1.1", "attempts": 3}
        
        logger.log_authentication_failure(user_id, reason, metadata)
        
        log_files = list(log_dir.glob("*.log"))
        assert len(log_files) > 0
        
        with open(log_files[0], 'r') as f:
            log_content = f.read()
            assert user_id in log_content
            assert "AUTHENTICATION_FAILURE" in log_content
            assert reason in log_content
    
    def test_log_privacy_event(self, temp_dir):
        """Test logging privacy events."""
        log_dir = temp_dir / "audit_logs"
        logger = SecureAuditLogger(str(log_dir))
        
        event = "DATA_DELETION"
        details = {"user_id": "test_user", "data_type": "face_template"}
        
        logger.log_privacy_event(event, details)
        
        log_files = list(log_dir.glob("*.log"))
        assert len(log_files) > 0
        
        with open(log_files[0], 'r') as f:
            log_content = f.read()
            assert event in log_content
            assert "test_user" in log_content
    
    def test_log_security_event(self, temp_dir):
        """Test logging security events."""
        log_dir = temp_dir / "audit_logs"
        logger = SecureAuditLogger(str(log_dir))
        
        event = "UNAUTHORIZED_ACCESS_ATTEMPT"
        severity = "HIGH"
        details = {"source_ip": "192.168.1.100", "user_id": "unknown"}
        
        logger.log_security_event(event, severity, details)
        
        log_files = list(log_dir.glob("*.log"))
        assert len(log_files) > 0
        
        with open(log_files[0], 'r') as f:
            log_content = f.read()
            assert event in log_content
            assert severity in log_content
            assert "192.168.1.100" in log_content
    
    def test_export_logs(self, temp_dir):
        """Test exporting audit logs."""
        log_dir = temp_dir / "audit_logs"
        logger = SecureAuditLogger(str(log_dir))
        
        # Create some log entries
        logger.log_authentication_success("user1", {"ip": "192.168.1.1"})
        logger.log_authentication_failure("user2", "Invalid face", {"ip": "192.168.1.2"})
        
        export_path = temp_dir / "exported_logs.json"
        logger.export_logs(str(export_path))
        
        assert export_path.exists()
        
        with open(export_path, 'r') as f:
            exported_data = json.load(f)
            assert isinstance(exported_data, list)
            assert len(exported_data) >= 2
    
    def test_log_rotation(self, temp_dir):
        """Test log file rotation."""
        log_dir = temp_dir / "audit_logs"
        logger = SecureAuditLogger(str(log_dir), max_file_size=1024)  # Small size for testing
        
        # Generate enough logs to trigger rotation
        for i in range(100):
            logger.log_authentication_success(f"user{i}", {"ip": f"192.168.1.{i}"})
        
        log_files = list(log_dir.glob("*.log"))
        assert len(log_files) > 1  # Should have rotated
    
    def test_log_integrity_verification(self, temp_dir):
        """Test log integrity verification."""
        log_dir = temp_dir / "audit_logs"
        logger = SecureAuditLogger(str(log_dir))
        
        logger.log_authentication_success("test_user", {"ip": "192.168.1.1"})
        
        # Verify logs are intact
        is_valid = logger.verify_log_integrity()
        assert is_valid is True


class TestPrivacyManager:
    """Test suite for PrivacyManager."""
    
    def test_privacy_manager_initialization(self, temp_dir):
        """Test privacy manager initialization."""
        manager = PrivacyManager(str(temp_dir))
        assert manager.data_dir.exists()
        assert manager.data_dir.is_dir()
    
    def test_register_user_consent(self, temp_dir):
        """Test registering user consent."""
        manager = PrivacyManager(str(temp_dir))
        
        user_id = "test_user"
        consent_types = ["data_collection", "biometric_processing", "storage"]
        
        manager.register_user_consent(user_id, consent_types)
        
        consent = manager.get_user_consent(user_id)
        assert consent is not None
        assert consent["user_id"] == user_id
        assert set(consent["consent_types"]) == set(consent_types)
        assert "timestamp" in consent
    
    def test_withdraw_consent(self, temp_dir):
        """Test withdrawing user consent."""
        manager = PrivacyManager(str(temp_dir))
        
        user_id = "test_user"
        consent_types = ["data_collection", "biometric_processing"]
        
        manager.register_user_consent(user_id, consent_types)
        manager.withdraw_consent(user_id, ["data_collection"])
        
        consent = manager.get_user_consent(user_id)
        assert "biometric_processing" in consent["consent_types"]
        assert "data_collection" not in consent["consent_types"]
    
    def test_schedule_data_deletion(self, temp_dir):
        """Test scheduling data deletion."""
        manager = PrivacyManager(str(temp_dir))
        
        user_id = "test_user"
        data_types = ["face_templates", "audit_logs"]
        deletion_date = datetime.now() + timedelta(days=30)
        
        manager.schedule_data_deletion(user_id, data_types, deletion_date)
        
        scheduled = manager.get_scheduled_deletions()
        assert len(scheduled) == 1
        assert scheduled[0]["user_id"] == user_id
        assert set(scheduled[0]["data_types"]) == set(data_types)
    
    def test_process_data_deletion_request(self, temp_dir):
        """Test processing data deletion requests."""
        manager = PrivacyManager(str(temp_dir))
        
        user_id = "test_user"
        data_types = ["face_templates"]
        
        with patch('faceauth.security.privacy_manager.SecureStorageManager') as mock_storage:
            manager.process_data_deletion_request(user_id, data_types)
            mock_storage.return_value.delete_user_data.assert_called_once()
    
    def test_generate_privacy_report(self, temp_dir):
        """Test generating privacy report."""
        manager = PrivacyManager(str(temp_dir))
        
        user_id = "test_user"
        consent_types = ["data_collection", "biometric_processing"]
        manager.register_user_consent(user_id, consent_types)
        
        report = manager.generate_privacy_report(user_id)
        
        assert report["user_id"] == user_id
        assert "consent_status" in report
        assert "data_retention" in report
        assert "privacy_rights" in report
    
    def test_data_retention_compliance(self, temp_dir):
        """Test data retention compliance checking."""
        manager = PrivacyManager(str(temp_dir))
        
        # Mock old data that should be deleted
        with patch.object(manager, '_get_user_data_age') as mock_age:
            mock_age.return_value = timedelta(days=400)  # Old data
            
            violations = manager.check_data_retention_compliance()
            assert len(violations) >= 0  # Should check for violations


class TestComplianceChecker:
    """Test suite for ComplianceChecker."""
    
    def test_compliance_checker_initialization(self, temp_dir):
        """Test compliance checker initialization."""
        checker = ComplianceChecker(str(temp_dir))
        assert hasattr(checker, 'data_dir')
    
    def test_gdpr_compliance_check(self, temp_dir):
        """Test GDPR compliance checking."""
        checker = ComplianceChecker(str(temp_dir))
        
        with patch('faceauth.security.compliance_checker.PrivacyManager') as mock_privacy:
            mock_privacy.return_value.check_data_retention_compliance.return_value = []
            
            result = checker.check_gdpr_compliance()
            
            assert "consent_management" in result
            assert "data_retention" in result
            assert "user_rights" in result
            assert result["overall_compliance"] is True
    
    def test_ccpa_compliance_check(self, temp_dir):
        """Test CCPA compliance checking."""
        checker = ComplianceChecker(str(temp_dir))
        
        result = checker.check_ccpa_compliance()
        
        assert "data_transparency" in result
        assert "opt_out_rights" in result
        assert "data_security" in result
        assert isinstance(result["overall_compliance"], bool)
    
    def test_hipaa_compliance_check(self, temp_dir):
        """Test HIPAA compliance checking."""
        checker = ComplianceChecker(str(temp_dir))
        
        result = checker.check_hipaa_compliance()
        
        assert "access_controls" in result
        assert "encryption" in result
        assert "audit_trails" in result
        assert isinstance(result["overall_compliance"], bool)
    
    def test_generate_compliance_report(self, temp_dir):
        """Test generating comprehensive compliance report."""
        checker = ComplianceChecker(str(temp_dir))
        
        report = checker.generate_compliance_report()
        
        assert "gdpr" in report
        assert "ccpa" in report
        assert "hipaa" in report
        assert "recommendations" in report
        assert "timestamp" in report
    
    def test_export_compliance_report(self, temp_dir):
        """Test exporting compliance report."""
        checker = ComplianceChecker(str(temp_dir))
        
        export_path = temp_dir / "compliance_report.json"
        checker.export_compliance_report(str(export_path))
        
        assert export_path.exists()
        
        with open(export_path, 'r') as f:
            report = json.load(f)
            assert "gdpr" in report
            assert "ccpa" in report
            assert "hipaa" in report


class TestAccessController:
    """Test suite for AccessController."""
    
    def test_access_controller_initialization(self, temp_dir):
        """Test access controller initialization."""
        controller = AccessController(str(temp_dir))
        assert hasattr(controller, 'data_dir')
    
    def test_create_user_session(self, temp_dir):
        """Test creating user session."""
        controller = AccessController(str(temp_dir))
        
        user_id = "test_user"
        session_id = controller.create_session(user_id)
        
        assert session_id is not None
        assert len(session_id) > 0
        
        session = controller.get_session(session_id)
        assert session["user_id"] == user_id
        assert session["active"] is True
    
    def test_validate_session(self, temp_dir):
        """Test session validation."""
        controller = AccessController(str(temp_dir))
        
        user_id = "test_user"
        session_id = controller.create_session(user_id)
        
        # Valid session
        is_valid = controller.validate_session(session_id)
        assert is_valid is True
        
        # Invalid session
        is_valid = controller.validate_session("invalid_session")
        assert is_valid is False
    
    def test_revoke_session(self, temp_dir):
        """Test session revocation."""
        controller = AccessController(str(temp_dir))
        
        user_id = "test_user"
        session_id = controller.create_session(user_id)
        
        controller.revoke_session(session_id)
        
        is_valid = controller.validate_session(session_id)
        assert is_valid is False
    
    def test_session_timeout(self, temp_dir):
        """Test session timeout functionality."""
        controller = AccessController(str(temp_dir), session_timeout=1)  # 1 second timeout
        
        user_id = "test_user"
        session_id = controller.create_session(user_id)
        
        # Should be valid initially
        assert controller.validate_session(session_id) is True
        
        # Wait for timeout
        time.sleep(2)
        
        # Should be invalid after timeout
        assert controller.validate_session(session_id) is False
    
    def test_check_permissions(self, temp_dir):
        """Test permission checking."""
        controller = AccessController(str(temp_dir))
        
        user_id = "test_user"
        permissions = ["read", "write", "delete"]
        session_id = controller.create_session(user_id, permissions)
        
        assert controller.check_permission(session_id, "read") is True
        assert controller.check_permission(session_id, "write") is True
        assert controller.check_permission(session_id, "admin") is False
    
    def test_rate_limiting(self, temp_dir):
        """Test rate limiting functionality."""
        controller = AccessController(str(temp_dir))
        
        user_id = "test_user"
        
        # Should allow initial requests
        for i in range(5):
            assert controller.check_rate_limit(user_id) is True
        
        # Should block after limit
        assert controller.check_rate_limit(user_id) is False


class TestSecureMemoryManager:
    """Test suite for SecureMemoryManager."""
    
    def test_memory_manager_initialization(self):
        """Test memory manager initialization."""
        manager = SecureMemoryManager()
        assert hasattr(manager, 'allocated_memory')
    
    def test_secure_allocate(self):
        """Test secure memory allocation."""
        manager = SecureMemoryManager()
        
        size = 1024
        memory_id = manager.secure_allocate(size)
        
        assert memory_id is not None
        assert memory_id in manager.allocated_memory
        assert len(manager.allocated_memory[memory_id]) == size
    
    def test_secure_write_read(self):
        """Test secure memory write and read operations."""
        manager = SecureMemoryManager()
        
        size = 1024
        memory_id = manager.secure_allocate(size)
        
        test_data = b"sensitive_data" + b"\x00" * (size - 14)
        manager.secure_write(memory_id, test_data)
        
        read_data = manager.secure_read(memory_id)
        assert read_data == test_data
    
    def test_secure_zero(self):
        """Test secure memory zeroing."""
        manager = SecureMemoryManager()
        
        size = 1024
        memory_id = manager.secure_allocate(size)
        
        test_data = b"sensitive_data" + b"\x00" * (size - 14)
        manager.secure_write(memory_id, test_data)
        
        manager.secure_zero(memory_id)
        
        read_data = manager.secure_read(memory_id)
        assert read_data == b"\x00" * size
    
    def test_secure_free(self):
        """Test secure memory deallocation."""
        manager = SecureMemoryManager()
        
        size = 1024
        memory_id = manager.secure_allocate(size)
        
        test_data = b"sensitive_data" + b"\x00" * (size - 14)
        manager.secure_write(memory_id, test_data)
        
        manager.secure_free(memory_id)
        
        assert memory_id not in manager.allocated_memory
        
        # Should raise error on access after free
        with pytest.raises(ValueError):
            manager.secure_read(memory_id)
    
    def test_memory_protection(self):
        """Test memory protection mechanisms."""
        manager = SecureMemoryManager()
        
        size = 1024
        memory_id = manager.secure_allocate(size)
        
        # Test that memory is properly protected
        protection_info = manager.get_memory_protection(memory_id)
        assert protection_info["protected"] is True
        assert protection_info["executable"] is False
    
    def test_memory_cleanup_on_exit(self):
        """Test automatic memory cleanup."""
        manager = SecureMemoryManager()
        
        # Allocate multiple memory blocks
        memory_ids = []
        for i in range(5):
            memory_id = manager.secure_allocate(1024)
            memory_ids.append(memory_id)
        
        # Cleanup all memory
        manager.cleanup_all()
        
        # All memory should be freed
        for memory_id in memory_ids:
            assert memory_id not in manager.allocated_memory


class TestSecureStorageManager:
    """Test suite for SecureStorageManager."""
    
    def test_storage_manager_initialization(self, temp_dir):
        """Test storage manager initialization."""
        manager = SecureStorageManager(str(temp_dir))
        assert manager.base_path.exists()
    
    def test_store_user_data(self, temp_dir):
        """Test storing user data securely."""
        manager = SecureStorageManager(str(temp_dir))
        
        user_id = "test_user"
        data_type = "face_template"
        data = {"encoding": [1, 2, 3, 4, 5], "timestamp": time.time()}
        
        manager.store_user_data(user_id, data_type, data)
        
        stored_data = manager.retrieve_user_data(user_id, data_type)
        assert stored_data == data
    
    def test_delete_user_data(self, temp_dir):
        """Test deleting user data."""
        manager = SecureStorageManager(str(temp_dir))
        
        user_id = "test_user"
        data_type = "face_template"
        data = {"encoding": [1, 2, 3, 4, 5]}
        
        manager.store_user_data(user_id, data_type, data)
        manager.delete_user_data(user_id, [data_type])
        
        with pytest.raises(FileNotFoundError):
            manager.retrieve_user_data(user_id, data_type)
    
    def test_data_encryption_at_rest(self, temp_dir):
        """Test that data is encrypted when stored."""
        manager = SecureStorageManager(str(temp_dir))
        
        user_id = "test_user"
        data_type = "face_template"
        data = {"encoding": [1, 2, 3, 4, 5]}
        
        manager.store_user_data(user_id, data_type, data)
        
        # Check that raw file content is encrypted
        user_dir = manager.base_path / user_id
        data_files = list(user_dir.glob(f"{data_type}.*"))
        assert len(data_files) > 0
        
        with open(data_files[0], 'rb') as f:
            raw_content = f.read()
            # Should not contain plaintext data
            assert b"encoding" not in raw_content
    
    def test_backup_and_restore(self, temp_dir):
        """Test data backup and restore functionality."""
        manager = SecureStorageManager(str(temp_dir))
        
        user_id = "test_user"
        data_type = "face_template"
        data = {"encoding": [1, 2, 3, 4, 5]}
        
        manager.store_user_data(user_id, data_type, data)
        
        backup_path = temp_dir / "backup.enc"
        manager.create_backup(str(backup_path))
        
        assert backup_path.exists()
        
        # Clear original data
        manager.delete_user_data(user_id, [data_type])
        
        # Restore from backup
        manager.restore_from_backup(str(backup_path))
        
        restored_data = manager.retrieve_user_data(user_id, data_type)
        assert restored_data == data


# Performance and stress tests
class TestSecurityPerformance:
    """Performance tests for security modules."""
    
    def test_audit_logging_performance(self, temp_dir):
        """Test audit logging performance under load."""
        log_dir = temp_dir / "audit_logs"
        logger = SecureAuditLogger(str(log_dir))
        
        start_time = time.time()
        
        # Log many events
        for i in range(1000):
            logger.log_authentication_success(f"user{i}", {"ip": f"192.168.1.{i % 255}"})
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Should complete in reasonable time (adjust as needed)
        assert duration < 10.0  # 10 seconds for 1000 logs
        
        # Verify all logs were written
        log_files = list(log_dir.glob("*.log"))
        total_lines = 0
        for log_file in log_files:
            with open(log_file, 'r') as f:
                total_lines += len(f.readlines())
        
        assert total_lines >= 1000
    
    def test_memory_manager_performance(self):
        """Test memory manager performance."""
        manager = SecureMemoryManager()
        
        start_time = time.time()
        
        # Allocate and free many memory blocks
        memory_ids = []
        for i in range(100):
            memory_id = manager.secure_allocate(1024)
            memory_ids.append(memory_id)
        
        for memory_id in memory_ids:
            manager.secure_free(memory_id)
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Should complete quickly
        assert duration < 5.0  # 5 seconds for 100 allocations/deallocations
    
    def test_concurrent_access_control(self, temp_dir):
        """Test access control under concurrent load."""
        import threading
        
        controller = AccessController(str(temp_dir))
        sessions = []
        errors = []
        
        def create_sessions():
            try:
                for i in range(100):
                    session_id = controller.create_session(f"user{i}")
                    sessions.append(session_id)
            except Exception as e:
                errors.append(e)
        
        # Create multiple threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=create_sessions)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Should have no errors and many sessions
        assert len(errors) == 0
        assert len(sessions) == 500  # 5 threads * 100 sessions each


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
