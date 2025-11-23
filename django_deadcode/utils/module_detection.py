"""Module detection utilities for identifying third-party code."""

import sys
from pathlib import Path
from typing import Any

from django.conf import settings


def get_module_path(view_callback: Any) -> str:
    """
    Extract the module path from a view callback.

    Args:
        view_callback: A view function or class

    Returns:
        Module path as a string (e.g., 'myapp.views')
    """
    if hasattr(view_callback, "__module__"):
        return view_callback.__module__
    return "Unknown"


def is_third_party_module(view_callback: Any) -> bool:
    """
    Check if a view callback is from a third-party module.

    A module is considered third-party if its file path is NOT under
    the project's BASE_DIR.

    Args:
        view_callback: A view function or class to check

    Returns:
        True if the module is third-party, False if it's project code
    """
    # Get the module path
    module_path = get_module_path(view_callback)

    # Try to get the module object
    try:
        module = sys.modules.get(module_path)
        if module is None:
            # Module not loaded, assume third-party for safety
            return True

        # Check if module has a file path
        if not hasattr(module, "__file__") or module.__file__ is None:
            # Built-in modules don't have __file__, treat as third-party
            return True

        # Get the module's file path
        module_file = Path(module.__file__).resolve()

        # Get BASE_DIR from settings
        base_dir = Path(settings.BASE_DIR).resolve()

        # Check if module file is under BASE_DIR
        try:
            module_file.relative_to(base_dir)
            # If successful, it's under BASE_DIR (project code)
            return False
        except ValueError:
            # Not under BASE_DIR, it's third-party
            return True

    except (AttributeError, TypeError, ValueError):
        # If anything goes wrong, assume third-party for safety
        return True
