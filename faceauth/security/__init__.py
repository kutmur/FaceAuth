"""
FaceAuth Security Module

This module provides comprehensive security and privacy protection for the FaceAuth system.
All components are designed with privacy-first principles and local-only data handling.

Key Security Features:
- Encrypted storage for all sensitive data
- Secure memory management with automatic cleanup
- Anti-forensic measures and secure deletion
- Access control and file permissions
- Secure logging with privacy protection
- Cryptographic key management
- Compliance verification tools

Privacy Guarantees:
- All data remains local to the user's machine
- No network requests or cloud dependencies
- Face images are never stored (only encrypted embeddings)
- Secure deletion of temporary files and memory
- Protection against memory dumps and swap exposure
"""

from .encryption_manager import EncryptionManager
from .secure_storage import SecureStorage
from .memory_manager import SecureMemoryManager
from .access_control import AccessControlManager
from .audit_logger import SecureAuditLogger
from .privacy_manager import PrivacyManager
from .compliance_checker import ComplianceChecker

__all__ = [
    'EncryptionManager',
    'SecureStorage', 
    'SecureMemoryManager',
    'AccessControlManager',
    'SecureAuditLogger',
    'PrivacyManager',
    'ComplianceChecker'
]

# Security module version for compatibility tracking
__version__ = '1.0.0'
__security_level__ = 'ENTERPRISE_GRADE'
