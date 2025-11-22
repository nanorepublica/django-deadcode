"""Tests for configuration handling."""

from django.conf import settings
from django.test import override_settings

from django_deadcode.utils.config import get_excluded_namespaces


class TestConfiguration:
    """Test suite for configuration handling."""

    @override_settings()
    def test_no_configuration_returns_empty_set(self):
        """Test that missing DEADCODE_EXCLUDE_NAMESPACES returns empty set."""
        # Remove the setting if it exists
        if hasattr(settings, "DEADCODE_EXCLUDE_NAMESPACES"):
            delattr(settings, "DEADCODE_EXCLUDE_NAMESPACES")

        excluded = get_excluded_namespaces()
        assert excluded == set()
        assert isinstance(excluded, set)

    @override_settings(DEADCODE_EXCLUDE_NAMESPACES=["admin", "debug_toolbar"])
    def test_read_configured_namespaces(self):
        """Test reading configured namespaces from settings."""
        excluded = get_excluded_namespaces()

        assert "admin" in excluded
        assert "debug_toolbar" in excluded
        assert len(excluded) == 2

    @override_settings(DEADCODE_EXCLUDE_NAMESPACES=[])
    def test_empty_list_returns_empty_set(self):
        """Test that empty list returns empty set."""
        excluded = get_excluded_namespaces()
        assert excluded == set()

    @override_settings(DEADCODE_EXCLUDE_NAMESPACES=("admin", "api"))
    def test_tuple_configuration(self):
        """Test that tuple configuration works."""
        excluded = get_excluded_namespaces()

        assert "admin" in excluded
        assert "api" in excluded
        assert isinstance(excluded, set)

    @override_settings(DEADCODE_EXCLUDE_NAMESPACES={"admin", "api"})
    def test_set_configuration(self):
        """Test that set configuration works."""
        excluded = get_excluded_namespaces()

        assert "admin" in excluded
        assert "api" in excluded
        assert isinstance(excluded, set)

    @override_settings(DEADCODE_EXCLUDE_NAMESPACES=["admin", "admin"])
    def test_duplicate_values_deduplicated(self):
        """Test that duplicate values are deduplicated."""
        excluded = get_excluded_namespaces()

        assert "admin" in excluded
        assert len(excluded) == 1

    @override_settings(DEADCODE_EXCLUDE_NAMESPACES=["admin", "api", "debug"])
    def test_multiple_namespaces(self):
        """Test handling multiple namespaces."""
        excluded = get_excluded_namespaces()

        assert len(excluded) == 3
        assert all(ns in excluded for ns in ["admin", "api", "debug"])
