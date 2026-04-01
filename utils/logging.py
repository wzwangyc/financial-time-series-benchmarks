# -*- coding: utf-8 -*-
"""
Structured Logging

Business Intent:
    Provide full observability for all core operations.
    All failures must emit structured, traceable logs.
    All core decisions must be fully diagnosable.

Design Boundaries:
    - JSON format for all logs
    - Structured fields for all log entries
    - Trace IDs for end-to-end tracing
    - Log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL

Applicable Scenarios:
    - All core operations
    - All error handling
    - All performance metrics
    - All business decisions
"""

import logging
import json
import sys
from datetime import datetime, timezone
from typing import Dict, Any, Optional
import traceback


def setup_logging(level: str = 'INFO', output_file: Optional[str] = None) -> logging.Logger:
    """
    Setup structured logging for production.
    
    Business Intent:
        All core decisions must be fully diagnosable.
        All failures must be traceable.
        All performance metrics must be measurable.
    
    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        output_file: Optional file to write logs (default: stdout)
    
    Returns:
        Configured logger with JSON formatter
    
    Usage:
        >>> logger = setup_logging('INFO')
        >>> logger.info('Operation started', extra={'operation': 'backtest'})
    """
    logger = logging.getLogger('ftsb')
    logger.setLevel(getattr(logging, level.upper()))
    
    # Create handler
    if output_file:
        handler = logging.FileHandler(output_file, encoding='utf-8')
    else:
        handler = logging.StreamHandler(sys.stdout)
    
    # Set JSON formatter
    formatter = JSONFormatter()
    handler.setFormatter(formatter)
    
    # Add handler to logger
    if not logger.handlers:
        logger.addHandler(handler)
    
    return logger


class JSONFormatter(logging.Formatter):
    """
    JSON formatter for structured logs.
    
    Business Intent:
        All logs must be machine-readable for analysis.
        All logs must have consistent structure.
        All logs must be traceable with trace IDs.
    """
    
    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
            'thread': record.thread,
            'process': record.process,
        }
        
        # Add extra fields
        if hasattr(record, 'extra'):
            log_entry['extra'] = record.extra
        
        # Add exception info
        if record.exc_info:
            log_entry['exception'] = {
                'type': record.exc_info[0].__name__ if record.exc_info[0] else None,
                'message': str(record.exc_info[1]) if record.exc_info[1] else None,
                'traceback': traceback.format_exception(*record.exc_info) if record.exc_info else None,
            }
        
        return json.dumps(log_entry, ensure_ascii=False, default=str)


# Global logger instance
_logger = None


def get_logger() -> logging.Logger:
    """
    Get global logger instance.
    
    Business Intent:
        Single logger instance for consistent logging.
        Lazy initialization.
    
    Returns:
        Global logger instance
    
    Usage:
        >>> logger = get_logger()
        >>> logger.info('Message')
    """
    global _logger
    if _logger is None:
        _logger = setup_logging()
    return _logger


# Convenience functions

def log_info(message: str, **kwargs) -> None:
    """
    Log info message with structured data.
    
    Business Intent:
        Log normal operations with context.
        All business operations should be logged.
    
    Args:
        message: Log message
        **kwargs: Additional structured data
    
    Usage:
        >>> log_info('Backtest started', strategy='momentum', capital=1000000)
    """
    logger = get_logger()
    logger.info(message, extra=kwargs)


def log_error(message: str, exc: Optional[Exception] = None, **kwargs) -> None:
    """
    Log error message with exception and context.
    
    Business Intent:
        Log all errors with full context.
        All errors must be traceable.
    
    Args:
        message: Error message
        exc: Exception object (optional)
        **kwargs: Additional structured data
    
    Usage:
        >>> try:
        ...     risky_operation()
        ... except Exception as e:
        ...     log_error('Operation failed', exc=e, operation='risky_operation')
    """
    logger = get_logger()
    logger.error(message, exc_info=exc, extra=kwargs)


def log_warning(message: str, **kwargs) -> None:
    """
    Log warning message with context.
    
    Business Intent:
        Log potential issues before they become errors.
        All warnings should be actionable.
    
    Args:
        message: Warning message
        **kwargs: Additional structured data
    
    Usage:
        >>> log_warning('High latency detected', latency_ms=500, threshold_ms=100)
    """
    logger = get_logger()
    logger.warning(message, extra=kwargs)


def log_debug(message: str, **kwargs) -> None:
    """
    Log debug message with context.
    
    Business Intent:
        Log detailed information for debugging.
        Debug logs should be verbose but structured.
    
    Args:
        message: Debug message
        **kwargs: Additional structured data
    
    Usage:
        >>> log_debug('Function called', args=args, kwargs=kwargs)
    """
    logger = get_logger()
    logger.debug(message, extra=kwargs)


def log_critical(message: str, exc: Optional[Exception] = None, **kwargs) -> None:
    """
    Log critical message requiring immediate attention.
    
    Business Intent:
        Log critical failures requiring immediate action.
        All critical logs should trigger alerts.
    
    Args:
        message: Critical message
        exc: Exception object (optional)
        **kwargs: Additional structured data
    
    Usage:
        >>> log_critical('System failure', exc=e, system='backtest_engine')
    """
    logger = get_logger()
    logger.critical(message, exc_info=exc, extra=kwargs)
