"""Utility functions for django-deadcode."""

from .config import get_excluded_namespaces
from .module_detection import get_module_path, is_third_party_module
from .url_matching import (
    find_matching_url_patterns,
    match_href_to_pattern,
    normalize_path,
)

__all__ = [
    "get_excluded_namespaces",
    "get_module_path",
    "is_third_party_module",
    "normalize_path",
    "match_href_to_pattern",
    "find_matching_url_patterns",
]
