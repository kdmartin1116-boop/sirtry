"""
Unit tests for the VeroBrix Exception Classes.
"""

import pytest
from modules.exceptions import (
    VeroBrixError, ConfigurationError, DocumentProcessingError, AnalysisError,
    TemplateError, DatabaseError, ValidationError, AuthenticationError,
    AuthorizationError, TimeoutError, ResourceError, NetworkError,
    IntegrationError, create_exception, EXCEPTION_MAP
)


class TestVeroBrixError:
    """Test cases for the base VeroBrixError class."""
    
    def test_basic_error_creation(self):
        """Test creating a basic VeroBrix error."""
        error = VeroBrixError("Test error message")
        
        assert str(error) == "Test error message"
        assert error.message == "Test error message"
        assert error.error_code is None
        assert error.details == {}
    
    def test_error_with_code(self):
        """Test creating an error with error code."""
        error = VeroBrixError("Test error", error_code="TEST_ERROR")
        
        assert str(error) == "[TEST_ERROR] Test error"
        assert error.error_code == "TEST_ERROR"
    
    def test_error_with_details(self):
        """Test creating an error with details."""
        details = {"key1": "value1", "key2": "value2"}
        error = VeroBrixError("Test error", details=details)
        
        assert error.details == details
    
    def test_error_to_dict(self):
        """Test converting error to dictionary."""
        details = {"test_key": "test_value"}
        error = VeroBrixError("Test message", "TEST_CODE", details)
        
        error_dict = error.to_dict()
        expected = {
            'error_type': 'VeroBrixError',
            'message': 'Test message',
            'error_code': 'TEST_CODE',
            'details': details
        }
        
        assert error_dict == expected


class TestSpecificExceptions:
    """Test cases for specific exception types."""
    
    def test_configuration_error(self):
        """Test ConfigurationError with specific parameters."""
        error = ConfigurationError(
            "Invalid config",
            config_key="test.key",
            config_file="test.yaml"
        )
        
        assert error.error_code == "CONFIG_ERROR"
        assert error.details["config_key"] == "test.key"
        assert error.details["config_file"] == "test.yaml"
    
    def test_document_processing_error(self):
        """Test DocumentProcessingError with specific parameters."""
        error = DocumentProcessingError(
            "Processing failed",
            document_path="/path/to/doc.txt",
            processing_stage="parsing"
        )
        
        assert error.error_code == "DOC_PROCESSING_ERROR"
        assert error.details["document_path"] == "/path/to/doc.txt"
        assert error.details["processing_stage"] == "parsing"
    
    def test_analysis_error(self):
        """Test AnalysisError with specific parameters."""
        error = AnalysisError(
            "Analysis failed",
            analysis_type="legal_risk",
            input_length=1000
        )
        
        assert error.error_code == "ANALYSIS_ERROR"
        assert error.details["analysis_type"] == "legal_risk"
        assert error.details["input_length"] == 1000
    
    def test_template_error(self):
        """Test TemplateError with specific parameters."""
        missing_vars = ["VAR1", "VAR2"]
        error = TemplateError(
            "Template processing failed",
            template_name="test_template",
            missing_variables=missing_vars
        )
        
        assert error.error_code == "TEMPLATE_ERROR"
        assert error.details["template_name"] == "test_template"
        assert error.details["missing_variables"] == missing_vars
    
    def test_database_error(self):
        """Test DatabaseError with specific parameters."""
        error = DatabaseError(
            "Database operation failed",
            operation="INSERT",
            table="legal_documents"
        )
        
        assert error.error_code == "DATABASE_ERROR"
        assert error.details["operation"] == "INSERT"
        assert error.details["table"] == "legal_documents"
    
    def test_validation_error(self):
        """Test ValidationError with specific parameters."""
        error = ValidationError(
            "Validation failed",
            field_name="email",
            field_value="invalid-email"
        )
        
        assert error.error_code == "VALIDATION_ERROR"
        assert error.details["field_name"] == "email"
        assert error.details["field_value"] == "invalid-email"
    
    def test_authentication_error(self):
        """Test AuthenticationError with specific parameters."""
        error = AuthenticationError(
            "Authentication failed",
            user_id="user123",
            auth_method="password"
        )
        
        assert error.error_code == "AUTH_ERROR"
        assert error.details["user_id"] == "user123"
        assert error.details["auth_method"] == "password"
    
    def test_authorization_error(self):
        """Test AuthorizationError with specific parameters."""
        error = AuthorizationError(
            "Access denied",
            user_id="user123",
            required_permission="admin"
        )
        
        assert error.error_code == "AUTHZ_ERROR"
        assert error.details["user_id"] == "user123"
        assert error.details["required_permission"] == "admin"
    
    def test_timeout_error(self):
        """Test TimeoutError with specific parameters."""
        error = TimeoutError(
            "Operation timed out",
            operation="document_analysis",
            timeout_seconds=300
        )
        
        assert error.error_code == "TIMEOUT_ERROR"
        assert error.details["operation"] == "document_analysis"
        assert error.details["timeout_seconds"] == 300
    
    def test_resource_error(self):
        """Test ResourceError with specific parameters."""
        error = ResourceError(
            "Resource not found",
            resource_type="template",
            resource_id="template_123"
        )
        
        assert error.error_code == "RESOURCE_ERROR"
        assert error.details["resource_type"] == "template"
        assert error.details["resource_id"] == "template_123"
    
    def test_network_error(self):
        """Test NetworkError with specific parameters."""
        error = NetworkError(
            "Network request failed",
            url="https://api.example.com",
            status_code=404
        )
        
        assert error.error_code == "NETWORK_ERROR"
        assert error.details["url"] == "https://api.example.com"
        assert error.details["status_code"] == 404
    
    def test_integration_error(self):
        """Test IntegrationError with specific parameters."""
        error = IntegrationError(
            "External service failed",
            service_name="legal_database",
            operation="search"
        )
        
        assert error.error_code == "INTEGRATION_ERROR"
        assert error.details["service_name"] == "legal_database"
        assert error.details["operation"] == "search"


class TestExceptionMapping:
    """Test cases for exception mapping and creation utilities."""
    
    def test_exception_map_completeness(self):
        """Test that all exception types are in the mapping."""
        expected_codes = [
            'CONFIG_ERROR', 'DOC_PROCESSING_ERROR', 'ANALYSIS_ERROR',
            'TEMPLATE_ERROR', 'DATABASE_ERROR', 'VALIDATION_ERROR',
            'AUTH_ERROR', 'AUTHZ_ERROR', 'TIMEOUT_ERROR',
            'RESOURCE_ERROR', 'NETWORK_ERROR', 'INTEGRATION_ERROR'
        ]
        
        for code in expected_codes:
            assert code in EXCEPTION_MAP
    
    def test_create_exception_known_code(self):
        """Test creating exceptions with known error codes."""
        error = create_exception('CONFIG_ERROR', 'Test config error')
        
        assert isinstance(error, ConfigurationError)
        assert error.message == 'Test config error'
        assert error.error_code == 'CONFIG_ERROR'
    
    def test_create_exception_unknown_code(self):
        """Test creating exceptions with unknown error codes."""
        error = create_exception('UNKNOWN_ERROR', 'Test unknown error')
        
        assert isinstance(error, VeroBrixError)
        assert error.message == 'Test unknown error'
    
    def test_create_exception_with_kwargs(self):
        """Test creating exceptions with additional keyword arguments."""
        error = create_exception(
            'TEMPLATE_ERROR',
            'Template error',
            template_name='test_template',
            missing_variables=['VAR1']
        )
        
        assert isinstance(error, TemplateError)
        assert error.details['template_name'] == 'test_template'
        assert error.details['missing_variables'] == ['VAR1']


class TestExceptionInheritance:
    """Test cases for exception inheritance and behavior."""
    
    def test_all_exceptions_inherit_from_base(self):
        """Test that all custom exceptions inherit from VeroBrixError."""
        exception_classes = [
            ConfigurationError, DocumentProcessingError, AnalysisError,
            TemplateError, DatabaseError, ValidationError,
            AuthenticationError, AuthorizationError, TimeoutError,
            ResourceError, NetworkError, IntegrationError
        ]
        
        for exc_class in exception_classes:
            assert issubclass(exc_class, VeroBrixError)
            assert issubclass(exc_class, Exception)
    
    def test_exception_catching(self):
        """Test that specific exceptions can be caught as base VeroBrixError."""
        with pytest.raises(VeroBrixError):
            raise ConfigurationError("Test error")
        
        with pytest.raises(VeroBrixError):
            raise AnalysisError("Test error")
    
    def test_exception_details_optional(self):
        """Test that exception details are optional."""
        # Test with no optional parameters
        error1 = ConfigurationError("Test error")
        assert error1.details == {}
        
        # Test with some optional parameters
        error2 = ConfigurationError("Test error", config_key="test.key")
        assert "config_key" in error2.details
        assert "config_file" not in error2.details
    
    def test_exception_string_conversion(self):
        """Test string conversion of field values in details."""
        error = ValidationError("Test error", field_value=123)
        assert error.details["field_value"] == "123"
        
        error2 = ValidationError("Test error", field_value=None)
        assert error2.details["field_value"] == "None"


if __name__ == '__main__':
    pytest.main([__file__])
