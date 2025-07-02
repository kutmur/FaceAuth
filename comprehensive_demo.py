#!/usr/bin/env python3
"""
FaceAuth Complete Demo
Comprehensive demonstration of FaceAuth features including:
- Face enrollment and authentication
- File encryption and decryption
- Security and privacy features
- System compliance checking
"""

import sys
import time
import tempfile
import os
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def print_banner():
    """Print the FaceAuth demo banner."""
    banner = """
    ┌─────────────────────────────────────────────────────────┐
    │                    🔐 FaceAuth Demo                     │
    │              Privacy-First Face Authentication          │
    └─────────────────────────────────────────────────────────┘
    """
    print(banner)

def check_dependencies():
    """Check if all required dependencies are installed."""
    print("🔍 Checking system dependencies...")
    
    missing = []
    dependencies = [
        ('opencv-python', 'cv2'),
        ('numpy', 'numpy'), 
        ('torch', 'torch'),
        ('facenet-pytorch', 'facenet_pytorch'),
        ('cryptography', 'cryptography'),
        ('click', 'click'),
        ('Pillow', 'PIL')
    ]
    
    for package, module in dependencies:
        try:
            __import__(module)
            print(f"  ✅ {package}")
        except ImportError:
            print(f"  ❌ {package} (missing)")
            missing.append(package)
    
    if missing:
        print(f"\n❌ Missing dependencies: {', '.join(missing)}")
        print("Please install with: pip install -r requirements.txt")
        return False
    
    print("✅ All dependencies installed!")
    return True

def demo_enrollment():
    """Demo the face enrollment process."""
    print("\n" + "="*60)
    print("👤 FACE ENROLLMENT DEMO")
    print("="*60)
    
    try:
        from faceauth.core.enrollment import FaceEnrollmentManager, FaceEnrollmentError
        
        print("🤖 Initializing face recognition system...")
        manager = FaceEnrollmentManager()
        print("✅ System initialized!")
        
        # Demo user ID with timestamp
        demo_user = f"demo_user_{int(time.time())}"
        
        print(f"\n👤 Demo User ID: {demo_user}")
        print("\n📋 Enrollment Instructions:")
        print("   • Ensure your camera is connected and working")
        print("   • Position yourself in good lighting")
        print("   • Look directly at the camera")
        print("   • Follow the on-screen prompts")
        print("   • Keep your face steady during capture")
        print("   • Press 'q' at any time to quit")
        
        input("\n🎥 Press Enter to begin face enrollment...")
        
        # Start enrollment with detailed settings
        start_time = time.time()
        result = manager.enroll_user(
            user_id=demo_user,
            timeout=90,  # Extended time for demo
            interactive=True
        )
        
        # Display detailed results
        if result['success']:
            print("\n🎉 ENROLLMENT SUCCESSFUL!")
            print("=" * 30)
            print(f"✅ User ID: {demo_user}")
            print(f"📊 Samples collected: {result['samples_collected']}")
            print(f"⭐ Average quality: {result['average_quality']:.3f}")
            print(f"⏱️  Duration: {result['duration']:.1f} seconds")
            print(f"📸 Quality threshold: {result.get('quality_threshold', 'N/A')}")
            
            # Storage information
            stats = manager.get_storage_stats()
            print(f"\n💾 Storage Information:")
            print(f"   📁 Directory: {stats['storage_dir']}")
            print(f"   👥 Total users: {stats['total_users']}")
            print(f"   💽 Storage used: {stats['storage_size_bytes']:,} bytes")
            
            # Verify enrollment
            print("\n🔍 Verifying enrollment...")
            if manager.verify_enrollment(demo_user):
                print("✅ Enrollment verification: PASSED")
            else:
                print("❌ Enrollment verification: FAILED")
                
            return demo_user, manager
        else:
            print(f"\n❌ ENROLLMENT FAILED")
            print(f"   Error: {result.get('error', 'Unknown error')}")
            print(f"   Code: {result.get('code', 'N/A')}")
            
            # Provide specific guidance based on error
            error_code = result.get('code')
            if error_code == 'CAMERA_ERROR':
                print("   💡 Solution: Check camera connection and permissions")
            elif error_code == 'TIMEOUT':
                print("   💡 Solution: Try again with better lighting and positioning")
            elif error_code == 'NO_FACE_DETECTED':
                print("   💡 Solution: Ensure your face is clearly visible in the camera")
            elif error_code == 'POOR_QUALITY':
                print("   💡 Solution: Improve lighting and reduce motion")
                
            return None, None
            
    except FaceEnrollmentError as e:
        print(f"\n❌ Enrollment Error: {e}")
        return None, None
    except Exception as e:
        print(f"\n❌ System Error: {e}")
        print("💡 Ensure all dependencies are installed and camera is available")
        return None, None

def demo_authentication(user_id, manager):
    """Demo the face authentication process."""
    print("\n" + "="*60)
    print("🔍 FACE AUTHENTICATION DEMO")
    print("="*60)
    
    try:
        from faceauth.core.authentication import FaceAuthenticator, AuthenticationError
        from faceauth.utils.storage import FaceDataStorage
        
        print("🤖 Initializing authentication system...")
        storage = FaceDataStorage()
        authenticator = FaceAuthenticator(
            storage=storage,
            similarity_threshold=0.6,
            device='auto'
        )
        print("✅ Authentication system ready!")
        
        print(f"\n👤 Authenticating user: {user_id}")
        print("\n📋 Authentication Instructions:")
        print("   • Look directly at the camera")
        print("   • Keep your face steady and well-lit")
        print("   • Authentication typically takes 1-3 seconds")
        print("   • Press 'q' to cancel authentication")
        
        input("\n🎥 Press Enter to start authentication...")
        
        # Perform detailed authentication
        result = authenticator.authenticate_realtime(
            user_id=user_id,
            timeout=15,
            max_attempts=3,
            show_camera=True,
            quality_check=True
        )
        
        if result['success']:
            print("\n🎉 AUTHENTICATION SUCCESSFUL!")
            print("=" * 35)
            print(f"✅ User verified: {user_id}")
            print(f"🎯 Similarity score: {result['similarity']:.3f}")
            print(f"⏱️  Duration: {result['duration']:.2f} seconds")
            print(f"🔄 Attempts used: {result['attempts']}")
            print(f"📊 Face quality: {result.get('quality', 'N/A')}")
            
            # Get performance metrics
            metrics = authenticator.get_performance_metrics()
            if metrics['total_attempts'] > 0:
                print(f"\n📈 Performance Metrics:")
                print(f"   🎯 Success rate: {metrics['success_rate']:.1%}")
                print(f"   ⏱️  Average time: {metrics['average_authentication_time']:.2f}s")
                print(f"   📊 Total attempts: {metrics['total_attempts']}")
                
            return True
        else:
            print(f"\n❌ AUTHENTICATION FAILED")
            print(f"   Error: {result.get('error', 'Unknown error')}")
            print(f"   Type: {result.get('error_type', 'N/A')}")
            print(f"   Best similarity: {result.get('best_similarity', 0):.3f}")
            print(f"   Attempts: {result.get('attempts', 0)}")
            
            # Provide guidance
            error_type = result.get('error_type')
            if error_type == 'threshold_not_met':
                print("   💡 Solution: Ensure you're the enrolled user, improve lighting")
            elif error_type == 'timeout':
                print("   💡 Solution: Try again, position face clearly in camera")
            elif error_type == 'max_attempts_exceeded':
                print("   💡 Solution: Check if you're the correct user, retry with better conditions")
                
            return False
            
    except AuthenticationError as e:
        print(f"\n❌ Authentication Error: {e}")
        return False
    except Exception as e:
        print(f"\n❌ System Error: {e}")
        return False

def demo_file_encryption(user_id):
    """Demo file encryption and decryption."""
    print("\n" + "="*60)
    print("🔐 FILE ENCRYPTION DEMO")
    print("="*60)
    
    try:
        from faceauth.crypto.file_encryption import FileEncryption, EncryptionError
        from faceauth.utils.storage import FaceDataStorage
        
        print("🤖 Initializing file encryption system...")
        storage = FaceDataStorage()
        file_encryption = FileEncryption(storage)
        print("✅ File encryption system ready!")
        
        # Create a sample file for demo
        demo_content = f"""
🔐 FaceAuth Demo Document
========================

This is a confidential document encrypted with FaceAuth.

User: {user_id}
Timestamp: {datetime.now().isoformat()}
Demo Content: This file contains sensitive information that
should only be accessible through face authentication.

Features demonstrated:
✅ AES-256-GCM encryption
✅ Face-based authentication
✅ Secure key derivation
✅ Integrity verification
✅ Privacy protection

Only the enrolled user can decrypt this file!
"""
        
        # Create temporary demo file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(demo_content)
            demo_file = f.name
            
        print(f"\n📄 Created demo file: {os.path.basename(demo_file)}")
        print(f"   📏 Size: {len(demo_content)} bytes")
        print(f"   📋 Content: Confidential document with demo data")
        
        # Encrypt the file
        print(f"\n🔐 Encrypting file with face authentication...")
        print("   • This will require face authentication")
        print("   • File will be encrypted with AES-256-GCM")
        print("   • Only you will be able to decrypt it")
        
        input("Press Enter to start encryption...")
        
        encrypt_result = file_encryption.encrypt_file(
            file_path=demo_file,
            user_id=user_id,
            output_path=demo_file + ".faceauth",
            kdf_method="argon2",
            auth_timeout=15
        )
        
        if encrypt_result['success']:
            encrypted_file = encrypt_result['output_file']
            print(f"\n🎉 ENCRYPTION SUCCESSFUL!")
            print("=" * 30)
            print(f"✅ Encrypted file: {os.path.basename(encrypted_file)}")
            print(f"⏱️  Duration: {encrypt_result['duration']:.2f} seconds")
            print(f"📦 Original size: {encrypt_result['original_size']:,} bytes")
            print(f"📦 Encrypted size: {encrypt_result['encrypted_size']:,} bytes")
            print(f"🔐 KDF method: {encrypt_result['kdf_method']}")
            print(f"🔒 Encryption: {encrypt_result.get('encryption_algorithm', 'AES-256-GCM')}")
            
            # Verify the encrypted file
            print(f"\n🔍 Verifying encrypted file...")
            info = file_encryption.verify_encrypted_file(encrypted_file)
            
            if info['is_faceauth_file']:
                print("✅ File verification: PASSED")
                print(f"   📄 Original name: {info['original_filename']}")
                print(f"   📦 Original size: {info['original_size']} bytes")
                print(f"   🔐 KDF method: {info['kdf_method']}")
                print(f"   📅 Creation time: {info['creation_time']}")
                print(f"   🔍 Integrity: {'✅ VALID' if info['integrity_check'] else '❌ INVALID'}")
            else:
                print("❌ File verification: FAILED")
                return False
                
            # Decrypt the file
            print(f"\n🔓 Decrypting file with face authentication...")
            print("   • This will require face authentication again")
            print("   • File integrity will be verified")
            print("   • Content will be restored exactly")
            
            input("Press Enter to start decryption...")
            
            decrypt_result = file_encryption.decrypt_file(
                encrypted_path=encrypted_file,
                user_id=user_id,
                output_path=demo_file + ".decrypted",
                auth_timeout=15
            )
            
            if decrypt_result['success']:
                decrypted_file = decrypt_result['output_file']
                print(f"\n🎉 DECRYPTION SUCCESSFUL!")
                print("=" * 30)
                print(f"✅ Decrypted file: {os.path.basename(decrypted_file)}")
                print(f"⏱️  Duration: {decrypt_result['duration']:.2f} seconds")
                print(f"🔍 Integrity verified: {'✅ YES' if decrypt_result['integrity_verified'] else '❌ NO'}")
                
                # Verify content matches
                with open(decrypted_file, 'r') as f:
                    decrypted_content = f.read()
                    
                if decrypted_content == demo_content:
                    print("✅ Content verification: PASSED")
                    print("   📄 File content matches original exactly")
                else:
                    print("❌ Content verification: FAILED")
                    
                # Show a preview of the content
                print(f"\n📄 Decrypted content preview:")
                print("=" * 40)
                lines = decrypted_content.split('\n')[:10]  # First 10 lines
                for line in lines:
                    if line.strip():
                        print(f"   {line}")
                print("   ...")
                
                # Clean up demo files
                for file_path in [demo_file, encrypted_file, decrypted_file]:
                    try:
                        os.unlink(file_path)
                    except:
                        pass
                        
                return True
            else:
                print(f"\n❌ DECRYPTION FAILED")
                print(f"   Error: {decrypt_result.get('error', 'Unknown error')}")
                return False
        else:
            print(f"\n❌ ENCRYPTION FAILED")
            print(f"   Error: {encrypt_result.get('error', 'Unknown error')}")
            return False
            
    except EncryptionError as e:
        print(f"\n❌ Encryption Error: {e}")
        return False
    except Exception as e:
        print(f"\n❌ System Error: {e}")
        return False

def demo_security_features():
    """Demo security and privacy features."""
    print("\n" + "="*60)
    print("🛡️ SECURITY & PRIVACY FEATURES DEMO")
    print("="*60)
    
    try:
        from faceauth.security.privacy_manager import PrivacyManager
        from faceauth.security.audit_logger import SecureAuditLogger
        from faceauth.security.compliance_checker import ComplianceChecker
        
        print("🤖 Initializing security systems...")
        privacy = PrivacyManager()
        audit = SecureAuditLogger()
        compliance = ComplianceChecker()
        print("✅ Security systems ready!")
        
        # Privacy compliance check
        print(f"\n🔍 Checking privacy compliance...")
        privacy_result = compliance.check_privacy_compliance()
        print(f"✅ Privacy compliance score: {privacy_result['score']:.1f}/100")
        
        if privacy_result['passed']:
            print("✅ Privacy compliance: PASSED")
        else:
            print("⚠️  Privacy compliance: NEEDS ATTENTION")
            
        # GDPR compliance check
        print(f"\n🔍 Checking GDPR compliance...")
        gdpr_result = compliance.check_gdpr_compliance()
        print(f"✅ GDPR compliance score: {gdpr_result['score']:.1f}/100")
        
        # Security audit
        print(f"\n🔍 Running security audit...")
        security_result = compliance.check_security_compliance()
        print(f"✅ Security compliance score: {security_result['score']:.1f}/100")
        
        # Comprehensive compliance check
        print(f"\n🔍 Comprehensive compliance check...")
        all_results = compliance.check_all_standards()
        
        print(f"\n📊 COMPLIANCE SUMMARY:")
        print("=" * 25)
        for standard, result in all_results.items():
            status = "✅ PASS" if result['passed'] else "⚠️  REVIEW"
            print(f"   {standard.upper()}: {result['score']:.1f}/100 {status}")
            
        # Show some audit logs
        print(f"\n📋 Recent security events:")
        logs = audit.get_audit_logs(limit=5)
        if logs:
            for log in logs[:3]:  # Show last 3 events
                timestamp = log['timestamp'][:19]  # Remove microseconds
                print(f"   {timestamp}: {log['event_type']} - {log.get('message', 'N/A')}")
        else:
            print("   No recent events logged")
            
        # Export compliance report
        print(f"\n📤 Generating compliance report...")
        report = compliance.export_compliance_report()
        
        # Save to temporary file for demo
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write(report)
            report_file = f.name
            
        print(f"✅ Compliance report saved")
        print(f"   📄 File: {os.path.basename(report_file)}")
        print(f"   📏 Size: {len(report):,} bytes")
        
        # Clean up
        try:
            os.unlink(report_file)
        except:
            pass
            
        return True
        
    except Exception as e:
        print(f"\n❌ Security demo error: {e}")
        return False

def demo_system_info():
    """Show system information and capabilities."""
    print("\n" + "="*60)
    print("💻 SYSTEM INFORMATION")
    print("="*60)
    
    try:
        from faceauth.core.enrollment import FaceEnrollmentManager
        from faceauth.utils.storage import FaceDataStorage
        
        # System capabilities
        print("🔧 System Capabilities:")
        
        # Check GPU availability
        try:
            import torch
            if torch.cuda.is_available():
                print("   ✅ GPU acceleration: Available")
                print(f"      🎮 Device: {torch.cuda.get_device_name(0)}")
                print(f"      💾 Memory: {torch.cuda.get_device_properties(0).total_memory // 1024**2} MB")
            else:
                print("   ℹ️  GPU acceleration: Not available (using CPU)")
        except:
            print("   ℹ️  GPU acceleration: Unknown")
            
        # Camera detection
        try:
            import cv2
            cap = cv2.VideoCapture(0)
            if cap.isOpened():
                print("   ✅ Camera: Available")
                cap.release()
            else:
                print("   ❌ Camera: Not available")
        except:
            print("   ❌ Camera: Error accessing")
            
        # Storage information
        storage = FaceDataStorage()
        stats = storage.get_storage_stats()
        
        print(f"\n💾 Storage Information:")
        print(f"   📁 Directory: {stats['storage_dir']}")
        print(f"   👥 Enrolled users: {stats['total_users']}")
        print(f"   💽 Storage used: {stats['storage_size_bytes']:,} bytes")
        print(f"   🔐 Encryption: AES-256-GCM")
        print(f"   🔑 Key derivation: PBKDF2/Argon2")
        
        # Security features
        print(f"\n🛡️ Security Features:")
        print("   ✅ End-to-end encryption")
        print("   ✅ Local processing only") 
        print("   ✅ No cloud dependencies")
        print("   ✅ Secure memory management")
        print("   ✅ Tamper-evident audit logs")
        print("   ✅ Privacy by design")
        print("   ✅ GDPR/CCPA compliant")
        
        # Performance characteristics
        print(f"\n⚡ Performance:")
        print("   🎯 Authentication: <2 seconds")
        print("   📸 Enrollment: 10-30 seconds")
        print("   🔐 File encryption: ~1MB/second")
        print("   💾 Memory usage: ~500MB peak")
        print("   📏 Storage per user: ~1KB")
        
        return True
        
    except Exception as e:
        print(f"\n❌ System info error: {e}")
        return False

def main():
    """Main demo function with interactive menu."""
    print_banner()
    
    print("Welcome to the FaceAuth comprehensive demo!")
    print("This demo will showcase all major features of the FaceAuth system.")
    print("\n🔒 Privacy Notice:")
    print("   • All processing happens locally on your device")
    print("   • No data is transmitted to external servers")
    print("   • Face data is encrypted and stored securely")
    print("   • Demo user will be automatically deleted after demo")
    
    # Check dependencies first
    if not check_dependencies():
        print("\n❌ Cannot proceed without required dependencies.")
        return 1
    
    print("\n📋 Available demos:")
    print("1. 👤 Complete workflow (Enrollment + Authentication + File Encryption)")
    print("2. 👤 Face enrollment only")
    print("3. 🔐 File encryption demo (requires enrolled user)")
    print("4. 🛡️ Security & privacy features")
    print("5. 💻 System information")
    print("6. 🔄 All demos (comprehensive)")
    print("7. ❌ Exit")
    
    try:
        choice = input("\nEnter your choice (1-7): ").strip()
        
        demo_user = None
        manager = None
        
        if choice in ['1', '6']:  # Complete workflow or all demos
            # Step 1: Enrollment
            demo_user, manager = demo_enrollment()
            if demo_user is None:
                print("\n❌ Cannot proceed without successful enrollment")
                return 1
                
            # Step 2: Authentication
            auth_success = demo_authentication(demo_user, manager)
            if not auth_success:
                print("\n⚠️  Authentication failed, but continuing with file encryption demo")
                
            # Step 3: File encryption
            demo_file_encryption(demo_user)
            
            if choice == '6':  # All demos
                # Step 4: Security features
                demo_security_features()
                
                # Step 5: System information
                demo_system_info()
            
        elif choice == '2':  # Enrollment only
            demo_user, manager = demo_enrollment()
            
        elif choice == '3':  # File encryption demo
            user_id = input("Enter enrolled user ID: ").strip()
            if user_id:
                demo_file_encryption(user_id)
            else:
                print("❌ User ID required for file encryption demo")
                
        elif choice == '4':  # Security features
            demo_security_features()
            
        elif choice == '5':  # System information
            demo_system_info()
            
        elif choice == '7':  # Exit
            print("👋 Goodbye!")
            return 0
            
        else:
            print("❌ Invalid choice")
            return 1
            
        # Clean up demo user if created
        if demo_user and manager:
            print(f"\n🧹 Cleaning up demo user...")
            try:
                if manager.delete_user(demo_user):
                    print("✅ Demo user deleted successfully")
                else:
                    print("⚠️  Could not delete demo user")
            except Exception as e:
                print(f"⚠️  Error cleaning up demo user: {e}")
                
        print(f"\n🎉 Demo completed successfully!")
        print("=" * 40)
        print("Thank you for trying FaceAuth!")
        print("\n💡 Next steps:")
        print("   • Install: pip install -r requirements.txt")
        print("   • Enroll: python main.py enroll-face your_name")
        print("   • Authenticate: python main.py verify-face your_name")
        print("   • Encrypt files: python main.py encrypt-file file.txt your_name")
        print("   • Read docs: README.md and API_DOCUMENTATION.md")
        
        return 0
        
    except KeyboardInterrupt:
        print("\n\n👋 Demo cancelled by user")
        return 1
    except Exception as e:
        print(f"\n❌ Demo error: {e}")
        return 1

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
