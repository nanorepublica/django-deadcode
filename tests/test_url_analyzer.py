"""Tests for the URL analyzer."""

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
        """Test finding unreferenced URLs."""
        analyzer = URLAnalyzer()
        analyzer.analyze_url_patterns("tests.urls")

        # Simulate only 'test_url' being referenced
        referenced = {"test_url"}
        unreferenced = analyzer.get_unreferenced_urls(referenced)

        assert "unused_url" in unreferenced
        assert "test_url" not in unreferenced

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
