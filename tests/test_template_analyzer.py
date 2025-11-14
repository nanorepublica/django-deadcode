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


class TestTemplatePathNormalization:
    """Test suite for template path normalization (Task Group 1)."""

    def test_normalize_standard_app_template_path(self):
        """Test normalization of standard app template path."""
        analyzer = TemplateAnalyzer()

        # Standard app template: /app/apps/collations/templates/collations/base.html
        filesystem_path = Path("/app/apps/collations/templates/collations/base.html")
        normalized = analyzer.normalize_template_path(filesystem_path)

        assert normalized == "collations/base.html"

    def test_normalize_project_level_template_path(self):
        """Test normalization of project-level template path."""
        analyzer = TemplateAnalyzer()

        # Project-level template: /app/templates/base.html
        filesystem_path = Path("/app/templates/base.html")
        normalized = analyzer.normalize_template_path(filesystem_path)

        assert normalized == "base.html"

    def test_normalize_nested_template_directory(self):
        """Test normalization with nested directory structure."""
        analyzer = TemplateAnalyzer()

        # Nested template: /app/templates/partials/header.html
        filesystem_path = Path("/app/templates/partials/header.html")
        normalized = analyzer.normalize_template_path(filesystem_path)

        assert normalized == "partials/header.html"

    def test_normalize_multiple_templates_in_path(self):
        """Test normalization when 'templates' appears multiple times in path."""
        analyzer = TemplateAnalyzer()

        # Edge case: /app/templates/old_templates/templates/base.html
        # Should use last occurrence of 'templates/'
        filesystem_path = Path("/app/templates/old_templates/templates/base.html")
        normalized = analyzer.normalize_template_path(filesystem_path)

        assert normalized == "base.html"

    def test_analyze_template_file_stores_normalized_path(self):
        """Test that analyze_template_file stores templates with normalized paths."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)

            # Create a Django app-like structure
            templates_dir = tmppath / "apps" / "myapp" / "templates"
            templates_dir.mkdir(parents=True)

            # Create template file
            template_file = templates_dir / "myapp" / "detail.html"
            template_file.parent.mkdir(parents=True)
            template_file.write_text("<html>{% url 'home' %}</html>")

            analyzer = TemplateAnalyzer()
            analyzer.analyze_template_file(template_file)

            # Should have normalized path as key
            assert "myapp/detail.html" in analyzer.templates
            # Should not have filesystem path as key
            assert str(template_file) not in analyzer.templates

    def test_template_relationships_use_normalized_paths(self):
        """Test that template relationships use normalized paths."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)

            # Create Django app-like structure
            templates_dir = tmppath / "templates"
            templates_dir.mkdir(parents=True)

            # Create base template
            base_template = templates_dir / "base.html"
            base_template.write_text("<html>{% block content %}{% endblock %}</html>")

            # Create child template that extends base
            child_dir = templates_dir / "myapp"
            child_dir.mkdir(parents=True)
            child_template = child_dir / "detail.html"
            child_template.write_text("{% extends 'base.html' %}")

            analyzer = TemplateAnalyzer()
            analyzer.analyze_template_file(base_template)
            analyzer.analyze_template_file(child_template)

            # Check that relationships use normalized paths
            assert "myapp/detail.html" in analyzer.template_extends
            assert "base.html" in analyzer.template_extends["myapp/detail.html"]

    def test_find_all_templates_uses_normalized_paths(self):
        """Test that find_all_templates stores templates with normalized paths."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)

            # Create Django project structure
            templates_dir = tmppath / "templates"
            templates_dir.mkdir(parents=True)

            # Create templates
            (templates_dir / "base.html").write_text("<html></html>")

            app_templates = templates_dir / "myapp"
            app_templates.mkdir(parents=True)
            (app_templates / "list.html").write_text("<div></div>")

            analyzer = TemplateAnalyzer([templates_dir], base_dir=tmppath)
            analyzer.find_all_templates()

            # Should have normalized paths as keys
            assert "base.html" in analyzer.templates
            assert "myapp/list.html" in analyzer.templates

            # Should not have filesystem paths
            template_keys = list(analyzer.templates.keys())
            for key in template_keys:
                assert not key.startswith("/")
                assert not key.startswith(str(tmppath))

    def test_normalize_path_with_windows_style_separators(self):
        """Test normalization handles path separators correctly."""
        analyzer = TemplateAnalyzer()

        # Test with forward slashes (Unix-style)
        path = Path("/app/templates/myapp/base.html")
        normalized = analyzer.normalize_template_path(path)

        # Result should use forward slashes (Django convention)
        assert normalized == "myapp/base.html"
        assert "/" in normalized


class TestTemplateAnalyzerGapTests:
    """Strategic gap-filling tests for template analyzer (Task Group 5)."""

    def test_normalize_path_without_templates_directory(self):
        """Test normalization when path doesn't contain 'templates' directory."""
        analyzer = TemplateAnalyzer()

        # Edge case: Path without 'templates' directory
        filesystem_path = Path("/app/myfile.html")
        normalized = analyzer.normalize_template_path(filesystem_path)

        # Should return just the filename as fallback
        assert normalized == "myfile.html"

    def test_empty_template_file(self):
        """Test handling of empty template files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)

            # Create empty template file
            templates_dir = tmppath / "templates"
            templates_dir.mkdir(parents=True)
            empty_template = templates_dir / "empty.html"
            empty_template.write_text("")

            analyzer = TemplateAnalyzer([templates_dir], base_dir=tmppath)
            analyzer.find_all_templates()

            # Should still process empty templates
            assert "empty.html" in analyzer.templates
            # Should have empty sets for relationships
            assert len(analyzer.templates["empty.html"]["includes"]) == 0
            assert len(analyzer.templates["empty.html"]["extends"]) == 0

    def test_template_with_mixed_includes_and_extends(self):
        """Test template with multiple includes and extends in complex pattern."""
        analyzer = TemplateAnalyzer()

        # Template with multiple includes and extends (Django only allows one extends)
        content = """
        {% extends 'base.html' %}
        {% block header %}
            {% include 'partials/nav.html' %}
            {% include 'partials/breadcrumb.html' %}
        {% endblock %}
        {% block content %}
            {% include 'partials/sidebar.html' %}
            {% include 'partials/main_content.html' %}
        {% endblock %}
        {% block footer %}
            {% include 'partials/footer.html' %}
        {% endblock %}
        """
        result = analyzer._analyze_template_content(content, "page.html")

        # Should extract all includes
        assert "partials/nav.html" in result["includes"]
        assert "partials/breadcrumb.html" in result["includes"]
        assert "partials/sidebar.html" in result["includes"]
        assert "partials/main_content.html" in result["includes"]
        assert "partials/footer.html" in result["includes"]
        assert len(result["includes"]) == 5

        # Should extract extends
        assert "base.html" in result["extends"]
        assert len(result["extends"]) == 1
