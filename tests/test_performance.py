#!/usr/bin/env python3
"""
Performance and benchmarking test suite for FaceAuth platform.
Tests system performance, scalability, and resource usage under various conditions.
"""

import pytest
import time
import threading
import concurrent.futures
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch
import numpy as np
import statistics

# Optional performance monitoring dependencies
try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False
    print("Warning: psutil not available. Memory monitoring will be limited.")

try:
    import memory_profiler
    HAS_MEMORY_PROFILER = True
except ImportError:
    HAS_MEMORY_PROFILER = False
    print("Warning: memory_profiler not available. Advanced memory profiling disabled.")

from faceauth.core.enrollment import FaceEnrollment
from faceauth.core.authentication import FaceAuthenticator
from faceauth.security.encryption_manager import EncryptionManager
from faceauth.security.audit_logger import SecureAuditLogger
from faceauth.security.memory_manager import SecureMemoryManager
from faceauth.utils.storage import FaceDataStorage


class PerformanceTimer:
    """Context manager for measuring execution time."""
    
    def __init__(self):
        self.start_time = None
        self.end_time = None
        self.duration = None
    
    def __enter__(self):
        self.start_time = time.perf_counter()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = time.perf_counter()
        self.duration = self.end_time - self.start_time


class MemoryProfiler:
    """Context manager for measuring memory usage."""
    
    def __init__(self):
        self.start_memory = None
        self.end_memory = None
        self.peak_memory = None
        self.memory_delta = None
    
    def __enter__(self):
        if HAS_PSUTIL:
            self.start_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        else:
            self.start_memory = 0  # Fallback
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if HAS_PSUTIL:
            self.end_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
            self.memory_delta = self.end_memory - self.start_memory
        else:
            self.end_memory = 0
            self.memory_delta = 0


class TestEnrollmentPerformance:
    """Performance tests for face enrollment."""
    
    def test_single_user_enrollment_performance(self, temp_dir, mock_face_data):
        """Test performance of single user enrollment."""
        storage_dir = temp_dir / "storage"
        storage = FaceDataStorage(str(storage_dir))
        enrollment = FaceEnrollment(storage)
        
        user_id = "perf_test_user"
        
        with PerformanceTimer() as timer, \
             MemoryProfiler() as memory, \
             patch('cv2.VideoCapture'), \
             patch('faceauth.face_model.extract_face_encoding') as mock_extract:
            
            mock_extract.return_value = mock_face_data["encoding"]
            
            success = enrollment.enroll_user(
                user_id=user_id,
                min_samples=5,
                quality_threshold=0.8
            )
            
            assert success is True
        
        # Performance assertions
        assert timer.duration < 2.0  # Should complete within 2 seconds
        if HAS_PSUTIL:
            assert memory.memory_delta < 50  # Should use less than 50MB additional memory
        
        print(f"Enrollment time: {timer.duration:.3f}s")
        if HAS_PSUTIL:
            print(f"Memory usage: {memory.memory_delta:.1f}MB")
    
    def test_multiple_users_enrollment_performance(self, temp_dir, mock_face_data):
        """Test performance of enrolling multiple users."""
        storage_dir = temp_dir / "storage"
        storage = FaceDataStorage(str(storage_dir))
        enrollment = FaceEnrollment(storage)
        
        num_users = 50
        enrollment_times = []
        
        with MemoryProfiler() as memory:
            for i in range(num_users):
                user_id = f"user_{i:03d}"
                
                with PerformanceTimer() as timer, \
                     patch('cv2.VideoCapture'), \
                     patch('faceauth.face_model.extract_face_encoding') as mock_extract:
                    
                    # Generate unique encoding for each user
                    encoding = np.random.rand(128)
                    mock_extract.return_value = encoding
                    
                    success = enrollment.enroll_user(user_id, min_samples=3)
                    assert success is True
                
                enrollment_times.append(timer.duration)
        
        # Performance analysis
        avg_time = statistics.mean(enrollment_times)
        max_time = max(enrollment_times)
        min_time = min(enrollment_times)
        
        # Performance assertions
        assert avg_time < 1.0  # Average enrollment should be under 1 second
        assert max_time < 2.0  # No enrollment should take more than 2 seconds
        if HAS_PSUTIL:
            assert memory.memory_delta < 200  # Total memory usage should be reasonable
        
        print(f"Enrolled {num_users} users")
        print(f"Average time: {avg_time:.3f}s")
        print(f"Min time: {min_time:.3f}s")
        print(f"Max time: {max_time:.3f}s")
        if HAS_PSUTIL:
            print(f"Total memory: {memory.memory_delta:.1f}MB")
    
    def test_enrollment_scalability(self, temp_dir, mock_face_data):
        """Test enrollment scalability with increasing load."""
        storage_dir = temp_dir / "storage"
        storage = FaceDataStorage(str(storage_dir))
        enrollment = FaceEnrollment(storage)
        
        user_counts = [10, 25, 50, 100]
        results = {}
        
        for num_users in user_counts:
            print(f"Testing with {num_users} users...")
            
            with PerformanceTimer() as timer, \
                 MemoryProfiler() as memory:
                
                for i in range(num_users):
                    user_id = f"scale_user_{num_users}_{i:03d}"
                    
                    with patch('cv2.VideoCapture'), \
                         patch('faceauth.face_model.extract_face_encoding') as mock_extract:
                        
                        encoding = np.random.rand(128)
                        mock_extract.return_value = encoding
                        
                        success = enrollment.enroll_user(user_id, min_samples=3)
                        assert success is True
            
            results[num_users] = {
                'total_time': timer.duration,
                'avg_time_per_user': timer.duration / num_users,
                'memory_usage': memory.memory_delta if HAS_PSUTIL else 0
            }
        
        # Scalability analysis
        for num_users in user_counts:
            result = results[num_users]
            memory_info = f", {result['memory_usage']:.1f}MB" if HAS_PSUTIL else ""
            print(f"{num_users} users: {result['avg_time_per_user']:.3f}s/user{memory_info}")
            
            # Ensure performance doesn't degrade significantly with scale
            assert result['avg_time_per_user'] < 1.0
            if HAS_PSUTIL:
                assert result['memory_usage'] < num_users * 5  # Linear memory growth limit


class TestAuthenticationPerformance:
    """Performance tests for face authentication."""
    
    def test_single_authentication_performance(self, temp_dir, mock_face_data):
        """Test performance of single authentication."""
        storage_dir = temp_dir / "storage"
        storage = FaceDataStorage(str(storage_dir))
        enrollment = FaceEnrollment(storage)
        authenticator = FaceAuthenticator(storage)
        
        user_id = "auth_perf_user"
        
        # Enroll user first
        with patch('cv2.VideoCapture'), \
             patch('faceauth.face_model.extract_face_encoding') as mock_extract:
            
            mock_extract.return_value = mock_face_data["encoding"]
            enrollment.enroll_user(user_id, min_samples=3)
        
        # Test authentication performance
        with PerformanceTimer() as timer, \
             MemoryProfiler() as memory, \
             patch('cv2.VideoCapture'), \
             patch('faceauth.face_model.extract_face_encoding') as mock_extract:
            
            mock_extract.return_value = mock_face_data["encoding"]
            
            auth_result = authenticator.authenticate(confidence_threshold=0.8)
            
            assert auth_result["success"] is True
        
        # Performance assertions
        assert timer.duration < 0.5  # Authentication should be fast
        if HAS_PSUTIL:
            assert memory.memory_delta < 20  # Should use minimal additional memory
        
        print(f"Authentication time: {timer.duration:.3f}s")
        if HAS_PSUTIL:
            print(f"Memory usage: {memory.memory_delta:.1f}MB")
    
    def test_repeated_authentication_performance(self, temp_dir, mock_face_data):
        """Test performance of repeated authentications."""
        storage_dir = temp_dir / "storage"
        storage = FaceDataStorage(str(storage_dir))
        enrollment = FaceEnrollment(storage)
        authenticator = FaceAuthenticator(storage)
        
        user_id = "repeat_auth_user"
        
        # Enroll user
        with patch('cv2.VideoCapture'), \
             patch('faceauth.face_model.extract_face_encoding') as mock_extract:
            
            mock_extract.return_value = mock_face_data["encoding"]
            enrollment.enroll_user(user_id, min_samples=3)
        
        # Test repeated authentications
        num_auths = 100
        auth_times = []
        
        with MemoryProfiler() as memory:
            for i in range(num_auths):
                with PerformanceTimer() as timer, \
                     patch('cv2.VideoCapture'), \
                     patch('faceauth.face_model.extract_face_encoding') as mock_extract:
                    
                    mock_extract.return_value = mock_face_data["encoding"]
                    auth_result = authenticator.authenticate()
                    
                    assert auth_result["success"] is True
                
                auth_times.append(timer.duration)
        
        # Performance analysis
        avg_time = statistics.mean(auth_times)
        max_time = max(auth_times)
        min_time = min(auth_times)
        
        # Performance assertions
        assert avg_time < 0.5  # Average authentication should be fast
        assert max_time < 1.0  # No authentication should take too long
        if HAS_PSUTIL:
            assert memory.memory_delta < 50  # Memory should not grow significantly
        
        print(f"Performed {num_auths} authentications")
        print(f"Average time: {avg_time:.3f}s")
        print(f"Min time: {min_time:.3f}s")
        print(f"Max time: {max_time:.3f}s")
        if HAS_PSUTIL:
            print(f"Total memory: {memory.memory_delta:.1f}MB")
    
    def test_multi_user_authentication_performance(self, temp_dir, mock_face_data):
        """Test authentication performance with multiple enrolled users."""
        storage_dir = temp_dir / "storage"
        storage = FaceDataStorage(str(storage_dir))
        enrollment = FaceEnrollment(storage)
        authenticator = FaceAuthenticator(storage)
        
        # Enroll multiple users
        num_users = 50
        user_encodings = {}
        
        for i in range(num_users):
            user_id = f"multi_user_{i:03d}"
            encoding = np.random.rand(128)
            user_encodings[user_id] = encoding
            
            with patch('cv2.VideoCapture'), \
                 patch('faceauth.face_model.extract_face_encoding') as mock_extract:
                
                mock_extract.return_value = encoding
                enrollment.enroll_user(user_id, min_samples=3)
        
        # Test authentication performance with many users
        test_user_id = "multi_user_025"  # Middle user
        test_encoding = user_encodings[test_user_id]
        
        auth_times = []
        for i in range(20):
            with PerformanceTimer() as timer, \
                 patch('cv2.VideoCapture'), \
                 patch('faceauth.face_model.extract_face_encoding') as mock_extract:
                
                mock_extract.return_value = test_encoding
                auth_result = authenticator.authenticate()
                
                assert auth_result["success"] is True
                assert auth_result["user_id"] == test_user_id
            
            auth_times.append(timer.duration)
        
        avg_time = statistics.mean(auth_times)
        
        # Performance should not degrade significantly with more users
        assert avg_time < 1.0  # Should still be fast with 50 users
        
        print(f"Authentication with {num_users} enrolled users")
        print(f"Average time: {avg_time:.3f}s")


class TestEncryptionPerformance:
    """Performance tests for encryption operations."""
    
    def test_file_encryption_performance(self, temp_dir):
        """Test file encryption performance with various file sizes."""
        encryption_manager = EncryptionManager()
        
        file_sizes = [1024, 10240, 102400, 1048576]  # 1KB, 10KB, 100KB, 1MB
        results = {}
        
        for size in file_sizes:
            test_file = temp_dir / f"test_{size}.txt"
            encrypted_file = temp_dir / f"test_{size}.enc"
            decrypted_file = temp_dir / f"test_{size}_dec.txt"
            
            # Create test file
            test_data = b"A" * size
            test_file.write_bytes(test_data)
            
            password = "test_password_123"
            
            # Test encryption
            with PerformanceTimer() as enc_timer:
                encryption_manager.encrypt_file(str(test_file), str(encrypted_file), password)
            
            # Test decryption
            with PerformanceTimer() as dec_timer:
                encryption_manager.decrypt_file(str(encrypted_file), str(decrypted_file), password)
            
            # Verify correctness
            decrypted_data = decrypted_file.read_bytes()
            assert decrypted_data == test_data
            
            results[size] = {
                'encryption_time': enc_timer.duration,
                'decryption_time': dec_timer.duration,
                'encryption_speed': size / enc_timer.duration,  # bytes/second
                'decryption_speed': size / dec_timer.duration
            }
        
        # Performance analysis
        for size, result in results.items():
            size_mb = size / 1048576
            print(f"File size: {size_mb:.2f}MB")
            print(f"  Encryption: {result['encryption_time']:.3f}s ({result['encryption_speed']/1048576:.1f} MB/s)")
            print(f"  Decryption: {result['decryption_time']:.3f}s ({result['decryption_speed']/1048576:.1f} MB/s)")
            
            # Performance assertions
            assert result['encryption_speed'] > 1048576  # At least 1 MB/s
            assert result['decryption_speed'] > 1048576  # At least 1 MB/s
    
    def test_key_derivation_performance(self, temp_dir):
        """Test key derivation performance."""
        encryption_manager = EncryptionManager()
        
        passwords = ["short", "medium_length_password", "very_long_password_with_many_characters_123456789"]
        num_iterations = 10
        
        for password in passwords:
            derivation_times = []
            
            for i in range(num_iterations):
                with PerformanceTimer() as timer:
                    salt = encryption_manager._generate_salt()
                    key = encryption_manager._derive_key(password, salt)
                
                derivation_times.append(timer.duration)
            
            avg_time = statistics.mean(derivation_times)
            
            print(f"Password length {len(password)}: {avg_time:.3f}s average")
            
            # Key derivation should be reasonably fast but not too fast (security)
            assert 0.01 < avg_time < 2.0  # Between 10ms and 2s


class TestConcurrencyPerformance:
    """Performance tests for concurrent operations."""
    
    def test_concurrent_enrollments(self, temp_dir, mock_face_data):
        """Test performance of concurrent user enrollments."""
        storage_dir = temp_dir / "storage"
        storage = FaceDataStorage(str(storage_dir))
        
        num_threads = 5
        users_per_thread = 10
        
        def enroll_users(thread_id):
            enrollment = FaceEnrollment(storage)
            thread_times = []
            
            for i in range(users_per_thread):
                user_id = f"concurrent_user_{thread_id}_{i:03d}"
                
                with PerformanceTimer() as timer, \
                     patch('cv2.VideoCapture'), \
                     patch('faceauth.face_model.extract_face_encoding') as mock_extract:
                    
                    encoding = np.random.rand(128)
                    mock_extract.return_value = encoding
                    
                    success = enrollment.enroll_user(user_id, min_samples=3)
                    assert success is True
                
                thread_times.append(timer.duration)
            
            return thread_times
        
        # Run concurrent enrollments
        with PerformanceTimer() as total_timer:
            with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
                futures = [executor.submit(enroll_users, i) for i in range(num_threads)]
                results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        # Analyze results
        all_times = [time for thread_times in results for time in thread_times]
        avg_time = statistics.mean(all_times)
        total_users = num_threads * users_per_thread
        
        print(f"Concurrent enrollment of {total_users} users")
        print(f"Total time: {total_timer.duration:.3f}s")
        print(f"Average time per user: {avg_time:.3f}s")
        print(f"Throughput: {total_users / total_timer.duration:.1f} users/second")
        
        # Performance assertions
        assert avg_time < 2.0  # Individual enrollments should still be fast
        assert total_timer.duration < num_threads * users_per_thread * 0.5  # Concurrency benefit
    
    def test_concurrent_authentications(self, temp_dir, mock_face_data):
        """Test performance of concurrent authentications."""
        storage_dir = temp_dir / "storage"
        storage = FaceDataStorage(str(storage_dir))
        enrollment = FaceEnrollment(storage)
        
        # Enroll users first
        num_users = 10
        user_encodings = {}
        
        for i in range(num_users):
            user_id = f"concurrent_auth_user_{i:03d}"
            encoding = np.random.rand(128)
            user_encodings[user_id] = encoding
            
            with patch('cv2.VideoCapture'), \
                 patch('faceauth.face_model.extract_face_encoding') as mock_extract:
                
                mock_extract.return_value = encoding
                enrollment.enroll_user(user_id, min_samples=3)
        
        # Test concurrent authentications
        num_threads = 5
        auths_per_thread = 20
        
        def perform_authentications(thread_id):
            authenticator = FaceAuthenticator(storage)
            thread_times = []
            
            for i in range(auths_per_thread):
                user_id = f"concurrent_auth_user_{i % num_users:03d}"
                encoding = user_encodings[user_id]
                
                with PerformanceTimer() as timer, \
                     patch('cv2.VideoCapture'), \
                     patch('faceauth.face_model.extract_face_encoding') as mock_extract:
                    
                    mock_extract.return_value = encoding
                    auth_result = authenticator.authenticate()
                    
                    assert auth_result["success"] is True
                
                thread_times.append(timer.duration)
            
            return thread_times
        
        # Run concurrent authentications
        with PerformanceTimer() as total_timer:
            with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
                futures = [executor.submit(perform_authentications, i) for i in range(num_threads)]
                results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        # Analyze results
        all_times = [time for thread_times in results for time in thread_times]
        avg_time = statistics.mean(all_times)
        total_auths = num_threads * auths_per_thread
        
        print(f"Concurrent authentication: {total_auths} attempts")
        print(f"Total time: {total_timer.duration:.3f}s")
        print(f"Average time per auth: {avg_time:.3f}s")
        print(f"Throughput: {total_auths / total_timer.duration:.1f} auths/second")
        
        # Performance assertions
        assert avg_time < 1.0  # Individual auths should be fast
        assert total_auths / total_timer.duration > 10  # Good throughput


class TestMemoryUsage:
    """Tests for memory usage and memory leaks."""
    
    def test_memory_usage_during_enrollment(self, temp_dir, mock_face_data):
        """Test memory usage during enrollment process."""
        if not HAS_PSUTIL:
            pytest.skip("psutil not available for memory monitoring")
            
        storage_dir = temp_dir / "storage"
        storage = FaceDataStorage(str(storage_dir))
        enrollment = FaceEnrollment(storage)
        
        initial_memory = psutil.Process().memory_info().rss / 1024 / 1024
        memory_samples = [initial_memory]
        
        # Enroll multiple users and track memory
        for i in range(20):
            user_id = f"memory_test_user_{i:03d}"
            
            with patch('cv2.VideoCapture'), \
                 patch('faceauth.face_model.extract_face_encoding') as mock_extract:
                
                mock_extract.return_value = mock_face_data["encoding"]
                enrollment.enroll_user(user_id, min_samples=3)
            
            current_memory = psutil.Process().memory_info().rss / 1024 / 1024
            memory_samples.append(current_memory)
        
        final_memory = memory_samples[-1]
        memory_growth = final_memory - initial_memory
        
        print(f"Initial memory: {initial_memory:.1f}MB")
        print(f"Final memory: {final_memory:.1f}MB")
        print(f"Memory growth: {memory_growth:.1f}MB")
        
        # Memory should not grow excessively
        assert memory_growth < 100  # Less than 100MB growth for 20 users
        
        # Check for memory leaks (memory should stabilize)
        last_5_samples = memory_samples[-5:]
        memory_variance = statistics.variance(last_5_samples)
        assert memory_variance < 10  # Memory should be stable
    
    def test_memory_cleanup_after_operations(self, temp_dir, mock_face_data):
        """Test that memory is properly cleaned up after operations."""
        if not HAS_PSUTIL:
            pytest.skip("psutil not available for memory monitoring")
            
        storage_dir = temp_dir / "storage"
        
        initial_memory = psutil.Process().memory_info().rss / 1024 / 1024
        
        # Perform multiple enrollment/authentication cycles
        for cycle in range(5):
            storage = FaceDataStorage(str(storage_dir))
            enrollment = FaceEnrollment(storage)
            authenticator = FaceAuthenticator(storage)
            
            user_id = f"cleanup_test_user_{cycle}"
            
            # Enroll
            with patch('cv2.VideoCapture'), \
                 patch('faceauth.face_model.extract_face_encoding') as mock_extract:
                
                mock_extract.return_value = mock_face_data["encoding"]
                enrollment.enroll_user(user_id, min_samples=3)
            
            # Authenticate multiple times
            for i in range(10):
                with patch('cv2.VideoCapture'), \
                     patch('faceauth.face_model.extract_face_encoding') as mock_extract:
                    
                    mock_extract.return_value = mock_face_data["encoding"]
                    auth_result = authenticator.authenticate()
                    assert auth_result["success"] is True
            
            # Force cleanup
            del storage, enrollment, authenticator
        
        final_memory = psutil.Process().memory_info().rss / 1024 / 1024
        memory_growth = final_memory - initial_memory
        
        print(f"Memory growth after {5} cycles: {memory_growth:.1f}MB")
        
        # Memory growth should be minimal after cleanup
        assert memory_growth < 50  # Less than 50MB growth after cleanup


class TestStressTests:
    """Stress tests for system limits."""
    
    def test_large_scale_user_enrollment(self, temp_dir):
        """Test enrollment of a large number of users."""
        storage_dir = temp_dir / "storage"
        storage = FaceDataStorage(str(storage_dir))
        enrollment = FaceEnrollment(storage)
        
        num_users = 500  # Large number of users
        
        start_time = time.time()
        initial_memory = 0
        if HAS_PSUTIL:
            initial_memory = psutil.Process().memory_info().rss / 1024 / 1024
        
        for i in range(num_users):
            user_id = f"stress_user_{i:05d}"
            
            with patch('cv2.VideoCapture'), \
                 patch('faceauth.face_model.extract_face_encoding') as mock_extract:
                
                # Generate unique encoding for each user
                encoding = np.random.rand(128)
                mock_extract.return_value = encoding
                
                success = enrollment.enroll_user(user_id, min_samples=3)
                assert success is True
            
            # Progress reporting
            if (i + 1) % 100 == 0:
                elapsed = time.time() - start_time
                current_memory = 0
                if HAS_PSUTIL:
                    current_memory = psutil.Process().memory_info().rss / 1024 / 1024
                print(f"Enrolled {i + 1} users in {elapsed:.1f}s, Memory: {current_memory:.1f}MB")
        
        total_time = time.time() - start_time
        final_memory = 0
        if HAS_PSUTIL:
            final_memory = psutil.Process().memory_info().rss / 1024 / 1024
        memory_usage = final_memory - initial_memory
        
        print(f"Enrolled {num_users} users in {total_time:.1f}s")
        print(f"Average: {total_time / num_users:.3f}s per user")
        if HAS_PSUTIL:
            print(f"Memory usage: {memory_usage:.1f}MB")
        
        # Stress test assertions
        assert total_time < num_users * 2  # Should not take more than 2s per user
        if HAS_PSUTIL:
            assert memory_usage < num_users * 2  # Should not use more than 2MB per user
    
    def test_sustained_authentication_load(self, temp_dir, mock_face_data):
        """Test sustained authentication load over time."""
        storage_dir = temp_dir / "storage"
        storage = FaceDataStorage(str(storage_dir))
        enrollment = FaceEnrollment(storage)
        authenticator = FaceAuthenticator(storage)
        
        # Enroll a user
        user_id = "sustained_test_user"
        with patch('cv2.VideoCapture'), \
             patch('faceauth.face_model.extract_face_encoding') as mock_extract:
            
            mock_extract.return_value = mock_face_data["encoding"]
            enrollment.enroll_user(user_id, min_samples=3)
        
        # Sustained authentication load
        num_authentications = 1000
        start_time = time.time()
        auth_times = []
        
        for i in range(num_authentications):
            with patch('cv2.VideoCapture'), \
                 patch('faceauth.face_model.extract_face_encoding') as mock_extract:
                
                auth_start = time.perf_counter()
                mock_extract.return_value = mock_face_data["encoding"]
                auth_result = authenticator.authenticate()
                auth_end = time.perf_counter()
                
                assert auth_result["success"] is True
                auth_times.append(auth_end - auth_start)
            
            # Progress reporting
            if (i + 1) % 200 == 0:
                elapsed = time.time() - start_time
                avg_time = statistics.mean(auth_times[-200:])
                print(f"Completed {i + 1} auths in {elapsed:.1f}s, Recent avg: {avg_time:.3f}s")
        
        total_time = time.time() - start_time
        avg_auth_time = statistics.mean(auth_times)
        throughput = num_authentications / total_time
        
        print(f"Sustained load: {num_authentications} authentications")
        print(f"Total time: {total_time:.1f}s")
        print(f"Average auth time: {avg_auth_time:.3f}s")
        print(f"Throughput: {throughput:.1f} auths/second")
        
        # Performance should remain stable under sustained load
        assert avg_auth_time < 1.0  # Average should still be fast
        assert throughput > 50  # Should maintain good throughput


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short", "-s"])
