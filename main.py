#!/usr/bin/env python3
"""
FaceAuth - Local Face Authentication System
Main CLI interface for face enrollment and authentication.
"""

import sys
import os
import click
import time
import logging
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from faceauth.core.enrollment import FaceEnrollmentManager, FaceEnrollmentError
from faceauth.core.authentication import FaceAuthenticator, AuthenticationError
from faceauth.crypto.file_encryption import FileEncryption, EncryptionError
from faceauth.utils.storage import FaceDataStorage, BackupManager
from faceauth.utils.security import SecurityManager
from faceauth.cli import config_commands, completion_commands

# Import security modules
from faceauth.security.compliance_checker import ComplianceChecker
from faceauth.security.privacy_manager import PrivacyManager
from faceauth.security.audit_logger import SecureAuditLogger
from faceauth.security.secure_storage import SecureStorage


@click.group()
@click.version_option(version='1.0.0')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--debug', is_flag=True, help='Enable debug logging')
@click.pass_context
def cli(ctx, verbose, debug):
    """
    FaceAuth - Local Face Authentication System
    
    A privacy-first face authentication platform that keeps all data local.
    
    Main Commands:
      enroll-face     Enroll a new user's face
      verify-face     Verify a user's identity  
      encrypt-file    Encrypt a file with face authentication
      decrypt-file    Decrypt a file with face authentication
      list-users      List all enrolled users
      
    Security & Privacy Commands:
      privacy-check   Check privacy compliance and generate reports
      compliance-check Run compliance checks against security standards
      security-audit  Perform comprehensive security audit
      privacy-settings Manage privacy settings for individual users
      
    Management Commands:
      config-*        Configuration management
      install-completion   Install shell completion
      system-check    Check system requirements
      
    For detailed help on any command, use: faceauth COMMAND --help
    """
    # Configure logging
    if debug:
        log_level = logging.DEBUG
    elif verbose:
        log_level = logging.INFO
    else:
        log_level = logging.WARNING
    
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Store context for sub-commands
    ctx.ensure_object(dict)
    ctx.obj['verbose'] = verbose
    ctx.obj['debug'] = debug


# Add CLI command groups
cli.add_command(config_commands)
cli.add_command(completion_commands)


def print_status(message: str, status_type: str = "info", quiet: bool = False):
    """Print status message with appropriate icon and formatting."""
    if quiet:
        return
    
    icons = {
        "info": "ℹ️",
        "success": "✅",
        "error": "❌",
        "warning": "⚠️",
        "progress": "🔄",
        "security": "🔐",
        "user": "👤",
        "file": "📁",
        "time": "⏱️",
        "stats": "📊"
    }
    
    icon = icons.get(status_type, "•")
    click.echo(f"{icon} {message}")


def print_progress_bar(current: int, total: int, description: str = "", quiet: bool = False):
    """Print a simple progress bar."""
    if quiet:
        return
    
    if total <= 0:
        return
        
    percentage = (current / total) * 100
    bar_length = 30
    filled_length = int(bar_length * current // total)
    bar = '█' * filled_length + '-' * (bar_length - filled_length)
    
    click.echo(f"\r{description} |{bar}| {percentage:.1f}% ({current}/{total})", nl=False)
    
    if current >= total:
        click.echo()  # New line when complete


def handle_cli_error(error: Exception, context: str = "", debug: bool = False):
    """Handle CLI errors with appropriate formatting and debug info."""
    click.echo(f"❌ Error: {str(error)}", err=True)
    
    if context:
        click.echo(f"   Context: {context}", err=True)
    
    if debug:
        import traceback
        click.echo("\n🐛 Debug Information:", err=True)
        click.echo(traceback.format_exc(), err=True)
    
    # Return appropriate exit codes
    if isinstance(error, (FileNotFoundError, PermissionError)):
        return 2
    elif isinstance(error, (ValueError, TypeError)):
        return 3
    else:
        return 1


@cli.command()
@click.argument('user_id', type=str)
@click.option('--timeout', '-t', default=30, help='Enrollment timeout in seconds (default: 30)')
@click.option('--storage-dir', '-s', help='Custom storage directory for face data')
@click.option('--master-key', '-k', help='Master key for encryption (optional)')
@click.option('--quiet', '-q', is_flag=True, help='Quiet mode - minimal output')
@click.pass_context
def enroll_face(ctx, user_id: str, timeout: int, storage_dir: str, master_key: str, quiet: bool):
    """
    Enroll a new user's face into the FaceAuth system.
    
    USER_ID: Unique identifier for the user (e.g., username, email)
    
    Examples:
        faceauth enroll-face john.doe
        faceauth enroll-face alice@example.com --timeout 45
        faceauth enroll-face user123 --storage-dir /custom/path
        
    The enrollment process will:
    1. Initialize the face recognition system
    2. Start webcam capture
    3. Collect multiple face samples for accuracy
    4. Generate secure enrollment data
    5. Store encrypted face data locally
    """
    verbose = ctx.obj.get('verbose', False)
    debug = ctx.obj.get('debug', False)
    
    try:
        if not quiet:
            click.echo("🔐 FaceAuth - Face Enrollment")
            click.echo("=" * 40)
            print_status(f"User ID: {user_id}", "user", quiet)
            print_status(f"Timeout: {timeout}s", "time", quiet)
            if storage_dir:
                print_status(f"Storage: {storage_dir}", "file", quiet)
            if verbose:
                print_status(f"Master key: {'Set' if master_key else 'Not set'}", "security", quiet)
            click.echo()
        
        # Validate user ID
        if not user_id or len(user_id.strip()) == 0:
            click.echo("❌ Error: User ID cannot be empty", err=True)
            sys.exit(1)
        
        user_id = user_id.strip()
        
        # Initialize enrollment manager
        print_status("Initializing face recognition system...", "progress", quiet)
        
        enrollment_manager = FaceEnrollmentManager(
            storage_dir=storage_dir,
            master_key=master_key
        )
        
        # Initialize privacy manager for consent handling
        storage_path = Path(storage_dir or str(Path.home() / '.faceauth'))
        privacy_manager = PrivacyManager(str(storage_path))
        
        # Check if user already exists
        if enrollment_manager.verify_enrollment(user_id):
            click.echo(f"❌ Error: User '{user_id}' is already enrolled", err=True)
            click.echo("💡 Tip: Use 'delete-user' command to remove existing enrollment first", err=True)
            sys.exit(1)
        
        # Request consent for data processing
        if not quiet:
            click.echo("\n📋 Data Processing Consent")
            click.echo("FaceAuth needs to process and store your facial data for authentication.")
            click.echo("Your data will be:")
            click.echo("  • Stored locally on your device")
            click.echo("  • Encrypted with strong encryption")
            click.echo("  • Never transmitted to external servers")
            click.echo("  • Used only for authentication purposes")
            click.echo()
            
            if not click.confirm("Do you consent to facial data processing for authentication?"):
                print_status("Enrollment cancelled - consent not given", "warning", quiet)
                sys.exit(1)
        
        # Record consent
        privacy_manager.grant_consent(user_id, purposes=['authentication'])
        
        print_status("System initialized successfully", "success", quiet)
        
        if not quiet and verbose:
            print_status("Starting webcam...", "progress", quiet)
            print_status("Position your face clearly in the camera view", "info", quiet)
            print_status("Look directly at the camera and move slightly for better coverage", "info", quiet)
        
        # Start enrollment process
        result = enrollment_manager.enroll_user(
            user_id=user_id,
            timeout=timeout,
            interactive=not quiet
        )
        
        # Handle results
        if result['success']:
            if not quiet:
                click.echo()
                print_status("Enrollment completed successfully!", "success", quiet)
                click.echo("=" * 30)
                print_status(f"User '{user_id}' enrolled successfully", "success", quiet)
                print_status(f"Samples collected: {result['samples_collected']}", "stats", quiet)
                print_status(f"Quality score: {result['average_quality']:.3f}", "stats", quiet)
                print_status(f"Duration: {result['duration']:.1f}s", "time", quiet)
                
                if verbose:
                    print_status("Face data encrypted and stored securely", "security", quiet)
                    print_status("You can now use verify-face to authenticate", "info", quiet)
            else:
                click.echo(f"SUCCESS: User '{user_id}' enrolled")
            
            sys.exit(0)
        else:
            error_messages = {
                'USER_EXISTS': f"User '{user_id}' is already enrolled",
                'CAMERA_ERROR': "Could not access camera. Please check camera permissions",
                'TIMEOUT': f"Enrollment timed out after {timeout}s",
                'CANCELLED': "Enrollment was cancelled by user",
                'UNKNOWN_ERROR': "An unexpected error occurred"
            }
            
            error_code = result.get('code', 'UNKNOWN_ERROR')
            error_msg = error_messages.get(error_code, result.get('error', 'Unknown error'))
            
            click.echo(f"❌ Enrollment Failed: {error_msg}", err=True)
            
            if 'samples_collected' in result and result['samples_collected'] > 0:
                click.echo(f"   Samples collected before failure: {result['samples_collected']}")
            
            # Provide helpful suggestions
            if error_code == 'CAMERA_ERROR':
                click.echo("💡 Troubleshooting tips:", err=True)
                click.echo("   • Ensure webcam is connected and not in use by other apps", err=True)
                click.echo("   • Check camera permissions for this application", err=True)
                click.echo("   • Try running 'system-check' to verify camera access", err=True)
            elif error_code == 'TIMEOUT':
                click.echo("💡 Troubleshooting tips:", err=True)
                click.echo("   • Increase timeout with --timeout option", err=True)
                click.echo("   • Ensure good lighting conditions", err=True)
                click.echo("   • Position face clearly in camera view", err=True)
            
            sys.exit(1)
            
    except FaceEnrollmentError as e:
        exit_code = handle_cli_error(e, "Face enrollment failed", debug)
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print_status("Enrollment cancelled by user", "warning", quiet)
        sys.exit(1)
    except Exception as e:
        exit_code = handle_cli_error(e, "Unexpected error during enrollment", debug)
        sys.exit(exit_code)


@cli.command('verify-face')
@click.argument('user_id', type=str)
@click.option('--timeout', '-t', default=10, help='Authentication timeout in seconds (default: 10)')
@click.option('--max-attempts', '-a', default=5, help='Maximum authentication attempts (default: 5)')
@click.option('--threshold', '-th', default=0.6, help='Similarity threshold for authentication (default: 0.6)')
@click.option('--storage-dir', '-s', help='Custom storage directory for face data')
@click.option('--master-key', '-k', help='Master key for encryption (optional)')
@click.option('--quiet', '-q', is_flag=True, help='Quiet mode - minimal output')
@click.option('--show-metrics', '-m', is_flag=True, help='Show detailed authentication metrics')
@click.pass_context
def verify_face(ctx, user_id: str, timeout: int, max_attempts: int, threshold: float, 
                storage_dir: str, master_key: str, quiet: bool, show_metrics: bool):
    """
    Verify a user's identity using real-time face authentication.
    
    USER_ID: Unique identifier for the enrolled user
    
    Examples:
        faceauth verify-face john.doe
        faceauth verify-face alice@example.com --timeout 15 --threshold 0.7
        faceauth verify-face user123 --show-metrics --verbose
    """
    verbose = ctx.obj.get('verbose', False)
    debug = ctx.obj.get('debug', False)
    
    try:
        if not quiet:
            click.echo("🔐 FaceAuth - Real-time Face Verification")
            click.echo("=" * 45)
        
        # Validate threshold
        if not 0.1 <= threshold <= 1.0:
            click.echo("❌ Error: Threshold must be between 0.1 and 1.0", err=True)
            sys.exit(1)
        
        # Initialize storage and authenticator with security features
        print_status("Initializing authentication system...", "progress", quiet)
        security_manager = SecurityManager(master_key)
        storage = FaceDataStorage(storage_dir, security_manager)
        authenticator = FaceAuthenticator(storage, similarity_threshold=threshold, storage_dir=storage_dir)
        
        # Initialize privacy manager
        storage_path = Path(storage_dir or str(Path.home() / '.faceauth'))
        privacy_manager = PrivacyManager(str(storage_path))
        
        # Check if user exists and has valid consent
        if not storage.user_exists(user_id):
            click.echo(f"❌ Error: User '{user_id}' is not enrolled", err=True)
            click.echo("💡 Tip: Use 'enroll-face' command to enroll the user first", err=True)
            sys.exit(1)
        
        # Check privacy consent
        if not privacy_manager.is_processing_allowed(user_id):
            click.echo(f"❌ Error: Data processing not permitted for user '{user_id}'", err=True)
            click.echo("💡 Tip: Use 'privacy-settings' command to grant consent", err=True)
            sys.exit(1)
            sys.exit(1)
        
        if not quiet:
            print_status(f"User ID: {user_id}", "user", quiet)
            print_status(f"Timeout: {timeout}s", "time", quiet)
            print_status(f"Similarity threshold: {threshold}", "stats", quiet)
            print_status(f"Max attempts: {max_attempts}", "stats", quiet)
            if verbose:
                print_status("Starting webcam for authentication...", "progress", quiet)
                print_status("Look directly at the camera", "info", quiet)
            click.echo()
        
        # Start authentication
        start_time = time.time()
        
        result = authenticator.authenticate_realtime(
            user_id=user_id,
            timeout=timeout,
            max_attempts=max_attempts
        )
        
        total_time = time.time() - start_time
        
        if result['success']:
            if not quiet:
                click.echo()
                print_status("Authentication successful!", "success", quiet)
                print_status(f"Similarity Score: {result['similarity']:.3f}", "stats", quiet)
                print_status(f"Duration: {result['duration']:.2f}s", "time", quiet)
                print_status(f"Attempts Used: {result['attempts']}", "stats", quiet)
                
                if show_metrics:
                    click.echo()
                    click.echo("📊 Detailed Metrics:")
                    print_status(f"Best Similarity: {result['best_similarity']:.3f}", "stats", quiet)
                    quality = result.get('quality_metrics', {})
                    if quality:
                        print_status(f"Image Sharpness: {quality.get('sharpness', 0):.1f}", "stats", quiet)
                        print_status(f"Image Brightness: {quality.get('brightness', 0):.1f}", "stats", quiet)
                        print_status(f"Image Contrast: {quality.get('contrast', 0):.1f}", "stats", quiet)
            else:
                click.echo("SUCCESS")
            
            sys.exit(0)
        
        else:
            if not quiet:
                click.echo()
                print_status("Authentication failed!", "error", quiet)
                print_status(f"Reason: {result['error']}", "error", quiet)
                print_status(f"Duration: {result['duration']:.2f}s", "time", quiet)
                
                if 'best_similarity' in result:
                    print_status(f"Best Similarity: {result['best_similarity']:.3f}", "stats", quiet)
                    print_status(f"Required Threshold: {threshold}", "stats", quiet)
                
                # Provide helpful suggestions
                click.echo()
                click.echo("💡 Suggestions:")
                error_type = result.get('error_type')
                if error_type == 'user_not_found':
                    print_status("Ensure the user ID is correct", "info", quiet)
                    print_status("Use 'list-users' to see enrolled users", "info", quiet)
                elif error_type == 'webcam_error':
                    print_status("Check webcam connection", "info", quiet)
                    print_status("Close other applications using the camera", "info", quiet)
                elif error_type == 'timeout':
                    print_status("Try increasing timeout with --timeout option", "info", quiet)
                    print_status("Ensure good lighting conditions", "info", quiet)
                    print_status("Position face clearly in camera view", "info", quiet)
                elif error_type == 'max_attempts_exceeded':
                    print_status("Try lowering threshold with --threshold option", "info", quiet)
                    print_status("Ensure good lighting and camera positioning", "info", quiet)
                    print_status("Consider re-enrolling if face has changed significantly", "info", quiet)
            else:
                click.echo("FAILED")
            
            sys.exit(1)
                
    except AuthenticationError as e:
        exit_code = handle_cli_error(e, "Authentication system error", debug)
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print_status("Authentication cancelled by user", "warning", quiet)
        sys.exit(1)
    except Exception as e:
        exit_code = handle_cli_error(e, "Unexpected error during authentication", debug)
        sys.exit(exit_code)


@cli.command()
@click.option('--storage-dir', '-s', help='Custom storage directory for face data')
@click.option('--master-key', '-k', help='Master key for encryption (optional)')
@click.pass_context
def list_users(ctx, storage_dir: str, master_key: str):
    """List all enrolled users in the system."""
    verbose = ctx.obj.get('verbose', False)
    debug = ctx.obj.get('debug', False)
    
    try:
        # Initialize storage
        security_manager = SecurityManager(master_key)
        storage = FaceDataStorage(storage_dir, security_manager)
        
        # Get enrolled users
        users = storage.list_enrolled_users()
        
        if not users:
            print_status("No users enrolled in the system", "info")
            return
        
        click.echo("👥 Enrolled Users")
        click.echo("=" * 20)
        
        for i, user_id in enumerate(users, 1):
            metadata = storage.get_user_metadata(user_id)
            
            click.echo(f"{i:2d}. {user_id}")
            
            if metadata and verbose:
                if 'enrollment_duration' in metadata:
                    click.echo(f"     Enrollment time: {metadata['enrollment_duration']:.1f}s")
                if 'average_quality' in metadata:
                    click.echo(f"     Quality score: {metadata['average_quality']:.3f}")
                if 'samples_collected' in metadata:
                    click.echo(f"     Samples: {metadata['samples_collected']}")
            
            if verbose:
                click.echo()
        
        print_status(f"Total: {len(users)} enrolled users", "stats")
        
    except Exception as e:
        exit_code = handle_cli_error(e, "Error listing users", debug)
        sys.exit(exit_code)


@cli.command()
def system_check():
    """Check system requirements and dependencies."""
    click.echo("🔍 FaceAuth System Check")
    click.echo("=" * 30)
    
    # Check Python version
    python_version = sys.version_info
    print_status(f"Python version: {python_version.major}.{python_version.minor}.{python_version.micro}", "info")
    
    if python_version < (3, 8):
        print_status("Python 3.8+ is required", "error")
        return False
    else:
        print_status("Python version OK", "success")
    
    # Check dependencies
    dependencies = [
        ('opencv-python', 'cv2'),
        ('numpy', 'numpy'),
        ('torch', 'torch'),
        ('facenet-pytorch', 'facenet_pytorch'),
        ('cryptography', 'cryptography'),
        ('click', 'click'),
        ('Pillow', 'PIL')
    ]
    
    missing_deps = []
    
    for package_name, import_name in dependencies:
        try:
            __import__(import_name)
            print_status(f"{package_name}", "success")
        except ImportError:
            print_status(f"{package_name} (missing)", "error")
            missing_deps.append(package_name)
    
    if missing_deps:
        click.echo()
        print_status("Missing dependencies:", "warning")
        for dep in missing_deps:
            click.echo(f"   • {dep}")
        click.echo()
        print_status("Install missing dependencies with:", "info")
        click.echo("   pip install -r requirements.txt")
    else:
        click.echo()
        print_status("All dependencies are installed!", "success")
    
    # Check camera access
    try:
        import cv2
        cap = cv2.VideoCapture(0)
        if cap.isOpened():
            print_status("Camera access OK", "success")
            cap.release()
        else:
            print_status("Cannot access camera", "error")
    except ImportError:
        print_status("Cannot test camera (OpenCV not installed)", "warning")
    except Exception:
        print_status("Camera test failed", "error")


@cli.command()
def version():
    """Show the version of FaceAuth."""
    click.echo("FaceAuth version 1.0.0")
    click.echo("A privacy-first face authentication platform")


@cli.command()
@click.argument('file_path', type=click.Path(exists=True))
@click.argument('user_id', type=str)
@click.option('--output', '-o', help='Output path for encrypted file')
@click.option('--kdf-method', '-k', default='argon2', 
              type=click.Choice(['argon2', 'pbkdf2', 'scrypt', 'multi']),
              help='Key derivation method (default: argon2)')
@click.option('--auth-timeout', '-t', default=10, help='Authentication timeout in seconds')
@click.option('--overwrite', '-f', is_flag=True, help='Overwrite existing files')
@click.option('--storage-dir', '-s', help='Custom storage directory for face data')
@click.option('--master-key', '-m', help='Master key for encryption (optional)')
@click.option('--quiet', '-q', is_flag=True, help='Quiet mode - minimal output')
@click.pass_context
def encrypt_file(ctx, file_path: str, user_id: str, output: str, kdf_method: str, 
                auth_timeout: int, overwrite: bool, storage_dir: str, 
                master_key: str, quiet: bool):
    """
    Encrypt a file using face authentication.
    
    FILE_PATH: Path to the file to encrypt
    USER_ID: User ID for face authentication
    
    Examples:
        faceauth encrypt-file document.pdf john.doe
        faceauth encrypt-file secret.txt alice --output secret.txt.encrypted
        faceauth encrypt-file data.json user123 --kdf-method pbkdf2
    """
    verbose = ctx.obj.get('verbose', False)
    debug = ctx.obj.get('debug', False)
    
    try:
        if not quiet:
            click.echo("🔒 FaceAuth - File Encryption")
            click.echo("=" * 35)
        
        # Initialize components
        security_manager = SecurityManager(master_key)
        storage = FaceDataStorage(storage_dir, security_manager)
        file_encryption = FileEncryption(storage)
        
        # Check if user exists
        if not storage.user_exists(user_id):
            click.echo(f"❌ Error: User '{user_id}' is not enrolled", err=True)
            click.echo("💡 Tip: Use 'enroll-face' command to enroll the user first", err=True)
            sys.exit(1)
        
        if not quiet:
            print_status(f"File: {file_path}", "file", quiet)
            print_status(f"User: {user_id}", "user", quiet)
            print_status(f"KDF Method: {kdf_method}", "security", quiet)
            print_status(f"Auth Timeout: {auth_timeout}s", "time", quiet)
            if verbose:
                print_status("Starting face authentication for encryption...", "progress", quiet)
            click.echo()
        
        # Perform encryption
        result = file_encryption.encrypt_file(
            file_path=file_path,
            user_id=user_id,
            output_path=output,
            kdf_method=kdf_method,
            auth_timeout=auth_timeout,
            overwrite=overwrite
        )
        
        if result['success']:
            if not quiet:
                click.echo()
                print_status("File encryption successful!", "success", quiet)
                print_status(f"Input: {result['input_file']}", "file", quiet)
                print_status(f"Output: {result['output_file']}", "file", quiet)
                print_status(f"Original Size: {result['original_size']:,} bytes", "stats", quiet)
                print_status(f"Encrypted Size: {result['encrypted_size']:,} bytes", "stats", quiet)
                print_status(f"Overhead: {result['encrypted_size'] - result['original_size']:,} bytes", "stats", quiet)
                print_status(f"Duration: {result['duration']:.2f}s", "time", quiet)
                print_status(f"KDF Method: {result['kdf_method']}", "security", quiet)
            else:
                click.echo("SUCCESS")
            
            sys.exit(0)
        else:
            click.echo("❌ Encryption failed", err=True)
            sys.exit(1)
            
    except EncryptionError as e:
        exit_code = handle_cli_error(e, "File encryption failed", debug)
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print_status("Encryption cancelled by user", "warning", quiet)
        sys.exit(1)
    except Exception as e:
        exit_code = handle_cli_error(e, "Unexpected error during encryption", debug)
        sys.exit(exit_code)


@cli.command('decrypt-file')
@click.argument('encrypted_path', type=click.Path(exists=True))
@click.argument('user_id', type=str)
@click.option('--output', '-o', help='Output path for decrypted file')
@click.option('--auth-timeout', '-t', default=10, help='Authentication timeout in seconds')
@click.option('--overwrite', '-f', is_flag=True, help='Overwrite existing files')
@click.option('--storage-dir', '-s', help='Custom storage directory for face data')
@click.option('--master-key', '-m', help='Master key for encryption (optional)')
@click.option('--quiet', '-q', is_flag=True, help='Quiet mode - minimal output')
@click.option('--verify-only', '-v', is_flag=True, help='Only verify file, do not decrypt')
@click.pass_context
def decrypt_file(ctx, encrypted_path: str, user_id: str, output: str, auth_timeout: int,
                overwrite: bool, storage_dir: str, master_key: str, quiet: bool,
                verify_only: bool):
    """
    Decrypt a FaceAuth encrypted file.
    
    ENCRYPTED_PATH: Path to the encrypted file
    USER_ID: User ID for face authentication
    
    Examples:
        faceauth decrypt-file document.pdf.faceauth john.doe
        faceauth decrypt-file secret.txt.encrypted alice --output secret.txt
        faceauth decrypt-file data.json.faceauth user123 --verify-only
    """
    verbose = ctx.obj.get('verbose', False)
    debug = ctx.obj.get('debug', False)
    
    try:
        if not quiet:
            click.echo("🔓 FaceAuth - File Decryption")
            click.echo("=" * 35)
        
        # Initialize components
        security_manager = SecurityManager(master_key)
        storage = FaceDataStorage(storage_dir, security_manager)
        file_encryption = FileEncryption(storage)
        
        # Verify file first
        file_info = file_encryption.verify_encrypted_file(encrypted_path)
        
        if not file_info.get('is_faceauth_file', False):
            error_msg = file_info.get('error', 'Not a FaceAuth encrypted file')
            click.echo(f"❌ Error: {error_msg}", err=True)
            sys.exit(1)
        
        if not quiet:
            print_status(f"Encrypted File: {encrypted_path}", "file", quiet)
            print_status(f"Original Name: {file_info['original_filename']}", "file", quiet)
            print_status(f"Original Size: {file_info['original_size']:,} bytes", "stats", quiet)
            print_status(f"Encrypted Size: {file_info['encrypted_size']:,} bytes", "stats", quiet)
            print_status(f"KDF Method: {file_info['kdf_method']}", "security", quiet)
            print_status(f"User: {user_id}", "user", quiet)
            if verbose:
                print_status(f"File Format Version: {file_info['file_format_version']}", "info", quiet)
            click.echo()
        
        if verify_only:
            if not quiet:
                print_status("File verification successful!", "success", quiet)
                print_status("File is a valid FaceAuth encrypted file", "success", quiet)
            else:
                click.echo("VALID")
            sys.exit(0)
        
        # Check if user exists
        if not storage.user_exists(user_id):
            click.echo(f"❌ Error: User '{user_id}' is not enrolled", err=True)
            sys.exit(1)
        
        if verbose and not quiet:
            print_status("Starting face authentication for decryption...", "progress", quiet)
        
        # Perform decryption
        result = file_encryption.decrypt_file(
            encrypted_path=encrypted_path,
            user_id=user_id,
            output_path=output,
            auth_timeout=auth_timeout,
            overwrite=overwrite
        )
        
        if result['success']:
            if not quiet:
                click.echo()
                print_status("File decryption successful!", "success", quiet)
                print_status(f"Encrypted File: {result['encrypted_file']}", "file", quiet)
                print_status(f"Output: {result['output_file']}", "file", quiet)
                print_status(f"File Size: {result['file_size']:,} bytes", "stats", quiet)
                print_status(f"Duration: {result['duration']:.2f}s", "time", quiet)
                print_status(f"Original Name: {result['original_filename']}", "file", quiet)
            else:
                click.echo("SUCCESS")
            
            sys.exit(0)
        else:
            click.echo("❌ Decryption failed", err=True)
            sys.exit(1)
            
    except EncryptionError as e:
        exit_code = handle_cli_error(e, "File decryption failed", debug)
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print_status("Decryption cancelled by user", "warning", quiet)
        sys.exit(1)
    except Exception as e:
        exit_code = handle_cli_error(e, "Unexpected error during decryption", debug)
        sys.exit(exit_code)


@cli.command('privacy-check')
@click.option('--storage-dir', '-s', help='Custom storage directory')
@click.option('--user-id', '-u', help='Check privacy for specific user')
@click.option('--export', '-e', help='Export privacy report to file')
@click.option('--quiet', '-q', is_flag=True, help='Quiet mode - minimal output')
@click.pass_context
def privacy_check(ctx, storage_dir: str, user_id: str, export: str, quiet: bool):
    """
    Check privacy compliance and generate privacy reports.
    
    Examples:
        faceauth privacy-check
        faceauth privacy-check --user-id john.doe
        faceauth privacy-check --export privacy_report.json
    """
    verbose = ctx.obj.get('verbose', False)
    debug = ctx.obj.get('debug', False)
    
    try:
        if not quiet:
            click.echo("🔒 FaceAuth - Privacy Compliance Check")
            click.echo("=" * 40)
        
        # Initialize privacy manager
        storage_path = Path(storage_dir or str(Path.home() / '.faceauth'))
        privacy_manager = PrivacyManager(str(storage_path))
        
        if user_id:
            # Check specific user
            user_data = privacy_manager.get_user_data_summary(user_id)
            if user_data:
                if not quiet:
                    print_status(f"Privacy data for user: {user_id}", "user", quiet)
                    print_status(f"Data stored: {user_data['has_data']}", "info", quiet)
                    print_status(f"Consent given: {user_data['consent_given']}", "info", quiet)
                    print_status(f"Processing allowed: {user_data['processing_allowed']}", "info", quiet)
                    if user_data['retention_until']:
                        print_status(f"Retention until: {user_data['retention_until']}", "time", quiet)
            else:
                click.echo(f"❌ No privacy data found for user: {user_id}", err=True)
                sys.exit(1)
        else:
            # Generate full privacy report
            report = privacy_manager.generate_privacy_report()
            
            if not quiet:
                print_status("Privacy Compliance Summary", "info", quiet)
                print_status(f"Total users: {report['statistics']['total_users']}", "stats", quiet)
                print_status(f"Total data records: {report['statistics']['total_data_records']}", "stats", quiet)
                print_status(f"Data types: {', '.join(report['statistics']['data_types'])}", "stats", quiet)
                print_status(f"Auto cleanup enabled: {report['compliance_status']['auto_cleanup_enabled']}", "stats", quiet)
                
                if verbose:
                    print_status(f"Expired data records: {report['statistics']['expired_data_records']}", "stats", quiet)
                    print_status(f"Expired consent records: {report['statistics']['expired_consent_records']}", "stats", quiet)
            
            if export:
                import json
                with open(export, 'w') as f:
                    json.dump(report, f, indent=2, default=str)
                print_status(f"Privacy report exported to: {export}", "file", quiet)
        
        sys.exit(0)
        
    except Exception as e:
        exit_code = handle_cli_error(e, "Privacy check failed", debug)
        sys.exit(exit_code)


@cli.command('compliance-check')
@click.option('--standard', '-s', multiple=True, 
              type=click.Choice(['gdpr', 'ccpa', 'soc2', 'iso27001', 'nist']),
              help='Compliance standards to check (can specify multiple)')
@click.option('--storage-dir', '-d', help='Custom storage directory')
@click.option('--export', '-e', help='Export compliance report to file')
@click.option('--quiet', '-q', is_flag=True, help='Quiet mode - minimal output')
@click.pass_context
def compliance_check(ctx, standard: tuple, storage_dir: str, export: str, quiet: bool):
    """
    Run comprehensive compliance checks against security standards.
    
    Examples:
        faceauth compliance-check
        faceauth compliance-check --standard gdpr --standard ccpa
        faceauth compliance-check --export compliance_report.json
    """
    verbose = ctx.obj.get('verbose', False)
    debug = ctx.obj.get('debug', False)
    
    try:
        if not quiet:
            click.echo("📋 FaceAuth - Compliance Assessment")
            click.echo("=" * 40)
        
        # Initialize compliance checker
        storage_path = Path(storage_dir or str(Path.home() / '.faceauth'))
        compliance_checker = ComplianceChecker(str(storage_path))
        
        # Run compliance checks
        if standard:
            # Check specific standards
            results = {}
            for std in standard:
                if not quiet:
                    print_status(f"Checking {std.upper()} compliance...", "progress", quiet)
                
                result = compliance_checker.check_compliance(std)
                results[std] = result
                
                if not quiet:
                    compliance_score = result['compliance_score']
                    status_type = "success" if compliance_score >= 0.8 else "warning" if compliance_score >= 0.6 else "error"
                    print_status(f"{std.upper()}: {compliance_score:.1%} compliant", status_type, quiet)
                    
                    if verbose:
                        passed_checks = sum(1 for check in result['checks'] if check['status'] == 'pass')
                        total_checks = len(result['checks'])
                        print_status(f"   Passed: {passed_checks}/{total_checks} checks", "stats", quiet)
        else:
            # Run all compliance checks
            if not quiet:
                print_status("Running comprehensive compliance assessment...", "progress", quiet)
            
            results = compliance_checker.run_all_compliance_checks()
            
            if not quiet:
                print_status("Compliance Results Summary", "info", quiet)
                for std_name, result in results.items():
                    compliance_score = result['compliance_score']
                    status_type = "success" if compliance_score >= 0.8 else "warning" if compliance_score >= 0.6 else "error"
                    print_status(f"{std_name.upper()}: {compliance_score:.1%}", status_type, quiet)
        
        # Export results if requested
        if export:
            import json
            with open(export, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            print_status(f"Compliance report exported to: {export}", "file", quiet)
        
        # Check if any compliance issues need attention
        low_compliance = any(
            result['compliance_score'] < 0.8 
            for result in results.values()
        )
        
        if low_compliance and not quiet:
            click.echo("\n⚠️  Some compliance issues detected. Use --verbose for details.")
            click.echo("💡 Consider running 'faceauth security-audit' for remediation suggestions.")
        
        sys.exit(0 if not low_compliance else 1)
        
    except Exception as e:
        exit_code = handle_cli_error(e, "Compliance check failed", debug)
        sys.exit(exit_code)


@cli.command('security-audit')
@click.option('--storage-dir', '-d', help='Custom storage directory')
@click.option('--fix', '-f', is_flag=True, help='Automatically fix security issues where possible')
@click.option('--export', '-e', help='Export audit report to file')
@click.option('--quiet', '-q', is_flag=True, help='Quiet mode - minimal output')
@click.pass_context
def security_audit(ctx, storage_dir: str, fix: bool, export: str, quiet: bool):
    """
    Perform comprehensive security audit and provide remediation suggestions.
    
    Examples:
        faceauth security-audit
        faceauth security-audit --fix
        faceauth security-audit --export security_audit.json
    """
    verbose = ctx.obj.get('verbose', False)
    debug = ctx.obj.get('debug', False)
    
    try:
        if not quiet:
            click.echo("🛡️  FaceAuth - Security Audit")
            click.echo("=" * 40)
        
        storage_path = storage_dir or str(Path.home() / '.faceauth')
        
        # Initialize security components
        secure_storage = SecureStorage(storage_path)
        audit_logger = SecureAuditLogger(Path(storage_path) / 'logs')
        compliance_checker = ComplianceChecker(storage_path)
        
        audit_results = {
            'timestamp': time.time(),
            'storage_path': storage_path,
            'checks': [],
            'issues': [],
            'recommendations': []
        }
        
        if not quiet:
            print_status("Performing security audit...", "progress", quiet)
        
        # Check storage security
        storage_issues = secure_storage.validate_security()
        if storage_issues:
            audit_results['issues'].extend(storage_issues)
            if not quiet:
                for issue in storage_issues:
                    print_status(f"Storage issue: {issue}", "warning", quiet)
        
        # Check audit logs
        try:
            log_integrity = audit_logger.verify_log_integrity()
            if log_integrity['valid']:
                audit_results['checks'].append({
                    'category': 'audit_logs',
                    'check': 'log_integrity',
                    'status': 'pass',
                    'details': 'Audit logs are intact and tamper-evident'
                })
            else:
                audit_results['issues'].append({
                    'category': 'audit_logs',
                    'severity': 'high',
                    'issue': 'Log integrity compromised',
                    'details': log_integrity.get('error', 'Unknown integrity issue')
                })
        except Exception as e:
            audit_results['issues'].append({
                'category': 'audit_logs',
                'severity': 'medium',
                'issue': 'Cannot verify log integrity',
                'details': str(e)
            })
        
        # Run compliance checks for security recommendations
        compliance_results = compliance_checker.run_all_compliance_checks()
        for std_name, result in compliance_results.items():
            failed_checks = [check for check in result['checks'] if check['status'] != 'pass']
            for check in failed_checks:
                audit_results['recommendations'].append({
                    'standard': std_name,
                    'recommendation': check['description'],
                    'priority': 'high' if check['status'] == 'fail' else 'medium'
                })
        
        # Generate summary
        high_issues = len([issue for issue in audit_results['issues'] if issue.get('severity') == 'high'])
        medium_issues = len([issue for issue in audit_results['issues'] if issue.get('severity') == 'medium'])
        
        if not quiet:
            click.echo()
            print_status("Security Audit Summary", "info", quiet)
            print_status(f"High priority issues: {high_issues}", "error" if high_issues > 0 else "success", quiet)
            print_status(f"Medium priority issues: {medium_issues}", "warning" if medium_issues > 0 else "success", quiet)
            print_status(f"Recommendations: {len(audit_results['recommendations'])}", "info", quiet)
            
            if verbose and audit_results['recommendations']:
                click.echo("\n💡 Top Recommendations:")
                for rec in audit_results['recommendations'][:5]:
                    click.echo(f"   • [{rec['standard'].upper()}] {rec['recommendation']}")
        
        # Auto-fix if requested
        if fix and audit_results['issues']:
            if not quiet:
                print_status("Attempting to fix security issues...", "progress", quiet)
            
            fixed_count = 0
            for issue in audit_results['issues']:
                if issue['category'] == 'storage' and 'permissions' in issue.get('details', ''):
                    try:
                        secure_storage.fix_permissions()
                        fixed_count += 1
                    except Exception as e:
                        if verbose:
                            print_status(f"Could not fix: {issue['issue']}", "warning", quiet)
            
            if not quiet:
                print_status(f"Fixed {fixed_count} security issues", "success", quiet)
        
        # Export results if requested
        if export:
            import json
            with open(export, 'w') as f:
                json.dump(audit_results, f, indent=2, default=str)
            print_status(f"Security audit report exported to: {export}", "file", quiet)
        
        sys.exit(0 if high_issues == 0 else 1)
        
    except Exception as e:
        exit_code = handle_cli_error(e, "Security audit failed", debug)
        sys.exit(exit_code)


@cli.command('privacy-settings')
@click.argument('user_id', type=str)
@click.option('--grant-consent', is_flag=True, help='Grant data processing consent')
@click.option('--revoke-consent', is_flag=True, help='Revoke data processing consent')
@click.option('--set-retention', type=int, help='Set data retention period in days')
@click.option('--delete-data', is_flag=True, help='Delete all user data (GDPR right to erasure)')
@click.option('--export-data', help='Export user data to file (GDPR right to portability)')
@click.option('--storage-dir', '-d', help='Custom storage directory')
@click.option('--quiet', '-q', is_flag=True, help='Quiet mode - minimal output')
@click.pass_context
def privacy_settings(ctx, user_id: str, grant_consent: bool, revoke_consent: bool, 
                     set_retention: int, delete_data: bool, export_data: str, 
                     storage_dir: str, quiet: bool):
    """
    Manage privacy settings for individual users.
    
    USER_ID: Unique identifier for the user
    
    Examples:
        faceauth privacy-settings john.doe --grant-consent
        faceauth privacy-settings alice@example.com --set-retention 365
        faceauth privacy-settings user123 --export-data user_data.json
        faceauth privacy-settings john.doe --delete-data
    """
    verbose = ctx.obj.get('verbose', False)
    debug = ctx.obj.get('debug', False)
    
    try:
        if not user_id or len(user_id.strip()) == 0:
            click.echo("❌ Error: User ID cannot be empty", err=True)
            sys.exit(1)
        
        user_id = user_id.strip()
        
        if not quiet:
            click.echo("🔒 FaceAuth - Privacy Settings")
            click.echo("=" * 40)
            print_status(f"User: {user_id}", "user", quiet)
        
        # Initialize privacy manager
        storage_path = Path(storage_dir or str(Path.home() / '.faceauth'))
        privacy_manager = PrivacyManager(str(storage_path))
        
        # Validate that at least one action is specified
        actions = [grant_consent, revoke_consent, set_retention is not None, delete_data, export_data is not None]
        if not any(actions):
            # Show current privacy settings
            user_data = privacy_manager.get_user_data_summary(user_id)
            if user_data:
                if not quiet:
                    print_status("Current Privacy Settings:", "info", quiet)
                    print_status(f"Data stored: {user_data['has_data']}", "info", quiet)
                    print_status(f"Consent given: {user_data['consent_given']}", "info", quiet)
                    print_status(f"Processing allowed: {user_data['processing_allowed']}", "info", quiet)
                    if user_data['retention_until']:
                        print_status(f"Retention until: {user_data['retention_until']}", "time", quiet)
                    else:
                        print_status("Retention: No limit set", "info", quiet)
            else:
                click.echo(f"❌ No data found for user: {user_id}", err=True)
                sys.exit(1)
            
            sys.exit(0)
        
        # Handle conflicting options
        if grant_consent and revoke_consent:
            click.echo("❌ Error: Cannot grant and revoke consent simultaneously", err=True)
            sys.exit(1)
        
        # Execute privacy actions
        if grant_consent:
            privacy_manager.grant_consent(user_id)
            print_status("Data processing consent granted", "success", quiet)
        
        if revoke_consent:
            privacy_manager.revoke_consent(user_id)
            print_status("Data processing consent revoked", "warning", quiet)
        
        if set_retention is not None:
            if set_retention < 0:
                click.echo("❌ Error: Retention period cannot be negative", err=True)
                sys.exit(1)
            
            from datetime import datetime, timedelta
            retention_until = datetime.now() + timedelta(days=set_retention)
            privacy_manager.set_data_retention(user_id, retention_until)
            print_status(f"Data retention set to {set_retention} days", "success", quiet)
        
        if export_data:
            try:
                user_data = privacy_manager.export_user_data(user_id)
                import json
                with open(export_data, 'w') as f:
                    json.dump(user_data, f, indent=2, default=str)
                print_status(f"User data exported to: {export_data}", "file", quiet)
            except Exception as e:
                click.echo(f"❌ Error exporting data: {str(e)}", err=True)
                sys.exit(1)
        
        if delete_data:
            # Confirm deletion
            if not quiet:
                click.echo("⚠️  WARNING: This will permanently delete all data for this user!")
                if not click.confirm("Are you sure you want to continue?"):
                    print_status("Data deletion cancelled", "info", quiet)
                    sys.exit(0)
            
            try:
                privacy_manager.delete_user_data(user_id)
                print_status(f"All data for user '{user_id}' has been permanently deleted", "success", quiet)
            except Exception as e:
                click.echo(f"❌ Error deleting data: {str(e)}", err=True)
                sys.exit(1)
        
        sys.exit(0)
        
    except Exception as e:
        exit_code = handle_cli_error(e, "Privacy settings update failed", debug)
        sys.exit(exit_code)


if __name__ == '__main__':
    cli()
