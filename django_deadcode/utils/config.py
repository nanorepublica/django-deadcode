"""Configuration utilities for django-deadcode settings."""

from typing import Any

from django.conf import settings


def get_excluded_namespaces() -> set[str]:
    """
    Get the list of URL namespaces to exclude from analysis.

    Reads from Django settings: DEADCODE_EXCLUDE_NAMESPACES

    Returns:
        Set of namespace strings to exclude (empty set if not configured)

    Examples:
        >>> # In settings.py:
        >>> # DEADCODE_EXCLUDE_NAMESPACES = ['admin', 'debug_toolbar']
        >>> get_excluded_namespaces()
        {'admin', 'debug_toolbar'}
    """
    excluded_namespaces: Any = getattr(settings, "DEADCODE_EXCLUDE_NAMESPACES", None)

    if excluded_namespaces is None:
        return set()

    # Convert to set to handle lists, tuples, or sets
    try:
        return set(excluded_namespaces)
    except (TypeError, ValueError):
        # If conversion fails, return empty set
        return set()
