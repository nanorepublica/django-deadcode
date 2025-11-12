"""Tests for the reverse analyzer."""

import tempfile
from pathlib import Path

from django_deadcode.analyzers import ReverseAnalyzer


class TestReverseAnalyzer:
    """Test suite for ReverseAnalyzer."""

    # Task Group 2 Tests (Foundation)

    def test_detect_reverse_call(self):
        """Test extracting URL name from reverse() call."""
        analyzer = ReverseAnalyzer()

        content = """
from django.urls import reverse

def my_view(request):
    url = reverse('my-url-name')
    return redirect(url)
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(content)
            f.flush()
            temp_path = Path(f.name)

        try:
            analyzer.analyze_python_file(temp_path)

            # Check that URL name was found
            referenced_urls = analyzer.get_referenced_urls()
            assert "my-url-name" in referenced_urls
        finally:
            temp_path.unlink()

    def test_detect_reverse_lazy_call(self):
        """Test extracting URL name from reverse_lazy() call."""
        analyzer = ReverseAnalyzer()

        content = """
from django.urls import reverse_lazy

class MyView:
    success_url = reverse_lazy('success-page')
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(content)
            f.flush()
            temp_path = Path(f.name)

        try:
            analyzer.analyze_python_file(temp_path)

            # Check that URL name was found
            referenced_urls = analyzer.get_referenced_urls()
            assert "success-page" in referenced_urls
        finally:
            temp_path.unlink()

    def test_detect_redirect_call(self):
        """Test extracting URL name from redirect() call."""
        analyzer = ReverseAnalyzer()

        content = """
from django.shortcuts import redirect

def my_view(request):
    return redirect('home-page')
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(content)
            f.flush()
            temp_path = Path(f.name)

        try:
            analyzer.analyze_python_file(temp_path)

            # Check that URL name was found
            referenced_urls = analyzer.get_referenced_urls()
            assert "home-page" in referenced_urls
        finally:
            temp_path.unlink()

    def test_detect_http_response_redirect(self):
        """Test extracting URL name from HttpResponseRedirect(reverse()) call."""
        analyzer = ReverseAnalyzer()

        content = """
from django.http import HttpResponseRedirect
from django.urls import reverse

def my_view(request):
    return HttpResponseRedirect(reverse('detail-page'))
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(content)
            f.flush()
            temp_path = Path(f.name)

        try:
            analyzer.analyze_python_file(temp_path)

            # Check that URL name was found
            referenced_urls = analyzer.get_referenced_urls()
            assert "detail-page" in referenced_urls
        finally:
            temp_path.unlink()

    def test_detect_multiple_patterns(self):
        """Test detecting multiple different calls in same file."""
        analyzer = ReverseAnalyzer()

        content = """
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.http import HttpResponseRedirect

def view1(request):
    return redirect('url1')

def view2(request):
    url = reverse('url2')
    return HttpResponseRedirect(url)

class MyView:
    success_url = reverse_lazy('url3')

def view3(request):
    return HttpResponseRedirect(reverse('url4'))
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(content)
            f.flush()
            temp_path = Path(f.name)

        try:
            analyzer.analyze_python_file(temp_path)

            # Check that all URL names were found
            referenced_urls = analyzer.get_referenced_urls()
            assert "url1" in referenced_urls
            assert "url2" in referenced_urls
            assert "url3" in referenced_urls
            assert "url4" in referenced_urls
            assert len(referenced_urls) == 4
        finally:
            temp_path.unlink()

    def test_ignore_method_calls(self):
        """Test that method calls like self.reverse() are ignored."""
        analyzer = ReverseAnalyzer()

        content = """
class MyClass:
    def reverse(self):
        return "reversed"

    def my_method(self):
        result = self.reverse()  # Should be ignored
        my_list = [1, 2, 3]
        my_list.reverse()  # Should also be ignored
        return result
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(content)
            f.flush()
            temp_path = Path(f.name)

        try:
            analyzer.analyze_python_file(temp_path)

            # Check that no URL names were found (method calls ignored)
            referenced_urls = analyzer.get_referenced_urls()
            assert len(referenced_urls) == 0
        finally:
            temp_path.unlink()

    def test_get_referenced_urls(self):
        """Test that get_referenced_urls returns correct set."""
        analyzer = ReverseAnalyzer()

        # Manually add some URLs
        analyzer.referenced_urls.add("url1")
        analyzer.referenced_urls.add("url2")
        analyzer.referenced_urls.add("url3")

        urls = analyzer.get_referenced_urls()

        assert isinstance(urls, set)
        assert len(urls) == 3
        assert "url1" in urls
        assert "url2" in urls
        assert "url3" in urls

    def test_namespace_urls(self):
        """Test detecting URL names with namespaces."""
        analyzer = ReverseAnalyzer()

        content = """
from django.urls import reverse

def my_view(request):
    url = reverse('myapp:detail')
    url2 = reverse('admin:index')
    return url
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(content)
            f.flush()
            temp_path = Path(f.name)

        try:
            analyzer.analyze_python_file(temp_path)

            # Check that namespaced URL names were found
            referenced_urls = analyzer.get_referenced_urls()
            assert "myapp:detail" in referenced_urls
            assert "admin:index" in referenced_urls
        finally:
            temp_path.unlink()

    # Task Group 3 Tests (Pattern Detection)

    def test_detect_dynamic_fstring(self):
        """Test detecting and flagging f-string patterns."""
        analyzer = ReverseAnalyzer()

        content = """
from django.urls import reverse

def my_view(request, action):
    url = reverse(f'myapp:{action}_list')
    return url
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(content)
            f.flush()
            temp_path = Path(f.name)

        try:
            analyzer.analyze_python_file(temp_path)

            # Check that dynamic pattern was flagged, not added to referenced URLs
            referenced_urls = analyzer.get_referenced_urls()
            dynamic_patterns = analyzer.get_dynamic_patterns()

            assert len(referenced_urls) == 0  # Should not add to referenced
            assert len(dynamic_patterns) > 0  # Should flag as dynamic

        finally:
            temp_path.unlink()

    def test_detect_dynamic_concatenation(self):
        """Test detecting and flagging string concatenation patterns."""
        analyzer = ReverseAnalyzer()

        content = """
from django.urls import reverse

def my_view(request, prefix):
    url = reverse('prefix_' + prefix)
    return url
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(content)
            f.flush()
            temp_path = Path(f.name)

        try:
            analyzer.analyze_python_file(temp_path)

            # Check that dynamic pattern was flagged
            referenced_urls = analyzer.get_referenced_urls()
            dynamic_patterns = analyzer.get_dynamic_patterns()

            assert len(referenced_urls) == 0
            assert len(dynamic_patterns) > 0

        finally:
            temp_path.unlink()

    def test_skip_malformed_file(self):
        """Test that SyntaxError is handled gracefully."""
        analyzer = ReverseAnalyzer()

        content = """
def my_view(request):
    # This is malformed Python
    return reverse('test'
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(content)
            f.flush()
            temp_path = Path(f.name)

        try:
            # Should not raise an exception
            analyzer.analyze_python_file(temp_path)

            # Should have no results
            referenced_urls = analyzer.get_referenced_urls()
            assert len(referenced_urls) == 0

        finally:
            temp_path.unlink()

    def test_skip_migration_files(self):
        """Test that migration files are excluded from analysis."""
        analyzer = ReverseAnalyzer()

        # Create a temporary directory structure
        with tempfile.TemporaryDirectory() as temp_dir:
            base_path = Path(temp_dir)

            # Create a migrations directory with a file
            migrations_dir = base_path / "migrations"
            migrations_dir.mkdir()

            migration_file = migrations_dir / "0001_initial.py"
            migration_file.write_text(
                """
from django.urls import reverse

def some_function():
    return reverse('should-not-be-found')
""",
                encoding="utf-8",
            )

            # Create a regular file that should be analyzed
            regular_file = base_path / "views.py"
            regular_file.write_text(
                """
from django.urls import reverse

def my_view(request):
    return reverse('should-be-found')
""",
                encoding="utf-8",
            )

            # Analyze all files
            analyzer.analyze_all_python_files(base_path)

            # Check that only the regular file was analyzed
            referenced_urls = analyzer.get_referenced_urls()
            assert "should-be-found" in referenced_urls
            assert "should-not-be-found" not in referenced_urls

    def test_multiple_files_analysis(self):
        """Test scanning multiple files and accumulating results."""
        analyzer = ReverseAnalyzer()

        # Create a temporary directory structure
        with tempfile.TemporaryDirectory() as temp_dir:
            base_path = Path(temp_dir)

            # Create multiple files
            file1 = base_path / "views.py"
            file1.write_text(
                """
from django.urls import reverse

def view1(request):
    return reverse('url-from-file1')
""",
                encoding="utf-8",
            )

            file2 = base_path / "forms.py"
            file2.write_text(
                """
from django.shortcuts import redirect

def form_handler():
    return redirect('url-from-file2')
""",
                encoding="utf-8",
            )

            subdir = base_path / "subapp"
            subdir.mkdir()

            file3 = subdir / "utils.py"
            file3.write_text(
                """
from django.urls import reverse_lazy

success_url = reverse_lazy('url-from-file3')
""",
                encoding="utf-8",
            )

            # Analyze all files
            analyzer.analyze_all_python_files(base_path)

            # Check that all URL names were found
            referenced_urls = analyzer.get_referenced_urls()
            assert "url-from-file1" in referenced_urls
            assert "url-from-file2" in referenced_urls
            assert "url-from-file3" in referenced_urls
            assert len(referenced_urls) == 3

    def test_keyword_argument_reverse(self):
        """Test detecting reverse with viewname keyword argument."""
        analyzer = ReverseAnalyzer()

        content = """
from django.urls import reverse

def my_view(request):
    url = reverse(viewname='my-url-name')
    return url
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(content)
            f.flush()
            temp_path = Path(f.name)

        try:
            analyzer.analyze_python_file(temp_path)

            # Check that URL name was found from keyword argument
            referenced_urls = analyzer.get_referenced_urls()
            assert "my-url-name" in referenced_urls
        finally:
            temp_path.unlink()

    def test_reverse_with_multiple_args(self):
        """Test detecting reverse with multiple arguments."""
        analyzer = ReverseAnalyzer()

        content = """
from django.urls import reverse

def my_view(request):
    url = reverse('detail-page', args=[1, 2])
    url2 = reverse('another-page', kwargs={'id': 1})
    return url
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(content)
            f.flush()
            temp_path = Path(f.name)

        try:
            analyzer.analyze_python_file(temp_path)

            # Check that URL names were found (first argument)
            referenced_urls = analyzer.get_referenced_urls()
            assert "detail-page" in referenced_urls
            assert "another-page" in referenced_urls
        finally:
            temp_path.unlink()
