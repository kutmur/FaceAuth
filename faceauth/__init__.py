"""
FaceAuth - Local Face Authentication System
===========================================

A secure, privacy-first face authentication system that runs entirely locally.
No cloud dependencies, no data sharing, complete privacy control.

Core Components:
- enrollment: Face enrollment and embedding generation
- authentication: Face verification and authentication
- crypto: Cryptographic operations for secure storage
- file_handler: File encryption/decryption with face authentication
- gui: Graphical user interface components

Author: FaceAuth Development Team
License: See LICENSE file
"""

__version__ = "1.0.0"
__author__ = "FaceAuth Development Team"

# Import key classes and functions for easy access
from .enrollment import FaceEnroller, FaceEnrollmentError, enroll_new_user
from .authentication import FaceAuthenticator, FaceAuthenticationError
from .crypto import SecureEmbeddingStorage, CryptoError
from .file_handler import encrypt_file, decrypt_file, FileEncryptionError
from .gui import FaceAuthGUI

# Define what gets imported with "from faceauth import *"
__all__ = [
    # Classes
    'FaceEnroller',
    'FaceAuthenticator', 
    'SecureEmbeddingStorage',
    'FaceAuthGUI',
    
    # Functions
    'enroll_new_user',
    'encrypt_file',
    'decrypt_file',
    
    # Exceptions
    'FaceEnrollmentError',
    'FaceAuthenticationError',
    'CryptoError',
    'FileEncryptionError',
]
