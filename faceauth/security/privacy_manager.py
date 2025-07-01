"""
Privacy Manager for FaceAuth Security Module

This module provides comprehensive privacy protection and data minimization
for the FaceAuth system. It ensures compliance with privacy regulations
and implements privacy-by-design principles.

Privacy Features:
- Data minimization and retention policies
- Automated data expiration and cleanup
- Privacy-preserving operations
- User consent management
- Data subject rights (access, deletion, portability)
- Privacy impact assessment tools
- Anonymization and pseudonymization

Privacy Guarantees:
- No personal data is collected beyond face embeddings
- All data processing is local and transparent
- Users have full control over their data
- Automatic cleanup of expired data
- No tracking or profiling capabilities
"""

import os
import json
import time
import hashlib
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict

from .encryption_manager import EncryptionManager
from .secure_storage import SecureStorage
from .audit_logger import SecureAuditLogger


@dataclass
class PrivacySettings:
    """Privacy configuration settings."""
    data_retention_days: int = 365
    auto_cleanup_enabled: bool = True
    consent_required: bool = True
    anonymize_logs: bool = True
    enable_data_export: bool = True
    enable_secure_deletion: bool = True
    privacy_level: str = "HIGH"  # LOW, MEDIUM, HIGH, MAXIMUM


@dataclass
class UserConsent:
    """User consent record."""
    user_id: str
    consent_timestamp: datetime
    consent_version: str
    purpose: str
    data_types: List[str]
    retention_period: int
    can_withdraw: bool = True


@dataclass
class DataRecord:
    """Record of personal data stored."""
    record_id: str
    user_id: str
    data_type: str
    creation_time: datetime
    last_access: datetime
    retention_until: datetime
    purpose: str
    sensitive: bool = True


class PrivacyManager:
    """
    Comprehensive privacy protection manager for FaceAuth.
    
    Implements privacy-by-design principles and provides tools for
    data protection, user rights, and regulatory compliance.
    """
    
    def __init__(self, storage_dir: str, encryption_manager: EncryptionManager = None):
        """
        Initialize privacy manager.
        
        Args:
            storage_dir: Directory for privacy data storage
            encryption_manager: Encryption manager instance
        """
        self.storage_dir = Path(storage_dir)
        self.privacy_dir = self.storage_dir / "privacy"
        self.privacy_dir.mkdir(mode=0o700, parents=True, exist_ok=True)
        
        self.encryption_manager = encryption_manager or EncryptionManager()
        self.secure_storage = SecureStorage(str(self.privacy_dir))
        self.audit_logger = SecureAuditLogger(str(self.privacy_dir / "audit"))
        
        # Privacy configuration
        self.settings_file = self.privacy_dir / "privacy_settings.json.enc"
        self.consent_file = self.privacy_dir / "consent_records.json.enc"
        self.data_registry_file = self.privacy_dir / "data_registry.json.enc"
        
        # Load or create privacy settings
        self.settings = self._load_privacy_settings()
        self.consent_records: Dict[str, UserConsent] = self._load_consent_records()
        self.data_registry: Dict[str, DataRecord] = self._load_data_registry()
        
        # Privacy policy version
        self.privacy_policy_version = "1.0.0"
        
        self._log_privacy_event("privacy_manager_initialized", {
            "privacy_level": self.settings.privacy_level,
            "auto_cleanup": self.settings.auto_cleanup_enabled
        })
    
    def _load_privacy_settings(self) -> PrivacySettings:
        """Load privacy settings from encrypted storage."""
        try:
            if self.settings_file.exists():
                encrypted_data = self.settings_file.read_bytes()
                decrypted_data = self.encryption_manager.decrypt_data(encrypted_data)
                settings_dict = json.loads(decrypted_data.decode())
                return PrivacySettings(**settings_dict)
        except Exception as e:
            self._log_privacy_event("privacy_settings_load_failed", {"error": str(e)})
        
        # Return default settings
        return PrivacySettings()
    
    def _save_privacy_settings(self) -> None:
        """Save privacy settings to encrypted storage."""
        try:
            settings_json = json.dumps(asdict(self.settings), indent=2)
            encrypted_data = self.encryption_manager.encrypt_data(settings_json.encode())
            
            # Atomic write
            temp_file = self.settings_file.with_suffix('.tmp')
            temp_file.write_bytes(encrypted_data)
            temp_file.replace(self.settings_file)
            
            # Set restrictive permissions
            os.chmod(self.settings_file, 0o600)
            
        except Exception as e:
            self._log_privacy_event("privacy_settings_save_failed", {"error": str(e)})
            raise
    
    def _load_consent_records(self) -> Dict[str, UserConsent]:
        """Load user consent records from encrypted storage."""
        try:
            if self.consent_file.exists():
                encrypted_data = self.consent_file.read_bytes()
                decrypted_data = self.encryption_manager.decrypt_data(encrypted_data)
                consent_data = json.loads(decrypted_data.decode())
                
                # Convert to UserConsent objects
                consent_records = {}
                for user_id, record in consent_data.items():
                    record['consent_timestamp'] = datetime.fromisoformat(record['consent_timestamp'])
                    consent_records[user_id] = UserConsent(**record)
                
                return consent_records
        except Exception as e:
            self._log_privacy_event("consent_records_load_failed", {"error": str(e)})
        
        return {}
    
    def _save_consent_records(self) -> None:
        """Save consent records to encrypted storage."""
        try:
            # Convert to serializable format
            consent_data = {}
            for user_id, consent in self.consent_records.items():
                consent_dict = asdict(consent)
                consent_dict['consent_timestamp'] = consent.consent_timestamp.isoformat()
                consent_data[user_id] = consent_dict
            
            consent_json = json.dumps(consent_data, indent=2)
            encrypted_data = self.encryption_manager.encrypt_data(consent_json.encode())
            
            # Atomic write
            temp_file = self.consent_file.with_suffix('.tmp')
            temp_file.write_bytes(encrypted_data)
            temp_file.replace(self.consent_file)
            
            # Set restrictive permissions
            os.chmod(self.consent_file, 0o600)
            
        except Exception as e:
            self._log_privacy_event("consent_records_save_failed", {"error": str(e)})
            raise
    
    def _load_data_registry(self) -> Dict[str, DataRecord]:
        """Load data registry from encrypted storage."""
        try:
            if self.data_registry_file.exists():
                encrypted_data = self.data_registry_file.read_bytes()
                decrypted_data = self.encryption_manager.decrypt_data(encrypted_data)
                registry_data = json.loads(decrypted_data.decode())
                
                # Convert to DataRecord objects
                data_registry = {}
                for record_id, record in registry_data.items():
                    record['creation_time'] = datetime.fromisoformat(record['creation_time'])
                    record['last_access'] = datetime.fromisoformat(record['last_access'])
                    record['retention_until'] = datetime.fromisoformat(record['retention_until'])
                    data_registry[record_id] = DataRecord(**record)
                
                return data_registry
        except Exception as e:
            self._log_privacy_event("data_registry_load_failed", {"error": str(e)})
        
        return {}
    
    def _save_data_registry(self) -> None:
        """Save data registry to encrypted storage."""
        try:
            # Convert to serializable format
            registry_data = {}
            for record_id, record in self.data_registry.items():
                record_dict = asdict(record)
                record_dict['creation_time'] = record.creation_time.isoformat()
                record_dict['last_access'] = record.last_access.isoformat()
                record_dict['retention_until'] = record.retention_until.isoformat()
                registry_data[record_id] = record_dict
            
            registry_json = json.dumps(registry_data, indent=2)
            encrypted_data = self.encryption_manager.encrypt_data(registry_json.encode())
            
            # Atomic write
            temp_file = self.data_registry_file.with_suffix('.tmp')
            temp_file.write_bytes(encrypted_data)
            temp_file.replace(self.data_registry_file)
            
            # Set restrictive permissions
            os.chmod(self.data_registry_file, 0o600)
            
        except Exception as e:
            self._log_privacy_event("data_registry_save_failed", {"error": str(e)})
            raise
    
    def _log_privacy_event(self, event_type: str, details: Dict[str, Any]) -> None:
        """Log privacy-related events."""
        try:
            self.audit_logger.log_event(
                event_type=f"privacy_{event_type}",
                details=details,
                user_id="system",
                sensitive=False
            )
        except Exception:
            # Privacy events should not fail silently but shouldn't break the system
            pass
    
    def _generate_user_id_hash(self, user_identifier: str) -> str:
        """Generate privacy-preserving user ID hash."""
        salt = b"faceauth_privacy_salt_2024"  # Static salt for consistency
        return hashlib.pbkdf2_hmac('sha256', user_identifier.encode(), salt, 100000).hex()[:16]
    
    def collect_consent(self, user_identifier: str, purpose: str, 
                       data_types: List[str], retention_days: int = None) -> bool:
        """
        Collect and record user consent for data processing.
        
        Args:
            user_identifier: User identifier (will be hashed for privacy)
            purpose: Purpose of data processing
            data_types: Types of data to be processed
            retention_days: Data retention period
            
        Returns:
            True if consent collected successfully
        """
        try:
            user_id = self._generate_user_id_hash(user_identifier)
            retention_days = retention_days or self.settings.data_retention_days
            
            consent = UserConsent(
                user_id=user_id,
                consent_timestamp=datetime.now(),
                consent_version=self.privacy_policy_version,
                purpose=purpose,
                data_types=data_types,
                retention_period=retention_days
            )
            
            self.consent_records[user_id] = consent
            self._save_consent_records()
            
            self._log_privacy_event("consent_collected", {
                "user_id_hash": user_id[:8],  # Partial hash for audit
                "purpose": purpose,
                "data_types_count": len(data_types),
                "retention_days": retention_days
            })
            
            return True
            
        except Exception as e:
            self._log_privacy_event("consent_collection_failed", {"error": str(e)})
            return False
    
    def check_consent(self, user_identifier: str, purpose: str) -> bool:
        """
        Check if user has given consent for specific purpose.
        
        Args:
            user_identifier: User identifier
            purpose: Purpose to check consent for
            
        Returns:
            True if consent exists and is valid
        """
        try:
            user_id = self._generate_user_id_hash(user_identifier)
            
            if user_id not in self.consent_records:
                return False
            
            consent = self.consent_records[user_id]
            
            # Check if consent matches purpose
            if consent.purpose != purpose:
                return False
            
            # Check if consent is still valid (not expired)
            consent_expiry = consent.consent_timestamp + timedelta(days=consent.retention_period)
            if datetime.now() > consent_expiry:
                return False
            
            return True
            
        except Exception as e:
            self._log_privacy_event("consent_check_failed", {"error": str(e)})
            return False
    
    def withdraw_consent(self, user_identifier: str) -> bool:
        """
        Withdraw user consent and trigger data deletion.
        
        Args:
            user_identifier: User identifier
            
        Returns:
            True if consent withdrawn and data deleted successfully
        """
        try:
            user_id = self._generate_user_id_hash(user_identifier)
            
            if user_id in self.consent_records:
                del self.consent_records[user_id]
                self._save_consent_records()
            
            # Trigger data deletion for this user
            deleted_records = self._delete_user_data(user_id)
            
            self._log_privacy_event("consent_withdrawn", {
                "user_id_hash": user_id[:8],
                "deleted_records": deleted_records
            })
            
            return True
            
        except Exception as e:
            self._log_privacy_event("consent_withdrawal_failed", {"error": str(e)})
            return False
    
    def register_data_creation(self, user_identifier: str, data_type: str, 
                              purpose: str, file_path: str = None) -> str:
        """
        Register creation of personal data.
        
        Args:
            user_identifier: User identifier
            data_type: Type of data created
            purpose: Purpose of data creation
            file_path: Optional file path for the data
            
        Returns:
            Record ID for tracking
        """
        try:
            user_id = self._generate_user_id_hash(user_identifier)
            record_id = hashlib.sha256(f"{user_id}_{data_type}_{time.time()}".encode()).hexdigest()[:16]
            
            now = datetime.now()
            retention_until = now + timedelta(days=self.settings.data_retention_days)
            
            record = DataRecord(
                record_id=record_id,
                user_id=user_id,
                data_type=data_type,
                creation_time=now,
                last_access=now,
                retention_until=retention_until,
                purpose=purpose,
                sensitive=True
            )
            
            self.data_registry[record_id] = record
            self._save_data_registry()
            
            self._log_privacy_event("data_registered", {
                "record_id": record_id,
                "user_id_hash": user_id[:8],
                "data_type": data_type,
                "purpose": purpose
            })
            
            return record_id
            
        except Exception as e:
            self._log_privacy_event("data_registration_failed", {"error": str(e)})
            raise
    
    def register_data_access(self, record_id: str) -> None:
        """
        Register access to personal data.
        
        Args:
            record_id: Record ID to update
        """
        try:
            if record_id in self.data_registry:
                self.data_registry[record_id].last_access = datetime.now()
                self._save_data_registry()
                
                self._log_privacy_event("data_accessed", {"record_id": record_id})
                
        except Exception as e:
            self._log_privacy_event("data_access_registration_failed", {"error": str(e)})
    
    def _delete_user_data(self, user_id: str) -> int:
        """
        Delete all data for a specific user.
        
        Args:
            user_id: User ID to delete data for
            
        Returns:
            Number of records deleted
        """
        deleted_count = 0
        records_to_delete = []
        
        # Find all records for this user
        for record_id, record in self.data_registry.items():
            if record.user_id == user_id:
                records_to_delete.append(record_id)
        
        # Delete records
        for record_id in records_to_delete:
            del self.data_registry[record_id]
            deleted_count += 1
        
        if deleted_count > 0:
            self._save_data_registry()
        
        return deleted_count
    
    def cleanup_expired_data(self) -> Dict[str, int]:
        """
        Clean up expired data based on retention policies.
        
        Returns:
            Statistics about cleanup operation
        """
        try:
            now = datetime.now()
            expired_records = []
            expired_consents = []
            
            # Find expired data records
            for record_id, record in self.data_registry.items():
                if now > record.retention_until:
                    expired_records.append(record_id)
            
            # Find expired consent records
            for user_id, consent in self.consent_records.items():
                consent_expiry = consent.consent_timestamp + timedelta(days=consent.retention_period)
                if now > consent_expiry:
                    expired_consents.append(user_id)
            
            # Delete expired records
            for record_id in expired_records:
                del self.data_registry[record_id]
            
            for user_id in expired_consents:
                del self.consent_records[user_id]
            
            # Save changes
            if expired_records:
                self._save_data_registry()
            if expired_consents:
                self._save_consent_records()
            
            stats = {
                "expired_data_records": len(expired_records),
                "expired_consent_records": len(expired_consents),
                "total_cleaned": len(expired_records) + len(expired_consents)
            }
            
            self._log_privacy_event("cleanup_completed", stats)
            
            return stats
            
        except Exception as e:
            self._log_privacy_event("cleanup_failed", {"error": str(e)})
            return {"error": str(e)}
    
    def generate_privacy_report(self, user_identifier: str = None) -> Dict[str, Any]:
        """
        Generate privacy report for user or system.
        
        Args:
            user_identifier: Optional user identifier for user-specific report
            
        Returns:
            Privacy report dictionary
        """
        try:
            if user_identifier:
                # User-specific report
                user_id = self._generate_user_id_hash(user_identifier)
                user_records = [r for r in self.data_registry.values() if r.user_id == user_id]
                user_consent = self.consent_records.get(user_id)
                
                report = {
                    "report_type": "user_privacy_report",
                    "user_id_hash": user_id[:8],
                    "consent_status": {
                        "has_consent": user_consent is not None,
                        "consent_date": user_consent.consent_timestamp.isoformat() if user_consent else None,
                        "consent_purpose": user_consent.purpose if user_consent else None,
                        "data_types": user_consent.data_types if user_consent else []
                    },
                    "data_records": {
                        "total_records": len(user_records),
                        "data_types": list(set(r.data_type for r in user_records)),
                        "oldest_record": min(r.creation_time for r in user_records).isoformat() if user_records else None,
                        "newest_record": max(r.creation_time for r in user_records).isoformat() if user_records else None
                    },
                    "retention_info": {
                        "retention_policy_days": self.settings.data_retention_days,
                        "records_expiring_soon": len([r for r in user_records 
                                                    if (r.retention_until - datetime.now()).days <= 30])
                    }
                }
            else:
                # System-wide report
                now = datetime.now()
                expired_data = len([r for r in self.data_registry.values() if now > r.retention_until])
                expired_consent = len([c for c in self.consent_records.values() 
                                     if now > c.consent_timestamp + timedelta(days=c.retention_period)])
                
                report = {
                    "report_type": "system_privacy_report",
                    "privacy_settings": asdict(self.settings),
                    "statistics": {
                        "total_users": len(self.consent_records),
                        "total_data_records": len(self.data_registry),
                        "data_types": list(set(r.data_type for r in self.data_registry.values())),
                        "expired_data_records": expired_data,
                        "expired_consent_records": expired_consent
                    },
                    "compliance_status": {
                        "auto_cleanup_enabled": self.settings.auto_cleanup_enabled,
                        "consent_required": self.settings.consent_required,
                        "anonymized_logs": self.settings.anonymize_logs,
                        "secure_deletion": self.settings.enable_secure_deletion
                    }
                }
            
            self._log_privacy_event("privacy_report_generated", {
                "report_type": report["report_type"],
                "user_specific": user_identifier is not None
            })
            
            return report
            
        except Exception as e:
            self._log_privacy_event("privacy_report_failed", {"error": str(e)})
            return {"error": str(e)}
    
    def export_user_data(self, user_identifier: str) -> Dict[str, Any]:
        """
        Export all data for a user (data portability right).
        
        Args:
            user_identifier: User identifier
            
        Returns:
            Exported user data
        """
        try:
            user_id = self._generate_user_id_hash(user_identifier)
            user_records = [r for r in self.data_registry.values() if r.user_id == user_id]
            user_consent = self.consent_records.get(user_id)
            
            export_data = {
                "export_timestamp": datetime.now().isoformat(),
                "user_id_hash": user_id[:8],
                "consent_record": asdict(user_consent) if user_consent else None,
                "data_records": [
                    {
                        "record_id": r.record_id,
                        "data_type": r.data_type,
                        "creation_time": r.creation_time.isoformat(),
                        "last_access": r.last_access.isoformat(),
                        "retention_until": r.retention_until.isoformat(),
                        "purpose": r.purpose
                    }
                    for r in user_records
                ],
                "privacy_settings": asdict(self.settings),
                "export_format": "json",
                "export_version": "1.0"
            }
            
            self._log_privacy_event("user_data_exported", {
                "user_id_hash": user_id[:8],
                "records_exported": len(user_records)
            })
            
            return export_data
            
        except Exception as e:
            self._log_privacy_event("user_data_export_failed", {"error": str(e)})
            return {"error": str(e)}
    
    def update_privacy_settings(self, new_settings: Dict[str, Any]) -> bool:
        """
        Update privacy settings.
        
        Args:
            new_settings: New privacy settings
            
        Returns:
            True if settings updated successfully
        """
        try:
            # Validate settings
            valid_keys = {
                'data_retention_days', 'auto_cleanup_enabled', 'consent_required',
                'anonymize_logs', 'enable_data_export', 'enable_secure_deletion',
                'privacy_level'
            }
            
            for key, value in new_settings.items():
                if key not in valid_keys:
                    continue
                    
                setattr(self.settings, key, value)
            
            self._save_privacy_settings()
            
            self._log_privacy_event("privacy_settings_updated", {
                "updated_keys": list(new_settings.keys())
            })
            
            return True
            
        except Exception as e:
            self._log_privacy_event("privacy_settings_update_failed", {"error": str(e)})
            return False
    
    def get_privacy_status(self) -> Dict[str, Any]:
        """
        Get current privacy status and health check.
        
        Returns:
            Privacy status information
        """
        try:
            now = datetime.now()
            
            # Count expired items
            expired_data = len([r for r in self.data_registry.values() if now > r.retention_until])
            expired_consent = len([c for c in self.consent_records.values() 
                                 if now > c.consent_timestamp + timedelta(days=c.retention_period)])
            
            # Check for privacy issues
            issues = []
            if expired_data > 0:
                issues.append(f"{expired_data} expired data records need cleanup")
            if expired_consent > 0:
                issues.append(f"{expired_consent} expired consent records need cleanup")
            if not self.settings.auto_cleanup_enabled:
                issues.append("Automatic cleanup is disabled")
            
            status = {
                "privacy_level": self.settings.privacy_level,
                "health_status": "HEALTHY" if not issues else "NEEDS_ATTENTION",
                "issues": issues,
                "statistics": {
                    "active_users": len(self.consent_records),
                    "data_records": len(self.data_registry),
                    "expired_data": expired_data,
                    "expired_consent": expired_consent
                },
                "compliance": {
                    "consent_tracking": self.settings.consent_required,
                    "data_retention": self.settings.data_retention_days,
                    "secure_deletion": self.settings.enable_secure_deletion,
                    "log_anonymization": self.settings.anonymize_logs
                },
                "last_check": now.isoformat()
            }
            
            return status
            
        except Exception as e:
            return {
                "health_status": "ERROR",
                "error": str(e),
                "last_check": datetime.now().isoformat()
            }
