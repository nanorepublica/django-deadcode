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

    def test_base_dir_filtering_includes_templates_inside(self):
        """Test that templates inside BASE_DIR are included."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            base_dir = tmppath

            # Create template inside BASE_DIR
            (tmppath / "test.html").write_text("<html>{% url 'home' %}</html>")

            analyzer = TemplateAnalyzer([tmppath], base_dir=base_dir)
            analyzer.find_all_templates()

            # Should find the template
            assert len(analyzer.templates) == 1
            assert any("test.html" in key for key in analyzer.templates.keys())

    def test_base_dir_filtering_excludes_templates_outside(self):
        """Test that templates outside BASE_DIR are excluded."""
        with tempfile.TemporaryDirectory() as tmpdir1:
            with tempfile.TemporaryDirectory() as tmpdir2:
                tmppath1 = Path(tmpdir1)
                tmppath2 = Path(tmpdir2)

                # tmppath1 is BASE_DIR
                base_dir = tmppath1

                # Create template outside BASE_DIR
                (tmppath2 / "test.html").write_text("<html>{% url 'home' %}</html>")

                # Analyzer with template_dirs pointing to tmppath2
                # but BASE_DIR as tmppath1
                analyzer = TemplateAnalyzer([tmppath2], base_dir=base_dir)
                analyzer.find_all_templates()

                # Should not find any templates
                assert len(analyzer.templates) == 0

    def test_symlink_preserves_original_path(self):
        """Test that symlinks preserve the original path."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            base_dir = tmppath

            # Create a real template
            real_template = tmppath / "real.html"
            real_template.write_text("<html>{% url 'home' %}</html>")

            # Create a symlink to the template
            symlink = tmppath / "link.html"
            symlink.symlink_to(real_template)

            analyzer = TemplateAnalyzer([tmppath], base_dir=base_dir)
            analyzer.find_all_templates()

            # Should find both templates with their original paths
            template_paths = list(analyzer.templates.keys())
            assert len(template_paths) == 2

            # Check that at least one path contains "link.html"
            assert any("link.html" in str(path) for path in template_paths)

    def test_template_analyzer_with_no_base_dir(self):
        """Test that analyzer works without BASE_DIR (backward compatibility)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)

            # Create template
            (tmppath / "test.html").write_text("<html>{% url 'home' %}</html>")

            # Analyzer without BASE_DIR
            analyzer = TemplateAnalyzer([tmppath])
            analyzer.find_all_templates()

            # Should find the template
            assert len(analyzer.templates) == 1

    def test_is_relative_to_helper(self):
        """Test the _is_relative_to helper method for Python 3.8 compatibility."""
        analyzer = TemplateAnalyzer()

        parent = Path("/home/user/project")
        child = Path("/home/user/project/templates/test.html")
        unrelated = Path("/var/www/templates/test.html")

        assert analyzer._is_relative_to(child, parent) is True
        assert analyzer._is_relative_to(unrelated, parent) is False
        assert analyzer._is_relative_to(parent, parent) is True

    def test_find_all_templates_with_multiple_extensions(self):
        """Test finding templates with different extensions."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            base_dir = tmppath

            # Create templates with different extensions
            (tmppath / "test1.html").write_text("<html></html>")
            (tmppath / "test2.txt").write_text("text")
            (tmppath / "test3.xml").write_text("<xml></xml>")
            (tmppath / "test4.svg").write_text("<svg></svg>")
            (tmppath / "test5.py").write_text("# python")

            analyzer = TemplateAnalyzer([tmppath], base_dir=base_dir)
            analyzer.find_all_templates()

            # Should find HTML, TXT, XML, SVG but not PY
            assert len(analyzer.templates) == 4

    def test_template_relationships_extraction(self):
        """Test extraction of template relationships."""
        analyzer = TemplateAnalyzer()

        # Template with includes and extends
        content = """
        {% extends 'base.html' %}
        {% include 'header.html' %}
        {% include 'footer.html' %}
        """
        analyzer._analyze_template_content(content, "test.html")

        relationships = analyzer.get_template_relationships()

        assert "test.html" in relationships["includes"]
        assert "header.html" in relationships["includes"]["test.html"]
        assert "footer.html" in relationships["includes"]["test.html"]
        assert "test.html" in relationships["extends"]
        assert "base.html" in relationships["extends"]["test.html"]
