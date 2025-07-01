#!/usr/bin/env python3
"""
FaceAuth Usage Example
Shows how to use the FaceAuth system programmatically
"""

from faceauth import FaceEnrollmentManager

def main():
    """Example usage of the FaceAuth system."""
    
    print("🔐 FaceAuth Usage Example")
    print("=" * 30)
    
    # Initialize the enrollment manager
    print("🤖 Initializing FaceAuth system...")
    manager = FaceEnrollmentManager()
    print("✅ System ready!")
    
    # Example 1: Check enrolled users
    print("\n📋 Step 1: Check enrolled users")
    users = manager.get_enrolled_users()
    print(f"Currently enrolled users: {len(users)}")
    if users:
        for user in users:
            print(f"  • {user}")
    else:
        print("  (No users enrolled)")
    
    # Example 2: Get storage statistics
    print("\n💾 Step 2: Storage information")
    stats = manager.get_storage_stats()
    print(f"Storage directory: {stats['storage_dir']}")
    print(f"Total users: {stats['total_users']}")
    print(f"Storage size: {stats['storage_size_bytes']:,} bytes")
    
    # Example 3: Programmatic enrollment (would require camera)
    print("\n👤 Step 3: Programmatic enrollment")
    print("Note: This would require a camera for actual enrollment")
    print("Example code:")
    print("""
    # Enroll a user
    result = manager.enroll_user("john.doe", timeout=30)
    
    if result['success']:
        print(f"✅ User enrolled successfully!")
        print(f"📊 Quality: {result['average_quality']:.3f}")
        print(f"⏱️  Duration: {result['duration']:.1f}s")
    else:
        print(f"❌ Enrollment failed: {result['error']}")
    """)
    
    # Example 4: Check if user exists
    print("\n🔍 Step 4: User verification")
    test_user = "john.doe"
    exists = manager.verify_enrollment(test_user)
    print(f"User '{test_user}' enrolled: {exists}")
    
    print("\n✨ Example complete!")
    print("\nTo try actual enrollment, run:")
    print("  python main.py enroll-face your-username")


if __name__ == '__main__':
    main()
