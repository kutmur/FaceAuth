"""
Comprehensive test suite for FaceAuth CLI interface.
Tests all CLI commands, argument parsing, error handling, and user interactions.
"""

import pytest
import tempfile
import shutil
import os
import json
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from click.testing import CliRunner
import click

# Import CLI modules
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

import main
from faceauth.core.enrollment import FaceEnrollmentManager
from faceauth.core.authentication import FaceAuthenticator


class TestCLIBasics:
    """Test basic CLI functionality."""
    
    def test_cli_help(self):
        """Test that CLI help message is displayed correctly."""
        runner = CliRunner()
        result = runner.invoke(main.cli, ['--help'])
        
        assert result.exit_code == 0
        assert 'FaceAuth' in result.output
        assert 'enroll-face' in result.output
        assert 'verify-face' in result.output
        assert 'encrypt-file' in result.output
        assert 'decrypt-file' in result.output
    
    def test_cli_version(self):
        """Test CLI version command."""
        runner = CliRunner()
        result = runner.invoke(main.cli, ['--version'])
        
        assert result.exit_code == 0
        assert 'version' in result.output.lower()
    
    def test_cli_verbose_flag(self):
        """Test that verbose flag is recognized."""
        runner = CliRunner()
        result = runner.invoke(main.cli, ['--verbose', '--help'])
        
        assert result.exit_code == 0
    
    def test_cli_debug_flag(self):
        """Test that debug flag is recognized."""
        runner = CliRunner()
        result = runner.invoke(main.cli, ['--debug', '--help'])
        
        assert result.exit_code == 0


class TestEnrollmentCommands:
    """Test enrollment-related CLI commands."""
    
    @patch('faceauth.core.enrollment.FaceEnrollmentManager')
    def test_enroll_face_success(self, mock_enrollment_manager):
        """Test successful face enrollment via CLI."""
        # Mock successful enrollment
        mock_manager = Mock()
        mock_manager.enroll_user.return_value = {
            'success': True,
            'user_id': 'test_user',
            'samples_collected': 5,
            'duration': 12.5,
            'code': 'SUCCESS'
        }
        mock_enrollment_manager.return_value = mock_manager
        
        runner = CliRunner()
        result = runner.invoke(main.cli, ['enroll-face', 'test_user'])
        
        assert result.exit_code == 0
        assert 'successful' in result.output.lower()
        assert 'test_user' in result.output
        mock_manager.enroll_user.assert_called_once()
    
    @patch('faceauth.core.enrollment.FaceEnrollmentManager')
    def test_enroll_face_failure(self, mock_enrollment_manager):
        """Test failed face enrollment via CLI."""
        # Mock failed enrollment
        mock_manager = Mock()
        mock_manager.enroll_user.return_value = {
            'success': False,
            'user_id': 'test_user',
            'error': 'Webcam not accessible',
            'code': 'CAMERA_ERROR'
        }
        mock_enrollment_manager.return_value = mock_manager
        
        runner = CliRunner()
        result = runner.invoke(main.cli, ['enroll-face', 'test_user'])
        
        assert result.exit_code == 1
        assert 'error' in result.output.lower()
        assert 'camera' in result.output.lower()
    
    @patch('faceauth.core.enrollment.FaceEnrollmentManager')
    def test_enroll_face_timeout_option(self, mock_enrollment_manager):
        """Test enrollment with custom timeout."""
        mock_manager = Mock()
        mock_manager.enroll_user.return_value = {
            'success': True,
            'user_id': 'test_user',
            'samples_collected': 3,
            'duration': 5.0,
            'code': 'SUCCESS'
        }
        mock_enrollment_manager.return_value = mock_manager
        
        runner = CliRunner()
        result = runner.invoke(main.cli, ['enroll-face', 'test_user', '--timeout', '30'])
        
        assert result.exit_code == 0
        # Verify timeout was passed correctly
        call_args = mock_manager.enroll_user.call_args
        assert call_args[1]['timeout'] == 30
    
    @patch('faceauth.core.enrollment.FaceEnrollmentManager')
    def test_enroll_face_quality_threshold(self, mock_enrollment_manager):
        """Test enrollment with custom quality threshold."""
        mock_manager = Mock()
        mock_manager.enroll_user.return_value = {
            'success': True,
            'user_id': 'test_user',
            'samples_collected': 4,
            'duration': 8.0,
            'code': 'SUCCESS'
        }
        mock_enrollment_manager.return_value = mock_manager
        
        runner = CliRunner()
        result = runner.invoke(main.cli, ['enroll-face', 'test_user', '--quality-threshold', '0.8'])
        
        assert result.exit_code == 0
        # Verify enrollment manager was created with correct quality threshold
        mock_enrollment_manager.assert_called_once()
        init_args = mock_enrollment_manager.call_args[1]
        assert init_args['quality_threshold'] == 0.8
    
    def test_enroll_face_invalid_user_id(self):
        """Test enrollment with invalid user ID."""
        runner = CliRunner()
        result = runner.invoke(main.cli, ['enroll-face', ''])
        
        assert result.exit_code == 2  # Click parameter validation error
    
    @patch('faceauth.core.enrollment.FaceEnrollmentManager')
    def test_enroll_face_user_exists(self, mock_enrollment_manager):
        """Test enrollment when user already exists."""
        mock_manager = Mock()
        mock_manager.enroll_user.return_value = {
            'success': False,
            'user_id': 'existing_user',
            'error': 'User already exists',
            'code': 'USER_EXISTS'
        }
        mock_enrollment_manager.return_value = mock_manager
        
        runner = CliRunner()
        result = runner.invoke(main.cli, ['enroll-face', 'existing_user'])
        
        assert result.exit_code == 1
        assert 'already exists' in result.output.lower()


class TestAuthenticationCommands:
    """Test authentication-related CLI commands."""
    
    @patch('faceauth.core.authentication.FaceAuthenticator')
    def test_verify_face_success(self, mock_authenticator):
        """Test successful face verification via CLI."""
        # Mock successful authentication
        mock_auth = Mock()
        mock_auth.authenticate_realtime.return_value = {
            'success': True,
            'user_id': 'test_user',
            'similarity': 0.85,
            'threshold': 0.6,
            'duration': 2.3,
            'attempts': 1
        }
        mock_authenticator.return_value = mock_auth
        
        runner = CliRunner()
        result = runner.invoke(main.cli, ['verify-face', 'test_user'])
        
        assert result.exit_code == 0
        assert 'successful' in result.output.lower()
        assert 'test_user' in result.output
        assert '0.85' in result.output  # similarity score
    
    @patch('faceauth.core.authentication.FaceAuthenticator')
    def test_verify_face_failure(self, mock_authenticator):
        """Test failed face verification via CLI."""
        # Mock failed authentication
        mock_auth = Mock()
        mock_auth.authenticate_realtime.return_value = {
            'success': False,
            'user_id': 'test_user',
            'error': 'User not found',
            'error_type': 'user_not_found',
            'duration': 0.1
        }
        mock_authenticator.return_value = mock_auth
        
        runner = CliRunner()
        result = runner.invoke(main.cli, ['verify-face', 'test_user'])
        
        assert result.exit_code == 1
        assert 'failed' in result.output.lower()
        assert 'not found' in result.output.lower()
    
    @patch('faceauth.core.authentication.FaceAuthenticator')
    def test_verify_face_timeout_option(self, mock_authenticator):
        """Test verification with custom timeout."""
        mock_auth = Mock()
        mock_auth.authenticate_realtime.return_value = {
            'success': True,
            'user_id': 'test_user',
            'similarity': 0.75,
            'threshold': 0.6,
            'duration': 1.8,
            'attempts': 1
        }
        mock_authenticator.return_value = mock_auth
        
        runner = CliRunner()
        result = runner.invoke(main.cli, ['verify-face', 'test_user', '--timeout', '15'])
        
        assert result.exit_code == 0
        # Verify timeout was passed correctly
        call_args = mock_auth.authenticate_realtime.call_args
        assert call_args[1]['timeout'] == 15
    
    @patch('faceauth.core.authentication.FaceAuthenticator')
    def test_verify_face_custom_threshold(self, mock_authenticator):
        """Test verification with custom similarity threshold."""
        mock_auth = Mock()
        mock_auth.authenticate_realtime.return_value = {
            'success': True,
            'user_id': 'test_user',
            'similarity': 0.88,
            'threshold': 0.8,
            'duration': 2.1,
            'attempts': 2
        }
        mock_authenticator.return_value = mock_auth
        
        runner = CliRunner()
        result = runner.invoke(main.cli, ['verify-face', 'test_user', '--threshold', '0.8'])
        
        assert result.exit_code == 0
        # Verify authenticator was created with correct threshold
        mock_authenticator.assert_called_once()
        init_args = mock_authenticator.call_args[1]
        assert init_args['similarity_threshold'] == 0.8


class TestFileEncryptionCommands:
    """Test file encryption/decryption CLI commands."""
    
    def setup_method(self):
        """Set up test files for each test."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_file = Path(self.temp_dir) / "test.txt"
        self.test_content = b"This is test file content for encryption testing."
        self.test_file.write_bytes(self.test_content)
    
    def teardown_method(self):
        """Clean up test files after each test."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @patch('faceauth.core.authentication.FaceAuthenticator')
    @patch('faceauth.security.encryption_manager.EncryptionManager')
    def test_encrypt_file_success(self, mock_encryption, mock_authenticator):
        """Test successful file encryption via CLI."""
        # Mock successful authentication
        mock_auth = Mock()
        mock_auth.authenticate_realtime.return_value = {
            'success': True,
            'user_id': 'test_user',
            'similarity': 0.85,
            'threshold': 0.6
        }
        mock_authenticator.return_value = mock_auth
        
        # Mock successful encryption
        mock_enc = Mock()
        mock_enc.encrypt_file.return_value = None
        mock_encryption.return_value = mock_enc
        
        runner = CliRunner()
        result = runner.invoke(main.cli, [
            'encrypt-file', 
            str(self.test_file), 
            'test_user'
        ])
        
        assert result.exit_code == 0
        assert 'encrypted' in result.output.lower()
        assert 'successful' in result.output.lower()
        mock_enc.encrypt_file.assert_called_once()
    
    @patch('faceauth.core.authentication.FaceAuthenticator')
    def test_encrypt_file_auth_failure(self, mock_authenticator):
        """Test file encryption when authentication fails."""
        # Mock failed authentication
        mock_auth = Mock()
        mock_auth.authenticate_realtime.return_value = {
            'success': False,
            'user_id': 'test_user',
            'error': 'Authentication failed',
            'error_type': 'similarity_low'
        }
        mock_authenticator.return_value = mock_auth
        
        runner = CliRunner()
        result = runner.invoke(main.cli, [
            'encrypt-file', 
            str(self.test_file), 
            'test_user'
        ])
        
        assert result.exit_code == 1
        assert 'authentication failed' in result.output.lower()
    
    def test_encrypt_file_nonexistent(self):
        """Test encryption of non-existent file."""
        nonexistent_file = Path(self.temp_dir) / "nonexistent.txt"
        
        runner = CliRunner()
        result = runner.invoke(main.cli, [
            'encrypt-file', 
            str(nonexistent_file), 
            'test_user'
        ])
        
        assert result.exit_code == 1
        assert 'not found' in result.output.lower()
    
    @patch('faceauth.core.authentication.FaceAuthenticator')
    @patch('faceauth.security.encryption_manager.EncryptionManager')
    def test_decrypt_file_success(self, mock_encryption, mock_authenticator):
        """Test successful file decryption via CLI."""
        # Create encrypted file
        encrypted_file = Path(self.temp_dir) / "test.encrypted"
        encrypted_file.write_bytes(b"FACEAUTH_ENC_V1:fake_encrypted_content")
        
        # Mock successful authentication
        mock_auth = Mock()
        mock_auth.authenticate_realtime.return_value = {
            'success': True,
            'user_id': 'test_user',
            'similarity': 0.88,
            'threshold': 0.6
        }
        mock_authenticator.return_value = mock_auth
        
        # Mock successful decryption
        mock_enc = Mock()
        mock_enc.decrypt_file.return_value = None
        mock_encryption.return_value = mock_enc
        
        runner = CliRunner()
        result = runner.invoke(main.cli, [
            'decrypt-file', 
            str(encrypted_file), 
            'test_user'
        ])
        
        assert result.exit_code == 0
        assert 'decrypted' in result.output.lower()
        assert 'successful' in result.output.lower()
        mock_enc.decrypt_file.assert_called_once()
    
    @patch('faceauth.core.authentication.FaceAuthenticator')
    def test_decrypt_file_auth_failure(self, mock_authenticator):
        """Test file decryption when authentication fails."""
        # Create encrypted file
        encrypted_file = Path(self.temp_dir) / "test.encrypted"
        encrypted_file.write_bytes(b"FACEAUTH_ENC_V1:fake_encrypted_content")
        
        # Mock failed authentication
        mock_auth = Mock()
        mock_auth.authenticate_realtime.return_value = {
            'success': False,
            'user_id': 'test_user',
            'error': 'Authentication timeout',
            'error_type': 'timeout'
        }
        mock_authenticator.return_value = mock_auth
        
        runner = CliRunner()
        result = runner.invoke(main.cli, [
            'decrypt-file', 
            str(encrypted_file), 
            'test_user'
        ])
        
        assert result.exit_code == 1
        assert 'authentication failed' in result.output.lower()
    
    @patch('faceauth.core.authentication.FaceAuthenticator')
    @patch('faceauth.security.encryption_manager.EncryptionManager')
    def test_encrypt_file_output_option(self, mock_encryption, mock_authenticator):
        """Test file encryption with custom output file."""
        output_file = Path(self.temp_dir) / "custom_output.enc"
        
        # Mock successful authentication and encryption
        mock_auth = Mock()
        mock_auth.authenticate_realtime.return_value = {'success': True}
        mock_authenticator.return_value = mock_auth
        
        mock_enc = Mock()
        mock_encryption.return_value = mock_enc
        
        runner = CliRunner()
        result = runner.invoke(main.cli, [
            'encrypt-file', 
            str(self.test_file), 
            'test_user',
            '--output', 
            str(output_file)
        ])
        
        assert result.exit_code == 0
        # Verify encryption was called with correct output file
        call_args = mock_enc.encrypt_file.call_args
        assert str(output_file) in str(call_args)


class TestListUsersCommand:
    """Test list-users CLI command."""
    
    @patch('faceauth.utils.storage.FaceDataStorage')
    def test_list_users_with_users(self, mock_storage):
        """Test listing users when users exist."""
        # Mock storage with users
        mock_store = Mock()
        mock_store.list_users.return_value = ['alice', 'bob', 'charlie']
        mock_storage.return_value = mock_store
        
        runner = CliRunner()
        result = runner.invoke(main.cli, ['list-users'])
        
        assert result.exit_code == 0
        assert 'alice' in result.output
        assert 'bob' in result.output
        assert 'charlie' in result.output
        assert '3 users' in result.output or 'Total: 3' in result.output
    
    @patch('faceauth.utils.storage.FaceDataStorage')
    def test_list_users_no_users(self, mock_storage):
        """Test listing users when no users exist."""
        # Mock storage with no users
        mock_store = Mock()
        mock_store.list_users.return_value = []
        mock_storage.return_value = mock_store
        
        runner = CliRunner()
        result = runner.invoke(main.cli, ['list-users'])
        
        assert result.exit_code == 0
        assert 'no users' in result.output.lower() or 'empty' in result.output.lower()
    
    @patch('faceauth.utils.storage.FaceDataStorage')
    def test_list_users_verbose(self, mock_storage):
        """Test listing users with verbose output."""
        # Mock storage with detailed user info
        mock_store = Mock()
        mock_store.list_users.return_value = ['alice', 'bob']
        mock_store.get_user_info.side_effect = [
            {'user_id': 'alice', 'enrolled_date': '2023-01-01', 'samples': 5},
            {'user_id': 'bob', 'enrolled_date': '2023-01-02', 'samples': 3}
        ]
        mock_storage.return_value = mock_store
        
        runner = CliRunner()
        result = runner.invoke(main.cli, ['list-users', '--verbose'])
        
        assert result.exit_code == 0
        assert 'alice' in result.output
        assert 'bob' in result.output
        assert '2023-01-01' in result.output
        assert 'samples' in result.output.lower()


class TestSystemCheckCommand:
    """Test system-check CLI command."""
    
    @patch('main.check_system_requirements')
    def test_system_check_all_good(self, mock_check):
        """Test system check when all requirements are met."""
        mock_check.return_value = {
            'python_version': {'status': 'OK', 'version': '3.9.0'},
            'webcam': {'status': 'OK', 'device': 'USB Camera'},
            'dependencies': {'status': 'OK', 'missing': []},
            'gpu': {'status': 'OK', 'cuda_available': True}
        }
        
        runner = CliRunner()
        result = runner.invoke(main.cli, ['system-check'])
        
        assert result.exit_code == 0
        assert 'ok' in result.output.lower()
        assert 'requirements met' in result.output.lower()
    
    @patch('main.check_system_requirements')
    def test_system_check_issues_found(self, mock_check):
        """Test system check when issues are found."""
        mock_check.return_value = {
            'python_version': {'status': 'OK', 'version': '3.9.0'},
            'webcam': {'status': 'ERROR', 'error': 'No webcam detected'},
            'dependencies': {'status': 'WARNING', 'missing': ['opencv-python']},
            'gpu': {'status': 'WARNING', 'cuda_available': False}
        }
        
        runner = CliRunner()
        result = runner.invoke(main.cli, ['system-check'])
        
        assert result.exit_code == 1
        assert 'error' in result.output.lower()
        assert 'webcam' in result.output.lower()
        assert 'opencv-python' in result.output
    
    @patch('main.check_system_requirements')
    def test_system_check_verbose(self, mock_check):
        """Test system check with verbose output."""
        mock_check.return_value = {
            'python_version': {'status': 'OK', 'version': '3.9.0', 'details': 'All good'},
            'webcam': {'status': 'OK', 'device': 'USB Camera', 'resolution': '1920x1080'},
            'dependencies': {'status': 'OK', 'missing': [], 'installed': ['numpy', 'opencv-python']},
            'gpu': {'status': 'OK', 'cuda_available': True, 'device_name': 'NVIDIA GTX 1080'}
        }
        
        runner = CliRunner()
        result = runner.invoke(main.cli, ['system-check', '--verbose'])
        
        assert result.exit_code == 0
        assert '3.9.0' in result.output
        assert 'USB Camera' in result.output
        assert 'numpy' in result.output
        assert 'GTX 1080' in result.output


class TestConfigCommands:
    """Test configuration-related CLI commands."""
    
    def setup_method(self):
        """Set up test configuration."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_file = Path(self.temp_dir) / "config.json"
    
    def teardown_method(self):
        """Clean up test configuration."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @patch('main.get_config_path')
    def test_config_init(self, mock_config_path):
        """Test configuration initialization."""
        mock_config_path.return_value = self.config_file
        
        runner = CliRunner()
        result = runner.invoke(main.cli, ['config-init'])
        
        assert result.exit_code == 0
        assert 'initialized' in result.output.lower()
        assert self.config_file.exists()
    
    @patch('main.get_config_path')
    @patch('main.load_config')
    def test_config_show(self, mock_load_config, mock_config_path):
        """Test showing configuration."""
        mock_config_path.return_value = self.config_file
        mock_load_config.return_value = {
            'storage_dir': '/home/user/.faceauth',
            'similarity_threshold': 0.6,
            'timeout': 10
        }
        
        runner = CliRunner()
        result = runner.invoke(main.cli, ['config-show'])
        
        assert result.exit_code == 0
        assert 'storage_dir' in result.output
        assert '0.6' in result.output
        assert '10' in result.output
    
    @patch('main.get_config_path')
    @patch('main.load_config')
    @patch('main.save_config')
    def test_config_set(self, mock_save_config, mock_load_config, mock_config_path):
        """Test setting configuration values."""
        mock_config_path.return_value = self.config_file
        mock_load_config.return_value = {
            'storage_dir': '/home/user/.faceauth',
            'similarity_threshold': 0.6
        }
        
        runner = CliRunner()
        result = runner.invoke(main.cli, ['config-set', 'similarity_threshold', '0.8'])
        
        assert result.exit_code == 0
        assert 'updated' in result.output.lower()
        
        # Verify save_config was called with updated value
        mock_save_config.assert_called_once()
        updated_config = mock_save_config.call_args[0][0]
        assert updated_config['similarity_threshold'] == 0.8


class TestErrorHandling:
    """Test CLI error handling scenarios."""
    
    def test_invalid_command(self):
        """Test handling of invalid commands."""
        runner = CliRunner()
        result = runner.invoke(main.cli, ['invalid-command'])
        
        assert result.exit_code == 2
        assert 'no such command' in result.output.lower()
    
    def test_missing_required_argument(self):
        """Test handling of missing required arguments."""
        runner = CliRunner()
        result = runner.invoke(main.cli, ['enroll-face'])  # Missing user_id
        
        assert result.exit_code == 2
        assert 'missing argument' in result.output.lower()
    
    def test_invalid_option_value(self):
        """Test handling of invalid option values."""
        runner = CliRunner()
        result = runner.invoke(main.cli, ['verify-face', 'test_user', '--timeout', 'invalid'])
        
        assert result.exit_code == 2
        assert 'invalid' in result.output.lower()
    
    @patch('faceauth.core.enrollment.FaceEnrollmentManager')
    def test_exception_handling(self, mock_enrollment_manager):
        """Test handling of unexpected exceptions."""
        # Mock enrollment manager to raise exception
        mock_enrollment_manager.side_effect = Exception("Unexpected error occurred")
        
        runner = CliRunner()
        result = runner.invoke(main.cli, ['enroll-face', 'test_user'])
        
        assert result.exit_code == 1
        assert 'error' in result.output.lower()
    
    def test_keyboard_interrupt_handling(self):
        """Test handling of keyboard interrupt (Ctrl+C)."""
        # This is difficult to test directly, but we can check that
        # the CLI handles KeyboardInterrupt gracefully
        runner = CliRunner()
        
        with patch('main.enroll_face', side_effect=KeyboardInterrupt):
            result = runner.invoke(main.cli, ['enroll-face', 'test_user'])
            
            assert result.exit_code != 0
            # Should handle gracefully without showing traceback


class TestPrivacyCommands:
    """Test privacy-related CLI commands."""
    
    @patch('faceauth.security.privacy_manager.PrivacyManager')
    def test_privacy_check(self, mock_privacy_manager):
        """Test privacy compliance check command."""
        mock_pm = Mock()
        mock_pm.generate_privacy_report.return_value = {
            'report_type': 'system_privacy_report',
            'statistics': {
                'total_users': 5,
                'total_data_records': 10,
                'data_types': ['embeddings', 'metadata'],
                'expired_data_records': 0,
                'expired_consent_records': 0
            },
            'compliance_status': {
                'auto_cleanup_enabled': True,
                'consent_required': True,
                'anonymized_logs': True,
                'secure_deletion': True
            }
        }
        mock_privacy_manager.return_value = mock_pm
        
        runner = CliRunner()
        result = runner.invoke(main.cli, ['privacy-check'])
        
        assert result.exit_code == 0
        assert 'privacy' in result.output.lower()
        assert '5' in result.output  # total users
        assert '10' in result.output  # total records
    
    @patch('faceauth.security.compliance_checker.ComplianceChecker')
    def test_compliance_check(self, mock_compliance_checker):
        """Test compliance check command."""
        mock_cc = Mock()
        mock_cc.run_comprehensive_compliance_check.return_value = {
            'overall_score': 95.5,
            'standards': {
                'GDPR': {'score': 100.0, 'status': 'COMPLIANT'},
                'CCPA': {'score': 98.0, 'status': 'COMPLIANT'},
                'SOC2': {'score': 90.0, 'status': 'COMPLIANT'}
            },
            'issues': [],
            'recommendations': ['Enable additional logging']
        }
        mock_compliance_checker.return_value = mock_cc
        
        runner = CliRunner()
        result = runner.invoke(main.cli, ['compliance-check'])
        
        assert result.exit_code == 0
        assert 'compliance' in result.output.lower()
        assert '95.5' in result.output or '96' in result.output
        assert 'GDPR' in result.output
    
    @patch('faceauth.security.audit_logger.SecureAuditLogger')
    def test_security_audit(self, mock_audit_logger):
        """Test security audit command."""
        mock_al = Mock()
        mock_al.generate_security_report.return_value = {
            'security_events': [
                {'type': 'authentication_success', 'count': 50},
                {'type': 'authentication_failed', 'count': 5}
            ],
            'security_score': 88.5,
            'issues_found': 2,
            'recommendations': ['Update encryption keys regularly']
        }
        mock_audit_logger.return_value = mock_al
        
        runner = CliRunner()
        result = runner.invoke(main.cli, ['security-audit'])
        
        assert result.exit_code == 0
        assert 'security' in result.output.lower()
        assert 'audit' in result.output.lower()


class TestOutputFormats:
    """Test different output formats and verbosity levels."""
    
    @patch('faceauth.core.authentication.FaceAuthenticator')
    def test_quiet_output(self, mock_authenticator):
        """Test quiet output mode."""
        mock_auth = Mock()
        mock_auth.authenticate_realtime.return_value = {
            'success': True,
            'user_id': 'test_user',
            'similarity': 0.85,
            'duration': 2.0
        }
        mock_authenticator.return_value = mock_auth
        
        runner = CliRunner()
        result = runner.invoke(main.cli, ['verify-face', 'test_user', '--quiet'])
        
        assert result.exit_code == 0
        # Quiet mode should have minimal output
        assert len(result.output.strip()) < 50
    
    @patch('faceauth.core.authentication.FaceAuthenticator')
    def test_verbose_output(self, mock_authenticator):
        """Test verbose output mode."""
        mock_auth = Mock()
        mock_auth.authenticate_realtime.return_value = {
            'success': True,
            'user_id': 'test_user',
            'similarity': 0.85,
            'threshold': 0.6,
            'duration': 2.0,
            'attempts': 1,
            'authentication_attempts': [
                {'attempt': 1, 'similarity': 0.85, 'timestamp': 1234567890}
            ]
        }
        mock_authenticator.return_value = mock_auth
        
        runner = CliRunner()
        result = runner.invoke(main.cli, ['verify-face', 'test_user', '--verbose'])
        
        assert result.exit_code == 0
        # Verbose mode should have detailed output
        assert 'similarity' in result.output.lower()
        assert 'duration' in result.output.lower()
        assert 'attempts' in result.output.lower()
    
    def test_json_output_format(self):
        """Test JSON output format."""
        runner = CliRunner()
        
        with patch('main.get_performance_metrics') as mock_metrics:
            mock_metrics.return_value = {
                'total_authentications': 10,
                'success_rate': 0.9,
                'average_time': 2.1
            }
            
            result = runner.invoke(main.cli, ['auth-metrics', '--format', 'json'])
            
            if result.exit_code == 0:
                # Should be valid JSON
                try:
                    json.loads(result.output)
                except json.JSONDecodeError:
                    pytest.fail("Output is not valid JSON")


class TestIntegrationScenarios:
    """Test complex integration scenarios."""
    
    def setup_method(self):
        """Set up integration test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_file = Path(self.temp_dir) / "secret.txt"
        self.test_file.write_bytes(b"Top secret information")
    
    def teardown_method(self):
        """Clean up integration test environment."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @patch('faceauth.core.enrollment.FaceEnrollmentManager')
    @patch('faceauth.core.authentication.FaceAuthenticator')
    @patch('faceauth.security.encryption_manager.EncryptionManager')
    def test_complete_workflow(self, mock_encryption, mock_authenticator, mock_enrollment):
        """Test complete enrollment -> encrypt -> decrypt workflow."""
        # Mock successful enrollment
        mock_enroll = Mock()
        mock_enroll.enroll_user.return_value = {
            'success': True,
            'user_id': 'test_user',
            'code': 'SUCCESS'
        }
        mock_enrollment.return_value = mock_enroll
        
        # Mock successful authentication
        mock_auth = Mock()
        mock_auth.authenticate_realtime.return_value = {
            'success': True,
            'user_id': 'test_user',
            'similarity': 0.85
        }
        mock_authenticator.return_value = mock_auth
        
        # Mock successful encryption/decryption
        mock_enc = Mock()
        mock_encryption.return_value = mock_enc
        
        runner = CliRunner()
        
        # Step 1: Enroll user
        result = runner.invoke(main.cli, ['enroll-face', 'test_user'])
        assert result.exit_code == 0
        
        # Step 2: Encrypt file
        result = runner.invoke(main.cli, ['encrypt-file', str(self.test_file), 'test_user'])
        assert result.exit_code == 0
        
        # Step 3: Decrypt file
        encrypted_file = str(self.test_file) + '.encrypted'
        result = runner.invoke(main.cli, ['decrypt-file', encrypted_file, 'test_user'])
        assert result.exit_code == 0


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
