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


@cli.command()
@click.option('--storage-dir', '-s', help='Custom storage directory for face data')
@click.option('--master-key', '-k', help='Master key for encryption (optional)')
def storage_info(storage_dir: str, master_key: str):
    """Display storage information and statistics."""
    try:
        # Initialize storage
        security_manager = SecurityManager(master_key)
        storage = FaceDataStorage(storage_dir, security_manager)
        
        # Get storage stats
        stats = storage.get_storage_stats()
        
        click.echo("💾 Storage Information")
        click.echo("=" * 25)
        click.echo(f"Storage directory: {stats['storage_dir']}")
        click.echo(f"Total users: {stats['total_users']}")
        click.echo(f"Storage size: {stats['storage_size_bytes']:,} bytes ({stats['storage_size_bytes']/1024:.1f} KB)")
        click.echo()
        
        if stats['files']:
            click.echo("📁 Files:")
            for file_info in stats['files']:
                modified_time = time.strftime('%Y-%m-%d %H:%M:%S', 
                                           time.localtime(file_info['modified']))
                click.echo(f"  • {file_info['name']} ({file_info['size_bytes']:,} bytes, {modified_time})")
        else:
            click.echo("📁 No data files found")
            
    except Exception as e:
        click.echo(f"❌ Error getting storage info: {str(e)}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('backup_path', type=click.Path())
@click.option('--storage-dir', '-s', help='Custom storage directory for face data')
@click.option('--master-key', '-k', help='Master key for encryption (optional)')
def backup(backup_path: str, storage_dir: str, master_key: str):
    """
    Create an encrypted backup of all enrollment data.
    
    BACKUP_PATH: Path where the backup file will be created
    """
    try:
        # Initialize storage and backup manager
        security_manager = SecurityManager(master_key)
        storage = FaceDataStorage(storage_dir, security_manager)
        backup_manager = BackupManager(storage)
        
        # Check if backup path already exists
        if os.path.exists(backup_path):
            if not click.confirm(f"Backup file '{backup_path}' already exists. Overwrite?"):
                click.echo("❌ Backup cancelled")
                return
        
        click.echo(f"💾 Creating backup to: {backup_path}")
        
        # Create backup
        success = backup_manager.create_backup(backup_path)
        
        if success:
            file_size = os.path.getsize(backup_path)
            click.echo(f"✅ Backup created successfully ({file_size:,} bytes)")
        else:
            click.echo("❌ Failed to create backup", err=True)
            sys.exit(1)
            
    except Exception as e:
        click.echo(f"❌ Error creating backup: {str(e)}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('backup_path', type=click.Path(exists=True))
@click.option('--storage-dir', '-s', help='Custom storage directory for face data')
@click.option('--master-key', '-k', help='Master key for encryption (optional)')
@click.option('--force', '-f', is_flag=True, help='Force restore without confirmation')
def restore(backup_path: str, storage_dir: str, master_key: str, force: bool):
    """
    Restore enrollment data from an encrypted backup.
    
    BACKUP_PATH: Path to the backup file to restore
    """
    try:
        # Initialize storage and backup manager
        security_manager = SecurityManager(master_key)
        storage = FaceDataStorage(storage_dir, security_manager)
        backup_manager = BackupManager(storage)
        
        # Check existing users
        existing_users = storage.list_enrolled_users()
        if existing_users and not force:
            click.echo(f"⚠️  Warning: {len(existing_users)} users are already enrolled.")
            click.echo("   Restore may overwrite existing data.")
            if not click.confirm("Continue with restore?"):
                click.echo("❌ Restore cancelled")
                return
        
        click.echo(f"📥 Restoring from backup: {backup_path}")
        
        # Restore backup
        success = backup_manager.restore_backup(backup_path)
        
        if success:
            click.echo("✅ Backup restored successfully")
            
            # Show updated user count
            updated_users = storage.list_enrolled_users()
            click.echo(f"👥 Total enrolled users: {len(updated_users)}")
        else:
            click.echo("❌ Failed to restore backup", err=True)
            sys.exit(1)
            
    except Exception as e:
        click.echo(f"❌ Error restoring backup: {str(e)}", err=True)
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


if __name__ == '__main__':
    cli()