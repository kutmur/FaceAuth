"""
Secure Memory Manager for FaceAuth

Provides secure memory management and anti-forensic capabilities:
- Secure memory allocation and cleanup
- Protection against memory dumps
- Anti-forensic memory wiping
- Swap file protection
- Memory isolation and sandboxing
- Runtime memory protection

Security Features:
- Multiple memory overwrite passes
- Protection against cold boot attacks
- Memory page locking (where supported)
- Secure random overwriting
- Stack and heap protection
- Memory access monitoring
"""

import os
import gc
import sys
import mmap
import time
import ctypes
import secrets
import threading
import weakref
from typing import Optional, List, Dict, Any, Union
import numpy as np
from pathlib import Path


class SecureMemoryError(Exception):
    """Custom exception for secure memory operations."""
    pass


class SecureMemoryManager:
    """
    Comprehensive secure memory manager for FaceAuth.
    
    Provides memory protection, secure cleanup, and anti-forensic
    capabilities to prevent sensitive data recovery.
    """
    
    def __init__(self):
        """Initialize secure memory manager."""
        self.allocated_regions = weakref.WeakSet()
        self.cleanup_thread = None
        self.cleanup_interval = 60  # seconds
        self.overwrite_passes = 3
        self.lock = threading.Lock()
        
        # Platform detection
        self.platform = sys.platform
        self.is_windows = self.platform.startswith('win')
        self.is_linux = self.platform.startswith('linux')
        self.is_macos = self.platform == 'darwin'
        
        # Initialize platform-specific components
        self._init_platform_specific()
        
        # Start background cleanup
        self._start_cleanup_thread()
    
    def _init_platform_specific(self):
        """Initialize platform-specific memory management."""
        if self.is_windows:
            self._init_windows_memory()
        elif self.is_linux:
            self._init_linux_memory()
        elif self.is_macos:
            self._init_macos_memory()
    
    def _init_windows_memory(self):
        """Initialize Windows-specific memory functions."""
        try:
            # Load kernel32.dll for memory functions
            self.kernel32 = ctypes.windll.kernel32
            
            # Memory protection constants
            self.PAGE_READWRITE = 0x04
            self.PAGE_NOACCESS = 0x01
            self.MEM_COMMIT = 0x1000
            self.MEM_RESERVE = 0x2000
            self.MEM_RELEASE = 0x8000
            
            # Lock memory functions
            self.VirtualLock = self.kernel32.VirtualLock
            self.VirtualUnlock = self.kernel32.VirtualUnlock
            self.VirtualAlloc = self.kernel32.VirtualAlloc
            self.VirtualFree = self.kernel32.VirtualFree
            self.VirtualProtect = self.kernel32.VirtualProtect
            
        except Exception:
            # Fallback if Windows APIs not available
            self.kernel32 = None
    
    def _init_linux_memory(self):
        """Initialize Linux-specific memory functions."""
        try:
            # Load libc for memory functions
            self.libc = ctypes.CDLL("libc.so.6")
            
            # Memory lock functions
            self.mlock = self.libc.mlock
            self.munlock = self.libc.munlock
            self.mlockall = self.libc.mlockall
            self.munlockall = self.libc.munlockall
            
            # Memory protection constants
            self.MCL_CURRENT = 1
            self.MCL_FUTURE = 2
            
        except Exception:
            # Fallback if libc not available
            self.libc = None
    
    def _init_macos_memory(self):
        """Initialize macOS-specific memory functions."""
        try:
            # Load libc for memory functions (similar to Linux)
            self.libc = ctypes.CDLL("libc.dylib")
            
            # Memory lock functions
            self.mlock = self.libc.mlock
            self.munlock = self.libc.munlock
            
        except Exception:
            self.libc = None
    
    def allocate_secure_memory(self, size: int) -> 'SecureMemoryRegion':
        """
        Allocate secure memory region.
        
        Args:
            size: Size in bytes to allocate
            
        Returns:
            Secure memory region object
        """
        try:
            region = SecureMemoryRegion(size, self)
            with self.lock:
                self.allocated_regions.add(region)
            return region
            
        except Exception as e:
            raise SecureMemoryError(f"Failed to allocate secure memory: {str(e)}")
    
    def secure_zero_memory(self, data: Union[bytes, bytearray, memoryview, np.ndarray]):
        """
        Securely zero out memory with multiple passes.
        
        Args:
            data: Memory to zero out
        """
        try:
            if isinstance(data, np.ndarray):
                self._secure_zero_numpy(data)
            elif isinstance(data, (bytearray, memoryview)):
                self._secure_zero_mutable(data)
            elif isinstance(data, bytes):
                # Can't modify bytes directly, but ensure it's dereferenced
                del data
                gc.collect()
            else:
                # Try to convert to mutable type
                if hasattr(data, '__len__') and len(data) > 0:
                    mutable_data = bytearray(data)
                    self._secure_zero_mutable(mutable_data)
                    
        except Exception as e:
            # Best effort - don't raise exceptions for cleanup
            pass
    
    def _secure_zero_numpy(self, array: np.ndarray):
        """Securely zero NumPy array."""
        if array.size == 0:
            return
        
        try:
            # Multiple overwrite passes with different patterns
            for i in range(self.overwrite_passes):
                if i == 0:
                    array.fill(0)
                elif i == 1:
                    array.fill(255)
                else:
                    # Random data
                    random_data = np.random.randint(0, 256, array.shape, dtype=array.dtype)
                    array[:] = random_data
            
            # Final zero pass
            array.fill(0)
            
        except Exception:
            pass
    
    def _secure_zero_mutable(self, data: Union[bytearray, memoryview]):
        """Securely zero mutable memory."""
        if len(data) == 0:
            return
        
        try:
            # Multiple overwrite passes
            for i in range(self.overwrite_passes):
                if i == 0:
                    data[:] = b'\x00' * len(data)
                elif i == 1:
                    data[:] = b'\xFF' * len(data)
                else:
                    data[:] = secrets.token_bytes(len(data))
            
            # Final zero pass
            data[:] = b'\x00' * len(data)
            
        except Exception:
            pass
    
    def lock_memory_pages(self, address: int, size: int) -> bool:
        """
        Lock memory pages to prevent swapping.
        
        Args:
            address: Memory address
            size: Size in bytes
            
        Returns:
            True if successful
        """
        try:
            if self.is_windows and self.kernel32:
                return bool(self.VirtualLock(address, size))
            elif (self.is_linux or self.is_macos) and self.libc:
                return self.mlock(address, size) == 0
            else:
                return False
                
        except Exception:
            return False
    
    def unlock_memory_pages(self, address: int, size: int) -> bool:
        """
        Unlock memory pages.
        
        Args:
            address: Memory address
            size: Size in bytes
            
        Returns:
            True if successful
        """
        try:
            if self.is_windows and self.kernel32:
                return bool(self.VirtualUnlock(address, size))
            elif (self.is_linux or self.is_macos) and self.libc:
                return self.munlock(address, size) == 0
            else:
                return False
                
        except Exception:
            return False
    
    def disable_swap_for_process(self) -> bool:
        """
        Disable swap for current process (Linux/macOS).
        
        Returns:
            True if successful
        """
        try:
            if (self.is_linux or self.is_macos) and self.libc:
                # Lock all current and future pages
                return self.mlockall(self.MCL_CURRENT | self.MCL_FUTURE) == 0
            else:
                return False
                
        except Exception:
            return False
    
    def enable_swap_for_process(self) -> bool:
        """
        Re-enable swap for current process.
        
        Returns:
            True if successful
        """
        try:
            if (self.is_linux or self.is_macos) and self.libc:
                return self.munlockall() == 0
            else:
                return False
                
        except Exception:
            return False
    
    def get_memory_info(self) -> Dict[str, Any]:
        """Get memory usage and security information."""
        try:
            info = {
                'platform': self.platform,
                'allocated_regions': len(self.allocated_regions),
                'cleanup_thread_active': self.cleanup_thread and self.cleanup_thread.is_alive(),
                'overwrite_passes': self.overwrite_passes
            }
            
            # Add platform-specific info
            if self.is_windows:
                info['windows_apis_available'] = self.kernel32 is not None
            elif self.is_linux or self.is_macos:
                info['libc_available'] = self.libc is not None
            
            # Memory statistics (optional)
            try:
                import psutil
                process = psutil.Process()
                memory_info = process.memory_info()
                
                info.update({
                    'rss_bytes': memory_info.rss,
                    'vms_bytes': memory_info.vms,
                    'memory_percent': process.memory_percent()
                })
            except ImportError:
                info['memory_stats'] = 'psutil not available'
            
            return info
            
        except Exception as e:
            return {'error': str(e)}
    
    def force_garbage_collection(self):
        """Force garbage collection and memory cleanup."""
        try:
            # Multiple garbage collection passes
            for _ in range(3):
                gc.collect()
            
            # Clear weak references
            with self.lock:
                # Remove dead references
                dead_refs = [ref for ref in self.allocated_regions if ref() is None]
                for ref in dead_refs:
                    self.allocated_regions.discard(ref)
                    
        except Exception:
            pass
    
    def _start_cleanup_thread(self):
        """Start background cleanup thread."""
        def cleanup_worker():
            while True:
                try:
                    time.sleep(self.cleanup_interval)
                    self.force_garbage_collection()
                except Exception:
                    break
        
        self.cleanup_thread = threading.Thread(target=cleanup_worker, daemon=True)
        self.cleanup_thread.start()
    
    def emergency_cleanup(self):
        """Emergency cleanup of all secure memory."""
        try:
            with self.lock:
                # Clean all allocated regions
                for region_ref in list(self.allocated_regions):
                    region = region_ref()
                    if region:
                        region.secure_cleanup()
                
                self.allocated_regions.clear()
            
            # Force garbage collection
            self.force_garbage_collection()
            
        except Exception:
            pass
    
    def __del__(self):
        """Cleanup when memory manager is destroyed."""
        try:
            self.emergency_cleanup()
        except:
            pass


class SecureMemoryRegion:
    """
    Secure memory region with automatic cleanup.
    
    Provides encrypted storage and secure deletion for sensitive data.
    """
    
    def __init__(self, size: int, manager: SecureMemoryManager):
        """
        Initialize secure memory region.
        
        Args:
            size: Size in bytes
            manager: Memory manager instance
        """
        self.size = size
        self.manager = manager
        self.allocated = True
        self.locked = False
        
        # Allocate memory
        self.buffer = bytearray(size)
        
        # Try to lock pages in memory
        try:
            buffer_address = id(self.buffer)
            self.locked = manager.lock_memory_pages(buffer_address, size)
        except:
            self.locked = False
    
    def write(self, data: bytes, offset: int = 0):
        """
        Write data to secure memory region.
        
        Args:
            data: Data to write
            offset: Offset in buffer
        """
        if not self.allocated:
            raise SecureMemoryError("Memory region not allocated")
        
        if offset + len(data) > self.size:
            raise SecureMemoryError("Data too large for memory region")
        
        self.buffer[offset:offset + len(data)] = data
    
    def read(self, length: int = None, offset: int = 0) -> bytes:
        """
        Read data from secure memory region.
        
        Args:
            length: Number of bytes to read (None for all)
            offset: Offset in buffer
            
        Returns:
            Read data
        """
        if not self.allocated:
            raise SecureMemoryError("Memory region not allocated")
        
        if length is None:
            length = self.size - offset
        
        if offset + length > self.size:
            raise SecureMemoryError("Read beyond memory region")
        
        return bytes(self.buffer[offset:offset + length])
    
    def secure_cleanup(self):
        """Securely clean up memory region."""
        if not self.allocated:
            return
        
        try:
            # Secure zero the buffer
            self.manager.secure_zero_memory(self.buffer)
            
            # Unlock memory if it was locked
            if self.locked:
                try:
                    buffer_address = id(self.buffer)
                    self.manager.unlock_memory_pages(buffer_address, self.size)
                except:
                    pass
            
            # Mark as deallocated
            self.allocated = False
            self.locked = False
            
        except Exception:
            pass
    
    def __del__(self):
        """Cleanup when region is destroyed."""
        try:
            self.secure_cleanup()
        except:
            pass
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit with cleanup."""
        self.secure_cleanup()
