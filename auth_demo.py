#!/usr/bin/env python3
"""
FaceAuth Authentication Demo
Demonstrates real-time face authentication capabilities.
"""

import sys
import time
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from faceauth.core.authentication import FaceAuthenticator, AuthenticationError
from faceauth.utils.storage import FaceDataStorage
from faceauth.utils.security import SecurityManager


def demo_authentication():
    """Demonstrate face authentication with various scenarios."""
    print("🔐 FaceAuth - Authentication Demo")
    print("=" * 40)
    
    # Initialize components
    try:
        security_manager = SecurityManager()
        storage = FaceDataStorage()
        authenticator = FaceAuthenticator(storage, similarity_threshold=0.6)
        
        print("✅ FaceAuth system initialized successfully")
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
        
        # Select user for authentication
        if len(users) == 1:
            selected_user = users[0]
            print(f"🎯 Auto-selecting user: {selected_user}")
        else:
            print("Select a user to authenticate:")
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
        print(f"🔍 Starting authentication for: {selected_user}")
        print("📷 Please position yourself in front of the camera")
        print("⏰ You have 15 seconds to authenticate")
        print("🔤 Press 'q' in the camera window to quit")
        print()
        
        # Perform authentication
        start_time = time.time()
        
        try:
            result = authenticator.authenticate_realtime(
                user_id=selected_user,
                timeout=15,
                max_attempts=8
            )
            
            total_time = time.time() - start_time
            
            print("\n" + "=" * 50)
            print("📊 AUTHENTICATION RESULTS")
            print("=" * 50)
            
            if result['success']:
                print("✅ STATUS: Authentication SUCCESSFUL!")
                print(f"👤 User: {result['user_id']}")
                print(f"🎯 Similarity Score: {result['similarity']:.3f}")
                print(f"📏 Threshold Used: {result['threshold']}")
                print(f"⏱️  Duration: {result['duration']:.2f} seconds")
                print(f"🔄 Attempts Used: {result['attempts']}")
                
                # Quality metrics
                if 'quality_metrics' in result:
                    quality = result['quality_metrics']
                    print(f"📸 Image Quality:")
                    print(f"   Sharpness: {quality.get('sharpness', 0):.1f}")
                    print(f"   Brightness: {quality.get('brightness', 0):.1f}")
                    print(f"   Contrast: {quality.get('contrast', 0):.1f}")
                
            else:
                print("❌ STATUS: Authentication FAILED!")
                print(f"🚫 Reason: {result['error']}")
                print(f"⏱️  Duration: {result['duration']:.2f} seconds")
                print(f"🔄 Attempts Used: {result.get('attempts', 0)}")
                
                if 'best_similarity' in result:
                    print(f"🎯 Best Similarity: {result['best_similarity']:.3f}")
                    print(f"📏 Required Threshold: {result['threshold']}")
                
                # Provide suggestions
                print("\n💡 SUGGESTIONS:")
                error_type = result.get('error_type', '')
                if error_type == 'timeout':
                    print("   • Increase timeout duration")
                    print("   • Improve lighting conditions")
                    print("   • Position face clearly in camera view")
                elif error_type == 'max_attempts_exceeded':
                    print("   • Lower the similarity threshold")
                    print("   • Ensure good lighting and positioning")
                    print("   • Consider re-enrolling if appearance changed")
                elif error_type == 'webcam_error':
                    print("   • Check webcam connection")
                    print("   • Close other camera applications")
                else:
                    print("   • Check error message for specific guidance")
            
            # Show attempt details
            if 'authentication_attempts' in result and result['authentication_attempts']:
                print("\n📋 ATTEMPT DETAILS:")
                for attempt in result['authentication_attempts']:
                    if 'similarity' in attempt:
                        print(f"   Attempt {attempt['attempt']}: "
                              f"Similarity {attempt['similarity']:.3f}")
                    elif 'error' in attempt:
                        print(f"   Attempt {attempt['attempt']}: {attempt['error']}")
            
        except AuthenticationError as e:
            print(f"\n❌ Authentication Error: {str(e)}")
        except KeyboardInterrupt:
            print("\n⚠️  Authentication cancelled by user")
        except Exception as e:
            print(f"\n❌ Unexpected error: {str(e)}")
        
        # Performance metrics
        print("\n" + "=" * 50)
        print("📈 PERFORMANCE METRICS")
        print("=" * 50)
        
        metrics = authenticator.get_performance_metrics()
        print(f"Total Attempts: {metrics['total_attempts']}")
        print(f"Successful Attempts: {metrics['successful_attempts']}")
        print(f"Average Time: {metrics['average_authentication_time']:.2f}s")
        print(f"False Positive Rate: {metrics['false_positive_rate']:.1%}")
        print(f"False Negative Rate: {metrics['false_negative_rate']:.1%}")
        
        # Performance assessment
        print("\n🎯 PERFORMANCE ASSESSMENT:")
        if metrics['average_authentication_time'] < 2.0:
            print("   ✅ Speed: Excellent (<2s target met)")
        elif metrics['average_authentication_time'] < 3.0:
            print("   ⚠️  Speed: Good but above 2s target")
        else:
            print("   ❌ Speed: Slow (exceeds targets)")
        
        print("\n✨ Demo completed successfully!")
        
    except Exception as e:
        print(f"❌ Error initializing FaceAuth: {str(e)}")
        return


def test_authentication_scenarios():
    """Test various authentication scenarios for validation."""
    print("🧪 FaceAuth - Scenario Testing")
    print("=" * 35)
    
    # Test scenarios
    scenarios = [
        {
            'name': 'Normal Authentication',
            'timeout': 10,
            'max_attempts': 5,
            'threshold': 0.6,
            'description': 'Standard authentication with default settings'
        },
        {
            'name': 'Quick Authentication',
            'timeout': 5,
            'max_attempts': 3,
            'threshold': 0.5,
            'description': 'Fast authentication with lower threshold'
        },
        {
            'name': 'Strict Authentication',
            'timeout': 15,
            'max_attempts': 8,
            'threshold': 0.8,
            'description': 'High-security authentication with strict threshold'
        }
    ]
    
    try:
        security_manager = SecurityManager()
        storage = FaceDataStorage()
        
        # Check for enrolled users
        users = storage.list_enrolled_users()
        if not users:
            print("❌ No enrolled users found for testing!")
            return
        
        test_user = users[0]
        print(f"🎯 Testing with user: {test_user}")
        print()
        
        for i, scenario in enumerate(scenarios, 1):
            print(f"🧪 Scenario {i}: {scenario['name']}")
            print(f"   {scenario['description']}")
            print(f"   Timeout: {scenario['timeout']}s, "
                  f"Max Attempts: {scenario['max_attempts']}, "
                  f"Threshold: {scenario['threshold']}")
            
            if input("   Run this scenario? (y/n): ").lower() != 'y':
                print("   ⏭️  Skipped")
                continue
            
            authenticator = FaceAuthenticator(
                storage, 
                similarity_threshold=scenario['threshold']
            )
            
            print("   🔍 Starting authentication...")
            result = authenticator.authenticate_realtime(
                user_id=test_user,
                timeout=scenario['timeout'],
                max_attempts=scenario['max_attempts']
            )
            
            if result['success']:
                print(f"   ✅ SUCCESS - Similarity: {result['similarity']:.3f}, "
                      f"Time: {result['duration']:.2f}s")
            else:
                print(f"   ❌ FAILED - {result['error']}")
            
            print()
        
        print("✨ Scenario testing completed!")
        
    except Exception as e:
        print(f"❌ Error in scenario testing: {str(e)}")


if __name__ == "__main__":
    print("Choose demo mode:")
    print("1. Interactive Authentication Demo")
    print("2. Scenario Testing")
    print("3. Exit")
    
    try:
        choice = input("\nEnter your choice (1-3): ").strip()
        
        if choice == '1':
            demo_authentication()
        elif choice == '2':
            test_authentication_scenarios()
        elif choice == '3':
            print("👋 Goodbye!")
        else:
            print("❌ Invalid choice")
    
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
