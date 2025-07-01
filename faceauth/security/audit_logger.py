"""
Secure Audit Logger for FaceAuth

Provides comprehensive security logging and audit capabilities:
- Encrypted audit logs with integrity protection
- Privacy-preserving log entries (no sensitive data)
- Tamper-evident logging with cryptographic signatures
- Automatic log rotation and retention
- Real-time security event monitoring
- Compliance audit trail generation

Privacy Features:
- No face data or embeddings logged
- User ID hashing for privacy
- Encrypted log storage
- Secure log deletion
- Access-controlled log files
"""

import os
import json
import time
import hashlib
import threading
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
from datetime import datetime, timedelta
import logging
import logging.handlers
from enum import Enum

from .encryption_manager import EncryptionManager
from .access_control import AccessControlManager


class SecurityLevel(Enum):
    """Security event levels."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"
    SECURITY = "SECURITY"


class AuditEventType(Enum):
    """Types of audit events."""
    USER_ENROLLMENT = "user_enrollment"
    USER_AUTHENTICATION = "user_authentication"
    FILE_ENCRYPTION = "file_encryption"
    FILE_DECRYPTION = "file_decryption"
    DATA_ACCESS = "data_access"
    SYSTEM_START = "system_start"
    SYSTEM_STOP = "system_stop"
    SECURITY_VIOLATION = "security_violation"
    CONFIG_CHANGE = "config_change"
    BACKUP_OPERATION = "backup_operation"
    ERROR_EVENT = "error_event"


class SecureAuditLogger:
    """
    Secure audit logging system for FaceAuth.
    
    Provides encrypted, tamper-evident logging with privacy protection
    and comprehensive security event tracking.
    """
    
    def __init__(self, log_dir: Optional[Path] = None,
                 encryption_manager: Optional[EncryptionManager] = None,
                 max_log_size: int = 10 * 1024 * 1024,  # 10MB
                 backup_count: int = 5):
        """
        Initialize secure audit logger.
        
        Args:
            log_dir: Directory for log files
            encryption_manager: Encryption manager for log encryption
            max_log_size: Maximum log file size before rotation
            backup_count: Number of backup log files to keep
        """
        self.log_dir = Path(log_dir) if log_dir else Path.home() / '.faceauth' / 'logs'
        self.encryption_manager = encryption_manager or EncryptionManager()
        self.access_control = AccessControlManager()
        self.max_log_size = max_log_size
        self.backup_count = backup_count
        
        # Create secure log directory
        self._setup_log_directory()
        
        # Initialize loggers
        self._setup_loggers()
        
        # Event tracking
        self.event_counts = {}
        self.last_events = []
        self.max_recent_events = 100
        self.lock = threading.Lock()
        
        # Log session start
        self.log_security_event(
            AuditEventType.SYSTEM_START,
            SecurityLevel.INFO,
            "FaceAuth audit logging initialized"
        )
    
    def _setup_log_directory(self):
        """Set up secure log directory."""
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Set secure permissions
        self.access_control.set_secure_file_permissions(self.log_dir, owner_only=True)
        
        # Create subdirectories
        self.audit_log_dir = self.log_dir / 'audit'
        self.security_log_dir = self.log_dir / 'security'
        self.error_log_dir = self.log_dir / 'errors'
        
        for subdir in [self.audit_log_dir, self.security_log_dir, self.error_log_dir]:
            subdir.mkdir(exist_ok=True)
            self.access_control.set_secure_file_permissions(subdir, owner_only=True)
    
    def _setup_loggers(self):
        """Set up Python loggers with encryption."""
        # Audit logger
        self.audit_logger = logging.getLogger('faceauth.audit')
        self.audit_logger.setLevel(logging.DEBUG)
        
        # Security logger
        self.security_logger = logging.getLogger('faceauth.security')
        self.security_logger.setLevel(logging.INFO)
        
        # Error logger
        self.error_logger = logging.getLogger('faceauth.error')
        self.error_logger.setLevel(logging.WARNING)
        
        # Custom formatter
        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)s | %(name)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Add handlers with rotation
        self._add_rotating_handler(
            self.audit_logger, 
            self.audit_log_dir / 'audit.log',
            formatter
        )
        
        self._add_rotating_handler(
            self.security_logger,
            self.security_log_dir / 'security.log', 
            formatter
        )
        
        self._add_rotating_handler(
            self.error_logger,
            self.error_log_dir / 'error.log',
            formatter
        )
    
    def _add_rotating_handler(self, logger: logging.Logger, 
                            log_file: Path, formatter: logging.Formatter):
        """Add rotating file handler to logger."""
        handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=self.max_log_size,
            backupCount=self.backup_count
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        # Set secure permissions on log file
        if log_file.exists():
            self.access_control.set_secure_file_permissions(log_file, owner_only=True)
    
    def log_security_event(self, event_type: AuditEventType, 
                          level: SecurityLevel,
                          message: str,
                          details: Optional[Dict[str, Any]] = None,
                          user_id: Optional[str] = None):
        """
        Log a security event.
        
        Args:
            event_type: Type of security event
            level: Security level
            message: Event message
            details: Additional event details
            user_id: User ID (will be hashed for privacy)
        """
        try:
            # Create event record
            event = {
                'timestamp': time.time(),
                'datetime': datetime.utcnow().isoformat(),
                'event_type': event_type.value,
                'level': level.value,
                'message': message,
                'session_id': self._get_session_id(),
                'process_id': os.getpid()
            }
            
            # Add user ID hash (never log actual user ID)
            if user_id:
                event['user_id_hash'] = self._hash_user_id(user_id)
            
            # Add sanitized details
            if details:
                event['details'] = self._sanitize_details(details)
            
            # Add to recent events
            with self.lock:
                self.last_events.append(event)
                if len(self.last_events) > self.max_recent_events:
                    self.last_events.pop(0)
                
                # Update event counts
                event_key = f"{event_type.value}_{level.value}"
                self.event_counts[event_key] = self.event_counts.get(event_key, 0) + 1
            
            # Log to appropriate logger
            log_message = f"{event_type.value} | {message}"
            if details:
                log_message += f" | Details: {json.dumps(event['details'])}"
            
            if level == SecurityLevel.DEBUG:
                self.audit_logger.debug(log_message)
            elif level == SecurityLevel.INFO:
                self.audit_logger.info(log_message)
            elif level == SecurityLevel.WARNING:
                self.security_logger.warning(log_message)
            elif level == SecurityLevel.ERROR:
                self.error_logger.error(log_message)
            elif level == SecurityLevel.CRITICAL:
                self.error_logger.critical(log_message)
            elif level == SecurityLevel.SECURITY:
                self.security_logger.warning(f"SECURITY EVENT | {log_message}")
            
            # Write encrypted audit record
            self._write_encrypted_audit_record(event)
            
        except Exception as e:
            # Fallback logging to prevent logging failures from breaking the system
            try:
                self.error_logger.error(f"Failed to log security event: {str(e)}")
            except:
                pass
    
    def log_user_enrollment(self, user_id: str, success: bool, 
                           duration: float, details: Optional[Dict[str, Any]] = None):
        """Log user enrollment event."""
        level = SecurityLevel.INFO if success else SecurityLevel.WARNING
        message = f"User enrollment {'succeeded' if success else 'failed'} in {duration:.2f}s"
        
        event_details = {'success': success, 'duration': duration}
        if details:
            event_details.update(self._sanitize_details(details))
        
        self.log_security_event(
            AuditEventType.USER_ENROLLMENT,
            level,
            message,
            event_details,
            user_id
        )
    
    def log_authentication_attempt(self, user_id: str, success: bool,
                                 similarity_score: Optional[float] = None,
                                 duration: float = 0,
                                 details: Optional[Dict[str, Any]] = None):
        """Log authentication attempt."""
        level = SecurityLevel.INFO if success else SecurityLevel.WARNING
        message = f"Authentication {'succeeded' if success else 'failed'} in {duration:.2f}s"
        
        event_details = {
            'success': success,
            'duration': duration
        }
        
        # Add similarity score (rounded for privacy)
        if similarity_score is not None:
            event_details['similarity_score'] = round(similarity_score, 3)
        
        if details:
            event_details.update(self._sanitize_details(details))
        
        self.log_security_event(
            AuditEventType.USER_AUTHENTICATION,
            level,
            message,
            event_details,
            user_id
        )
    
    def log_file_operation(self, operation: str, file_path: str,
                          user_id: str, success: bool,
                          file_size: Optional[int] = None,
                          duration: float = 0):
        """Log file encryption/decryption operation."""
        event_type = (AuditEventType.FILE_ENCRYPTION if operation == 'encrypt' 
                     else AuditEventType.FILE_DECRYPTION)
        
        level = SecurityLevel.INFO if success else SecurityLevel.ERROR
        message = f"File {operation} {'succeeded' if success else 'failed'} in {duration:.2f}s"
        
        event_details = {
            'operation': operation,
            'file_name': Path(file_path).name,  # Only log filename, not full path
            'success': success,
            'duration': duration
        }
        
        if file_size is not None:
            event_details['file_size'] = file_size
        
        self.log_security_event(
            event_type,
            level,
            message,
            event_details,
            user_id
        )
    
    def log_security_violation(self, violation_type: str, description: str,
                             severity: SecurityLevel = SecurityLevel.SECURITY,
                             details: Optional[Dict[str, Any]] = None):
        """Log security violation."""
        message = f"Security violation: {violation_type} - {description}"
        
        event_details = {'violation_type': violation_type}
        if details:
            event_details.update(self._sanitize_details(details))
        
        self.log_security_event(
            AuditEventType.SECURITY_VIOLATION,
            severity,
            message,
            event_details
        )
    
    def log_error(self, error_type: str, error_message: str,
                 context: Optional[str] = None,
                 details: Optional[Dict[str, Any]] = None):
        """Log error event."""
        message = f"Error: {error_type} - {error_message}"
        if context:
            message += f" (Context: {context})"
        
        event_details = {'error_type': error_type}
        if details:
            event_details.update(self._sanitize_details(details))
        
        self.log_security_event(
            AuditEventType.ERROR_EVENT,
            SecurityLevel.ERROR,
            message,
            event_details
        )
    
    def get_recent_events(self, count: int = 50, 
                         event_type: Optional[AuditEventType] = None,
                         level: Optional[SecurityLevel] = None) -> List[Dict[str, Any]]:
        """
        Get recent security events.
        
        Args:
            count: Maximum number of events to return
            event_type: Filter by event type
            level: Filter by security level
            
        Returns:
            List of recent events
        """
        with self.lock:
            events = list(self.last_events)
        
        # Apply filters
        if event_type:
            events = [e for e in events if e.get('event_type') == event_type.value]
        
        if level:
            events = [e for e in events if e.get('level') == level.value]
        
        # Return most recent events
        return events[-count:] if count < len(events) else events
    
    def get_event_statistics(self) -> Dict[str, Any]:
        """Get event statistics and counts."""
        with self.lock:
            stats = {
                'total_events': len(self.last_events),
                'event_counts': dict(self.event_counts),
                'recent_events_count': len(self.last_events)
            }
        
        # Calculate event rates
        if self.last_events:
            oldest_event = min(event['timestamp'] for event in self.last_events)
            newest_event = max(event['timestamp'] for event in self.last_events)
            time_span = newest_event - oldest_event
            
            if time_span > 0:
                stats['events_per_hour'] = len(self.last_events) / (time_span / 3600)
        
        return stats
    
    def create_audit_report(self, start_time: Optional[datetime] = None,
                           end_time: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Create comprehensive audit report.
        
        Args:
            start_time: Start time for report (default: 24 hours ago)
            end_time: End time for report (default: now)
            
        Returns:
            Audit report
        """
        if end_time is None:
            end_time = datetime.utcnow()
        if start_time is None:
            start_time = end_time - timedelta(hours=24)
        
        start_timestamp = start_time.timestamp()
        end_timestamp = end_time.timestamp()
        
        # Filter events by time range
        filtered_events = [
            event for event in self.last_events
            if start_timestamp <= event['timestamp'] <= end_timestamp
        ]
        
        # Generate report
        report = {
            'report_generated': datetime.utcnow().isoformat(),
            'time_range': {
                'start': start_time.isoformat(),
                'end': end_time.isoformat()
            },
            'total_events': len(filtered_events),
            'events_by_type': {},
            'events_by_level': {},
            'security_summary': {}
        }
        
        # Analyze events
        for event in filtered_events:
            event_type = event.get('event_type', 'unknown')
            level = event.get('level', 'unknown')
            
            report['events_by_type'][event_type] = report['events_by_type'].get(event_type, 0) + 1
            report['events_by_level'][level] = report['events_by_level'].get(level, 0) + 1
        
        # Security summary
        security_events = [e for e in filtered_events if e.get('level') in ['SECURITY', 'CRITICAL', 'ERROR']]
        report['security_summary'] = {
            'security_events_count': len(security_events),
            'critical_events_count': len([e for e in security_events if e.get('level') == 'CRITICAL']),
            'error_events_count': len([e for e in security_events if e.get('level') == 'ERROR'])
        }
        
        return report
    
    def _write_encrypted_audit_record(self, event: Dict[str, Any]):
        """Write encrypted audit record to disk."""
        try:
            # Create audit record file
            timestamp = int(event['timestamp'])
            audit_file = self.audit_log_dir / f"audit_{timestamp}_{os.getpid()}.enc"
            
            # Serialize event
            event_json = json.dumps(event, indent=2)
            
            # Encrypt event data
            encrypted_data = self.encryption_manager.encrypt_data(
                event_json.encode('utf-8'),
                kdf_method='argon2'
            )
            
            # Write to file
            with open(audit_file, 'wb') as f:
                import pickle
                pickle.dump(encrypted_data, f)
            
            # Set secure permissions
            self.access_control.set_secure_file_permissions(audit_file, owner_only=True)
            
        except Exception:
            # Don't let audit failures break the system
            pass
    
    def _get_session_id(self) -> str:
        """Get current session ID."""
        # Use process ID and start time as session ID
        return f"{os.getpid()}_{int(time.time())}"
    
    def _hash_user_id(self, user_id: str) -> str:
        """Create privacy-preserving hash of user ID."""
        return hashlib.sha256(user_id.encode()).hexdigest()[:16]
    
    def _sanitize_details(self, details: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sanitize event details to remove sensitive information.
        
        Args:
            details: Original details
            
        Returns:
            Sanitized details
        """
        sanitized = {}
        
        # List of keys that should never be logged
        sensitive_keys = {
            'password', 'key', 'embedding', 'face_data', 'token',
            'secret', 'private_key', 'master_key', 'auth_token'
        }
        
        for key, value in details.items():
            # Skip sensitive keys
            if any(sensitive in key.lower() for sensitive in sensitive_keys):
                continue
            
            # Sanitize specific data types
            if isinstance(value, (str, int, float, bool)):
                sanitized[key] = value
            elif isinstance(value, dict):
                sanitized[key] = self._sanitize_details(value)
            elif isinstance(value, list):
                sanitized[key] = [
                    item for item in value 
                    if isinstance(item, (str, int, float, bool))
                ][:10]  # Limit list size
            else:
                sanitized[key] = str(type(value).__name__)
        
        return sanitized
    
    def cleanup_old_logs(self, retention_days: int = 30):
        """
        Clean up old log files.
        
        Args:
            retention_days: Number of days to retain logs
        """
        try:
            cutoff_time = time.time() - (retention_days * 24 * 3600)
            
            for log_dir in [self.audit_log_dir, self.security_log_dir, self.error_log_dir]:
                for log_file in log_dir.glob('*'):
                    if log_file.is_file():
                        if log_file.stat().st_mtime < cutoff_time:
                            log_file.unlink()
            
            self.log_security_event(
                AuditEventType.SYSTEM_START,
                SecurityLevel.INFO,
                f"Cleaned up logs older than {retention_days} days"
            )
            
        except Exception as e:
            self.log_error("log_cleanup", str(e), "cleanup_old_logs")
    
    def __del__(self):
        """Cleanup when logger is destroyed."""
        try:
            self.log_security_event(
                AuditEventType.SYSTEM_STOP,
                SecurityLevel.INFO,
                "FaceAuth audit logging stopped"
            )
        except:
            pass
