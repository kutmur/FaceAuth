#!/usr/bin/env python3
"""
FaceAuth Configuration Management
Handles user preferences and system settings.
"""

import os
import json
import configparser
from pathlib import Path
from typing import Dict, Any, Optional
import click


class ConfigManager:
    """Manages FaceAuth configuration settings."""
    
    def __init__(self):
        """Initialize configuration manager."""
        self.config_dir = Path.home() / '.faceauth'
        self.config_file = self.config_dir / 'config.ini'
        self.defaults = {
            'general': {
                'storage_dir': str(self.config_dir / 'data'),
                'log_level': 'INFO',
                'quiet_mode': 'false',
                'auto_backup': 'true'
            },
            'authentication': {
                'timeout': '10',
                'max_attempts': '5',
                'similarity_threshold': '0.6',
                'device': 'auto'
            },
            'encryption': {
                'kdf_method': 'argon2',
                'chunk_size': '1048576',
                'overwrite_existing': 'false'
            },
            'enrollment': {
                'timeout': '30',
                'quality_threshold': '0.7',
                'min_samples': '5'
            }
        }
        self._ensure_config_exists()
        
    def _ensure_config_exists(self):
        """Ensure configuration directory and file exist."""
        self.config_dir.mkdir(exist_ok=True)
        
        if not self.config_file.exists():
            self._create_default_config()
    
    def _create_default_config(self):
        """Create default configuration file."""
        config = configparser.ConfigParser()
        
        for section, settings in self.defaults.items():
            config[section] = settings
        
        with open(self.config_file, 'w') as f:
            config.write(f)
    
    def get(self, section: str, key: str, fallback: str = None) -> str:
        """Get configuration value."""
        config = configparser.ConfigParser()
        config.read(self.config_file)
        
        try:
            return config.get(section, key)
        except (configparser.NoSectionError, configparser.NoOptionError):
            if fallback is not None:
                return fallback
            return self.defaults.get(section, {}).get(key, '')
    
    def set(self, section: str, key: str, value: str):
        """Set configuration value."""
        config = configparser.ConfigParser()
        config.read(self.config_file)
        
        if not config.has_section(section):
            config.add_section(section)
        
        config.set(section, key, str(value))
        
        with open(self.config_file, 'w') as f:
            config.write(f)
    
    def get_all(self) -> Dict[str, Dict[str, str]]:
        """Get all configuration values."""
        config = configparser.ConfigParser()
        config.read(self.config_file)
        
        result = {}
        for section in config.sections():
            result[section] = dict(config.items(section))
        
        return result
    
    def reset_to_defaults(self):
        """Reset configuration to defaults."""
        self._create_default_config()
    
    def get_storage_dir(self) -> str:
        """Get configured storage directory."""
        return self.get('general', 'storage_dir')
    
    def get_log_level(self) -> str:
        """Get configured log level."""
        return self.get('general', 'log_level')
    
    def is_quiet_mode(self) -> bool:
        """Check if quiet mode is enabled."""
        return self.get('general', 'quiet_mode').lower() == 'true'
    
    def get_auth_timeout(self) -> int:
        """Get authentication timeout."""
        return int(self.get('authentication', 'timeout', '10'))
    
    def get_similarity_threshold(self) -> float:
        """Get similarity threshold."""
        return float(self.get('authentication', 'similarity_threshold', '0.6'))


# Global configuration instance
config = ConfigManager()


@click.group()
def config_commands():
    """Configuration management commands."""
    pass


@config_commands.command('config-show')
def show_config():
    """Display current configuration settings."""
    click.echo("🔧 FaceAuth Configuration")
    click.echo("=" * 30)
    
    all_config = config.get_all()
    
    for section, settings in all_config.items():
        click.echo(f"\n[{section.upper()}]")
        for key, value in settings.items():
            click.echo(f"  {key}: {value}")
    
    click.echo(f"\nConfiguration file: {config.config_file}")


@config_commands.command('config-set')
@click.argument('section')
@click.argument('key')
@click.argument('value')
def set_config(section: str, key: str, value: str):
    """Set a configuration value."""
    try:
        config.set(section, key, value)
        click.echo(f"✅ Set {section}.{key} = {value}")
    except Exception as e:
        click.echo(f"❌ Error setting configuration: {e}", err=True)
        sys.exit(1)


@config_commands.command('config-reset')
@click.confirmation_option(prompt='Reset all configuration to defaults?')
def reset_config():
    """Reset configuration to default values."""
    try:
        config.reset_to_defaults()
        click.echo("✅ Configuration reset to defaults")
    except Exception as e:
        click.echo(f"❌ Error resetting configuration: {e}", err=True)
        sys.exit(1)


@config_commands.command('config-init')
def init_config():
    """Initialize FaceAuth configuration directory."""
    try:
        config._ensure_config_exists()
        
        # Create data directory
        data_dir = Path(config.get_storage_dir())
        data_dir.mkdir(parents=True, exist_ok=True)
        
        # Create logs directory
        logs_dir = config.config_dir / 'logs'
        logs_dir.mkdir(exist_ok=True)
        
        click.echo("✅ FaceAuth configuration initialized")
        click.echo(f"   Config dir: {config.config_dir}")
        click.echo(f"   Data dir: {data_dir}")
        click.echo(f"   Logs dir: {logs_dir}")
        
    except Exception as e:
        click.echo(f"❌ Error initializing configuration: {e}", err=True)
        sys.exit(1)


if __name__ == '__main__':
    config_commands()
