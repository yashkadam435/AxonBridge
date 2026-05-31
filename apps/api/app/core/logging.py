"""
AxonBridge — Structured Logging

PHI-safe structured logging with structlog. Automatically scrubs
Protected Health Information from log output.
"""

import logging
import re
import sys

import structlog

from app.core.config import get_settings

settings = get_settings()

# ---------- PHI Scrubbing Patterns ----------

PHI_PATTERNS = [
    # SSN patterns
    (re.compile(r"\b\d{3}-\d{2}-\d{4}\b"), "[SSN_REDACTED]"),
    # MRN patterns (common formats)
    (re.compile(r"\bMRN[:\s]*\d{6,10}\b", re.IGNORECASE), "[MRN_REDACTED]"),
    # Email-like patient identifiers in certain contexts
    (re.compile(r"patient[_\s]*(?:email|mail)[:\s]*\S+", re.IGNORECASE), "[PATIENT_EMAIL_REDACTED]"),
    # Phone numbers
    (re.compile(r"\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b"), "[PHONE_REDACTED]"),
    # Date of birth patterns
    (re.compile(r"(?:dob|date.?of.?birth)[:\s]*\d{1,2}[/-]\d{1,2}[/-]\d{2,4}", re.IGNORECASE), "[DOB_REDACTED]"),
]


def scrub_phi(_, __, event_dict: dict) -> dict:
    """Structlog processor that scrubs PHI from log messages."""
    message = event_dict.get("event", "")
    if isinstance(message, str):
        for pattern, replacement in PHI_PATTERNS:
            message = pattern.sub(replacement, message)
        event_dict["event"] = message

    # Also scrub values in the event dict
    for key, value in list(event_dict.items()):
        if isinstance(value, str):
            for pattern, replacement in PHI_PATTERNS:
                value = pattern.sub(replacement, value)
            event_dict[key] = value

    return event_dict


def add_app_context(_, __, event_dict: dict) -> dict:
    """Add application context to every log entry."""
    event_dict["app"] = settings.APP_NAME
    event_dict["env"] = settings.APP_ENV
    event_dict["version"] = settings.APP_VERSION
    return event_dict


def setup_logging() -> None:
    """Configure structured logging for the application."""
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)

    # Structlog processors
    shared_processors: list[structlog.types.Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        add_app_context,
        scrub_phi,
    ]

    if settings.LOG_FORMAT == "json":
        renderer = structlog.processors.JSONRenderer()
    else:
        renderer = structlog.dev.ConsoleRenderer(colors=True)

    structlog.configure(
        processors=[
            *shared_processors,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    # Configure standard logging
    formatter = structlog.stdlib.ProcessorFormatter(
        processors=[
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            renderer,
        ],
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.addHandler(handler)
    root_logger.setLevel(log_level)

    # Suppress noisy loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(
        logging.INFO if settings.APP_DEBUG else logging.WARNING
    )


def get_logger(name: str | None = None) -> structlog.stdlib.BoundLogger:
    """Get a structured logger instance."""
    return structlog.get_logger(name)
