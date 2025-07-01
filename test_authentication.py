#!/usr/bin/env python3
"""
Test script for FaceAuth authentication module
==============================================

This script tests the face authentication functionality independently.
"""

import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

def test_authentication():
    """Test the face authentication module"""
    try:
        from authentication import verify_user_face, FaceAuthenticationError
        
        print("🧪 Testing FaceAuth authentication module...")
        print("=" * 50)
        
        # Test authentication
        result = verify_user_face()
        
        if result:
            print("\n✅ TEST PASSED: Authentication successful!")
            return True
        else:
            print("\n❌ TEST FAILED: Authentication failed!")
            return False
            
    except FaceAuthenticationError as e:
        print(f"\n❌ Authentication Error: {e}")
        return False
    except ImportError as e:
        print(f"\n❌ Import Error: {e}")
        print("💡 Please install dependencies: pip install -r requirements.txt")
        return False
    except Exception as e:
        print(f"\n💥 Unexpected Error: {e}")
        return False


if __name__ == "__main__":
    success = test_authentication()
    sys.exit(0 if success else 1)
