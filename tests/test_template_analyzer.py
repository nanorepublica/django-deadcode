"""Tests for the template analyzer."""

import tempfile
from pathlib import Path

from django_deadcode.analyzers import TemplateAnalyzer


class TestTemplateAnalyzer:
    """Test suite for TemplateAnalyzer."""

    def test_analyze_url_tags(self):
        """Test extraction of {% url %} tags."""
        analyzer = TemplateAnalyzer()
        content = """
        <a href="{% url 'home' %}">Home</a>
        <a href="{% url 'about' %}">About</a>
        """
        result = analyzer._analyze_template_content(content, "test.html")

        assert "home" in result["urls"]
        assert "about" in result["urls"]
        assert len(result["urls"]) == 2

    def test_analyze_href_attributes(self):
        """Test extraction of internal href attributes."""
        analyzer = TemplateAnalyzer()
        content = """
        <a href="/internal/page/">Internal</a>
        <a href="https://external.com">External</a>
        <a href="//cdn.example.com">CDN</a>
        """
        result = analyzer._analyze_template_content(content, "test.html")

        assert "/internal/page/" in result["hrefs"]
        assert "https://external.com" not in result["hrefs"]
        assert "//cdn.example.com" not in result["hrefs"]

    def test_analyze_include_tags(self):
        """Test extraction of {% include %} tags."""
        analyzer = TemplateAnalyzer()
        content = """
        {% include 'partials/header.html' %}
        {% include "partials/footer.html" %}
        """
        result = analyzer._analyze_template_content(content, "test.html")

        assert "partials/header.html" in result["includes"]
        assert "partials/footer.html" in result["includes"]

    def test_analyze_extends_tags(self):
        """Test extraction of {% extends %} tags."""
        analyzer = TemplateAnalyzer()
        content = """
        {% extends 'base.html' %}
        """
        result = analyzer._analyze_template_content(content, "test.html")

        assert "base.html" in result["extends"]

    def test_find_templates(self):
        """Test finding template files in directory."""
        analyzer = TemplateAnalyzer()

        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)

            # Create some template files
            (tmppath / "test1.html").write_text("<html></html>")
            (tmppath / "test2.html").write_text("<html></html>")
            (tmppath / "test.txt").write_text("text")
            (tmppath / "other.py").write_text("# python")

            templates = analyzer.find_all_templates(tmppath)

            # Should find HTML and TXT files, not PY
            template_names = [t.name for t in templates]
            assert "test1.html" in template_names
            assert "test2.html" in template_names
            assert "test.txt" in template_names
            assert "other.py" not in template_names

    def test_get_unused_url_names(self):
        """Test finding unused URL names."""
        analyzer = TemplateAnalyzer()

        # Analyze a template that references some URLs
        content = "{% url 'home' %} {% url 'about' %}"
        analyzer._analyze_template_content(content, "test.html")

        # Define some URL names
        defined_urls = {"home", "about", "contact", "unused"}

        # Find unused
        unused = analyzer.get_unused_url_names(defined_urls)

        assert "contact" in unused
        assert "unused" in unused
        assert "home" not in unused
        assert "about" not in unused
