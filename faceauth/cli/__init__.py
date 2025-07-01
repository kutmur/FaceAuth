"""
FaceAuth CLI package.

This package contains CLI-related modules for configuration management,
shell completion, and other command-line utilities.
"""

from .config import config_commands
from .completion import completion_commands

__all__ = ['config_commands', 'completion_commands']
