"""Integration tests for reverse/redirect detection feature."""

import tempfile
from pathlib import Path

from django_deadcode.analyzers import ReverseAnalyzer, TemplateAnalyzer, URLAnalyzer


class TestReverseDetectionIntegration:
    """Integration tests for the reverse/redirect detection feature."""

    def test_reverse_refs_prevent_false_positives(self):
        """
        Test that URLs referenced via reverse() are not reported as unreferenced.

        This is the core use case: a URL pattern that is only referenced in Python
        code via reverse() should NOT appear in the unreferenced URLs list.
        """
        # Create a temporary directory structure
        with tempfile.TemporaryDirectory() as temp_dir:
            base_path = Path(temp_dir)

            # Create a Python file with reverse() call
            views_file = base_path / "views.py"
            views_file.write_text(
                """
from django.shortcuts import redirect
from django.urls import reverse

def my_view(request):
    # This URL is only referenced here, not in any template
    return redirect('detail-page')

def another_view(request):
    url = reverse('list-page')
    return url
""",
                encoding="utf-8",
            )

            # Analyze with ReverseAnalyzer
            reverse_analyzer = ReverseAnalyzer()
            reverse_analyzer.analyze_all_python_files(base_path)

            # Verify URLs were detected
            referenced_urls = reverse_analyzer.get_referenced_urls()
            assert "detail-page" in referenced_urls
            assert "list-page" in referenced_urls
            assert len(referenced_urls) == 2

            # Simulate URLAnalyzer behavior
            all_url_names = {"detail-page", "list-page", "unused-page"}
            url_analyzer = URLAnalyzer()

            # Manually set URL patterns and names (simulating URL analysis)
            for name in all_url_names:
                url_analyzer.url_patterns[name] = {"pattern": f"/{name}/"}
                url_analyzer.url_names.add(name)

            # Get unreferenced URLs (excluding reverse references)
            unreferenced = url_analyzer.get_unreferenced_urls(referenced_urls)

            # Verify that reverse-referenced URLs are NOT in unreferenced list
            assert "detail-page" not in unreferenced
            assert "list-page" not in unreferenced
            assert "unused-page" in unreferenced

    def test_combined_template_and_reverse_refs(self):
        """
        Test URLs referenced in both templates and reverse() calls.

        Some URLs are in templates, some in reverse() calls, some in both.
        All should be excluded from unreferenced list.
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            base_path = Path(temp_dir)

            # Create Python file with reverse() calls
            views_file = base_path / "views.py"
            views_file.write_text(
                """
from django.urls import reverse

def view1(request):
    return reverse('python-only-url')

def view2(request):
    return reverse('shared-url')
""",
                encoding="utf-8",
            )

            # Create template file with {% url %} tags
            templates_dir = base_path / "templates"
            templates_dir.mkdir()
            template_file = templates_dir / "index.html"
            template_file.write_text(
                """
<a href="{% url 'template-only-url' %}">Link</a>
<a href="{% url 'shared-url' %}">Shared</a>
""",
                encoding="utf-8",
            )

            # Analyze with both analyzers
            reverse_analyzer = ReverseAnalyzer()
            reverse_analyzer.analyze_all_python_files(base_path)

            template_analyzer = TemplateAnalyzer()
            template_analyzer.analyze_all_templates(templates_dir)

            # Get references from both sources
            reverse_refs = reverse_analyzer.get_referenced_urls()
            template_refs = template_analyzer.get_referenced_urls()

            # Verify individual sources
            assert "python-only-url" in reverse_refs
            assert "shared-url" in reverse_refs
            assert "template-only-url" in template_refs
            assert "shared-url" in template_refs

            # Combine references (as done in finddeadcode command)
            all_referenced = reverse_refs | template_refs

            # Verify combined set
            assert "python-only-url" in all_referenced
            assert "template-only-url" in all_referenced
            assert "shared-url" in all_referenced
            assert len(all_referenced) == 3

            # Simulate unreferenced URL check
            all_url_names = {
                "python-only-url",
                "template-only-url",
                "shared-url",
                "truly-unused-url",
            }
            url_analyzer = URLAnalyzer()
            for name in all_url_names:
                url_analyzer.url_patterns[name] = {"pattern": f"/{name}/"}
                url_analyzer.url_names.add(name)

            unreferenced = url_analyzer.get_unreferenced_urls(all_referenced)

            # Only truly unused URL should be unreferenced
            assert unreferenced == {"truly-unused-url"}

    def test_dynamic_patterns_not_marked_as_referenced(self):
        """
        Test that dynamic URL patterns (f-strings, etc.) are flagged but not
        marked as referenced.
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            base_path = Path(temp_dir)

            # Create Python file with dynamic reverse() calls
            views_file = base_path / "views.py"
            views_file.write_text(
                """
from django.urls import reverse

def dynamic_view(request, action):
    # F-string pattern - should be flagged as dynamic
    url = reverse(f'myapp:{action}_detail')
    return url

def static_view(request):
    # Static pattern - should be added to referenced URLs
    url = reverse('static-url')
    return url

def concatenation_view(request, prefix):
    # Concatenation pattern - should be flagged as dynamic
    url = reverse('prefix_' + prefix)
    return url
""",
                encoding="utf-8",
            )

            # Analyze with ReverseAnalyzer
            reverse_analyzer = ReverseAnalyzer()
            reverse_analyzer.analyze_all_python_files(base_path)

            # Get results
            referenced_urls = reverse_analyzer.get_referenced_urls()
            dynamic_patterns = reverse_analyzer.get_dynamic_patterns()

            # Verify static URL was added to referenced
            assert "static-url" in referenced_urls

            # Verify dynamic patterns were flagged, not added to referenced
            assert len(dynamic_patterns) > 0
            assert (
                "<dynamic:f-string>" in dynamic_patterns
                or "<dynamic:concatenation>" in dynamic_patterns
            )

            # Verify dynamic URLs were NOT added to referenced
            # (We can't know the exact URL names, so we just check the count)
            assert len(referenced_urls) == 1  # Only 'static-url'

    def test_integration_with_url_analyzer(self):
        """
        Test that ReverseAnalyzer integrates correctly with URLAnalyzer.

        This tests the actual workflow used in the finddeadcode command.
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            base_path = Path(temp_dir)

            # Create Python files with various patterns
            app_dir = base_path / "myapp"
            app_dir.mkdir()

            views_file = app_dir / "views.py"
            views_file.write_text(
                """
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.http import HttpResponseRedirect

def view1(request):
    return redirect('url1')

def view2(request):
    return HttpResponseRedirect(reverse('url2'))

class MyView:
    success_url = reverse_lazy('url3')
""",
                encoding="utf-8",
            )

            forms_file = app_dir / "forms.py"
            forms_file.write_text(
                """
from django.urls import reverse

def get_redirect_url():
    return reverse('url4')
""",
                encoding="utf-8",
            )

            # Create a migration file that should be skipped
            migrations_dir = app_dir / "migrations"
            migrations_dir.mkdir()
            migration_file = migrations_dir / "0001_initial.py"
            migration_file.write_text(
                """
from django.urls import reverse

def do_something():
    # This should be skipped
    return reverse('migration-url')
""",
                encoding="utf-8",
            )

            # Analyze with ReverseAnalyzer
            reverse_analyzer = ReverseAnalyzer()
            reverse_analyzer.analyze_all_python_files(app_dir)

            # Verify URLs from views and forms were found
            referenced_urls = reverse_analyzer.get_referenced_urls()
            assert "url1" in referenced_urls
            assert "url2" in referenced_urls
            assert "url3" in referenced_urls
            assert "url4" in referenced_urls

            # Verify migration URL was NOT found (migrations are skipped)
            assert "migration-url" not in referenced_urls

            # Total should be 4 URLs
            assert len(referenced_urls) == 4

            # Simulate URLAnalyzer interaction
            all_defined_urls = {"url1", "url2", "url3", "url4", "url5", "migration-url"}
            url_analyzer = URLAnalyzer()
            for name in all_defined_urls:
                url_analyzer.url_patterns[name] = {"pattern": f"/{name}/"}
                url_analyzer.url_names.add(name)

            # Get unreferenced URLs
            unreferenced = url_analyzer.get_unreferenced_urls(referenced_urls)

            # url1-url4 are referenced in Python, so only url5 and
            # migration-url are unreferenced
            assert "url1" not in unreferenced
            assert "url2" not in unreferenced
            assert "url3" not in unreferenced
            assert "url4" not in unreferenced
            assert "url5" in unreferenced
            assert "migration-url" in unreferenced

    def test_empty_files_handled_gracefully(self):
        """Test that empty Python files are handled without errors."""
        with tempfile.TemporaryDirectory() as temp_dir:
            base_path = Path(temp_dir)

            # Create an empty Python file
            empty_file = base_path / "empty.py"
            empty_file.write_text("", encoding="utf-8")

            # Create a file with only comments
            comments_file = base_path / "comments.py"
            comments_file.write_text(
                """
# This file only has comments
# reverse('should-not-be-found')
""",
                encoding="utf-8",
            )

            # Analyze
            reverse_analyzer = ReverseAnalyzer()
            reverse_analyzer.analyze_all_python_files(base_path)

            # Should not crash and should find nothing
            referenced_urls = reverse_analyzer.get_referenced_urls()
            assert len(referenced_urls) == 0
