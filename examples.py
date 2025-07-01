#!/usr/bin/env python3
"""
FaceAuth Example Usage
=====================

This script demonstrates how to use the FaceAuth enrollment module
programmatically in your own applications.
"""

import sys
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from enrollment import FaceEnroller, FaceEnrollmentError


def example_enrollment():
    """Example of how to use the FaceAuth enrollment module."""
    
    print("🚀 FaceAuth Enrollment Example")
    print("=" * 40)
    
    try:
        # Create enroller instance
        enroller = FaceEnroller(
            model_name="Facenet",  # or "ArcFace", "VGG-Face", "Facenet512"
            data_dir="example_face_data"
        )
        
        # Enroll a new user
        print("\n📸 Starting enrollment process...")
        result = enroller.enroll_new_user(user_id="example_user")
        
        if result['success']:
            print(f"\n✅ Success! User enrolled with the following details:")
            print(f"   User ID: {result['user_id']}")
            print(f"   File path: {result['file_path']}")
            print(f"   Embedding size: {result['embedding_size']} dimensions")
            print(f"   Model used: {result['model_used']}")
            
            return True
        else:
            print("❌ Enrollment failed")
            return False
            
    except FaceEnrollmentError as e:
        print(f"❌ Enrollment error: {e}")
        return False
    except Exception as e:
        print(f"💥 Unexpected error: {e}")
        return False


def example_with_custom_settings():
    """Example with custom settings and error handling."""
    
    print("\n🔧 Custom Settings Example")
    print("=" * 40)
    
    try:
        # Create enroller with custom settings
        enroller = FaceEnroller(
            model_name="ArcFace",  # High accuracy model
            data_dir="secure_face_data"
        )
        
        # You can access and modify settings
        enroller.min_confidence = 0.8  # Higher confidence threshold
        enroller.capture_delay = 5     # Longer capture delay
        
        print("📋 Custom settings applied:")
        print(f"   Model: {enroller.model_name}")
        print(f"   Data directory: {enroller.data_dir}")
        print(f"   Min confidence: {enroller.min_confidence}")
        print(f"   Capture delay: {enroller.capture_delay}s")
        
        # Enroll user
        result = enroller.enroll_new_user(user_id="custom_user")
        
        return result['success'] if result else False
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def example_batch_enrollment():
    """Example of enrolling multiple users."""
    
    print("\n👥 Batch Enrollment Example")
    print("=" * 40)
    
    users = ["alice", "bob", "charlie"]
    results = []
    
    try:
        enroller = FaceEnroller(model_name="Facenet")
        
        for user in users:
            print(f"\n📸 Enrolling user: {user}")
            print("-" * 30)
            
            try:
                result = enroller.enroll_new_user(user_id=user)
                results.append(result)
                
                if result['success']:
                    print(f"✅ {user} enrolled successfully")
                else:
                    print(f"❌ {user} enrollment failed")
                    
            except FaceEnrollmentError as e:
                print(f"❌ {user} enrollment error: {e}")
                results.append({'success': False, 'user_id': user, 'error': str(e)})
            except KeyboardInterrupt:
                print(f"\n⏹️ Batch enrollment stopped by user")
                break
        
        # Summary
        successful = sum(1 for r in results if r.get('success', False))
        print(f"\n📊 Batch enrollment summary:")
        print(f"   Total users: {len(users)}")
        print(f"   Successful: {successful}")
        print(f"   Failed: {len(results) - successful}")
        
        return results
        
    except Exception as e:
        print(f"💥 Batch enrollment error: {e}")
        return []


def main():
    """Main example function."""
    
    print("🔐 FaceAuth - Programming Examples")
    print("=" * 50)
    
    # Example 1: Basic enrollment
    print("\n1️⃣ Basic Enrollment Example")
    success1 = example_enrollment()
    
    if success1:
        print("✅ Basic example completed successfully")
    else:
        print("❌ Basic example failed")
    
    # Ask user if they want to continue
    if input("\nContinue with more examples? (y/N): ").strip().lower() != 'y':
        return
    
    # Example 2: Custom settings
    print("\n2️⃣ Custom Settings Example")
    success2 = example_with_custom_settings()
    
    if success2:
        print("✅ Custom settings example completed")
    else:
        print("❌ Custom settings example failed")
    
    # Ask user if they want to continue
    if input("\nContinue with batch enrollment? (y/N): ").strip().lower() != 'y':
        return
    
    # Example 3: Batch enrollment
    print("\n3️⃣ Batch Enrollment Example")
    batch_results = example_batch_enrollment()
    
    if batch_results:
        print("✅ Batch enrollment example completed")
    else:
        print("❌ Batch enrollment example failed")
    
    print("\n🎉 All examples completed!")
    print("\n📋 Next steps:")
    print("• Check the generated face data directories")
    print("• Try the CLI interface: python main.py --help")
    print("• Implement face verification in your application")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Examples cancelled by user")
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
