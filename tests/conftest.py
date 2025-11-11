"""Pytest configuration for django-deadcode tests."""

import os
import sys
from pathlib import Path

import django
from django.conf import settings

# Add the parent directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent))


def pytest_configure():
    """Configure Django settings for pytest."""
    if not settings.configured:
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tests.settings")
        django.setup()
