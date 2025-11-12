"""Tests for the view analyzer."""

import tempfile
from pathlib import Path

from django_deadcode.analyzers import ViewAnalyzer


class TestViewAnalyzer:
    """Test suite for ViewAnalyzer."""

    def test_analyze_render_call(self):
        """Test extracting template from render() call."""
        analyzer = ViewAnalyzer()

        content = """
from django.shortcuts import render

def my_view(request):
    return render(request, 'myapp/template.html', context)
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(content)
            f.flush()
            temp_path = Path(f.name)

        try:
            analyzer.analyze_view_file(temp_path)

            # Check that template was found
            assert "myapp/template.html" in analyzer.template_usage
        finally:
            temp_path.unlink()

    def test_analyze_class_based_view(self):
        """Test extracting template from class-based view."""
        analyzer = ViewAnalyzer()

        content = """
from django.views.generic import TemplateView

class MyView(TemplateView):
    template_name = 'myapp/cbv_template.html'
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(content)
            f.flush()
            temp_path = Path(f.name)

        try:
            analyzer.analyze_view_file(temp_path)

            # Check that template was found
            assert "myapp/cbv_template.html" in analyzer.template_usage
        finally:
            temp_path.unlink()

    def test_get_views_for_template(self):
        """Test getting views for a specific template."""
        analyzer = ViewAnalyzer()

        # Add some test data
        analyzer._add_template_reference("view1.py", "template1.html")
        analyzer._add_template_reference("view2.py", "template1.html")
        analyzer._add_template_reference("view3.py", "template2.html")

        views = analyzer.get_views_for_template("template1.html")

        assert "view1.py" in views
        assert "view2.py" in views
        assert "view3.py" not in views

    def test_get_templates_for_view(self):
        """Test getting templates for a specific view."""
        analyzer = ViewAnalyzer()

        # Add some test data
        analyzer._add_template_reference("view1.py", "template1.html")
        analyzer._add_template_reference("view1.py", "template2.html")
        analyzer._add_template_reference("view2.py", "template3.html")

        templates = analyzer.get_templates_for_view("view1.py")

        assert "template1.html" in templates
        assert "template2.html" in templates
        assert "template3.html" not in templates

    def test_get_unused_templates(self):
        """Test finding unused templates."""
        analyzer = ViewAnalyzer()

        # Add some references
        analyzer._add_template_reference("view1.py", "used1.html")
        analyzer._add_template_reference("view2.py", "used2.html")

        # Define all templates
        all_templates = {"used1.html", "used2.html", "unused1.html", "unused2.html"}

        unused = analyzer.get_unused_templates(all_templates)

        assert "unused1.html" in unused
        assert "unused2.html" in unused
        assert "used1.html" not in unused
        assert "used2.html" not in unused
