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
        
        # Check if user already exists
        if enrollment_manager.verify_enrollment(user_id):
            click.echo(f"❌ Error: User '{user_id}' is already enrolled", err=True)
            click.echo("💡 Tip: Use 'delete-user' command to remove existing enrollment first", err=True)
            sys.exit(1)
        
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
        
        # Initialize storage and authenticator
        print_status("Initializing authentication system...", "progress", quiet)
        security_manager = SecurityManager(master_key)
        storage = FaceDataStorage(storage_dir, security_manager)
        authenticator = FaceAuthenticator(storage, similarity_threshold=threshold)
        
        # Check if user exists
        if not storage.user_exists(user_id):
            click.echo(f"❌ Error: User '{user_id}' is not enrolled", err=True)
            click.echo("💡 Tip: Use 'enroll-face' command to enroll the user first", err=True)
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


if __name__ == '__main__':
    cli()
