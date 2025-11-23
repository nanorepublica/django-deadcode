"""Tests for the URL analyzer."""

from unittest.mock import patch

import pytest

from django_deadcode.analyzers import URLAnalyzer


class TestURLAnalyzer:
    """Test suite for URLAnalyzer."""

    @pytest.mark.django_db
    def test_analyze_url_patterns(self):
        """Test analyzing URL patterns."""
        analyzer = URLAnalyzer()
        analyzer.analyze_url_patterns("tests.urls")

        # Should find the test URLs
        url_names = analyzer.get_all_url_names()
        assert "test_url" in url_names
        assert "unused_url" in url_names

    @pytest.mark.django_db
    def test_get_view_for_url(self):
        """Test getting view for a URL name."""
        analyzer = URLAnalyzer()
        analyzer.analyze_url_patterns("tests.urls")

        view = analyzer.get_view_for_url("test_url")
        assert view is not None
        assert "test_view" in view

    @pytest.mark.django_db
    def test_get_unreferenced_urls(self):
        """Test finding unreferenced URLs with new tuple return."""
        analyzer = URLAnalyzer()
        analyzer.analyze_url_patterns("tests.urls")

        # Simulate only 'test_url' being referenced
        referenced = {"test_url"}
        unreferenced, excluded = analyzer.get_unreferenced_urls(referenced)

        assert "unused_url" in unreferenced
        assert "test_url" not in unreferenced
        # excluded should be a set (empty in this case)
        assert isinstance(excluded, set)

    @pytest.mark.django_db
    def test_get_url_statistics(self):
        """Test getting URL statistics."""
        analyzer = URLAnalyzer()
        analyzer.analyze_url_patterns("tests.urls")

        stats = analyzer.get_url_statistics()

        assert "total_urls" in stats
        assert stats["total_urls"] >= 2
        assert "total_views" in stats
        assert "urls_per_view" in stats


class TestURLAnalyzerThirdParty:
    """Test suite for URLAnalyzer third-party detection features."""

    @pytest.mark.django_db
    def test_url_pattern_stores_module_path(self):
        """Test that URL patterns store the module path."""
        analyzer = URLAnalyzer()
        analyzer.analyze_url_patterns("tests.urls")

        # Check that patterns have module_path field
        for url_name, details in analyzer.url_patterns.items():
            assert "module_path" in details
            assert isinstance(details["module_path"], str)

    @pytest.mark.django_db
    def test_url_pattern_stores_is_third_party_flag(self):
        """Test that URL patterns store is_third_party flag."""
        analyzer = URLAnalyzer()
        analyzer.analyze_url_patterns("tests.urls")

        # Check that patterns have is_third_party field
        for url_name, details in analyzer.url_patterns.items():
            assert "is_third_party" in details
            assert isinstance(details["is_third_party"], bool)

    @pytest.mark.django_db
    @patch("django_deadcode.analyzers.url_analyzer.is_third_party_module")
    def test_third_party_detection_for_project_views(self, mock_is_third_party):
        """Test that project views are correctly identified as not third-party."""
        # Mock the function to return False (not third-party)
        mock_is_third_party.return_value = False

        analyzer = URLAnalyzer()
        analyzer.analyze_url_patterns("tests.urls")

        # At least one URL should be marked as not third-party
        non_third_party = [
            details
            for details in analyzer.url_patterns.values()
            if not details["is_third_party"]
        ]
        assert len(non_third_party) > 0

    @pytest.mark.django_db
    def test_detect_third_party_namespaces(self):
        """Test detection of third-party namespaces."""
        analyzer = URLAnalyzer()
        analyzer.analyze_url_patterns("tests.urls")

        # Should return a set of namespace strings
        third_party_namespaces = analyzer.get_third_party_namespaces()
        assert isinstance(third_party_namespaces, set)

    @pytest.mark.django_db
    def test_get_unreferenced_urls_with_exclusions(self):
        """Test that get_unreferenced_urls excludes specified namespaces."""
        analyzer = URLAnalyzer()
        analyzer.analyze_url_patterns("tests.urls")

        # Simulate excluding all URLs
        referenced = set()
        excluded_namespaces = set()  # Don't exclude anything

        unreferenced, excluded = analyzer.get_unreferenced_urls(
            referenced, excluded_namespaces
        )

        # Should return unreferenced URLs and excluded namespaces
        assert isinstance(unreferenced, set)
        assert isinstance(excluded, set)

    @pytest.mark.django_db
    def test_namespace_exclusion_removes_urls(self):
        """Test that excluding a namespace removes all URLs in that namespace."""
        analyzer = URLAnalyzer()

        # Create some mock URL patterns with namespaces
        analyzer.url_patterns = {
            "admin:index": {
                "name": "admin:index",
                "namespace": "admin",
                "is_third_party": True,
            },
            "admin:login": {
                "name": "admin:login",
                "namespace": "admin",
                "is_third_party": True,
            },
            "app:view1": {
                "name": "app:view1",
                "namespace": "app",
                "is_third_party": False,
            },
        }
        analyzer.url_names = {"admin:index", "admin:login", "app:view1"}

        # Exclude admin namespace
        referenced = set()
        excluded_namespaces = {"admin"}

        unreferenced, excluded = analyzer.get_unreferenced_urls(
            referenced, excluded_namespaces
        )

        # admin URLs should be excluded
        assert "admin:index" not in unreferenced
        assert "admin:login" not in unreferenced
        # app URLs should still be there
        assert "app:view1" in unreferenced
        # Should report admin as excluded
        assert "admin" in excluded

    @pytest.mark.django_db
    def test_namespace_with_any_third_party_is_excluded(self):
        """Test any third-party pattern marks whole namespace as third-party."""
        analyzer = URLAnalyzer()

        # Create mock patterns where namespace has mixed third-party status
        analyzer.url_patterns = {
            "myapp:view1": {
                "name": "myapp:view1",
                "namespace": "myapp",
                "is_third_party": False,
            },
            "myapp:view2": {
                "name": "myapp:view2",
                "namespace": "myapp",
                "is_third_party": True,  # One third-party view
            },
        }

        # Get third-party namespaces
        third_party = analyzer.get_third_party_namespaces()

        # The whole namespace should be marked as third-party
        assert "myapp" in third_party
