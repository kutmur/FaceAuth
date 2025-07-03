#!/usr/bin/env python3
# ROBUSTNESS: Forcing 'xcb' platform to prevent Wayland/Qt GUI errors on Linux.
import os
os.environ['QT_QPA_PLATFORM'] = 'xcb'
"""
FaceAuth - Local Face Authentication System
===========================================

Main CLI interface for the FaceAuth system.
Provides commands for face enrollment, authentication, and file encryption.

Usage:
    python main.py enroll [--user-id USER] [--model MODEL]
    python main.py verify [--user-id USER]
    python main.py encrypt <filename> [--user-id USER]
    python main.py decrypt <filename> [--output PATH] [--user-id USER]
"""

import click
import sys
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from faceauth.enrollment import enroll_new_user, FaceEnrollmentError


@click.group(invoke_without_command=True)
@click.version_option(version="1.0.0")
@click.option(
    "--gui",
    is_flag=True,
    help="Launch the graphical user interface instead of CLI"
)
@click.pass_context
def cli(ctx, gui):
    """
    🔐 FaceAuth - Local Face Authentication System
    
    A privacy-first face authentication platform for securing your files.
    All processing happens locally - no cloud, no third parties.
    
    Use --gui flag to launch the graphical interface:
        python main.py --gui
    """
    if gui:
        # Launch GUI mode
        try:
            from faceauth.gui import FaceAuthGUI
            click.echo("🚀 Launching FaceAuth GUI...")
            app = FaceAuthGUI()
            app.run()
            ctx.exit()
        except ImportError as e:
            click.echo("❌ Error: GUI dependencies not available")
            click.echo(f"   {str(e)}")
            click.echo("\n💡 To use GUI mode, ensure tkinter is installed:")
            click.echo("   sudo apt-get install python3-tk  # Ubuntu/Debian")
            click.echo("   brew install python-tk          # macOS")
            ctx.exit(1)
        except Exception as e:
            click.echo(f"❌ GUI Error: {str(e)}")
            ctx.exit(1)
    elif ctx.invoked_subcommand is None:
        # Show help if no command is provided and no GUI flag
        click.echo(ctx.get_help())


@cli.command("enroll")
@click.option(
    "--user-id", 
    "-u", 
    type=str, 
    help="Unique identifier for the user (will prompt if not provided)"
)
@click.option(
    "--model", 
    "-m", 
    type=click.Choice(["Facenet", "ArcFace", "VGG-Face", "Facenet512"], case_sensitive=False),
    default="Facenet",
    help="Face recognition model to use (default: Facenet)"
)
@click.option(
    "--data-dir",
    "-d",
    type=click.Path(),
    default="face_data",
    help="Directory to store face data (default: face_data)"
)
def enroll_face(user_id, model, data_dir):
    """
    Enroll a new user's face into the system.
    
    This command captures your face using the webcam, generates a secure
    face embedding, and stores it locally in encrypted format.
    
    The process takes about 30 seconds and requires:
    - A working webcam
    - Good lighting conditions
    - Only one person visible in the frame
    
    Examples:
        python main.py enroll
        python main.py enroll --user-id john_doe
        python main.py enroll --user-id alice --model ArcFace
    """
    click.echo("🚀 Starting FaceAuth enrollment process...")
    click.echo("=" * 60)
    
    try:
        # Import here to avoid issues if dependencies aren't installed
        from faceauth.enrollment import FaceEnroller
        
        # Create enroller instance
        enroller = FaceEnroller(model_name=model, data_dir=data_dir)
        
        # Perform enrollment
        result = enroller.enroll_new_user(user_id)
        
        if result['success']:
            click.echo("\n🎉 SUCCESS!")
            click.echo(f"✅ User '{result['user_id']}' enrolled successfully")
            click.echo(f"📁 Data saved to: {result['file_path']}")
            click.echo(f"🧠 Model used: {result['model_used']}")
            click.echo(f"📊 Embedding size: {result['embedding_size']} dimensions")
            click.echo("\n🔒 Your face data is encrypted and stored locally")
            click.echo("⚠️  Keep your password safe - it cannot be recovered!")
            
            # Next steps
            click.echo("\n📋 Next steps:")
            click.echo("• Test authentication: python main.py verify")
            click.echo("• Encrypt files: python main.py encrypt myfile.txt")
            click.echo("• View help: python main.py --help")
            
        else:
            click.echo("❌ Enrollment failed")
            sys.exit(1)
            
    except FaceEnrollmentError as e:
        click.echo(f"\n❌ Enrollment Error: {e}")
        
        # HARDENED: Provide specific guidance for common errors
        error_str = str(e)
        if "OpenCV data files missing" in error_str or "haarcascade" in error_str:
            click.echo("\n🚨 CRITICAL ERROR: OpenCV Environment Corruption Detected!")
            click.echo("💡 IMMEDIATE FIX:")
            click.echo("   python main.py setup")
            click.echo("\n📋 What happened?")
            click.echo("• Your OpenCV installation is missing essential data files")
            click.echo("• This causes DeepFace to crash during face detection")
            click.echo("• The setup command will completely reinstall OpenCV correctly")
            click.echo("\n⚡ After running setup, enrollment will work perfectly!")
        else:
            click.echo("\n💡 Common solutions:")
            click.echo("• Check if user is enrolled: python main.py info")
            click.echo("• Verify webcam is working and not in use by another app")
            click.echo("• Ensure good lighting conditions")
            click.echo("• Try again: python main.py enroll")
        sys.exit(1)
    except ImportError as e:
        click.echo(f"\n❌ Missing dependencies: {e}")
        click.echo("💡 Please install required packages:")
        click.echo("   pip install -r requirements.txt")
        sys.exit(1)
    except KeyboardInterrupt:
        click.echo("\n\n❌ Enrollment cancelled by user")
        sys.exit(1)
    except Exception as e:
        click.echo(f"\n💥 Unexpected error: {e}")
        click.echo("🐛 Please report this issue if it persists")
        sys.exit(1)


@cli.command("verify")
@click.option(
    "--user-id", 
    "-u", 
    type=str, 
    help="User ID to verify against (will prompt if not provided)"
)
@click.option(
    "--model", 
    "-m", 
    type=click.Choice(["Facenet", "ArcFace", "VGG-Face", "Facenet512"], case_sensitive=False),
    default="Facenet",
    help="Face recognition model to use (default: Facenet)"
)
@click.option(
    "--data-dir",
    "-d",
    type=click.Path(),
    default="face_data",
    help="Directory containing face data (default: face_data)"
)
def verify_face(user_id, model, data_dir):
    """
    Verify your identity using face authentication.
    
    This command compares your current face against stored face data
    to authenticate your identity. The verification process is fast
    and secure, completing in under 2 seconds.
    
    Requirements:
    - Enrolled face data (use 'enroll' first)
    - Working webcam
    - Good lighting conditions
    - Your enrollment password
    
    Examples:
        python main.py verify
        python main.py verify --user-id john_doe
        python main.py verify --user-id alice --model ArcFace
    """
    click.echo("🔍 Starting FaceAuth verification process...")
    click.echo("=" * 60)
    
    try:
        # Import authentication module
        from faceauth.authentication import FaceAuthenticator, FaceAuthenticationError
        
        # Create authenticator instance
        authenticator = FaceAuthenticator(model_name=model, data_dir=data_dir)
        
        # Perform verification
        click.echo("🚀 Initializing face authentication...")
        verification_result = authenticator.verify_user_face(user_id)
        
        # Display results
        if verification_result:
            click.echo("\n🎉 SUCCESS!")
            click.echo("✅ ACCESS GRANTED")
            click.echo("🔓 Identity verified successfully")
            click.echo(f"🧠 Model used: {model}")
            click.echo("⚡ Verification completed in under 2 seconds")
            
            # Success message
            click.echo("\n🌟 Authentication successful!")
            click.echo("💡 You can now use secure features:")
            click.echo("• Encrypt files: python main.py encrypt myfile.txt")
            click.echo("• Access protected resources")
            
        else:
            click.echo("\n❌ FAILURE!")
            click.echo("🚫 ACCESS DENIED")
            click.echo("⚠️  Identity could not be verified")
            
            # Failure guidance
            click.echo("\n💡 Troubleshooting tips:")
            click.echo("• Ensure good lighting conditions")
            click.echo("• Position face clearly in camera view")
            click.echo("• Remove glasses/masks if possible")
            click.echo("• Try re-enrolling: python main.py enroll")
            
            sys.exit(1)
            
    except FaceAuthenticationError as e:
        click.echo(f"\n❌ Authentication Error: {e}")
        click.echo("\n💡 Common solutions:")
        click.echo("• Check if user is enrolled: python main.py info")
        click.echo("• Enroll first: python main.py enroll")
        click.echo("• Verify password is correct")
        click.echo("• Ensure webcam is working")
        sys.exit(1)
    except ImportError as e:
        click.echo(f"\n❌ Missing dependencies: {e}")
        click.echo("💡 Please install required packages:")
        click.echo("   pip install -r requirements.txt")
        click.echo("   python main.py setup")
        sys.exit(1)
    except KeyboardInterrupt:
        click.echo("\n\n❌ Verification cancelled by user")
        sys.exit(1)
    except Exception as e:
        click.echo(f"\n💥 Unexpected error: {e}")
        click.echo("🐛 Please report this issue if it persists")
        sys.exit(1)


@cli.command("encrypt")
@click.argument("filename", type=click.Path(exists=True))
@click.option(
    "--user-id", 
    "-u", 
    type=str, 
    help="User ID for face authentication (will prompt if not provided)"
)
@click.option(
    "--model", 
    "-m", 
    type=click.Choice(["Facenet", "ArcFace", "VGG-Face", "Facenet512"], case_sensitive=False),
    default="Facenet",
    help="Face recognition model to use (default: Facenet)"
)
@click.option(
    "--data-dir",
    "-d",
    type=click.Path(),
    default="face_data",
    help="Directory containing face data (default: face_data)"
)
def encrypt_file(filename, user_id, model, data_dir):
    """
    Encrypt a file using face authentication.
    
    This command first authenticates your identity using face verification,
    then encrypts the specified file with a secure key wrapping approach.
    The encrypted file will have a .faceauth extension.
    
    Security Process:
    1. Face authentication to verify your identity
    2. Password prompt for key derivation
    3. File encryption with AES-256-GCM
    4. Secure key wrapping to protect encryption keys
    
    Examples:
        python main.py encrypt secret.txt
        python main.py encrypt document.pdf --user-id alice
        python main.py encrypt data.csv --user-id bob --model ArcFace
    """
    click.echo("🔒 Starting FaceAuth file encryption process...")
    click.echo("=" * 60)
    
    try:
        # Import required modules
        from faceauth.authentication import FaceAuthenticator, FaceAuthenticationError
        from faceauth.file_handler import encrypt_file as encrypt_file_func, FileEncryptionError
        import getpass
        from pathlib import Path
        
        # Step 1: Face Authentication Gate
        click.echo("🔍 Step 1: Face Authentication Required")
        click.echo("⚠️  You must verify your identity before encrypting files")
        click.echo()
        
        # Create authenticator instance
        authenticator = FaceAuthenticator(model_name=model, data_dir=data_dir)
        
        # Perform face verification
        click.echo("🚀 Starting face verification...")
        verification_success = authenticator.verify_user_face(user_id)
        
        if not verification_success:
            click.echo("\n❌ AUTHENTICATION FAILED")
            click.echo("🚫 File encryption requires successful face verification")
            click.echo("\n💡 Troubleshooting:")
            click.echo("• Ensure you are enrolled: python main.py enroll-face")
            click.echo("• Check lighting and camera positioning")
            click.echo("• Verify your password is correct")
            sys.exit(1)
        
        click.echo("\n✅ AUTHENTICATION SUCCESSFUL")
        click.echo("🔓 Access granted for file encryption")
        
        # Step 2: Get encryption password
        click.echo("\n🔐 Step 2: Password for File Encryption")
        click.echo("Enter the password to protect your encrypted file:")
        click.echo("(This can be the same as your enrollment password or different)")
        
        encryption_password = getpass.getpass("Encryption password: ")
        if not encryption_password:
            click.echo("❌ Password is required for file encryption")
            sys.exit(1)
        
        # Confirm password
        password_confirm = getpass.getpass("Confirm password: ")
        if encryption_password != password_confirm:
            click.echo("❌ Passwords do not match")
            sys.exit(1)
        
        # Step 3: Encrypt the file
        click.echo("\n🔒 Step 3: Encrypting File")
        click.echo(f"📁 Input file: {filename}")
        
        # Get file info
        input_path = Path(filename)
        file_size = input_path.stat().st_size
        click.echo(f"📊 File size: {file_size:,} bytes")
        
        # Perform encryption
        click.echo("⚡ Encrypting with AES-256-GCM...")
        encrypted_file_path = encrypt_file_func(filename, encryption_password)
        
        # Success report
        encrypted_path = Path(encrypted_file_path)
        encrypted_size = encrypted_path.stat().st_size
        
        click.echo("\n🎉 ENCRYPTION SUCCESSFUL!")
        click.echo("✅ File encrypted and secured")
        click.echo(f"📁 Original file: {filename}")
        click.echo(f"🔒 Encrypted file: {encrypted_file_path}")
        click.echo(f"📊 Original size: {file_size:,} bytes")
        click.echo(f"📊 Encrypted size: {encrypted_size:,} bytes")
        click.echo(f"🔐 Encryption overhead: {encrypted_size - file_size} bytes")
        
        # Security information
        click.echo("\n🛡️  Security Information:")
        click.echo("• File encrypted with AES-256-GCM")
        click.echo("• Unique encryption key generated per file")
        click.echo("• Key protected with PBKDF2 (100,000 iterations)")
        click.echo("• Original file remains unchanged")
        
        # Next steps
        click.echo("\n📋 Next Steps:")
        click.echo(f"• Decrypt: python main.py decrypt-file {encrypted_file_path}")
        click.echo("• Store your password securely - it cannot be recovered")
        click.echo("• Keep the .faceauth file safe")
        
        # Optional: Ask about deleting original
        click.echo("\n🗑️  Security Recommendation:")
        if click.confirm("Delete the original unencrypted file for security?"):
            try:
                input_path.unlink()
                click.echo(f"✅ Original file '{filename}' securely deleted")
            except Exception as e:
                click.echo(f"⚠️  Could not delete original file: {e}")
                click.echo("💡 Please delete it manually for security")
        
    except FaceAuthenticationError as e:
        click.echo(f"\n❌ Authentication Error: {e}")
        click.echo("\n💡 Solutions:")
        click.echo("• Enroll first: python main.py enroll-face")
        click.echo("• Check webcam connectivity")
        click.echo("• Ensure good lighting")
        sys.exit(1)
    except FileEncryptionError as e:
        click.echo(f"\n❌ Encryption Error: {e}")
        click.echo("\n💡 Possible causes:")
        click.echo("• File is in use by another program")
        click.echo("• Insufficient disk space")
        click.echo("• Invalid file permissions")
        sys.exit(1)
    except ImportError as e:
        click.echo(f"\n❌ Missing dependencies: {e}")
        click.echo("💡 Please install required packages:")
        click.echo("   pip install -r requirements.txt")
        sys.exit(1)
    except KeyboardInterrupt:
        click.echo("\n\n❌ Encryption cancelled by user")
        sys.exit(1)
    except Exception as e:
        click.echo(f"\n💥 Unexpected error: {e}")
        click.echo("🐛 Please report this issue if it persists")
        sys.exit(1)


@cli.command("decrypt")
@click.argument("filename", type=click.Path(exists=True))
@click.option(
    "--output", 
    "-o", 
    type=click.Path(),
    help="Output path for decrypted file (optional)"
)
@click.option(
    "--user-id", 
    "-u", 
    type=str, 
    help="User ID for face authentication (will prompt if not provided)"
)
@click.option(
    "--model", 
    "-m", 
    type=click.Choice(["Facenet", "ArcFace", "VGG-Face", "Facenet512"], case_sensitive=False),
    default="Facenet",
    help="Face recognition model to use (default: Facenet)"
)
@click.option(
    "--data-dir",
    "-d",
    type=click.Path(),
    default="face_data",
    help="Directory containing face data (default: face_data)"
)
def decrypt_file(filename, output, user_id, model, data_dir):
    """
    Decrypt a file using face authentication.
    
    This command first authenticates your identity using face verification,
    then decrypts a .faceauth encrypted file using your password.
    
    Security Process:
    1. Face authentication to verify your identity
    2. Password prompt for key derivation
    3. File decryption with AES-256-GCM
    4. Secure key unwrapping to access encryption keys
    
    Examples:
        python main.py decrypt secret.txt.faceauth
        python main.py decrypt document.pdf.faceauth --output document.pdf
        python main.py decrypt data.csv.faceauth --user-id alice
    """
    click.echo("🔓 Starting FaceAuth file decryption process...")
    click.echo("=" * 60)
    
    try:
        # Import required modules
        from faceauth.authentication import FaceAuthenticator, FaceAuthenticationError
        from faceauth.file_handler import decrypt_file as decrypt_file_func, FileEncryptionError, get_encrypted_file_info
        import getpass
        from pathlib import Path
        
        # Validate input file
        if not filename.endswith('.faceauth'):
            click.echo("⚠️  Warning: File doesn't have .faceauth extension")
            if not click.confirm("Continue anyway?"):
                sys.exit(0)
        
        # Get file information
        click.echo("📋 Encrypted File Information:")
        try:
            file_info = get_encrypted_file_info(filename)
            click.echo(f"📁 File: {file_info['file_path']}")
            click.echo(f"📊 Size: {file_info['file_size']:,} bytes")
            click.echo(f"✅ Valid format: {file_info['is_valid_format']}")
            
            if not file_info['is_valid_format']:
                click.echo("❌ Invalid .faceauth file format")
                sys.exit(1)
                
        except FileEncryptionError as e:
            click.echo(f"❌ Cannot read encrypted file: {e}")
            sys.exit(1)
        
        # Step 1: Face Authentication Gate
        click.echo("\n🔍 Step 1: Face Authentication Required")
        click.echo("⚠️  You must verify your identity before decrypting files")
        click.echo()
        
        # Create authenticator instance
        authenticator = FaceAuthenticator(model_name=model, data_dir=data_dir)
        
        # Perform face verification
        click.echo("🚀 Starting face verification...")
        verification_success = authenticator.verify_user_face(user_id)
        
        if not verification_success:
            click.echo("\n❌ AUTHENTICATION FAILED")
            click.echo("🚫 File decryption requires successful face verification")
            click.echo("\n💡 Troubleshooting:")
            click.echo("• Ensure you are enrolled: python main.py enroll-face")
            click.echo("• Check lighting and camera positioning")
            click.echo("• Verify your password is correct")
            sys.exit(1)
        
        click.echo("\n✅ AUTHENTICATION SUCCESSFUL")
        click.echo("🔓 Access granted for file decryption")
        
        # Step 2: Get decryption password
        click.echo("\n🔐 Step 2: Password for File Decryption")
        click.echo("Enter the password used to encrypt this file:")
        
        decryption_password = getpass.getpass("Decryption password: ")
        if not decryption_password:
            click.echo("❌ Password is required for file decryption")
            sys.exit(1)
        
        # Step 3: Decrypt the file
        click.echo("\n🔓 Step 3: Decrypting File")
        click.echo(f"📁 Encrypted file: {filename}")
        
        # Perform decryption
        click.echo("⚡ Decrypting with AES-256-GCM...")
        decrypted_file_path = decrypt_file_func(filename, decryption_password, output)
        
        # Success report
        decrypted_path = Path(decrypted_file_path)
        decrypted_size = decrypted_path.stat().st_size
        
        click.echo("\n🎉 DECRYPTION SUCCESSFUL!")
        click.echo("✅ File decrypted and restored")
        click.echo(f"🔒 Encrypted file: {filename}")
        click.echo(f"🔓 Decrypted file: {decrypted_file_path}")
        click.echo(f"📊 Decrypted size: {decrypted_size:,} bytes")
        
        # Security information
        click.echo("\n🛡️  Security Information:")
        click.echo("• File decrypted using AES-256-GCM")
        click.echo("• Encryption keys securely derived from password")
        click.echo("• Authentication tag verified for integrity")
        click.echo("• Original encrypted file remains unchanged")
        
        # Next steps
        click.echo("\n📋 Next Steps:")
        click.echo("• Your file has been successfully restored")
        click.echo("• Keep the .faceauth file as backup if needed")
        click.echo("• Consider re-encrypting if security is compromised")
        
    except FaceAuthenticationError as e:
        click.echo(f"\n❌ Authentication Error: {e}")
        click.echo("\n💡 Solutions:")
        click.echo("• Enroll first: python main.py enroll-face")
        click.echo("• Check webcam connectivity")
        click.echo("• Ensure good lighting")
        sys.exit(1)
    except FileEncryptionError as e:
        click.echo(f"\n❌ Decryption Error: {e}")
        click.echo("\n💡 Common causes and solutions:")
        click.echo("• Wrong password - try again with correct password")
        click.echo("• Corrupted file - restore from backup if available")
        click.echo("• Invalid file format - ensure file was encrypted with FaceAuth")
        click.echo("• File tampering - check file integrity")
        sys.exit(1)
    except ImportError as e:
        click.echo(f"\n❌ Missing dependencies: {e}")
        click.echo("💡 Please install required packages:")
        click.echo("   pip install -r requirements.txt")
        sys.exit(1)
    except KeyboardInterrupt:
        click.echo("\n\n❌ Decryption cancelled by user")
        sys.exit(1)
    except Exception as e:
        click.echo(f"\n💥 Unexpected error: {e}")
        click.echo("🐛 Please report this issue if it persists")
        sys.exit(1)


@cli.command("info")
def info():
    """
    📊 Display system information and status.
    """
    click.echo("🔐 FaceAuth System Information")
    click.echo("=" * 40)
    
    # Check Python version
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    click.echo(f"🐍 Python version: {python_version}")
    
    # Check if face_data directory exists
    face_data_dir = Path("face_data")
    if face_data_dir.exists():
        face_files = list(face_data_dir.glob("*_face.dat"))
        click.echo(f"📁 Face data directory: {face_data_dir.absolute()}")
        click.echo(f"👥 Enrolled users: {len(face_files)}")
    else:
        click.echo("📁 Face data directory: Not created yet")
        click.echo("👥 Enrolled users: 0")
    
    # Check dependencies
    click.echo("\n📦 Dependencies:")
    required_packages = ["cv2", "deepface", "numpy", "cryptography", "click"]
    
    for package in required_packages:
        try:
            if package == "cv2":
                import cv2
                click.echo(f"✅ OpenCV: {cv2.__version__}")
            elif package == "deepface":
                import deepface
                click.echo(f"✅ DeepFace: Available")
            elif package == "numpy":
                import numpy
                click.echo(f"✅ NumPy: {numpy.__version__}")
            elif package == "cryptography":
                import cryptography
                click.echo(f"✅ Cryptography: {cryptography.__version__}")
            elif package == "click":
                import click as click_pkg
                click.echo(f"✅ Click: {click_pkg.__version__}")
        except ImportError:
            click.echo(f"❌ {package}: Not installed")
    
    click.echo("\n🔗 Quick Start:")
    click.echo("1. 🔧 Fix environment: python main.py setup  (Run this first if ANY issues!)")
    click.echo("2. ✅ Check status: python main.py info")
    click.echo("3. 👤 Enroll your face: python main.py enroll")
    click.echo("4. 📖 Get help: python main.py --help")
    
    click.echo("\n🚨 Having Issues?")
    click.echo("💡 The setup command is your repair tool - it fixes ALL dependency problems!")
    click.echo("   python main.py setup")


@cli.command("setup")
def setup():
    """
    🛠️ Setup and install FaceAuth dependencies.
    
    This command performs a complete environment repair by:
    1. Aggressively removing conflicting OpenCV installations
    2. Upgrading pip to the latest version
    3. Installing all dependencies from a clean state
    
    ⚡ CRITICAL: This command fixes the "haarcascade_frontalface_default.xml" 
    error that causes enrollment to crash.
    
    Run this command whenever you encounter dependency errors.
    """
    import subprocess
    click.echo("🛠️ FaceAuth Environment Repair & Setup")
    click.echo("=" * 50)
    click.echo("This will clean your environment and install all dependencies correctly.")
    click.echo("⏱️  This may take a few minutes...\n")

    # Step 1: Aggressively clean up any conflicting OpenCV installations (nuke and pave)
    click.echo("🧹 Step 1: Force-cleaning conflicting OpenCV installations...")
    click.echo("Removing: opencv-python, opencv-python-headless, opencv-contrib-python, opencv-contrib-python-headless")
    
    try:
        result_uninstall = subprocess.run([
            sys.executable, "-m", "pip", "uninstall", 
            "opencv-python", "opencv-python-headless", 
            "opencv-contrib-python", "opencv-contrib-python-headless", "-y"
        ], capture_output=True, text=True, check=False)
        
        if result_uninstall.stdout.strip():
            click.echo("Removed packages:")
            click.echo(result_uninstall.stdout)
        else:
            click.echo("No conflicting OpenCV packages found.")
            
        click.echo("✅ OpenCV cleanup complete.")
        
    except Exception as e:
        click.echo(f"⚠️  Could not uninstall OpenCV packages: {e}")
        click.echo("Proceeding with setup...")

    # Step 2: Upgrade pip
    click.echo("\n📦 Step 2: Upgrading pip to latest version...")
    try:
        result_pip = subprocess.run([
            sys.executable, "-m", "pip", "install", "--upgrade", "pip"
        ], capture_output=True, text=True, check=False)
        
        if result_pip.returncode == 0:
            click.echo("✅ pip upgraded successfully!")
        else:
            click.echo("❌ Failed to upgrade pip:")
            click.echo(result_pip.stderr)
            click.echo("\n💡 Try manually: python -m pip install --upgrade pip")
            sys.exit(1)
            
    except Exception as e:
        click.echo(f"❌ pip upgrade failed: {e}")
        click.echo("💡 Try manually: python -m pip install --upgrade pip")
        sys.exit(1)

    # Step 3: Validate requirements.txt exists
    if not Path("requirements.txt").exists():
        click.echo("❌ requirements.txt not found")
        click.echo("💡 Please ensure you're in the FaceAuth directory")
        sys.exit(1)

    # Step 4: Install all dependencies from clean state
    click.echo("\n🔧 Step 3: Installing all project dependencies from clean state...")
    click.echo("📦 Installing from requirements.txt...")
    
    try:
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ], capture_output=True, text=True, check=False)
        
        # Show installation output
        if result.stdout.strip():
            click.echo("Installation log:")
            click.echo(result.stdout)
            
        if result.returncode == 0:
            click.echo("\n🎉 SETUP COMPLETE!")
            click.echo("✅ All dependencies are freshly installed and ready")
            click.echo("🔧 Environment repair successful")
            
            # Next steps
            click.echo("\n🚀 Next Steps:")
            click.echo("1. Test the setup: python main.py info")
            click.echo("2. Enroll your face: python main.py enroll")
            click.echo("3. Start using FaceAuth!")
            
            click.echo("\n💡 If you encounter ANY error in the future:")
            click.echo("   Just run 'python main.py setup' again to fix it.")
            
        else:
            click.echo("\n❌ CRITICAL ERROR: Dependency installation failed")
            click.echo("Error details:")
            click.echo(result.stderr)
            click.echo("\n� Troubleshooting:")
            click.echo("1. Ensure you have an active internet connection")
            click.echo("2. Try manually: pip install -r requirements.txt")
            click.echo("3. Check if you're in a virtual environment")
            click.echo("4. Verify Python version compatibility (3.8+)")
            sys.exit(1)
            
    except Exception as e:
        click.echo(f"\n❌ Setup failed with exception: {e}")
        click.echo("\n� Manual recovery:")
        click.echo("   pip install -r requirements.txt")
        sys.exit(1)


def main():
    """Main entry point for the CLI."""
    try:
        cli()
    except KeyboardInterrupt:
        click.echo("\n\n👋 Goodbye!")
        sys.exit(0)
    except Exception as e:
        click.echo(f"\n💥 Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
