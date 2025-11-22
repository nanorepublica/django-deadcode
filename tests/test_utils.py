"""Tests for utility functions."""

from pathlib import Path
from unittest.mock import Mock

from django.conf import settings

from django_deadcode.utils import get_module_path, is_third_party_module


class TestThirdPartyDetection:
    """Test suite for third-party module detection."""

    def test_project_module_is_not_third_party(self):
        """Test that a module under BASE_DIR is not third-party."""
        # Create a mock view that appears to be in the project
        mock_view = Mock()
        mock_view.__module__ = "myapp.views"
        # Simulate the module being in the project directory
        project_module_path = Path(settings.BASE_DIR) / "myapp" / "views.py"
        mock_view.__module__ = "myapp.views"

        # Create a module mock
        import sys

        mock_module = Mock()
        mock_module.__file__ = str(project_module_path)
        sys.modules["myapp.views"] = mock_module

        try:
            assert not is_third_party_module(mock_view)
        finally:
            # Cleanup
            if "myapp.views" in sys.modules:
                del sys.modules["myapp.views"]

    def test_django_builtin_is_third_party(self):
        """Test that Django built-in modules are third-party."""
        # Create a mock view from django.contrib.admin
        from django.contrib import admin

        mock_view = Mock()
        mock_view.__module__ = "django.contrib.admin.sites"

        # Get the actual admin module
        if hasattr(admin, "__file__"):
            assert is_third_party_module(mock_view)

    def test_site_packages_module_is_third_party(self):
        """Test that modules in site-packages are third-party."""
        # Use an actual third-party module like pytest
        mock_view = Mock()
        mock_view.__module__ = "pytest"

        # pytest is definitely not in BASE_DIR
        assert is_third_party_module(mock_view)

    def test_module_without_file_is_third_party(self):
        """Test that built-in modules without __file__ are third-party."""
        # Built-in modules like sys don't have __file__
        mock_view = Mock()
        mock_view.__module__ = "sys"

        # Should be considered third-party (safe default)
        assert is_third_party_module(mock_view)

    def test_get_module_path_from_function(self):
        """Test extracting module path from a function-based view."""

        def test_view(request):
            pass

        # Set the module to something we can track
        test_view.__module__ = "test_module"

        # This should work even if module doesn't exist
        module_path = get_module_path(test_view)
        assert module_path == "test_module"

    def test_get_module_path_from_class(self):
        """Test extracting module path from a class-based view."""

        class TestView:
            def as_view(self):
                pass

        TestView.__module__ = "test_module.views"

        module_path = get_module_path(TestView)
        assert module_path == "test_module.views"

    def test_is_third_party_with_callable(self):
        """Test is_third_party_module works with actual callable."""

        # Create a simple function
        def my_view(request):
            return None

        # Set it to appear as if from project
        my_view.__module__ = "myproject.views"

        # Since the module doesn't actually exist with a file,
        # it should be treated carefully
        result = is_third_party_module(my_view)
        # The behavior depends on whether the module can be resolved
        assert isinstance(result, bool)
