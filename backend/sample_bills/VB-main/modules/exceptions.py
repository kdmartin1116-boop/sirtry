"""
VeroBrix Custom Exception Classes

Defines custom exception classes for different types of errors
that can occur in the VeroBrix system.
"""

from typing import Optional, Dict, Any

class VeroBrixError(Exception):
    """Base exception class for all VeroBrix-related errors."""
    
    def __init__(self, message: str, error_code: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        """
        Initialize VeroBrix error.
        
        Args:
            message: Human-readable error message
            error_code: Optional error code for programmatic handling
            details: Optional dictionary with additional error details
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}
    
    def __str__(self) -> str:
        """String representation of the error."""
        if self.error_code:
            return f"[{self.error_code}] {self.message}"
        return self.message
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary for logging/serialization."""
        return {
            'error_type': self.__class__.__name__,
            'message': self.message,
            'error_code': self.error_code,
            'details': self.details
        }

class ConfigurationError(VeroBrixError):
    """Raised when there are configuration-related errors."""
    
    def __init__(self, message: str, config_key: Optional[str] = None, config_file: Optional[str] = None):
        details = {}
        if config_key:
            details['config_key'] = config_key
        if config_file:
            details['config_file'] = config_file
        
        super().__init__(message, 'CONFIG_ERROR', details)

class DocumentProcessingError(VeroBrixError):
    """Raised when document processing fails."""
    
    def __init__(self, message: str, document_path: Optional[str] = None, processing_stage: Optional[str] = None):
        details = {}
        if document_path:
            details['document_path'] = document_path
        if processing_stage:
            details['processing_stage'] = processing_stage
        
        super().__init__(message, 'DOC_PROCESSING_ERROR', details)

class AnalysisError(VeroBrixError):
    """Raised when legal analysis fails."""
    
    def __init__(self, message: str, analysis_type: Optional[str] = None, input_length: Optional[int] = None):
        details = {}
        if analysis_type:
            details['analysis_type'] = analysis_type
        if input_length:
            details['input_length'] = input_length
        
        super().__init__(message, 'ANALYSIS_ERROR', details)

class TemplateError(VeroBrixError):
    """Raised when template processing fails."""
    
    def __init__(self, message: str, template_name: Optional[str] = None, missing_variables: Optional[list] = None):
        details = {}
        if template_name:
            details['template_name'] = template_name
        if missing_variables:
            details['missing_variables'] = missing_variables
        
        super().__init__(message, 'TEMPLATE_ERROR', details)

class DatabaseError(VeroBrixError):
    """Raised when database operations fail."""
    
    def __init__(self, message: str, operation: Optional[str] = None, table: Optional[str] = None):
        details = {}
        if operation:
            details['operation'] = operation
        if table:
            details['table'] = table
        
        super().__init__(message, 'DATABASE_ERROR', details)

class ValidationError(VeroBrixError):
    """Raised when input validation fails."""
    
    def __init__(self, message: str, field_name: Optional[str] = None, field_value: Optional[str] = None):
        details = {}
        if field_name:
            details['field_name'] = field_name
        if field_value:
            details['field_value'] = str(field_value)
        
        super().__init__(message, 'VALIDATION_ERROR', details)

class AuthenticationError(VeroBrixError):
    """Raised when authentication fails."""
    
    def __init__(self, message: str, user_id: Optional[str] = None, auth_method: Optional[str] = None):
        details = {}
        if user_id:
            details['user_id'] = user_id
        if auth_method:
            details['auth_method'] = auth_method
        
        super().__init__(message, 'AUTH_ERROR', details)

class AuthorizationError(VeroBrixError):
    """Raised when authorization fails."""
    
    def __init__(self, message: str, user_id: Optional[str] = None, required_permission: Optional[str] = None):
        details = {}
        if user_id:
            details['user_id'] = user_id
        if required_permission:
            details['required_permission'] = required_permission
        
        super().__init__(message, 'AUTHZ_ERROR', details)

class TimeoutError(VeroBrixError):
    """Raised when operations timeout."""
    
    def __init__(self, message: str, operation: Optional[str] = None, timeout_seconds: Optional[int] = None):
        details = {}
        if operation:
            details['operation'] = operation
        if timeout_seconds:
            details['timeout_seconds'] = timeout_seconds
        
        super().__init__(message, 'TIMEOUT_ERROR', details)

class ResourceError(VeroBrixError):
    """Raised when resource-related errors occur."""
    
    def __init__(self, message: str, resource_type: Optional[str] = None, resource_id: Optional[str] = None):
        details = {}
        if resource_type:
            details['resource_type'] = resource_type
        if resource_id:
            details['resource_id'] = resource_id
        
        super().__init__(message, 'RESOURCE_ERROR', details)

class NetworkError(VeroBrixError):
    """Raised when network operations fail."""
    
    def __init__(self, message: str, url: Optional[str] = None, status_code: Optional[int] = None):
        details = {}
        if url:
            details['url'] = url
        if status_code:
            details['status_code'] = status_code
        
        super().__init__(message, 'NETWORK_ERROR', details)

class IntegrationError(VeroBrixError):
    """Raised when external integration fails."""
    
    def __init__(self, message: str, service_name: Optional[str] = None, operation: Optional[str] = None):
        details = {}
        if service_name:
            details['service_name'] = service_name
        if operation:
            details['operation'] = operation
        
        super().__init__(message, 'INTEGRATION_ERROR', details)

# Exception mapping for easy lookup
EXCEPTION_MAP = {
    'CONFIG_ERROR': ConfigurationError,
    'DOC_PROCESSING_ERROR': DocumentProcessingError,
    'ANALYSIS_ERROR': AnalysisError,
    'TEMPLATE_ERROR': TemplateError,
    'DATABASE_ERROR': DatabaseError,
    'VALIDATION_ERROR': ValidationError,
    'AUTH_ERROR': AuthenticationError,
    'AUTHZ_ERROR': AuthorizationError,
    'TIMEOUT_ERROR': TimeoutError,
    'RESOURCE_ERROR': ResourceError,
    'NETWORK_ERROR': NetworkError,
    'INTEGRATION_ERROR': IntegrationError
}

def create_exception(error_code: str, message: str, **kwargs) -> VeroBrixError:
    """
    Create an exception instance based on error code.
    
    Args:
        error_code: Error code to determine exception type
        message: Error message
        **kwargs: Additional arguments for specific exception types
        
    Returns:
        Appropriate exception instance
    """
    exception_class = EXCEPTION_MAP.get(error_code, VeroBrixError)
    return exception_class(message, **kwargs)
