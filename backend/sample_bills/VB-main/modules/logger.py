"""
VeroBrix Enhanced Logging System

Provides structured logging with configuration-based setup,
multiple handlers, and integration with the VeroBrix error system.
"""

import logging
import logging.handlers
import os
import sys
import json
from datetime import datetime
from typing import Dict, Any, Optional, Union
from pathlib import Path

from .config_manager import config
from .exceptions import VeroBrixError

class VeroBrixFormatter(logging.Formatter):
    """Custom formatter for VeroBrix logs with structured output."""
    
    def __init__(self, include_context: bool = True):
        """
        Initialize the formatter.
        
        Args:
            include_context: Whether to include additional context in logs
        """
        self.include_context = include_context
        super().__init__()
    
    def format(self, record: logging.LogRecord) -> str:
        """Format the log record."""
        # Get base format from configuration
        base_format = config.get('logging.format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        
        # Create base formatter
        formatter = logging.Formatter(base_format)
        formatted_message = formatter.format(record)
        
        # Add context if enabled and available
        if self.include_context and hasattr(record, 'context'):
            context_str = json.dumps(record.context, default=str)
            formatted_message += f" | Context: {context_str}"
        
        # Add error details if this is an exception log
        if record.exc_info and isinstance(record.exc_info[1], VeroBrixError):
            error = record.exc_info[1]
            error_details = json.dumps(error.to_dict(), default=str)
            formatted_message += f" | Error Details: {error_details}"
        
        return formatted_message

class VeroBrixLogger:
    """Enhanced logger for VeroBrix system."""
    
    def __init__(self, name: str):
        """
        Initialize the logger.
        
        Args:
            name: Logger name (usually module name)
        """
        self.name = name
        self.logger = logging.getLogger(name)
        self._setup_logger()
    
    def _setup_logger(self) -> None:
        """Setup the logger with handlers and formatters."""
        # Clear existing handlers
        self.logger.handlers.clear()
        
        # Set log level from configuration
        log_level = getattr(logging, config.get_log_level())
        self.logger.setLevel(log_level)
        
        # Prevent duplicate logs
        self.logger.propagate = False
        
        # Setup console handler if enabled
        if config.get('logging.console_output', True):
            self._setup_console_handler()
        
        # Setup file handler if enabled
        if config.get('logging.file_output', True):
            self._setup_file_handler()
    
    def _setup_console_handler(self) -> None:
        """Setup console logging handler."""
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, config.get_log_level()))
        
        # Use colored output if supported and enabled
        if config.get('ui.color_output', True) and self._supports_color():
            formatter = ColoredFormatter()
        else:
            formatter = VeroBrixFormatter(include_context=False)
        
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
    
    def _setup_file_handler(self) -> None:
        """Setup file logging handler with rotation."""
        log_file = config.get_log_file()
        
        # Ensure log directory exists
        log_dir = os.path.dirname(log_file)
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)
        
        # Parse max size (e.g., "100MB" -> 100 * 1024 * 1024)
        max_size_str = config.get('logging.max_size', '100MB')
        max_size = self._parse_size(max_size_str)
        
        # Setup rotating file handler
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=max_size,
            backupCount=config.get('logging.backup_count', 5),
            encoding='utf-8'
        )
        
        file_handler.setLevel(getattr(logging, config.get_log_level()))
        file_handler.setFormatter(VeroBrixFormatter(include_context=True))
        
        self.logger.addHandler(file_handler)
    
    def _parse_size(self, size_str: str) -> int:
        """Parse size string (e.g., '100MB') to bytes."""
        size_str = size_str.upper().strip()
        
        if size_str.endswith('KB'):
            return int(size_str[:-2]) * 1024
        elif size_str.endswith('MB'):
            return int(size_str[:-2]) * 1024 * 1024
        elif size_str.endswith('GB'):
            return int(size_str[:-2]) * 1024 * 1024 * 1024
        else:
            # Assume bytes
            return int(size_str)
    
    def _supports_color(self) -> bool:
        """Check if the terminal supports color output."""
        return (
            hasattr(sys.stdout, 'isatty') and 
            sys.stdout.isatty() and 
            os.getenv('TERM') != 'dumb'
        )
    
    def debug(self, message: str, context: Optional[Dict[str, Any]] = None) -> None:
        """Log debug message."""
        self._log(logging.DEBUG, message, context)
    
    def info(self, message: str, context: Optional[Dict[str, Any]] = None) -> None:
        """Log info message."""
        self._log(logging.INFO, message, context)
    
    def warning(self, message: str, context: Optional[Dict[str, Any]] = None) -> None:
        """Log warning message."""
        self._log(logging.WARNING, message, context)
    
    def error(self, message: str, context: Optional[Dict[str, Any]] = None, exc_info: bool = False) -> None:
        """Log error message."""
        self._log(logging.ERROR, message, context, exc_info=exc_info)
    
    def critical(self, message: str, context: Optional[Dict[str, Any]] = None, exc_info: bool = False) -> None:
        """Log critical message."""
        self._log(logging.CRITICAL, message, context, exc_info=exc_info)
    
    def exception(self, message: str, context: Optional[Dict[str, Any]] = None) -> None:
        """Log exception with traceback."""
        self._log(logging.ERROR, message, context, exc_info=True)
    
    def _log(self, level: int, message: str, context: Optional[Dict[str, Any]] = None, exc_info: bool = False) -> None:
        """Internal logging method."""
        # Create log record
        record = self.logger.makeRecord(
            self.name, level, __file__, 0, message, (), None
        )
        
        # Add context if provided
        if context:
            record.context = context
        
        # Add exception info if requested
        if exc_info:
            record.exc_info = sys.exc_info()
        
        # Handle the record
        self.logger.handle(record)
    
    def log_operation_start(self, operation: str, **kwargs) -> str:
        """Log the start of an operation and return operation ID."""
        operation_id = f"{operation}_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        context = {'operation_id': operation_id, 'operation': operation, **kwargs}
        self.info(f"Starting operation: {operation}", context)
        return operation_id
    
    def log_operation_end(self, operation_id: str, success: bool = True, **kwargs) -> None:
        """Log the end of an operation."""
        status = "completed successfully" if success else "failed"
        context = {'operation_id': operation_id, 'success': success, **kwargs}
        
        if success:
            self.info(f"Operation {status}", context)
        else:
            self.error(f"Operation {status}", context)
    
    def log_performance(self, operation: str, duration_ms: float, **kwargs) -> None:
        """Log performance metrics."""
        context = {
            'operation': operation,
            'duration_ms': duration_ms,
            'performance_log': True,
            **kwargs
        }
        self.info(f"Performance: {operation} took {duration_ms:.2f}ms", context)

class ColoredFormatter(VeroBrixFormatter):
    """Colored formatter for console output."""
    
    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
        'RESET': '\033[0m'        # Reset
    }
    
    def format(self, record: logging.LogRecord) -> str:
        """Format with colors."""
        # Get base formatted message
        message = super().format(record)
        
        # Add color
        color = self.COLORS.get(record.levelname, '')
        reset = self.COLORS['RESET']
        
        return f"{color}{message}{reset}"

# Global logger instances
_loggers: Dict[str, VeroBrixLogger] = {}

def get_logger(name: str) -> VeroBrixLogger:
    """
    Get or create a logger instance.
    
    Args:
        name: Logger name (usually __name__)
        
    Returns:
        VeroBrixLogger instance
    """
    if name not in _loggers:
        _loggers[name] = VeroBrixLogger(name)
    return _loggers[name]

def setup_logging() -> None:
    """Setup logging system with current configuration."""
    # Clear existing loggers
    _loggers.clear()
    
    # Setup root logger
    root_logger = get_logger('verobrix')
    root_logger.info("Logging system initialized")

def log_system_info() -> None:
    """Log system information at startup."""
    logger = get_logger('verobrix.system')
    
    system_info = {
        'python_version': sys.version,
        'platform': sys.platform,
        'working_directory': os.getcwd(),
        'log_level': config.get_log_level(),
        'config_file': config._config_file_path
    }
    
    logger.info("System startup", context=system_info)

# Convenience functions for backward compatibility
def log_provenance(component: str, message: str, **kwargs) -> None:
    """Log provenance information (backward compatibility)."""
    logger = get_logger(f'verobrix.{component.lower().replace(" ", "_")}')
    context = {'component': component, **kwargs}
    logger.info(message, context)

# Performance monitoring decorator
def log_performance(operation_name: Optional[str] = None):
    """Decorator to log performance of functions."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            import time
            
            op_name = operation_name or f"{func.__module__}.{func.__name__}"
            logger = get_logger(func.__module__)
            
            start_time = time.time()
            operation_id = logger.log_operation_start(op_name)
            
            try:
                result = func(*args, **kwargs)
                duration_ms = (time.time() - start_time) * 1000
                logger.log_operation_end(operation_id, success=True)
                logger.log_performance(op_name, duration_ms)
                return result
            except Exception as e:
                duration_ms = (time.time() - start_time) * 1000
                logger.log_operation_end(operation_id, success=False, error=str(e))
                logger.log_performance(op_name, duration_ms, success=False)
                raise
        
        return wrapper
    return decorator
