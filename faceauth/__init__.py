"""
FaceAuth - Local Face Authentication System

A privacy-first face authentication platform that keeps all face data local.
No cloud dependencies, no third-party services.
"""

__version__ = "1.0.0"
__author__ = "FaceAuth Team"

from .core.enrollment import FaceEnrollmentManager, FaceEnrollmentError
from .utils.security import SecurityManager
from .utils.storage import FaceDataStorage

__all__ = [
    'FaceEnrollmentManager',
    'FaceEnrollmentError', 
    'SecurityManager',
    'FaceDataStorage'
]