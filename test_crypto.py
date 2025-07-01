#!/usr/bin/env python3
"""
FaceAuth Crypto Module Tests
============================

Simple tests to verify the cryptographic functions work correctly.
"""

import numpy as np
import sys
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

try:
    from crypto import (
        encrypt_embedding_with_password,
        decrypt_embedding, 
        SecureEmbeddingStorage,
        verify_embedding_integrity,
        SECURITY_NOTES
    )
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("💡 Please install dependencies: pip install -r requirements.txt")
    sys.exit(1)


def test_basic_encryption():
    """Test basic encryption and decryption."""
    print("🧪 Testing basic encryption/decryption...")
    
    # Create a dummy face embedding (simulating what DeepFace would generate)
    original_embedding = np.random.rand(512).astype(np.float32)
    password = "test_password_123"
    
    try:
        # Encrypt
        encrypted_data = encrypt_embedding_with_password(original_embedding, password)
        print(f"✅ Encryption successful (size: {len(encrypted_data)} bytes)")
        
        # Decrypt
        decrypted_embedding = decrypt_embedding(encrypted_data, password)
        print(f"✅ Decryption successful (shape: {decrypted_embedding.shape})")
        
        # Verify they match
        if np.allclose(original_embedding, decrypted_embedding, rtol=1e-6):
            print("✅ Embeddings match perfectly!")
            return True
        else:
            print("❌ Embeddings don't match")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


def test_wrong_password():
    """Test decryption with wrong password."""
    print("\n🧪 Testing wrong password protection...")
    
    # Create test data
    original_embedding = np.random.rand(256).astype(np.float32)
    correct_password = "correct_password"
    wrong_password = "wrong_password"
    
    try:
        # Encrypt with correct password
        encrypted_data = encrypt_embedding_with_password(original_embedding, correct_password)
        print("✅ Encryption with correct password successful")
        
        # Try to decrypt with wrong password
        try:
            decrypted_embedding = decrypt_embedding(encrypted_data, wrong_password)
            print("❌ Wrong password should have failed!")
            return False
        except Exception:
            print("✅ Wrong password correctly rejected")
            return True
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


def test_embedding_integrity():
    """Test embedding integrity verification."""
    print("\n🧪 Testing embedding integrity verification...")
    
    # Valid embedding
    valid_embedding = np.random.rand(512).astype(np.float32)
    if verify_embedding_integrity(valid_embedding):
        print("✅ Valid embedding correctly identified")
    else:
        print("❌ Valid embedding incorrectly rejected")
        return False
    
    # Invalid embeddings
    invalid_cases = [
        np.zeros(512),  # All zeros
        np.array([]),   # Empty array
        np.array([[1, 2], [3, 4]]),  # Wrong shape
        "not_an_array"  # Not an array
    ]
    
    for i, invalid_embedding in enumerate(invalid_cases):
        if not verify_embedding_integrity(invalid_embedding):
            print(f"✅ Invalid case {i+1} correctly rejected")
        else:
            print(f"❌ Invalid case {i+1} incorrectly accepted")
            return False
    
    return True


def test_secure_storage():
    """Test the SecureEmbeddingStorage class."""
    print("\n🧪 Testing SecureEmbeddingStorage...")
    
    # Create storage instance
    storage = SecureEmbeddingStorage("test_storage")
    
    # Test data
    user_id = "test_user"
    embedding = np.random.rand(512).astype(np.float32)
    password = "storage_test_password"
    
    try:
        # Save embedding
        filepath = storage.save_user_embedding(user_id, embedding, password)
        print(f"✅ Embedding saved to: {filepath}")
        
        # Check if user exists
        if storage.user_exists(user_id):
            print("✅ User existence check passed")
        else:
            print("❌ User existence check failed")
            return False
        
        # Load embedding
        loaded_embedding = storage.load_user_embedding(user_id, password)
        print("✅ Embedding loaded successfully")
        
        # Verify they match
        if np.allclose(embedding, loaded_embedding, rtol=1e-6):
            print("✅ Loaded embedding matches original")
            return True
        else:
            print("❌ Loaded embedding doesn't match")
            return False
            
    except Exception as e:
        print(f"❌ Secure storage test failed: {e}")
        return False


def test_performance():
    """Test encryption/decryption performance."""
    print("\n⏱️ Testing performance...")
    
    import time
    
    # Test with different embedding sizes
    sizes = [128, 256, 512, 1024, 2048]
    password = "performance_test"
    
    for size in sizes:
        embedding = np.random.rand(size).astype(np.float32)
        
        # Time encryption
        start_time = time.time()
        encrypted_data = encrypt_embedding_with_password(embedding, password)
        encrypt_time = time.time() - start_time
        
        # Time decryption
        start_time = time.time()
        decrypted_embedding = decrypt_embedding(encrypted_data, password)
        decrypt_time = time.time() - start_time
        
        print(f"📊 Size {size:4d}: Encrypt {encrypt_time*1000:.1f}ms, Decrypt {decrypt_time*1000:.1f}ms")
    
    return True


def main():
    """Run all tests."""
    print("🔐 FaceAuth Crypto Module Tests")
    print("=" * 50)
    
    print(SECURITY_NOTES)
    
    tests = [
        ("Basic Encryption/Decryption", test_basic_encryption),
        ("Wrong Password Protection", test_wrong_password),
        ("Embedding Integrity", test_embedding_integrity),
        ("Secure Storage", test_secure_storage),
        ("Performance", test_performance)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*60}")
        print(f"Running: {test_name}")
        print('='*60)
        
        try:
            result = test_func()
            results.append((test_name, result))
            
            if result:
                print(f"✅ {test_name} PASSED")
            else:
                print(f"❌ {test_name} FAILED")
                
        except Exception as e:
            print(f"💥 {test_name} ERROR: {e}")
            results.append((test_name, False))
    
    # Summary
    print(f"\n{'='*60}")
    print("TEST SUMMARY")
    print('='*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Crypto module is working correctly.")
        return True
    else:
        print(f"⚠️  {total - passed} tests failed. Please check the implementation.")
        return False


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n❌ Tests cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        sys.exit(1)
