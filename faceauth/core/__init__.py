"""
Core modules for FaceAuth face recognition system.
"""

from .enrollment import FaceEnrollmentManager, FaceEnrollmentError
from .authentication import FaceAuthenticator  # For future implementation

__all__ = [
    'FaceEnrollmentManager',
    'FaceEnrollmentError',
    'FaceAuthenticator'
]