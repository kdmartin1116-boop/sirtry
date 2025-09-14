"""
VeroBrix Configuration Manager

Centralized configuration management system for VeroBrix.
Handles loading, validation, and access to configuration settings.
"""

import os
import yaml
import logging
from typing import Dict, Any, Optional, Union
from pathlib import Path

class ConfigurationError(Exception):
    """Custom exception for configuration-related errors."""
    pass

class ConfigManager:
    """
    Centralized configuration manager for VeroBrix system.
    
    This class handles loading configuration from YAML files,
    environment variable overrides, and provides type-safe access
    to configuration values.
    """
    
    _instance: Optional['ConfigManager'] = None
    _config: Dict[str, Any] = {}
    _config_file_path: Optional[str] = None
    
    def __new__(cls) -> 'ConfigManager':
        """Singleton pattern implementation."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize the configuration manager."""
        if not hasattr(self, '_initialized'):
            self._initialized = True
            self._load_default_config()
    
    def load_config(self, config_path: str) -> None:
        """
        Load configuration from a YAML file.
        
        Args:
            config_path: Path to the configuration YAML file
            
        Raises:
            ConfigurationError: If the configuration file cannot be loaded or is invalid
        """
        try:
            config_file = Path(config_path)
            if not config_file.exists():
                raise ConfigurationError(f"Configuration file not found: {config_path}")
            
            with open(config_file, 'r', encoding='utf-8') as f:
                self._config = yaml.safe_load(f) or {}
            
            self._config_file_path = config_path
            self._apply_environment_overrides()
            self._validate_config()
            
            logging.info(f"Configuration loaded successfully from {config_path}")
            
        except yaml.YAMLError as e:
            raise ConfigurationError(f"Invalid YAML in configuration file: {e}")
        except Exception as e:
            raise ConfigurationError(f"Error loading configuration: {e}")
    
    def _load_default_config(self) -> None:
        """Load the default configuration file."""
        default_config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'verobrix.yaml')
        if os.path.exists(default_config_path):
            self.load_config(default_config_path)
        else:
            # Fallback to minimal default configuration
            self._config = self._get_minimal_config()
            logging.warning("Default configuration file not found, using minimal configuration")
    
    def _get_minimal_config(self) -> Dict[str, Any]:
        """Get minimal default configuration when config file is not available."""
        return {
            'analysis': {
                'max_document_size': '10MB',
                'timeout_seconds': 300,
                'enable_ml_features': False,
                'enable_advanced_nlp': True,
                'confidence_threshold': 0.7
            },
            'logging': {
                'level': 'INFO',
                'file': 'logs/verobrix.log',
                'console_output': True,
                'file_output': True
            },
            'templates': {
                'directory': 'templates/',
                'auto_reload': True
            },
            'document_generation': {
                'output_directory': 'output/',
                'default_format': 'txt'
            }
        }
    
    def _apply_environment_overrides(self) -> None:
        """Apply environment variable overrides to configuration."""
        env_mappings = {
            'VEROBRIX_LOG_LEVEL': ['logging', 'level'],
            'VEROBRIX_LOG_FILE': ['logging', 'file'],
            'VEROBRIX_DB_PATH': ['database', 'path'],
            'VEROBRIX_TIMEOUT': ['analysis', 'timeout_seconds'],
            'VEROBRIX_DEBUG': ['development', 'debug_mode']
        }
        
        for env_var, config_path in env_mappings.items():
            env_value = os.getenv(env_var)
            if env_value is not None:
                self._set_nested_value(self._config, config_path, self._convert_env_value(env_value))
    
    def _convert_env_value(self, value: str) -> Union[str, int, float, bool]:
        """Convert environment variable string to appropriate type."""
        # Boolean conversion
        if value.lower() in ('true', 'false'):
            return value.lower() == 'true'
        
        # Integer conversion
        try:
            return int(value)
        except ValueError:
            pass
        
        # Float conversion
        try:
            return float(value)
        except ValueError:
            pass
        
        # Return as string
        return value
    
    def _set_nested_value(self, config: Dict[str, Any], path: list, value: Any) -> None:
        """Set a nested configuration value using a path list."""
        current = config
        for key in path[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        current[path[-1]] = value
    
    def _validate_config(self) -> None:
        """Validate the loaded configuration."""
        required_sections = ['analysis', 'logging', 'templates', 'document_generation']
        
        for section in required_sections:
            if section not in self._config:
                raise ConfigurationError(f"Required configuration section missing: {section}")
        
        # Validate specific settings
        if not isinstance(self._config['analysis'].get('timeout_seconds'), int):
            raise ConfigurationError("analysis.timeout_seconds must be an integer")
        
        if self._config['analysis']['timeout_seconds'] <= 0:
            raise ConfigurationError("analysis.timeout_seconds must be positive")
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value using dot notation.
        
        Args:
            key: Configuration key in dot notation (e.g., 'analysis.timeout_seconds')
            default: Default value if key is not found
            
        Returns:
            Configuration value or default
        """
        keys = key.split('.')
        current = self._config
        
        try:
            for k in keys:
                current = current[k]
            return current
        except (KeyError, TypeError):
            return default
    
    def get_section(self, section: str) -> Dict[str, Any]:
        """
        Get an entire configuration section.
        
        Args:
            section: Section name
            
        Returns:
            Dictionary containing the section configuration
        """
        return self._config.get(section, {})
    
    def set(self, key: str, value: Any) -> None:
        """
        Set a configuration value using dot notation.
        
        Args:
            key: Configuration key in dot notation
            value: Value to set
        """
        keys = key.split('.')
        self._set_nested_value(self._config, keys, value)
    
    def is_enabled(self, feature: str) -> bool:
        """
        Check if a feature is enabled.
        
        Args:
            feature: Feature key in dot notation
            
        Returns:
            True if feature is enabled, False otherwise
        """
        return bool(self.get(feature, False))
    
    def get_log_level(self) -> str:
        """Get the configured logging level."""
        return self.get('logging.level', 'INFO').upper()
    
    def get_log_file(self) -> str:
        """Get the configured log file path."""
        return self.get('logging.file', 'logs/verobrix.log')
    
    def get_output_directory(self) -> str:
        """Get the configured output directory."""
        return self.get('document_generation.output_directory', 'output/')
    
    def get_templates_directory(self) -> str:
        """Get the configured templates directory."""
        return self.get('templates.directory', 'templates/')
    
    def get_database_path(self) -> str:
        """Get the configured database path."""
        return self.get('database.path', 'data/verobrix.db')
    
    def get_analysis_timeout(self) -> int:
        """Get the configured analysis timeout in seconds."""
        return self.get('analysis.timeout_seconds', 300)
    
    def get_max_document_size(self) -> str:
        """Get the configured maximum document size."""
        return self.get('analysis.max_document_size', '10MB')
    
    def is_debug_mode(self) -> bool:
        """Check if debug mode is enabled."""
        return self.is_enabled('development.debug_mode')
    
    def is_test_mode(self) -> bool:
        """Check if test mode is enabled."""
        return self.is_enabled('development.test_mode')
    
    def reload_config(self) -> None:
        """Reload configuration from the file."""
        if self._config_file_path:
            self.load_config(self._config_file_path)
        else:
            self._load_default_config()
    
    def get_all_config(self) -> Dict[str, Any]:
        """Get the complete configuration dictionary."""
        return self._config.copy()
    
    def __str__(self) -> str:
        """String representation of the configuration."""
        return f"ConfigManager(config_file='{self._config_file_path}', sections={list(self._config.keys())})"
    
    def __repr__(self) -> str:
        """Detailed string representation."""
        return self.__str__()

# Global configuration instance
config = ConfigManager()

# Convenience functions for common operations
def get_config(key: str, default: Any = None) -> Any:
    """Get a configuration value."""
    return config.get(key, default)

def is_feature_enabled(feature: str) -> bool:
    """Check if a feature is enabled."""
    return config.is_enabled(feature)

def get_log_level() -> str:
    """Get the logging level."""
    return config.get_log_level()

def get_output_dir() -> str:
    """Get the output directory."""
    return config.get_output_directory()

def reload_config() -> None:
    """Reload the configuration."""
    config.reload_config()
