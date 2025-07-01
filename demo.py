#!/usr/bin/env python3
"""
FaceAuth Demo Script
Demonstrates the face enrollment functionality
"""

import sys
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def check_dependencies():
    """Check if all required dependencies are installed."""
    print("🔍 Checking dependencies...")
    
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
    try:
        from faceauth.core.enrollment import FaceEnrollmentManager, FaceEnrollmentError
        
        print("\n🎬 FaceAuth Enrollment Demo")
        print("=" * 40)
        
        # Initialize enrollment manager
        print("🤖 Initializing face recognition system...")
        
        enrollment_manager = FaceEnrollmentManager()
        
        print("✅ System initialized!")
        
        # Demo user ID
        demo_user = "demo_user_" + str(int(time.time()))
        
        print(f"\n👤 Demo User ID: {demo_user}")
        print("\n📋 Demo Instructions:")
        print("   • Make sure your camera is connected")
        print("   • Ensure good lighting")
        print("   • Look directly at the camera")
        print("   • Follow the on-screen instructions")
        print("   • Press 'q' to quit anytime")
        
        input("\n🎥 Press Enter to start enrollment demo...")
        
        # Start enrollment
        result = enrollment_manager.enroll_user(
            user_id=demo_user,
            timeout=60,  # Give more time for demo
            interactive=True
        )
        
        # Show results
        if result['success']:
            print("\n🎉 Demo Enrollment Successful!")
            print("=" * 35)
            print(f"✅ User '{demo_user}' enrolled")
            print(f"📊 Samples: {result['samples_collected']}")
            print(f"⭐ Quality: {result['average_quality']:.3f}")
            print(f"⏱️  Time: {result['duration']:.1f}s")
            
            # Show storage info
            stats = enrollment_manager.get_storage_stats()
            print(f"\n💾 Storage: {stats['total_users']} users, {stats['storage_size_bytes']:,} bytes")
            
            # Verify enrollment
            if enrollment_manager.verify_enrollment(demo_user):
                print("🔍 Verification: PASSED")
            else:
                print("❌ Verification: FAILED")
            
            # Clean up demo user
            print(f"\n🧹 Cleaning up demo user...")
            if enrollment_manager.delete_user(demo_user):
                print("✅ Demo user deleted")
            else:
                print("⚠️  Could not delete demo user")
                
        else:
            print(f"\n❌ Demo Failed: {result.get('error', 'Unknown error')}")
            if result.get('code') == 'CAMERA_ERROR':
                print("   💡 Make sure your camera is connected and not in use")
            elif result.get('code') == 'TIMEOUT':
                print("   💡 Try the demo again with better lighting")
        
    except FaceEnrollmentError as e:
        print(f"\n❌ Enrollment Error: {e}")
    except Exception as e:
        print(f"\n❌ Demo Error: {e}")
        print("💡 Make sure you've installed all dependencies")


def demo_cli():
    """Demo the CLI interface."""
    print("\n📱 CLI Demo")
    print("=" * 15)
    print("You can also use the CLI interface:")
    print()
    print("🔧 System check:")
    print("   python main.py system-check")
    print()
    print("👤 Enroll a user:")
    print("   python main.py enroll-face john.doe")
    print()
    print("📋 List users:")
    print("   python main.py list-users")
    print()
    print("🗑️  Delete a user:")
    print("   python main.py delete-user john.doe")
    print()
    print("💾 Storage info:")
    print("   python main.py storage-info")
    print()
    print("📦 Backup & Restore:")
    print("   python main.py backup my_backup.zip")
    print("   python main.py restore my_backup.zip")


def main():
    """Main demo function."""
    print("🔐 FaceAuth System Demo")
    print("=" * 30)
    print("Privacy-first local face authentication")
    print()
    
    # Check dependencies first
    if not check_dependencies():
        return
    
    print("\n📋 What would you like to demo?")
    print("1. Face Enrollment (Interactive)")
    print("2. CLI Commands (Information)")
    print("3. Both")
    print("4. Exit")
    
    try:
        choice = input("\nEnter choice (1-4): ").strip()
        
        if choice == '1':
            demo_enrollment()
        elif choice == '2':
            demo_cli()
        elif choice == '3':
            demo_enrollment()
            demo_cli()
        elif choice == '4':
            print("👋 Goodbye!")
        else:
            print("❌ Invalid choice")
            
    except KeyboardInterrupt:
        print("\n👋 Demo cancelled")
    except Exception as e:
        print(f"\n❌ Demo error: {e}")


if __name__ == '__main__':
    main()