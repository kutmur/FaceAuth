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
    
    # Example 4: Face authentication
    print("\n🔍 Step 4: Face authentication")
    print("Note: This would require a camera and enrolled user")
    print("Example code:")
    print("""
    from faceauth.core.authentication import FaceAuthenticator
    from faceauth.utils.storage import FaceDataStorage
    
    # Initialize authenticator
    storage = FaceDataStorage()
    authenticator = FaceAuthenticator(storage, similarity_threshold=0.6)
    
    # Simple authentication
    success = authenticator.authenticate("john.doe", timeout=10)
    print(f"Authentication result: {success}")
    
    # Detailed authentication
    result = authenticator.authenticate_realtime(
        user_id="john.doe",
        timeout=10,
        max_attempts=5
    )
    
    if result['success']:
        print(f"✅ Authentication successful!")
        print(f"🎯 Similarity: {result['similarity']:.3f}")
        print(f"⏱️  Duration: {result['duration']:.2f}s")
        print(f"🔄 Attempts: {result['attempts']}")
    else:
        print(f"❌ Authentication failed: {result['error']}")
        
    # Get performance metrics
    metrics = authenticator.get_performance_metrics()
    print(f"📊 Average time: {metrics['average_authentication_time']:.2f}s")
    print(f"📈 False positive rate: {metrics['false_positive_rate']:.1%}")
    print(f"📉 False negative rate: {metrics['false_negative_rate']:.1%}")
    """)
    
    # Example 5: Error scenarios
    print("\n⚠️  Step 5: Error handling examples")
    print("Example code:")
    print("""
    # Handle authentication errors
    result = authenticator.authenticate_realtime("nonexistent_user")
    
    if not result['success']:
        error_type = result.get('error_type')
        
        if error_type == 'user_not_found':
            print("User not enrolled - run enrollment first")
        elif error_type == 'webcam_error':
            print("Camera not accessible - check connections")
        elif error_type == 'timeout':
            print("Authentication timed out - try again")
        elif error_type == 'max_attempts_exceeded':
            print("Too many failed attempts - check threshold")
    """)
    
    print("\n✨ Example completed!")
    print("\n💡 To see actual enrollment and authentication:")
    print("   1. Run: python main.py enroll-face your_name")
    print("   2. Run: python main.py verify-face your_name")
    print("   3. Run: python auth_demo.py for interactive demo")


if __name__ == "__main__":
    main()
