"""
Unit tests for the VeroBrix Configuration Manager.
"""

import pytest
import tempfile
import os
import yaml
from unittest.mock import patch, mock_open

from modules.config_manager import ConfigManager, ConfigurationError, get_config, is_feature_enabled


class TestConfigManager:
    """Test cases for ConfigManager class."""
    
    def setup_method(self):
        """Setup for each test method."""
        # Reset singleton instance for each test
        ConfigManager._instance = None
        ConfigManager._config = {}
        ConfigManager._config_file_path = None
    
    def test_singleton_pattern(self):
        """Test that ConfigManager follows singleton pattern."""
        config1 = ConfigManager()
        config2 = ConfigManager()
        assert config1 is config2
    
    def test_minimal_config_fallback(self):
        """Test fallback to minimal configuration when no config file exists."""
        with patch('os.path.exists', return_value=False):
            config = ConfigManager()
            assert config.get('analysis.timeout_seconds') == 300
            assert config.get('logging.level') == 'INFO'
    
    def test_load_valid_config(self):
        """Test loading a valid configuration file."""
        test_config = {
            'analysis': {'timeout_seconds': 600},
            'logging': {'level': 'DEBUG'},
            'templates': {'directory': 'test_templates/'},
            'document_generation': {'output_directory': 'test_output/'}
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(test_config, f)
            config_path = f.name
        
        try:
            config = ConfigManager()
            config.load_config(config_path)
            
            assert config.get('analysis.timeout_seconds') == 600
            assert config.get('logging.level') == 'DEBUG'
        finally:
            os.unlink(config_path)
    
    def test_load_nonexistent_config(self):
        """Test loading a non-existent configuration file."""
        config = ConfigManager()
        
        with pytest.raises(ConfigurationError, match="Configuration file not found"):
            config.load_config('/nonexistent/path/config.yaml')
    
    def test_load_invalid_yaml(self):
        """Test loading an invalid YAML file."""
        invalid_yaml = "invalid: yaml: content: ["
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(invalid_yaml)
            config_path = f.name
        
        try:
            config = ConfigManager()
            with pytest.raises(ConfigurationError, match="Invalid YAML"):
                config.load_config(config_path)
        finally:
            os.unlink(config_path)
    
    def test_environment_overrides(self):
        """Test environment variable overrides."""
        test_config = {
            'analysis': {'timeout_seconds': 300},
            'logging': {'level': 'INFO', 'file': 'logs/test.log'},
            'templates': {'directory': 'templates/'},
            'document_generation': {'output_directory': 'output/'}
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(test_config, f)
            config_path = f.name
        
        try:
            with patch.dict(os.environ, {
                'VEROBRIX_LOG_LEVEL': 'DEBUG',
                'VEROBRIX_TIMEOUT': '600'
            }):
                config = ConfigManager()
                config.load_config(config_path)
                
                assert config.get('logging.level') == 'DEBUG'
                assert config.get('analysis.timeout_seconds') == 600
        finally:
            os.unlink(config_path)
    
    def test_get_with_dot_notation(self):
        """Test getting configuration values with dot notation."""
        config = ConfigManager()
        config._config = {
            'section': {
                'subsection': {
                    'value': 'test_value'
                }
            }
        }
        
        assert config.get('section.subsection.value') == 'test_value'
        assert config.get('section.nonexistent', 'default') == 'default'
        assert config.get('nonexistent.key') is None
    
    def test_set_with_dot_notation(self):
        """Test setting configuration values with dot notation."""
        config = ConfigManager()
        config.set('new.section.value', 'test_value')
        
        assert config.get('new.section.value') == 'test_value'
    
    def test_is_enabled(self):
        """Test feature enablement checking."""
        config = ConfigManager()
        config._config = {
            'features': {
                'enabled_feature': True,
                'disabled_feature': False,
                'string_feature': 'yes'
            }
        }
        
        assert config.is_enabled('features.enabled_feature') is True
        assert config.is_enabled('features.disabled_feature') is False
        assert config.is_enabled('features.string_feature') is True
        assert config.is_enabled('features.nonexistent') is False
    
    def test_get_section(self):
        """Test getting entire configuration sections."""
        config = ConfigManager()
        config._config = {
            'test_section': {
                'key1': 'value1',
                'key2': 'value2'
            }
        }
        
        section = config.get_section('test_section')
        assert section == {'key1': 'value1', 'key2': 'value2'}
        
        empty_section = config.get_section('nonexistent')
        assert empty_section == {}
    
    def test_convenience_methods(self):
        """Test convenience methods for common configuration values."""
        config = ConfigManager()
        config._config = {
            'logging': {'level': 'WARNING', 'file': 'custom.log'},
            'document_generation': {'output_directory': 'custom_output/'},
            'templates': {'directory': 'custom_templates/'},
            'database': {'path': 'custom.db'},
            'analysis': {'timeout_seconds': 120, 'max_document_size': '5MB'},
            'development': {'debug_mode': True, 'test_mode': False}
        }
        
        assert config.get_log_level() == 'WARNING'
        assert config.get_log_file() == 'custom.log'
        assert config.get_output_directory() == 'custom_output/'
        assert config.get_templates_directory() == 'custom_templates/'
        assert config.get_database_path() == 'custom.db'
        assert config.get_analysis_timeout() == 120
        assert config.get_max_document_size() == '5MB'
        assert config.is_debug_mode() is True
        assert config.is_test_mode() is False
    
    def test_validation_missing_sections(self):
        """Test configuration validation with missing required sections."""
        config = ConfigManager()
        config._config = {'analysis': {}}  # Missing required sections
        
        with pytest.raises(ConfigurationError, match="Required configuration section missing"):
            config._validate_config()
    
    def test_validation_invalid_timeout(self):
        """Test configuration validation with invalid timeout."""
        config = ConfigManager()
        config._config = {
            'analysis': {'timeout_seconds': 'invalid'},
            'logging': {},
            'templates': {},
            'document_generation': {}
        }
        
        with pytest.raises(ConfigurationError, match="analysis.timeout_seconds must be an integer"):
            config._validate_config()
    
    def test_validation_negative_timeout(self):
        """Test configuration validation with negative timeout."""
        config = ConfigManager()
        config._config = {
            'analysis': {'timeout_seconds': -10},
            'logging': {},
            'templates': {},
            'document_generation': {}
        }
        
        with pytest.raises(ConfigurationError, match="analysis.timeout_seconds must be positive"):
            config._validate_config()


class TestConvenienceFunctions:
    """Test cases for convenience functions."""
    
    def setup_method(self):
        """Setup for each test method."""
        ConfigManager._instance = None
        ConfigManager._config = {}
        ConfigManager._config_file_path = None
    
    def test_get_config_function(self):
        """Test get_config convenience function."""
        config = ConfigManager()
        config._config = {'test': {'value': 'test_result'}}
        
        assert get_config('test.value') == 'test_result'
        assert get_config('nonexistent', 'default') == 'default'
    
    def test_is_feature_enabled_function(self):
        """Test is_feature_enabled convenience function."""
        config = ConfigManager()
        config._config = {'features': {'enabled': True, 'disabled': False}}
        
        assert is_feature_enabled('features.enabled') is True
        assert is_feature_enabled('features.disabled') is False
        assert is_feature_enabled('features.nonexistent') is False


if __name__ == '__main__':
    pytest.main([__file__])
