#!/usr/bin/env python3
"""
FaceAuth - Local Face Authentication System
===========================================

Main CLI interface for the FaceAuth system.
Provides commands for face enrollment, authentication, and file encryption.

Usage:
    python main.py enroll-face [--user-id USER] [--model MODEL]
    python main.py verify-face [--user-id USER]
    python main.py encrypt-file [--file PATH] [--user-id USER]
    python main.py decrypt-file [--file PATH] [--user-id USER]
"""

import click
import sys
import os
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from enrollment import enroll_new_user, FaceEnrollmentError


@click.group()
@click.version_option(version="1.0.0")
def cli():
    """
    🔐 FaceAuth - Local Face Authentication System
    
    A privacy-first face authentication platform for securing your files.
    All processing happens locally - no cloud, no third parties.
    """
    pass


@cli.command("enroll-face")
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
    📸 Enroll a new user's face into the system.
    
    This command captures your face using the webcam, generates a secure
    face embedding, and stores it locally in encrypted format.
    
    The process takes about 30 seconds and requires:
    - A working webcam
    - Good lighting conditions
    - Only one person visible in the frame
    
    Examples:
        python main.py enroll-face
        python main.py enroll-face --user-id john_doe
        python main.py enroll-face --user-id alice --model ArcFace
    """
    click.echo("🚀 Starting FaceAuth enrollment process...")
    click.echo("=" * 60)
    
    try:
        # Import here to avoid issues if dependencies aren't installed
        from enrollment import FaceEnroller
        
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
            click.echo("• Test authentication: python main.py verify-face")
            click.echo("• Encrypt files: python main.py encrypt-file --file myfile.txt")
            click.echo("• View help: python main.py --help")
            
        else:
            click.echo("❌ Enrollment failed")
            sys.exit(1)
            
    except FaceEnrollmentError as e:
        click.echo(f"\n❌ Enrollment Error: {e}")
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


@cli.command("verify-face")
@click.option(
    "--user-id", 
    "-u", 
    type=str, 
    help="User ID to verify against (will prompt if not provided)"
)
@click.option(
    "--data-dir",
    "-d",
    type=click.Path(),
    default="face_data",
    help="Directory containing face data (default: face_data)"
)
def verify_face(user_id, data_dir):
    """
    🔍 Verify your identity using face authentication.
    
    This command compares your current face against stored face data
    to authenticate your identity.
    
    Examples:
        python main.py verify-face
        python main.py verify-face --user-id john_doe
    """
    click.echo("🔍 Face verification not yet implemented")
    click.echo("📋 This feature will be available in the next version")
    click.echo("💡 Use 'enroll-face' to register your face first")


@cli.command("encrypt-file")
@click.option(
    "--file", 
    "-f", 
    type=click.Path(exists=True),
    help="File to encrypt (will prompt if not provided)"
)
@click.option(
    "--user-id", 
    "-u", 
    type=str, 
    help="User ID for face authentication (will prompt if not provided)"
)
def encrypt_file(file, user_id):
    """
    🔒 Encrypt a file using face authentication.
    
    This command encrypts a file and requires face authentication
    to decrypt it later.
    
    Examples:
        python main.py encrypt-file --file secret.txt
        python main.py encrypt-file --file document.pdf --user-id alice
    """
    click.echo("🔒 File encryption not yet implemented")
    click.echo("📋 This feature will be available in the next version")
    click.echo("💡 Use 'enroll-face' to register your face first")


@cli.command("decrypt-file")
@click.option(
    "--file", 
    "-f", 
    type=click.Path(exists=True),
    help="Encrypted file to decrypt (will prompt if not provided)"
)
@click.option(
    "--user-id", 
    "-u", 
    type=str, 
    help="User ID for face authentication (will prompt if not provided)"
)
def decrypt_file(file, user_id):
    """
    🔓 Decrypt a file using face authentication.
    
    This command decrypts a previously encrypted file after
    successful face authentication.
    
    Examples:
        python main.py decrypt-file --file secret.txt.encrypted
        python main.py decrypt-file --file document.pdf.encrypted --user-id alice
    """
    click.echo("🔓 File decryption not yet implemented")
    click.echo("📋 This feature will be available in the next version")
    click.echo("💡 Use 'enroll-face' to register your face first")


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
    click.echo("1. Install dependencies: pip install -r requirements.txt")
    click.echo("2. Enroll your face: python main.py enroll-face")
    click.echo("3. Get help: python main.py --help")


@cli.command("setup")
def setup():
    """
    🛠️ Setup and install FaceAuth dependencies.
    """
    click.echo("🛠️ Setting up FaceAuth...")
    
    # Check if requirements.txt exists
    if not Path("requirements.txt").exists():
        click.echo("❌ requirements.txt not found")
        click.echo("💡 Please ensure you're in the FaceAuth directory")
        sys.exit(1)
    
    click.echo("📦 Installing dependencies...")
    
    try:
        import subprocess
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            click.echo("✅ Dependencies installed successfully!")
            click.echo("\n🎉 FaceAuth is ready to use!")
            click.echo("🚀 Try: python main.py enroll-face")
        else:
            click.echo("❌ Installation failed:")
            click.echo(result.stderr)
            sys.exit(1)
            
    except Exception as e:
        click.echo(f"❌ Setup failed: {e}")
        click.echo("💡 Try manually: pip install -r requirements.txt")
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
