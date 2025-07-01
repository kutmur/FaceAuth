#!/usr/bin/env python3
"""
FaceAuth - Local Face Authentication System
Main CLI interface for face enrollment and authentication.
"""

import sys
import os
import click
import time
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from faceauth.core.enrollment import FaceEnrollmentManager, FaceEnrollmentError
from faceauth.core.authentication import FaceAuthenticator, AuthenticationError
from faceauth.crypto.file_encryption import FileEncryption, EncryptionError
from faceauth.utils.storage import FaceDataStorage, BackupManager
from faceauth.utils.security import SecurityManager


@click.group()
@click.version_option(version='1.0.0')
def cli():
    """
    FaceAuth - Local Face Authentication System
    
    A privacy-first face authentication platform that keeps all data local.
    """
    pass


@cli.command()
@click.argument('user_id', type=str)
@click.option('--timeout', '-t', default=30, help='Enrollment timeout in seconds (default: 30)')
@click.option('--storage-dir', '-s', help='Custom storage directory for face data')
@click.option('--master-key', '-k', help='Master key for encryption (optional)')
@click.option('--quiet', '-q', is_flag=True, help='Quiet mode - minimal output')
def enroll_face(user_id: str, timeout: int, storage_dir: str, master_key: str, quiet: bool):
    """
    Enroll a new user's face into the FaceAuth system.
    
    USER_ID: Unique identifier for the user (e.g., username, email)
    
    Example:
        python main.py enroll-face john.doe
        python main.py enroll-face alice@example.com --timeout 45
    """
    try:
        if not quiet:
            click.echo("🔐 FaceAuth - Face Enrollment")
            click.echo("=" * 40)
            click.echo(f"User ID: {user_id}")
            click.echo(f"Timeout: {timeout}s")
            if storage_dir:
                click.echo(f"Storage: {storage_dir}")
            click.echo()
        
        # Validate user ID
        if not user_id or len(user_id.strip()) == 0:
            click.echo("❌ Error: User ID cannot be empty", err=True)
            sys.exit(1)
        
        user_id = user_id.strip()
        
        # Initialize enrollment manager
        if not quiet:
            click.echo("🤖 Initializing face recognition system...")
        
        enrollment_manager = FaceEnrollmentManager(
            storage_dir=storage_dir,
            master_key=master_key
        )
        
        # Check if user already exists
        if enrollment_manager.verify_enrollment(user_id):
            click.echo(f"❌ Error: User '{user_id}' is already enrolled", err=True)
            click.echo("   Use 'delete-user' command to remove existing enrollment first")
            sys.exit(1)
        
        if not quiet:
            click.echo("✅ System initialized successfully")
            click.echo()
        
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
                click.echo("🎉 Enrollment Success!")
                click.echo("=" * 20)
                click.echo(f"✅ User '{user_id}' enrolled successfully")
                click.echo(f"📊 Samples collected: {result['samples_collected']}")
                click.echo(f"⭐ Quality score: {result['average_quality']:.3f}")
                click.echo(f"⏱️  Duration: {result['duration']:.1f}s")
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
            
            sys.exit(1)
            
    except FaceEnrollmentError as e:
        click.echo(f"❌ Enrollment Error: {str(e)}", err=True)
        sys.exit(1)
    except KeyboardInterrupt:
        click.echo("\n❌ Enrollment cancelled by user", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"❌ Unexpected error: {str(e)}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--storage-dir', '-s', help='Custom storage directory for face data')
@click.option('--master-key', '-k', help='Master key for encryption (optional)')
def list_users(storage_dir: str, master_key: str):
    """List all enrolled users in the system."""
    try:
        # Initialize storage
        security_manager = SecurityManager(master_key)
        storage = FaceDataStorage(storage_dir, security_manager)
        
        # Get enrolled users
        users = storage.list_enrolled_users()
        
        if not users:
            click.echo("📝 No users enrolled in the system")
            return
        
        click.echo("👥 Enrolled Users")
        click.echo("=" * 20)
        
        for i, user_id in enumerate(users, 1):
            metadata = storage.get_user_metadata(user_id)
            
            click.echo(f"{i:2d}. {user_id}")
            
            if metadata:
                if 'enrollment_duration' in metadata:
                    click.echo(f"     Enrollment time: {metadata['enrollment_duration']:.1f}s")
                if 'average_quality' in metadata:
                    click.echo(f"     Quality score: {metadata['average_quality']:.3f}")
                if 'samples_collected' in metadata:
                    click.echo(f"     Samples: {metadata['samples_collected']}")
            
            click.echo()
        
        click.echo(f"Total: {len(users)} enrolled users")
        
    except Exception as e:
        click.echo(f"❌ Error listing users: {str(e)}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('user_id', type=str)
@click.option('--storage-dir', '-s', help='Custom storage directory for face data')
@click.option('--master-key', '-k', help='Master key for encryption (optional)')
@click.option('--force', '-f', is_flag=True, help='Force deletion without confirmation')
def delete_user(user_id: str, storage_dir: str, master_key: str, force: bool):
    """
    Delete a user's enrollment from the system.
    
    USER_ID: The user to delete
    """
    try:
        # Initialize storage
        security_manager = SecurityManager(master_key)
        storage = FaceDataStorage(storage_dir, security_manager)
        
        # Check if user exists
        if not storage.user_exists(user_id):
            click.echo(f"❌ User '{user_id}' is not enrolled in the system", err=True)
            sys.exit(1)
        
        # Confirm deletion unless forced
        if not force:
            click.echo(f"⚠️  Warning: This will permanently delete enrollment data for '{user_id}'")
            if not click.confirm("Are you sure you want to continue?"):
                click.echo("❌ Deletion cancelled")
                return
        
        # Delete user
        success = storage.delete_user_enrollment(user_id)
        
        if success:
            click.echo(f"✅ Successfully deleted user '{user_id}'")
        else:
            click.echo(f"❌ Failed to delete user '{user_id}'", err=True)
            sys.exit(1)
            
    except Exception as e:
        click.echo(f"❌ Error deleting user: {str(e)}", err=True)
        sys.exit(1)


@cli.command('verify-face')
@click.argument('user_id', type=str)
@click.option('--timeout', '-t', default=10, help='Authentication timeout in seconds (default: 10)')
@click.option('--max-attempts', '-a', default=5, help='Maximum authentication attempts (default: 5)')
@click.option('--threshold', '-th', default=0.6, help='Similarity threshold for authentication (default: 0.6)')
@click.option('--storage-dir', '-s', help='Custom storage directory for face data')
@click.option('--master-key', '-k', help='Master key for encryption (optional)')
@click.option('--quiet', '-q', is_flag=True, help='Quiet mode - minimal output')
@click.option('--show-metrics', '-m', is_flag=True, help='Show detailed authentication metrics')
def verify_face(user_id: str, timeout: int, max_attempts: int, threshold: float, 
                storage_dir: str, master_key: str, quiet: bool, show_metrics: bool):
    """
    Verify a user's identity using real-time face authentication.
    
    USER_ID: Unique identifier for the enrolled user
    
    Example:
        python main.py verify-face john.doe
        python main.py verify-face alice@example.com --timeout 15 --threshold 0.7
    """
    try:
        if not quiet:
            click.echo("🔐 FaceAuth - Real-time Face Verification")
            click.echo("=" * 45)
        
        # Validate threshold
        if not 0.1 <= threshold <= 1.0:
            click.echo("❌ Error: Threshold must be between 0.1 and 1.0", err=True)
            sys.exit(1)
        
        # Initialize storage and authenticator
        security_manager = SecurityManager(master_key)
        storage = FaceDataStorage(storage_dir, security_manager)
        authenticator = FaceAuthenticator(storage, similarity_threshold=threshold)
        
        # Check if user exists
        if not storage.user_exists(user_id):
            click.echo(f"❌ Error: User '{user_id}' is not enrolled", err=True)
            click.echo("💡 Tip: Use 'enroll-face' command to enroll the user first")
            sys.exit(1)
        
        if not quiet:
            click.echo(f"👤 User ID: {user_id}")
            click.echo(f"⏱️  Timeout: {timeout}s")
            click.echo(f"🎯 Threshold: {threshold}")
            click.echo(f"🔄 Max attempts: {max_attempts}")
            click.echo()
        
        # Start authentication
        start_time = time.time()
        
        try:
            result = authenticator.authenticate_realtime(
                user_id=user_id,
                timeout=timeout,
                max_attempts=max_attempts
            )
            
            total_time = time.time() - start_time
            
            if result['success']:
                if not quiet:
                    click.echo()
                    click.echo("✅ Authentication Successful!")
                    click.echo(f"   Similarity Score: {result['similarity']:.3f}")
                    click.echo(f"   Duration: {result['duration']:.2f}s")
                    click.echo(f"   Attempts Used: {result['attempts']}")
                    
                    if show_metrics:
                        click.echo()
                        click.echo("📊 Detailed Metrics:")
                        click.echo(f"   Best Similarity: {result['best_similarity']:.3f}")
                        quality = result.get('quality_metrics', {})
                        if quality:
                            click.echo(f"   Image Sharpness: {quality.get('sharpness', 0):.1f}")
                            click.echo(f"   Image Brightness: {quality.get('brightness', 0):.1f}")
                            click.echo(f"   Image Contrast: {quality.get('contrast', 0):.1f}")
                        
                        # Show attempt details
                        if 'authentication_attempts' in result:
                            click.echo("   Attempt Details:")
                            for attempt in result['authentication_attempts']:
                                click.echo(f"     Attempt {attempt['attempt']}: "
                                         f"Similarity {attempt.get('similarity', 0):.3f}")
                else:
                    click.echo("SUCCESS")
                
                sys.exit(0)
            
            else:
                if not quiet:
                    click.echo()
                    click.echo("❌ Authentication Failed!")
                    click.echo(f"   Reason: {result['error']}")
                    click.echo(f"   Duration: {result['duration']:.2f}s")
                    
                    if 'best_similarity' in result:
                        click.echo(f"   Best Similarity: {result['best_similarity']:.3f}")
                        click.echo(f"   Required Threshold: {threshold}")
                    
                    if show_metrics and 'authentication_attempts' in result:
                        click.echo("   Attempt Details:")
                        for attempt in result['authentication_attempts']:
                            if 'similarity' in attempt:
                                click.echo(f"     Attempt {attempt['attempt']}: "
                                         f"Similarity {attempt['similarity']:.3f}")
                            elif 'error' in attempt:
                                click.echo(f"     Attempt {attempt['attempt']}: {attempt['error']}")
                    
                    # Provide helpful suggestions
                    click.echo()
                    click.echo("💡 Suggestions:")
                    if result.get('error_type') == 'user_not_found':
                        click.echo("   • Ensure the user ID is correct")
                        click.echo("   • Use 'list-users' to see enrolled users")
                    elif result.get('error_type') == 'webcam_error':
                        click.echo("   • Check webcam connection")
                        click.echo("   • Close other applications using the camera")
                    elif result.get('error_type') == 'timeout':
                        click.echo("   • Try increasing timeout with --timeout option")
                        click.echo("   • Ensure good lighting conditions")
                        click.echo("   • Position face clearly in camera view")
                    elif result.get('error_type') == 'max_attempts_exceeded':
                        click.echo("   • Try lowering threshold with --threshold option")
                        click.echo("   • Ensure good lighting and camera positioning")
                        click.echo("   • Consider re-enrolling if face has changed significantly")
                else:
                    click.echo("FAILED")
                
                sys.exit(1)
                
        except AuthenticationError as e:
            click.echo(f"❌ Authentication error: {str(e)}", err=True)
            sys.exit(1)
        except KeyboardInterrupt:
            click.echo("\n⚠️  Authentication cancelled by user")
            sys.exit(1)
            
    except Exception as e:
        click.echo(f"❌ Unexpected error: {str(e)}", err=True)
        if show_metrics:
            import traceback
            click.echo("Debug information:", err=True)
            click.echo(traceback.format_exc(), err=True)
        sys.exit(1)


@cli.command()
def system_check():
    """Check system requirements and dependencies."""
    click.echo("🔍 FaceAuth System Check")
    click.echo("=" * 30)
    
    # Check Python version
    python_version = sys.version_info
    click.echo(f"🐍 Python version: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    if python_version < (3, 8):
        click.echo("❌ Python 3.8+ is required", err=True)
        return
    else:
        click.echo("✅ Python version OK")
    
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
            click.echo(f"✅ {package_name}")
        except ImportError:
            click.echo(f"❌ {package_name} (missing)")
            missing_deps.append(package_name)
    
    if missing_deps:
        click.echo()
        click.echo("📦 Missing dependencies:")
        for dep in missing_deps:
            click.echo(f"   • {dep}")
        click.echo()
        click.echo("Install missing dependencies with:")
        click.echo("   pip install -r requirements.txt")
    else:
        click.echo()
        click.echo("🎉 All dependencies are installed!")
    
    # Check camera access
    try:
        import cv2
        cap = cv2.VideoCapture(0)
        if cap.isOpened():
            click.echo("✅ Camera access OK")
            cap.release()
        else:
            click.echo("❌ Cannot access camera")
    except ImportError:
        click.echo("⚠️  Cannot test camera (OpenCV not installed)")
    except Exception:
        click.echo("❌ Camera test failed")


@cli.command('auth-metrics')
@click.option('--storage-dir', '-s', help='Custom storage directory for face data')
@click.option('--master-key', '-k', help='Master key for encryption (optional)')
@click.option('--reset', '-r', is_flag=True, help='Reset performance metrics')
def auth_metrics(storage_dir: str, master_key: str, reset: bool):
    """
    Display authentication performance metrics and statistics.
    
    Shows false positive/negative rates, average authentication times,
    and other performance indicators.
    """
    try:
        # Initialize storage and authenticator
        security_manager = SecurityManager(master_key)
        storage = FaceDataStorage(storage_dir, security_manager)
        authenticator = FaceAuthenticator(storage)
        
        if reset:
            # Reset metrics (this is a simple implementation)
            authenticator.authentication_times = []
            authenticator.false_positives = 0
            authenticator.false_negatives = 0
            authenticator.total_attempts = 0
            click.echo("✅ Performance metrics reset")
            return
        
        # Get performance metrics
        metrics = authenticator.get_performance_metrics()
        
        click.echo("📊 Authentication Performance Metrics")
        click.echo("=" * 40)
        click.echo(f"Total Authentication Attempts: {metrics['total_attempts']}")
        click.echo(f"Successful Authentications: {metrics['successful_attempts']}")
        click.echo(f"Average Authentication Time: {metrics['average_authentication_time']:.2f}s")
        click.echo()
        
        click.echo("📈 Error Rates:")
        click.echo(f"False Positive Rate: {metrics['false_positive_rate']:.1%}")
        click.echo(f"False Negative Rate: {metrics['false_negative_rate']:.1%}")
        click.echo(f"False Positives: {metrics['false_positives']}")
        click.echo(f"False Negatives: {metrics['false_negatives']}")
        click.echo()
        
        # Calculate success rate
        if metrics['total_attempts'] > 0:
            success_rate = metrics['successful_attempts'] / metrics['total_attempts']
            click.echo(f"Success Rate: {success_rate:.1%}")
        else:
            click.echo("Success Rate: No data available")
        
        # Performance assessment
        click.echo()
        click.echo("🎯 Performance Assessment:")
        
        if metrics['average_authentication_time'] < 2.0:
            click.echo("   ✅ Authentication speed: Excellent (<2s)")
        elif metrics['average_authentication_time'] < 3.0:
            click.echo("   ⚠️  Authentication speed: Good (<3s)")
        else:
            click.echo("   ❌ Authentication speed: Slow (>3s)")
        
        if metrics['false_positive_rate'] < 0.01:
            click.echo("   ✅ False positive rate: Excellent (<1%)")
        elif metrics['false_positive_rate'] < 0.05:
            click.echo("   ⚠️  False positive rate: Acceptable (<5%)")
        else:
            click.echo("   ❌ False positive rate: High (>5%)")
        
        if metrics['false_negative_rate'] < 0.05:
            click.echo("   ✅ False negative rate: Excellent (<5%)")
        elif metrics['false_negative_rate'] < 0.10:
            click.echo("   ⚠️  False negative rate: Acceptable (<10%)")
        else:
            click.echo("   ❌ False negative rate: High (>10%)")
            
    except Exception as e:
        click.echo(f"❌ Error getting metrics: {str(e)}", err=True)
        sys.exit(1)


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
def encrypt_file(file_path: str, user_id: str, output: str, kdf_method: str, 
                auth_timeout: int, overwrite: bool, storage_dir: str, 
                master_key: str, quiet: bool):
    """
    Encrypt a file using face authentication.
    
    FILE_PATH: Path to the file to encrypt
    USER_ID: User ID for face authentication
    
    Example:
        python main.py encrypt-file document.pdf john.doe
        python main.py encrypt-file secret.txt alice --output secret.txt.encrypted
    """
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
            click.echo("💡 Tip: Use 'enroll-face' command to enroll the user first")
            sys.exit(1)
        
        if not quiet:
            click.echo(f"📁 File: {file_path}")
            click.echo(f"👤 User: {user_id}")
            click.echo(f"🔑 KDF Method: {kdf_method}")
            click.echo(f"⏱️  Auth Timeout: {auth_timeout}s")
            click.echo()
        
        # Perform encryption
        try:
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
                    click.echo("✅ File Encryption Successful!")
                    click.echo(f"   Input: {result['input_file']}")
                    click.echo(f"   Output: {result['output_file']}")
                    click.echo(f"   Original Size: {result['original_size']:,} bytes")
                    click.echo(f"   Encrypted Size: {result['encrypted_size']:,} bytes")
                    click.echo(f"   Overhead: {result['encrypted_size'] - result['original_size']:,} bytes")
                    click.echo(f"   Duration: {result['duration']:.2f}s")
                    click.echo(f"   KDF Method: {result['kdf_method']}")
                else:
                    click.echo("SUCCESS")
                
                sys.exit(0)
            else:
                click.echo("❌ Encryption failed", err=True)
                sys.exit(1)
                
        except EncryptionError as e:
            click.echo(f"❌ Encryption error: {str(e)}", err=True)
            sys.exit(1)
        except KeyboardInterrupt:
            click.echo("\n⚠️  Encryption cancelled by user")
            sys.exit(1)
            
    except Exception as e:
        click.echo(f"❌ Unexpected error: {str(e)}", err=True)
        sys.exit(1)


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
def decrypt_file(encrypted_path: str, user_id: str, output: str, auth_timeout: int,
                overwrite: bool, storage_dir: str, master_key: str, quiet: bool,
                verify_only: bool):
    """
    Decrypt a FaceAuth encrypted file.
    
    ENCRYPTED_PATH: Path to the encrypted file
    USER_ID: User ID for face authentication
    
    Example:
        python main.py decrypt-file document.pdf.faceauth john.doe
        python main.py decrypt-file secret.txt.encrypted alice --output secret.txt
    """
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
            click.echo(f"📁 Encrypted File: {encrypted_path}")
            click.echo(f"📄 Original Name: {file_info['original_filename']}")
            click.echo(f"📊 Original Size: {file_info['original_size']:,} bytes")
            click.echo(f"📊 Encrypted Size: {file_info['encrypted_size']:,} bytes")
            click.echo(f"🔑 KDF Method: {file_info['kdf_method']}")
            click.echo(f"👤 User: {user_id}")
            click.echo()
        
        if verify_only:
            if not quiet:
                click.echo("✅ File verification successful!")
                click.echo("   File is a valid FaceAuth encrypted file")
            else:
                click.echo("VALID")
            sys.exit(0)
        
        # Check if user exists
        if not storage.user_exists(user_id):
            click.echo(f"❌ Error: User '{user_id}' is not enrolled", err=True)
            sys.exit(1)
        
        # Perform decryption
        try:
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
                    click.echo("✅ File Decryption Successful!")
                    click.echo(f"   Encrypted File: {result['encrypted_file']}")
                    click.echo(f"   Output: {result['output_file']}")
                    click.echo(f"   File Size: {result['file_size']:,} bytes")
                    click.echo(f"   Duration: {result['duration']:.2f}s")
                    click.echo(f"   Original Name: {result['original_filename']}")
                else:
                    click.echo("SUCCESS")
                
                sys.exit(0)
            else:
                click.echo("❌ Decryption failed", err=True)
                sys.exit(1)
                
        except EncryptionError as e:
            click.echo(f"❌ Decryption error: {str(e)}", err=True)
            sys.exit(1)
        except KeyboardInterrupt:
            click.echo("\n⚠️  Decryption cancelled by user")
            sys.exit(1)
            
    except Exception as e:
        click.echo(f"❌ Unexpected error: {str(e)}", err=True)
        sys.exit(1)


@cli.command('file-info')
@click.argument('file_path', type=click.Path(exists=True))
@click.option('--storage-dir', '-s', help='Custom storage directory for face data')
@click.option('--master-key', '-m', help='Master key for encryption (optional)')
def file_info(file_path: str, storage_dir: str, master_key: str):
    """
    Display information about a FaceAuth encrypted file.
    
    FILE_PATH: Path to the encrypted file
    
    Example:
        python main.py file-info document.pdf.faceauth
    """
    try:
        # Initialize components
        security_manager = SecurityManager(master_key)
        storage = FaceDataStorage(storage_dir, security_manager)
        file_encryption = FileEncryption(storage)
        
        # Get file information
        file_info = file_encryption.verify_encrypted_file(file_path)
        
        click.echo("📄 FaceAuth File Information")
        click.echo("=" * 35)
        click.echo(f"File: {file_path}")
        click.echo()
        
        if file_info.get('is_faceauth_file', False):
            click.echo("✅ Valid FaceAuth encrypted file")
            click.echo(f"Format Version: {file_info['file_format_version']}")
            click.echo(f"KDF Method: {file_info['kdf_method']}")
            click.echo(f"Original Filename: {file_info['original_filename']}")
            click.echo(f"Original Size: {file_info['original_size']:,} bytes")
            click.echo(f"Encrypted Size: {file_info['encrypted_size']:,} bytes")
            click.echo(f"Overhead: {file_info['overhead_bytes']:,} bytes")
            click.echo(f"Header Size: {file_info['header_size']} bytes")
            
            # Calculate compression ratio
            ratio = (file_info['overhead_bytes'] / file_info['original_size']) * 100
            click.echo(f"Overhead Ratio: {ratio:.1f}%")
        else:
            click.echo("❌ Not a FaceAuth encrypted file")
            error_msg = file_info.get('error', 'Unknown error')
            click.echo(f"Error: {error_msg}")
            sys.exit(1)
            
    except Exception as e:
        click.echo(f"❌ Error reading file: {str(e)}", err=True)
        sys.exit(1)


@cli.command('crypto-info')
@click.option('--kdf-method', '-k', default='argon2',
              type=click.Choice(['argon2', 'pbkdf2', 'scrypt', 'multi']),
              help='Key derivation method to show info for')
@click.option('--storage-dir', '-s', help='Custom storage directory for face data')
@click.option('--master-key', '-m', help='Master key for encryption (optional)')
def crypto_info(kdf_method: str, storage_dir: str, master_key: str):
    """
    Display cryptographic information and parameters.
    
    Example:
        python main.py crypto-info
        python main.py crypto-info --kdf-method pbkdf2
    """
    try:
        # Initialize components
        security_manager = SecurityManager(master_key)
        storage = FaceDataStorage(storage_dir, security_manager)
        file_encryption = FileEncryption(storage)
        
        # Get encryption information
        crypto_info = file_encryption.get_encryption_info(kdf_method)
        
        click.echo("🔐 FaceAuth Cryptographic Information")
        click.echo("=" * 45)
        
        click.echo("📊 Encryption Parameters:")
        click.echo(f"   Algorithm: {crypto_info['encryption_algorithm']}")
        click.echo(f"   Key Size: {crypto_info['key_size_bits']} bits")
        click.echo(f"   Nonce Size: {crypto_info['nonce_size_bits']} bits")
        click.echo(f"   Auth Tag Size: {crypto_info['tag_size_bits']} bits")
        click.echo(f"   Chunk Size: {crypto_info['chunk_size_bytes']:,} bytes")
        click.echo(f"   File Format Version: {crypto_info['file_format_version']}")
        click.echo()
        
        kdf_info = crypto_info['kdf_info']
        click.echo("🔑 Key Derivation Parameters:")
        click.echo(f"   Method: {kdf_info['method']}")
        
        if 'iterations' in kdf_info:
            click.echo(f"   Iterations: {kdf_info['iterations']:,}")
        if 'time_cost' in kdf_info:
            click.echo(f"   Time Cost: {kdf_info['time_cost']}")
        if 'memory_cost' in kdf_info:
            click.echo(f"   Memory Cost: {kdf_info['memory_cost']:,} KB")
        if 'parallelism' in kdf_info:
            click.echo(f"   Parallelism: {kdf_info['parallelism']}")
        if 'n' in kdf_info:
            click.echo(f"   N (memory cost): {kdf_info['n']:,}")
            click.echo(f"   r (block size): {kdf_info['r']}")
            click.echo(f"   p (parallelism): {kdf_info['p']}")
        if 'combines' in kdf_info:
            click.echo(f"   Combines: {', '.join(kdf_info['combines'])}")
        
        click.echo(f"   Key Length: {kdf_info['key_length']} bytes")
        click.echo(f"   Salt Length: {kdf_info['salt_length']} bytes")
        click.echo()
        
        click.echo("🛡️  Security Features:")
        click.echo("   ✅ AES-256-GCM authenticated encryption")
        click.echo("   ✅ Cryptographically secure key derivation")
        click.echo("   ✅ Unique per-file encryption keys")
        click.echo("   ✅ Face embedding normalization")
        click.echo("   ✅ Secure memory handling")
        click.echo("   ✅ File integrity verification")
        click.echo("   ✅ Forward secrecy (keys not stored)")
        
    except Exception as e:
        click.echo(f"❌ Error: {str(e)}", err=True)
        sys.exit(1)


@cli.command()
def version():
    """Show the version of FaceAuth."""
    click.echo("FaceAuth version 1.0.0")


if __name__ == '__main__':
    cli()