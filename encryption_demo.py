#!/usr/bin/env python3
"""
FaceAuth File Encryption Demo
Demonstrates secure file encryption controlled by face authentication.
"""

import sys
import time
import tempfile
import shutil
from pathlib import Path
import secrets

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from faceauth.crypto.file_encryption import FileEncryption, EncryptionError
from faceauth.utils.storage import FaceDataStorage
from faceauth.utils.security import SecurityManager


def demo_file_encryption():
    """Demonstrate file encryption and decryption with face authentication."""
    print("🔒 FaceAuth - File Encryption Demo")
    print("=" * 45)
    
    try:
        # Initialize components
        security_manager = SecurityManager()
        storage = FaceDataStorage()
        file_encryption = FileEncryption(storage)
        
        print("✅ FaceAuth file encryption system initialized")
        print()
        
        # Check for enrolled users
        users = storage.list_enrolled_users()
        if not users:
            print("❌ No enrolled users found!")
            print("💡 Please enroll a user first using:")
            print("   python main.py enroll-face <user_id>")
            return
        
        print(f"👥 Found {len(users)} enrolled user(s):")
        for i, user_id in enumerate(users, 1):
            print(f"   {i}. {user_id}")
        print()
        
        # Select user
        if len(users) == 1:
            selected_user = users[0]
            print(f"🎯 Auto-selecting user: {selected_user}")
        else:
            print("Select a user for file encryption:")
            try:
                choice = int(input("Enter user number: ")) - 1
                if 0 <= choice < len(users):
                    selected_user = users[choice]
                else:
                    print("❌ Invalid selection")
                    return
            except ValueError:
                print("❌ Invalid input")
                return
        
        print()
        
        # Create a demo file
        demo_content = f"""
🔒 FaceAuth File Encryption Demo

This is a demonstration file containing sensitive information.

User: {selected_user}
Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}
Random Data: {secrets.token_hex(32)}

This file has been encrypted using military-grade AES-256-GCM encryption
with a key derived from your unique face embedding using Argon2 key derivation.

Security Features:
✅ Face authentication required for access
✅ Unique encryption key per file
✅ Forward secrecy (keys not stored)
✅ Authenticated encryption (integrity protection)
✅ Secure key derivation from biometric data

Thank you for using FaceAuth!
        """.strip()
        
        demo_file = Path("faceauth_demo.txt")
        encrypted_file = Path("faceauth_demo.txt.faceauth")
        decrypted_file = Path("faceauth_demo_decrypted.txt")
        
        try:
            # Create demo file
            demo_file.write_text(demo_content, encoding='utf-8')
            print(f"📝 Created demo file: {demo_file.name} ({len(demo_content)} bytes)")
            print()
            
            # Show encryption options
            print("🔧 Encryption Options:")
            print("1. Argon2 (recommended - high security)")
            print("2. PBKDF2 (standard - good security)")
            print("3. scrypt (alternative - good security)")
            print("4. Multi-KDF (maximum security)")
            
            kdf_methods = ['argon2', 'pbkdf2', 'scrypt', 'multi']
            try:
                choice = input("\\nSelect KDF method (1-4, default=1): ").strip()
                if not choice:
                    choice = "1"
                kdf_method = kdf_methods[int(choice) - 1]
            except (ValueError, IndexError):
                kdf_method = 'argon2'
                print("Using default: Argon2")
            
            print(f"🔑 Selected KDF method: {kdf_method}")
            print()
            
            # Encrypt file
            print("🔒 Starting file encryption...")
            print("📷 Face authentication will be required...")
            print()
            
            start_time = time.time()
            
            try:
                result = file_encryption.encrypt_file(
                    file_path=str(demo_file),
                    user_id=selected_user,
                    output_path=str(encrypted_file),
                    kdf_method=kdf_method,
                    auth_timeout=15,
                    overwrite=True
                )
                
                encryption_time = time.time() - start_time
                
                if result['success']:
                    print()
                    print("✅ FILE ENCRYPTION SUCCESSFUL!")
                    print("=" * 35)
                    print(f"Original file: {result['input_file']}")
                    print(f"Encrypted file: {result['output_file']}")
                    print(f"Original size: {result['original_size']:,} bytes")
                    print(f"Encrypted size: {result['encrypted_size']:,} bytes")
                    overhead = result['encrypted_size'] - result['original_size']
                    print(f"Encryption overhead: {overhead:,} bytes")
                    print(f"Encryption time: {result['duration']:.2f}s")
                    print(f"KDF method: {result['kdf_method']}")
                    print()
                    
                    # Show file information
                    print("📄 Encrypted File Information:")
                    file_info = file_encryption.verify_encrypted_file(str(encrypted_file))
                    if file_info['is_faceauth_file']:
                        print(f"   Format version: {file_info['file_format_version']}")
                        print(f"   KDF method: {file_info['kdf_method']}")
                        print(f"   Original filename: {file_info['original_filename']}")
                        print(f"   Header size: {file_info['header_size']} bytes")
                    print()
                    
                    # Ask about decryption
                    if input("🔓 Would you like to decrypt the file? (y/n): ").lower() == 'y':
                        print()
                        print("🔓 Starting file decryption...")
                        print("📷 Face authentication will be required again...")
                        print()
                        
                        start_time = time.time()
                        
                        decrypt_result = file_encryption.decrypt_file(
                            encrypted_path=str(encrypted_file),
                            user_id=selected_user,
                            output_path=str(decrypted_file),
                            auth_timeout=15,
                            overwrite=True
                        )
                        
                        if decrypt_result['success']:
                            print()
                            print("✅ FILE DECRYPTION SUCCESSFUL!")
                            print("=" * 35)
                            print(f"Encrypted file: {decrypt_result['encrypted_file']}")
                            print(f"Decrypted file: {decrypt_result['output_file']}")
                            print(f"File size: {decrypt_result['file_size']:,} bytes")
                            print(f"Decryption time: {decrypt_result['duration']:.2f}s")
                            print()
                            
                            # Verify content integrity
                            original_content = demo_file.read_text(encoding='utf-8')
                            decrypted_content = decrypted_file.read_text(encoding='utf-8')
                            
                            if original_content == decrypted_content:
                                print("✅ Content integrity verified - files match perfectly!")
                            else:
                                print("❌ Content integrity check failed!")
                            
                            print()
                            print("📊 Demo Statistics:")
                            total_time = encryption_time + decrypt_result['duration']
                            print(f"   Total demo time: {total_time:.2f}s")
                            print(f"   Encryption speed: {result['original_size']/result['duration']:.0f} bytes/s")
                            print(f"   Decryption speed: {decrypt_result['file_size']/decrypt_result['duration']:.0f} bytes/s")
                            
                        else:
                            print("❌ File decryption failed!")
                    
                    # Show cryptographic information
                    print()
                    print("🔐 Cryptographic Information:")
                    crypto_info = file_encryption.get_encryption_info(kdf_method)
                    print(f"   Encryption: {crypto_info['encryption_algorithm']}")
                    print(f"   Key size: {crypto_info['key_size_bits']} bits")
                    print(f"   Authentication tag: {crypto_info['tag_size_bits']} bits")
                    kdf_info = crypto_info['kdf_info']
                    print(f"   KDF: {kdf_info['method']}")
                    if 'iterations' in kdf_info:
                        print(f"   KDF iterations: {kdf_info['iterations']:,}")
                    if 'memory_cost' in kdf_info:
                        print(f"   KDF memory: {kdf_info['memory_cost']:,} KB")
                    
                else:
                    print("❌ File encryption failed!")
                    
            except EncryptionError as e:
                print(f"❌ Encryption error: {str(e)}")
            except KeyboardInterrupt:
                print("\\n⚠️  Demo cancelled by user")
            
        finally:
            # Cleanup demo files
            cleanup_files = [demo_file, encrypted_file, decrypted_file]
            for file_path in cleanup_files:
                if file_path.exists():
                    file_path.unlink()
            
            print()
            print("🧹 Demo files cleaned up")
        
        print()
        print("✨ File encryption demo completed!")
        print()
        print("💡 To encrypt your own files:")
        print("   python main.py encrypt-file <file_path> <user_id>")
        print("   python main.py decrypt-file <encrypted_path> <user_id>")
        
    except Exception as e:
        print(f"❌ Demo error: {str(e)}")


def security_demonstration():
    """Demonstrate security features of the file encryption system."""
    print("🛡️  FaceAuth - Security Features Demonstration")
    print("=" * 55)
    
    try:
        file_encryption = FileEncryption()
        
        print("🔐 Cryptographic Security Features:")
        print()
        
        # Show encryption information
        crypto_info = file_encryption.get_encryption_info()
        
        print("1. 🔒 Encryption Algorithm:")
        print(f"   • {crypto_info['encryption_algorithm']}")
        print(f"   • {crypto_info['key_size_bits']}-bit encryption key")
        print(f"   • {crypto_info['tag_size_bits']}-bit authentication tag")
        print(f"   • Authenticated encryption (prevents tampering)")
        print()
        
        print("2. 🔑 Key Derivation:")
        kdf_methods = ['argon2', 'pbkdf2', 'scrypt', 'multi']
        for method in kdf_methods:
            info = file_encryption.get_encryption_info(method)['kdf_info']
            print(f"   • {info['method']}")
            if 'iterations' in info:
                print(f"     - {info['iterations']:,} iterations")
            if 'memory_cost' in info:
                print(f"     - {info['memory_cost']:,} KB memory cost")
            if 'time_cost' in info:
                print(f"     - {info['time_cost']} time cost")
        print()
        
        print("3. 🎯 Face Authentication Security:")
        print("   • Face embedding normalization")
        print("   • Biometric key derivation")
        print("   • No stored encryption keys")
        print("   • Forward secrecy")
        print()
        
        print("4. 📁 File Protection:")
        print("   • Unique key per file")
        print("   • File path in key derivation")
        print("   • Header integrity protection")
        print("   • Secure file format")
        print()
        
        print("5. 🧹 Secure Operations:")
        print("   • Secure key deletion from memory")
        print("   • Streaming encryption for large files")
        print("   • Chunk-based processing")
        print("   • Error rollback and cleanup")
        print()
        
        print("6. 🏛️  Compliance & Standards:")
        print("   • NIST-approved algorithms (AES, SHA-256)")
        print("   • OWASP key derivation recommendations")
        print("   • Modern cryptographic libraries")
        print("   • Industry best practices")
        print()
        
        print("✅ Military-grade security implemented!")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")


if __name__ == "__main__":
    print("Choose demo mode:")
    print("1. File Encryption Demo")
    print("2. Security Features Demonstration")
    print("3. Exit")
    
    try:
        choice = input("\\nEnter your choice (1-3): ").strip()
        
        if choice == '1':
            demo_file_encryption()
        elif choice == '2':
            security_demonstration()
        elif choice == '3':
            print("👋 Goodbye!")
        else:
            print("❌ Invalid choice")
    
    except KeyboardInterrupt:
        print("\\n👋 Goodbye!")
    except Exception as e:
        print(f"\\n❌ Error: {str(e)}")
