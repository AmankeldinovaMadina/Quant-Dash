"""
Logging configuration for Quant-Dash backend.

This module provides:
1. Structured logging configuration
2. Different log levels for different environments
3. Proper log formatting for production debugging
4. Security-aware logging (no sensitive data)
"""

import logging
import logging.config
import os
from typing import Any, Dict

from app.core.config import settings


def get_logging_config() -> Dict[str, Any]:
    """
    Get logging configuration based on environment.

    Returns structured logging config with appropriate levels
    and formatters for development vs production.
    """
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            "detailed": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": "DEBUG" if settings.DEBUG else "INFO",
                "formatter": "detailed" if settings.DEBUG else "default",
                "stream": "ext://sys.stdout",
            },
        },
        "loggers": {
            "app": {
                "level": "DEBUG" if settings.DEBUG else "INFO",
                "handlers": ["console"],
                "propagate": False,
            },
            "uvicorn": {
                "level": "INFO",
                "handlers": ["console"],
                "propagate": False,
            },
            "uvicorn.error": {
                "level": "INFO",
                "handlers": ["console"],
                "propagate": False,
            },
            "uvicorn.access": {
                "level": "INFO",
                "handlers": ["console"],
                "propagate": False,
            },
        },
        "root": {
            "level": "INFO",
            "handlers": ["console"],
        },
    }


def setup_logging():
    """
    Setup logging configuration.

    Configures logging based on environment with fallback to basic setup.
    """
    try:
        # Apply logging configuration
        config = get_logging_config()
        logging.config.dictConfig(config)

        # Log startup message
        logger = logging.getLogger("app.core.logging")
        logger.info("Logging configured successfully")

    except Exception as e:
        # Fallback to basic logging if configuration fails
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        logger = logging.getLogger("app.core.logging")
        logger.warning(f"Failed to setup advanced logging, using basic config: {e}")


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger with proper configuration.

    Args:
        name: Logger name (usually __name__)

    Returns:
        Configured logger instance
    """
    return logging.getLogger(f"app.{name}")


# Security logging helpers
def log_security_event(logger: logging.Logger, event: str, **kwargs):
    """
    Log security-related events with proper context.

    Args:
        logger: Logger instance
        event: Security event description
        **kwargs: Additional context (sanitized)
    """
    # Remove sensitive data from kwargs
    sanitized_kwargs = {
        k: v
        for k, v in kwargs.items()
        if k not in ["password", "token", "secret", "key"]
    }

    logger.warning(
        "SECURITY_EVENT: %s. Context: %s",
        event,
        sanitized_kwargs,
        extra={"security_event": True, **sanitized_kwargs},
    )


def log_authentication_failure(
    logger: logging.Logger, email: str, reason: str, request_info: dict = None
):
    """
    Log authentication failures for security monitoring.

    Args:
        logger: Logger instance
        email: User email (for legitimate security monitoring)
        reason: Failure reason
        request_info: Request context (IP, user agent, etc.)
    """
    context = {"email": email, "reason": reason, "event_type": "authentication_failure"}

    if request_info:
        context.update(
            {
                "client_ip": request_info.get("client_ip"),
                "user_agent": request_info.get("user_agent", "")[
                    :100
                ],  # Truncate user agent
            }
        )

    logger.warning(
        "Authentication failure for email: %s. Reason: %s", email, reason, extra=context
    )
