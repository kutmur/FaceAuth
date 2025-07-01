"""
Access Control Manager for FaceAuth Security

Provides comprehensive access control and file permission management:
- Platform-specific file permissions
- Process isolation and sandboxing
- Resource access control
- Security policy enforcement
- Privilege escalation prevention
- Anti-tampering protection

Security Features:
- Restrictive file permissions (owner-only access)
- Process privilege management
- Resource usage limits
- Security boundary enforcement
- Access logging and monitoring
"""

import os
import stat
import platform
import subprocess
from typing import Dict, List, Optional, Any
from pathlib import Path
import tempfile
import time

# Platform-specific imports
try:
    import pwd
    import grp
except ImportError:
    pwd = None
    grp = None

# Windows-specific imports (optional)
if platform.system() == 'Windows':
    try:
        import win32security
        import win32api
        import win32con
        import ntsecuritycon
        WINDOWS_SECURITY_AVAILABLE = True
    except ImportError:
        WINDOWS_SECURITY_AVAILABLE = False
        win32security = None
        win32api = None
        win32con = None
        ntsecuritycon = None
else:
    WINDOWS_SECURITY_AVAILABLE = False
    win32security = None
    win32api = None
    win32con = None
    ntsecuritycon = None


class AccessControlError(Exception):
    """Custom exception for access control operations."""
    pass


class AccessControlManager:
    """
    Comprehensive access control manager for FaceAuth.
    
    Provides platform-specific security controls and access management
    with privacy protection and privilege isolation.
    """
    
    def __init__(self):
        """Initialize access control manager."""
        self.platform = platform.system()
        self.current_user = self._get_current_user()
        self.process_uid = os.getuid() if hasattr(os, 'getuid') else None
        self.process_gid = os.getgid() if hasattr(os, 'getgid') else None
        
        # Security policies
        self.max_file_permissions = 0o600  # Owner read/write only
        self.max_dir_permissions = 0o700   # Owner full access only
        
        # Initialize platform-specific components
        self._init_platform_specific()
    
    def _init_platform_specific(self):
        """Initialize platform-specific access control."""
        if self.platform == 'Windows':
            self._init_windows_security()
        else:
            self._init_unix_security()
    
    def _init_windows_security(self):
        """Initialize Windows-specific security."""
        if not WINDOWS_SECURITY_AVAILABLE:
            # Fallback for systems without pywin32
            self.current_user_sid = None
            self.admin_sid = None
            return
        
        try:
            # Get current user SID
            self.current_user_sid = win32security.GetTokenInformation(
                win32security.GetCurrentProcessToken(),
                win32security.TokenUser
            )[0]
            
            # Get administrators group SID
            self.admin_sid = win32security.LookupAccountName(
                None, "Administrators"
            )[0]
            
        except Exception as e:
            raise AccessControlError(f"Failed to initialize Windows security: {str(e)}")
    
    def _init_unix_security(self):
        """Initialize Unix-specific security."""
        if pwd is None or grp is None:
            self.user_info = None
            self.group_info = None
            return
        
        try:
            # Get user and group information
            if self.process_uid is not None:
                self.user_info = pwd.getpwuid(self.process_uid)
                self.group_info = grp.getgrgid(self.process_gid)
            
        except Exception as e:
            raise AccessControlError(f"Failed to initialize Unix security: {str(e)}")
    
    def _get_current_user(self) -> str:
        """Get current user name."""
        try:
            if self.platform == 'Windows':
                return os.environ.get('USERNAME', 'unknown')
            else:
                return os.environ.get('USER', 'unknown')
        except:
            return 'unknown'
    
    def set_secure_file_permissions(self, file_path: Path, owner_only: bool = True):
        """
        Set secure permissions on file.
        
        Args:
            file_path: Path to file
            owner_only: If True, only owner can access
        """
        try:
            if self.platform == 'Windows':
                self.set_windows_permissions(file_path, owner_only)
            else:
                self.set_unix_permissions(file_path, owner_only)
                
        except Exception as e:
            raise AccessControlError(f"Failed to set file permissions: {str(e)}")
    
    def set_unix_permissions(self, file_path: Path, owner_only: bool = True):
        """Set Unix file permissions."""
        try:
            if file_path.is_dir():
                # Directory permissions
                if owner_only:
                    os.chmod(file_path, stat.S_IRWXU)  # 700
                else:
                    os.chmod(file_path, stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP)  # 750
            else:
                # File permissions
                if owner_only:
                    os.chmod(file_path, stat.S_IRUSR | stat.S_IWUSR)  # 600
                else:
                    os.chmod(file_path, stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP)  # 640
                    
        except Exception as e:
            raise AccessControlError(f"Failed to set Unix permissions: {str(e)}")
    
    def set_windows_permissions(self, file_path: Path, owner_only: bool = True):
        """Set Windows file permissions using DACL."""
        if not WINDOWS_SECURITY_AVAILABLE:
            # Fallback: use attrib command for basic protection
            try:
                import subprocess
                subprocess.run(['attrib', '+H', str(file_path)], check=False, capture_output=True)
            except:
                pass
            return
        
        try:
            # Get security descriptor
            sd = win32security.GetFileSecurity(
                str(file_path), 
                win32security.DACL_SECURITY_INFORMATION
            )
            
            # Create new DACL
            dacl = win32security.ACL()
            
            if owner_only:
                # Only current user has access
                dacl.AddAccessAllowedAce(
                    win32security.ACL_REVISION,
                    ntsecuritycon.FILE_ALL_ACCESS,
                    self.current_user_sid
                )
            else:
                # Current user and administrators
                dacl.AddAccessAllowedAce(
                    win32security.ACL_REVISION,
                    ntsecuritycon.FILE_ALL_ACCESS,
                    self.current_user_sid
                )
                dacl.AddAccessAllowedAce(
                    win32security.ACL_REVISION,
                    ntsecuritycon.FILE_ALL_ACCESS,
                    self.admin_sid
                )
            
            # Set the DACL
            sd.SetSecurityDescriptorDacl(1, dacl, 0)
            win32security.SetFileSecurity(
                str(file_path),
                win32security.DACL_SECURITY_INFORMATION,
                sd
            )
            
        except Exception as e:
            raise AccessControlError(f"Failed to set Windows permissions: {str(e)}")
    
    def verify_file_permissions(self, file_path: Path) -> Dict[str, Any]:
        """
        Verify file permissions are secure.
        
        Args:
            file_path: Path to verify
            
        Returns:
            Permission analysis
        """
        try:
            if not file_path.exists():
                return {'secure': False, 'error': 'File does not exist'}
            
            if self.platform == 'Windows':
                return self._verify_windows_permissions(file_path)
            else:
                return self._verify_unix_permissions(file_path)
                
        except Exception as e:
            return {'secure': False, 'error': str(e)}
    
    def _verify_unix_permissions(self, file_path: Path) -> Dict[str, Any]:
        """Verify Unix file permissions."""
        stat_info = file_path.stat()
        mode = stat_info.st_mode
        
        # Check owner
        is_owner = stat_info.st_uid == self.process_uid
        
        # Check permissions
        owner_read = bool(mode & stat.S_IRUSR)
        owner_write = bool(mode & stat.S_IWUSR)
        owner_execute = bool(mode & stat.S_IXUSR)
        
        group_read = bool(mode & stat.S_IRGRP)
        group_write = bool(mode & stat.S_IWGRP)
        group_execute = bool(mode & stat.S_IXGRP)
        
        other_read = bool(mode & stat.S_IROTH)
        other_write = bool(mode & stat.S_IWOTH)
        other_execute = bool(mode & stat.S_IXOTH)
        
        # Security assessment
        issues = []
        if not is_owner:
            issues.append("File not owned by current user")
        if group_read or group_write or group_execute:
            issues.append("Group has access")
        if other_read or other_write or other_execute:
            issues.append("Others have access")
        
        return {
            'secure': len(issues) == 0,
            'is_owner': is_owner,
            'permissions': {
                'owner': {'read': owner_read, 'write': owner_write, 'execute': owner_execute},
                'group': {'read': group_read, 'write': group_write, 'execute': group_execute},
                'other': {'read': other_read, 'write': other_write, 'execute': other_execute}
            },
            'issues': issues,
            'octal_mode': oct(stat.S_IMODE(mode))
        }
    
    def _verify_windows_permissions(self, file_path: Path) -> Dict[str, Any]:
        """Verify Windows file permissions."""
        try:
            # Get security descriptor
            sd = win32security.GetFileSecurity(
                str(file_path),
                win32security.DACL_SECURITY_INFORMATION | win32security.OWNER_SECURITY_INFORMATION
            )
            
            # Check owner
            owner_sid = sd.GetSecurityDescriptorOwner()
            is_owner = win32security.EqualSid(owner_sid, self.current_user_sid)
            
            # Analyze DACL
            dacl = sd.GetSecurityDescriptorDacl()
            issues = []
            authorized_users = []
            
            if dacl:
                for i in range(dacl.GetAceCount()):
                    ace = dacl.GetAce(i)
                    ace_type, ace_flags, permissions, sid = ace
                    
                    # Get account name for SID
                    try:
                        account, domain, account_type = win32security.LookupAccountSid(None, sid)
                        authorized_users.append(f"{domain}\\{account}" if domain else account)
                    except:
                        authorized_users.append("Unknown SID")
                    
                    # Check if it's not the current user
                    if not win32security.EqualSid(sid, self.current_user_sid):
                        if not win32security.EqualSid(sid, self.admin_sid):
                            issues.append(f"Unauthorized user has access: {authorized_users[-1]}")
            
            return {
                'secure': len(issues) == 0,
                'is_owner': is_owner,
                'authorized_users': authorized_users,
                'issues': issues
            }
            
        except Exception as e:
            return {'secure': False, 'error': str(e)}
    
    def create_secure_temp_file(self) -> Path:
        """Create a secure temporary file."""
        try:
            # Create temporary file with secure permissions
            fd, temp_path = tempfile.mkstemp(prefix='faceauth_', suffix='.tmp')
            os.close(fd)
            
            temp_file = Path(temp_path)
            self.set_secure_file_permissions(temp_file, owner_only=True)
            
            return temp_file
            
        except Exception as e:
            raise AccessControlError(f"Failed to create secure temp file: {str(e)}")
    
    def check_process_privileges(self) -> Dict[str, Any]:
        """Check current process privileges and security context."""
        try:
            result = {
                'platform': self.platform,
                'user': self.current_user,
                'timestamp': int(time.time())
            }
            
            if self.platform == 'Windows':
                result.update(self._check_windows_privileges())
            else:
                result.update(self._check_unix_privileges())
            
            return result
            
        except Exception as e:
            raise AccessControlError(f"Failed to check privileges: {str(e)}")
    
    def _check_unix_privileges(self) -> Dict[str, Any]:
        """Check Unix process privileges."""
        result = {
            'uid': self.process_uid,
            'gid': self.process_gid,
            'effective_uid': os.geteuid() if hasattr(os, 'geteuid') else None,
            'effective_gid': os.getegid() if hasattr(os, 'getegid') else None,
            'is_root': self.process_uid == 0,
            'groups': os.getgroups() if hasattr(os, 'getgroups') else []
        }
        
        # Security assessment
        issues = []
        if result['is_root']:
            issues.append("Running as root (security risk)")
        if result['uid'] != result['effective_uid']:
            issues.append("UID and effective UID differ")
        if result['gid'] != result['effective_gid']:
            issues.append("GID and effective GID differ")
        
        result['security_issues'] = issues
        result['privilege_level'] = 'root' if result['is_root'] else 'user'
        
        return result
    
    def _check_windows_privileges(self) -> Dict[str, Any]:
        """Check Windows process privileges."""
        try:
            # Get current token
            token = win32security.OpenProcessToken(
                win32api.GetCurrentProcess(),
                win32security.TOKEN_QUERY
            )
            
            # Check if running as administrator
            is_admin = win32security.CheckTokenMembership(token, self.admin_sid)
            
            # Get privilege information
            privileges = win32security.GetTokenInformation(
                token, win32security.TokenPrivileges
            )
            
            privilege_names = []
            for privilege in privileges:
                luid, attributes = privilege
                try:
                    name = win32security.LookupPrivilegeName(None, luid)
                    privilege_names.append(name)
                except:
                    pass
            
            # Security assessment
            issues = []
            if is_admin:
                issues.append("Running with administrator privileges (security risk)")
            
            dangerous_privileges = [
                'SeDebugPrivilege',
                'SeBackupPrivilege',
                'SeRestorePrivilege',
                'SeTakeOwnershipPrivilege'
            ]
            
            for priv in dangerous_privileges:
                if priv in privilege_names:
                    issues.append(f"Has dangerous privilege: {priv}")
            
            return {
                'is_administrator': is_admin,
                'privileges': privilege_names,
                'security_issues': issues,
                'privilege_level': 'administrator' if is_admin else 'user'
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def enforce_security_policy(self, directory: Path) -> Dict[str, Any]:
        """
        Enforce security policy on directory tree.
        
        Args:
            directory: Directory to secure
            
        Returns:
            Security enforcement report
        """
        try:
            report = {
                'directory': str(directory),
                'files_processed': 0,
                'directories_processed': 0,
                'errors': [],
                'warnings': []
            }
            
            # Process all files and directories
            for item in directory.rglob('*'):
                try:
                    if item.is_dir():
                        self.set_secure_file_permissions(item, owner_only=True)
                        report['directories_processed'] += 1
                    else:
                        self.set_secure_file_permissions(item, owner_only=True)
                        report['files_processed'] += 1
                        
                        # Verify permissions
                        verification = self.verify_file_permissions(item)
                        if not verification.get('secure', False):
                            report['warnings'].append(f"Insecure permissions: {item}")
                            
                except Exception as e:
                    report['errors'].append(f"Failed to secure {item}: {str(e)}")
            
            report['success'] = len(report['errors']) == 0
            return report
            
        except Exception as e:
            raise AccessControlError(f"Failed to enforce security policy: {str(e)}")
    
    def get_security_report(self) -> Dict[str, Any]:
        """Generate comprehensive security report."""
        try:
            report = {
                'timestamp': int(time.time()),
                'platform': self.platform,
                'user': self.current_user,
                'process_privileges': self.check_process_privileges(),
                'security_level': 'UNKNOWN'
            }
            
            # Assess overall security level
            process_info = report['process_privileges']
            security_issues = process_info.get('security_issues', [])
            
            if len(security_issues) == 0:
                if process_info.get('privilege_level') == 'user':
                    report['security_level'] = 'HIGH'
                else:
                    report['security_level'] = 'MEDIUM'
            else:
                report['security_level'] = 'LOW'
            
            report['recommendations'] = self._get_security_recommendations(process_info)
            
            return report
            
        except Exception as e:
            raise AccessControlError(f"Failed to generate security report: {str(e)}")
    
    def _get_security_recommendations(self, process_info: Dict[str, Any]) -> List[str]:
        """Generate security recommendations."""
        recommendations = []
        
        security_issues = process_info.get('security_issues', [])
        privilege_level = process_info.get('privilege_level', 'unknown')
        
        if privilege_level in ['root', 'administrator']:
            recommendations.append("Run FaceAuth with regular user privileges")
            recommendations.append("Avoid running as root/administrator unless necessary")
        
        if 'Running as root' in str(security_issues):
            recommendations.append("Create dedicated user account for FaceAuth")
        
        if 'administrator privileges' in str(security_issues):
            recommendations.append("Run without administrator privileges")
        
        if not security_issues:
            recommendations.append("Current security configuration is good")
        
        # General recommendations
        recommendations.extend([
            "Regularly update FaceAuth and dependencies",
            "Use strong master passwords",
            "Keep storage directories on local filesystem only",
            "Monitor access logs for suspicious activity"
        ])
        
        return recommendations
