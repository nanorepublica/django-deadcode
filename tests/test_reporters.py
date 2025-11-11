"""Tests for reporters."""

import json

import pytest

from django_deadcode.reporters import ConsoleReporter, JSONReporter, MarkdownReporter


class TestReporters:
    """Test suite for reporters."""

    @pytest.fixture
    def sample_data(self):
        """Sample analysis data."""
        return {
            "summary": {
                "total_urls": 10,
                "total_templates": 15,
                "total_views": 8,
                "unreferenced_urls_count": 2,
                "unused_templates_count": 3,
            },
            "unreferenced_urls": ["unused_url1", "unused_url2"],
            "url_details": {
                "unused_url1": {
                    "name": "unused_url1",
                    "pattern": "/unused1/",
                    "view": "myapp.views.unused_view1",
                    "namespace": None,
                }
            },
            "url_references": {"template1.html": {"home", "about"}},
            "template_usage": {"myapp.views.home": ["home.html"]},
            "unused_templates": ["unused1.html", "unused2.html"],
            "template_relationships": {
                "includes": {"base.html": {"header.html"}},
                "extends": {"page.html": {"base.html"}},
            },
        }

    def test_console_reporter(self, sample_data):
        """Test console reporter generates valid output."""
        reporter = ConsoleReporter()
        report = reporter.generate_report(sample_data)

        assert "Django Dead Code Analysis Report" in report
        assert "SUMMARY" in report
        assert "Total URL patterns: 10" in report
        assert "unused_url1" in report

    def test_json_reporter(self, sample_data):
        """Test JSON reporter generates valid JSON."""
        reporter = JSONReporter()
        report = reporter.generate_report(sample_data)

        # Should be valid JSON
        data = json.loads(report)

        assert data["summary"]["total_urls"] == 10
        assert "unused_url1" in data["unreferenced_urls"]

    def test_json_reporter_handles_sets(self):
        """Test JSON reporter converts sets to lists."""
        reporter = JSONReporter()
        data = {"test_set": {"a", "b", "c"}}

        report = reporter.generate_report(data)
        parsed = json.loads(report)

        # Sets should be converted to sorted lists
        assert isinstance(parsed["test_set"], list)
        assert sorted(parsed["test_set"]) == ["a", "b", "c"]

    def test_markdown_reporter(self, sample_data):
        """Test Markdown reporter generates valid Markdown."""
        reporter = MarkdownReporter()
        report = reporter.generate_report(sample_data)

        assert "# Django Dead Code Analysis Report" in report
        assert "## Summary" in report
        assert "**Total URL patterns:** 10" in report
        assert "`unused_url1`" in report
