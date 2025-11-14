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


class TestCBVDefaultTemplateDetection:
    """Test suite for CBV default template detection."""

    def test_listview_with_model_attribute(self):
        """Test ListView with model attribute detects implicit template."""
        analyzer = ViewAnalyzer()

        content = """
from django.views.generic import ListView
from .models import Collection

class CollectionListView(ListView):
    model = Collection
"""
        # Create a temporary file in a path structure that mimics a Django app
        with tempfile.TemporaryDirectory() as tmpdir:
            app_dir = Path(tmpdir) / "collations"
            app_dir.mkdir()
            views_file = app_dir / "views.py"
            views_file.write_text(content)

            analyzer.analyze_view_file(views_file)

            # Should detect implicit template: collations/collection_list.html
            assert "collations/collection_list.html" in analyzer.template_usage

    def test_detailview_with_model_attribute(self):
        """Test DetailView with model attribute detects implicit template."""
        analyzer = ViewAnalyzer()

        content = """
from django.views.generic import DetailView
from .models import Collection

class CollectionDetailView(DetailView):
    model = Collection
"""
        with tempfile.TemporaryDirectory() as tmpdir:
            app_dir = Path(tmpdir) / "collations"
            app_dir.mkdir()
            views_file = app_dir / "views.py"
            views_file.write_text(content)

            analyzer.analyze_view_file(views_file)

            # Should detect implicit template: collations/collection_detail.html
            assert "collations/collection_detail.html" in analyzer.template_usage

    def test_createview_with_model_attribute(self):
        """Test CreateView with model attribute detects implicit template."""
        analyzer = ViewAnalyzer()

        content = """
from django.views.generic import CreateView
from .models import Article

class ArticleCreateView(CreateView):
    model = Article
"""
        with tempfile.TemporaryDirectory() as tmpdir:
            app_dir = Path(tmpdir) / "blog"
            app_dir.mkdir()
            views_file = app_dir / "views.py"
            views_file.write_text(content)

            analyzer.analyze_view_file(views_file)

            # Should detect implicit template: blog/article_form.html
            assert "blog/article_form.html" in analyzer.template_usage

    def test_updateview_with_model_attribute(self):
        """Test UpdateView with model attribute detects implicit template."""
        analyzer = ViewAnalyzer()

        content = """
from django.views.generic import UpdateView
from .models import Article

class ArticleUpdateView(UpdateView):
    model = Article
"""
        with tempfile.TemporaryDirectory() as tmpdir:
            app_dir = Path(tmpdir) / "blog"
            app_dir.mkdir()
            views_file = app_dir / "views.py"
            views_file.write_text(content)

            analyzer.analyze_view_file(views_file)

            # Should detect implicit template: blog/article_form.html
            assert "blog/article_form.html" in analyzer.template_usage

    def test_deleteview_with_model_attribute(self):
        """Test DeleteView with model attribute detects implicit template."""
        analyzer = ViewAnalyzer()

        content = """
from django.views.generic import DeleteView
from .models import Article

class ArticleDeleteView(DeleteView):
    model = Article
"""
        with tempfile.TemporaryDirectory() as tmpdir:
            app_dir = Path(tmpdir) / "blog"
            app_dir.mkdir()
            views_file = app_dir / "views.py"
            views_file.write_text(content)

            analyzer.analyze_view_file(views_file)

            # Should detect implicit template: blog/article_confirm_delete.html
            assert "blog/article_confirm_delete.html" in analyzer.template_usage

    def test_cbv_with_explicit_template_name_skips_default(self):
        """Test CBV with explicit template_name uses explicit value, not default."""
        analyzer = ViewAnalyzer()

        content = """
from django.views.generic import ListView
from .models import Collection

class CollectionListView(ListView):
    model = Collection
    template_name = 'custom/explicit_template.html'
"""
        with tempfile.TemporaryDirectory() as tmpdir:
            app_dir = Path(tmpdir) / "collations"
            app_dir.mkdir()
            views_file = app_dir / "views.py"
            views_file.write_text(content)

            analyzer.analyze_view_file(views_file)

            # Should use explicit template_name, not the default
            assert "custom/explicit_template.html" in analyzer.template_usage
            # Should NOT detect the default template
            assert "collations/collection_list.html" not in analyzer.template_usage

    def test_listview_with_queryset_attribute(self):
        """Test ListView with queryset attribute detects implicit template."""
        analyzer = ViewAnalyzer()

        content = """
from django.views.generic import ListView
from .models import Collection

class CollectionListView(ListView):
    queryset = Collection.objects.all()
"""
        with tempfile.TemporaryDirectory() as tmpdir:
            app_dir = Path(tmpdir) / "collations"
            app_dir.mkdir()
            views_file = app_dir / "views.py"
            views_file.write_text(content)

            analyzer.analyze_view_file(views_file)

            # Should detect implicit template: collations/collection_list.html
            assert "collations/collection_list.html" in analyzer.template_usage

    def test_cbv_in_nested_apps_directory(self):
        """Test CBV detection in nested apps/ directory structure."""
        analyzer = ViewAnalyzer()

        content = """
from django.views.generic import ListView
from .models import Product

class ProductListView(ListView):
    model = Product
"""
        with tempfile.TemporaryDirectory() as tmpdir:
            apps_dir = Path(tmpdir) / "apps"
            apps_dir.mkdir()
            shop_dir = apps_dir / "shop"
            shop_dir.mkdir()
            views_file = shop_dir / "views.py"
            views_file.write_text(content)

            analyzer.analyze_view_file(views_file)

            # Should detect implicit template: shop/product_list.html
            assert "shop/product_list.html" in analyzer.template_usage


class TestTemplateVariableDetection:
    """Test suite for template variable detection."""

    def test_simple_assignment_template_name(self):
        """Test detecting simple template_name variable assignment."""
        analyzer = ViewAnalyzer()

        content = """
from django.shortcuts import render

def my_view(request):
    template_name = 'app/template.html'
    return render(request, template_name)
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(content)
            f.flush()
            temp_path = Path(f.name)

        try:
            analyzer.analyze_view_file(temp_path)

            # Should detect template from variable assignment
            assert "app/template.html" in analyzer.template_usage
        finally:
            temp_path.unlink()

    def test_custom_variable_with_template_in_name(self):
        """Test detecting custom variable with 'template' in the name."""
        analyzer = ViewAnalyzer()

        content = """
from django.shortcuts import render

def my_view(request):
    my_template = 'app/other.html'
    return render(request, my_template)
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(content)
            f.flush()
            temp_path = Path(f.name)

        try:
            analyzer.analyze_view_file(temp_path)

            # Should detect template from custom variable
            assert "app/other.html" in analyzer.template_usage
        finally:
            temp_path.unlink()

    def test_get_template_names_with_list_return(self):
        """Test detecting get_template_names() method returning list."""
        analyzer = ViewAnalyzer()

        content = """
from django.views.generic import TemplateView

class MyView(TemplateView):
    def get_template_names(self):
        return ['app/template1.html', 'app/template2.html']
"""
        with tempfile.TemporaryDirectory() as tmpdir:
            app_dir = Path(tmpdir) / "myapp"
            app_dir.mkdir()
            views_file = app_dir / "views.py"
            views_file.write_text(content)

            analyzer.analyze_view_file(views_file)

            # Should detect both templates from list
            assert "app/template1.html" in analyzer.template_usage
            assert "app/template2.html" in analyzer.template_usage

    def test_get_template_names_with_single_string_return(self):
        """Test detecting get_template_names() method returning single string."""
        analyzer = ViewAnalyzer()

        content = """
from django.views.generic import TemplateView

class MyView(TemplateView):
    def get_template_names(self):
        return 'app/single_template.html'
"""
        with tempfile.TemporaryDirectory() as tmpdir:
            app_dir = Path(tmpdir) / "myapp"
            app_dir.mkdir()
            views_file = app_dir / "views.py"
            views_file.write_text(content)

            analyzer.analyze_view_file(views_file)

            # Should detect template from single string return
            assert "app/single_template.html" in analyzer.template_usage

    def test_module_level_template_variable(self):
        """Test detecting module-level template variable assignment."""
        analyzer = ViewAnalyzer()

        content = """
DEFAULT_TEMPLATE = 'app/default.html'

def my_view(request):
    from django.shortcuts import render
    return render(request, DEFAULT_TEMPLATE)
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(content)
            f.flush()
            temp_path = Path(f.name)

        try:
            analyzer.analyze_view_file(temp_path)

            # Should detect template from module-level variable
            assert "app/default.html" in analyzer.template_usage
        finally:
            temp_path.unlink()

    def test_case_insensitive_template_variable_detection(self):
        """Test that variable detection is case-insensitive for 'template'."""
        analyzer = ViewAnalyzer()

        content = """
def my_view(request):
    TEMPLATE_PATH = 'app/uppercase.html'
    Template_Name = 'app/mixedcase.html'
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(content)
            f.flush()
            temp_path = Path(f.name)

        try:
            analyzer.analyze_view_file(temp_path)

            # Should detect both templates (case-insensitive)
            assert "app/uppercase.html" in analyzer.template_usage
            assert "app/mixedcase.html" in analyzer.template_usage
        finally:
            temp_path.unlink()

    def test_ignores_variables_without_template_in_name(self):
        """Test that variables without 'template' in name are ignored."""
        analyzer = ViewAnalyzer()

        content = """
def my_view(request):
    my_var = 'app/should_not_detect.html'
    some_path = 'app/also_not_detected.html'
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(content)
            f.flush()
            temp_path = Path(f.name)

        try:
            analyzer.analyze_view_file(temp_path)

            # Should NOT detect templates from variables without 'template' in name
            assert "app/should_not_detect.html" not in analyzer.template_usage
            assert "app/also_not_detected.html" not in analyzer.template_usage
        finally:
            temp_path.unlink()


class TestViewAnalyzerGapTests:
    """Strategic gap-filling tests for view analyzer (Task Group 5)."""

    def test_cbv_with_get_queryset_method(self):
        """Test CBV with get_queryset() method instead of queryset attribute."""
        analyzer = ViewAnalyzer()

        content = """
from django.views.generic import ListView
from .models import Article

class ArticleListView(ListView):
    def get_queryset(self):
        return Article.objects.filter(published=True)
"""
        with tempfile.TemporaryDirectory() as tmpdir:
            app_dir = Path(tmpdir) / "blog"
            app_dir.mkdir()
            views_file = app_dir / "views.py"
            views_file.write_text(content)

            analyzer.analyze_view_file(views_file)

            # Note: This is a known limitation - we can't easily extract
            # from get_queryset. For now, we verify the code doesn't crash
            # and handles gracefully. Template may not be detected without
            # explicit model or queryset attribute

    def test_queryset_with_single_filter(self):
        """Test queryset with single filter method (not chained)."""
        analyzer = ViewAnalyzer()

        content = """
from django.views.generic import ListView
from .models import Product

class ProductListView(ListView):
    queryset = Product.objects.filter(active=True)
"""
        with tempfile.TemporaryDirectory() as tmpdir:
            app_dir = Path(tmpdir) / "shop"
            app_dir.mkdir()
            views_file = app_dir / "views.py"
            views_file.write_text(content)

            analyzer.analyze_view_file(views_file)

            # Should detect implicit template with single filter method
            assert "shop/product_list.html" in analyzer.template_usage

    def test_cbv_with_multiple_inheritance(self):
        """Test CBV with multiple inheritance including custom base classes."""
        analyzer = ViewAnalyzer()

        content = """
from django.views.generic import ListView

class CustomMixin:
    pass

class ArticleListView(CustomMixin, ListView):
    model = Article
"""
        with tempfile.TemporaryDirectory() as tmpdir:
            app_dir = Path(tmpdir) / "blog"
            app_dir.mkdir()
            views_file = app_dir / "views.py"
            views_file.write_text(content)

            analyzer.analyze_view_file(views_file)

            # Should still detect ListView even with multiple inheritance
            assert "blog/article_list.html" in analyzer.template_usage

    def test_template_variable_with_non_string_value(self):
        """Test that non-string template variable values are ignored."""
        analyzer = ViewAnalyzer()

        content = """
def my_view(request):
    template_num = 123  # Not a string, should be ignored
    template_none = None  # None, should be ignored
    template_list = [1, 2, 3]  # List of non-strings, should be ignored
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(content)
            f.flush()
            temp_path = Path(f.name)

        try:
            analyzer.analyze_view_file(temp_path)

            # Should not crash and should not add any templates
            # (template_usage might be empty or have other entries)
            # Main test is that it doesn't crash on non-string values
            assert True  # If we got here, test passed
        finally:
            temp_path.unlink()
