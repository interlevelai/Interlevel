"""
Structured logging utility for Interlevel POC
Provides JSON-formatted logs with correlation IDs
"""
import logging
import json
import sys
from datetime import datetime
from typing import Optional
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from config.settings import settings
import uuid


class StructuredLogger:
    """Structured logger with JSON output"""

    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, settings.LOG_LEVEL))

        # Console handler with JSON formatter
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(JsonFormatter())
        self.logger.addHandler(handler)

        self.correlation_id: Optional[str] = None

    def set_correlation_id(self, correlation_id: str):
        """Set correlation ID for request tracking"""
        self.correlation_id = correlation_id

    def _build_log_entry(self, level: str, message: str, **kwargs) -> dict:
        """Build structured log entry"""
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": level,
            "logger": self.logger.name,
            "message": message,
        }

        if self.correlation_id:
            entry["correlation_id"] = self.correlation_id

        # Add any additional context
        entry.update(kwargs)

        return entry

    def debug(self, message: str, **kwargs):
        self.logger.debug(json.dumps(self._build_log_entry("DEBUG", message, **kwargs)))

    def info(self, message: str, **kwargs):
        self.logger.info(json.dumps(self._build_log_entry("INFO", message, **kwargs)))

    def warning(self, message: str, **kwargs):
        self.logger.warning(json.dumps(self._build_log_entry("WARNING", message, **kwargs)))

    def error(self, message: str, **kwargs):
        self.logger.error(json.dumps(self._build_log_entry("ERROR", message, **kwargs)))

    def critical(self, message: str, **kwargs):
        self.logger.critical(json.dumps(self._build_log_entry("CRITICAL", message, **kwargs)))


class JsonFormatter(logging.Formatter):
    """JSON formatter for standard logging"""

    def format(self, record):
        # If message is already JSON, return as-is
        if record.getMessage().startswith('{'):
            return record.getMessage()

        # Otherwise, wrap in JSON
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_entry)


def get_logger(name: str) -> StructuredLogger:
    """Get a structured logger instance"""
    return StructuredLogger(name)


def generate_correlation_id() -> str:
    """Generate a new correlation ID"""
    return str(uuid.uuid4())


# Example usage
if __name__ == "__main__":
    logger = get_logger("test")
    logger.set_correlation_id(generate_correlation_id())

    logger.info("Test log message", user_id="user-123", action="test")
    logger.error("Error occurred", error_code="ERR001")
