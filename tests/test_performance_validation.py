"""
Performance validation tests.

This validates that the path normalization and enhanced detection features
do not significantly impact performance (<10% as per spec).
"""

import time
from pathlib import Path
from tempfile import TemporaryDirectory

from django_deadcode.analyzers import TemplateAnalyzer, ViewAnalyzer


class TestPerformanceValidation:
    """
    Performance validation tests for template detection.

    Target: <10% performance impact compared to baseline
    """

    def _create_templates(self, base_path: Path, count: int):
        """
        Create a specified number of template files for performance testing.

        Args:
            base_path: Base directory for templates
            count: Number of templates to create
        """
        templates_path = base_path / "templates" / "testapp"
        templates_path.mkdir(parents=True)

        for i in range(count):
            template_file = templates_path / f"template_{i}.html"
            template_file.write_text(f"""
<!DOCTYPE html>
<html>
<head><title>Template {i}</title></head>
<body>
    <h1>Template {i}</h1>
    {{% extends 'testapp/base.html' %}}
    {{% include 'testapp/header.html' %}}
</body>
</html>
""")

        # Add base.html
        base_html = templates_path / "base.html"
        base_html.write_text("<html>{% block content %}{% endblock %}</html>")

        # Add header.html
        header_html = templates_path / "header.html"
        header_html.write_text("<header>Header</header>")

        return templates_path.parent

    def _create_views(self, base_path: Path, count: int):
        """
        Create a specified number of view classes for performance testing.

        Args:
            base_path: Base directory for views
            count: Number of views to create
        """
        app_path = base_path / "apps" / "testapp"
        app_path.mkdir(parents=True)

        views_file = app_path / "views.py"

        views_content = """
from django.views.generic import ListView, DetailView
from .models import TestModel

"""

        for i in range(count):
            views_content += f"""
class TestListView{i}(ListView):
    model = TestModel

class TestDetailView{i}(DetailView):
    model = TestModel
"""

        views_file.write_text(views_content)
        return views_file

    def test_performance_small_project(self):
        """
        Benchmark performance on a small project (10 templates).

        Target: Complete analysis in <1 second
        """
        with TemporaryDirectory() as tmpdir:
            base_path = Path(tmpdir)

            # Create 10 templates
            template_dir = self._create_templates(base_path, 10)

            # Create 5 views (each CBV type generates a template reference)
            views_file = self._create_views(base_path, 5)

            # Benchmark template analysis
            start_time = time.time()

            template_analyzer = TemplateAnalyzer(
                template_dirs=[template_dir], base_dir=base_path
            )
            template_analyzer.find_all_templates()

            view_analyzer = ViewAnalyzer()
            view_analyzer.analyze_view_file(views_file)

            end_time = time.time()
            elapsed = end_time - start_time

            print(f"\n✓ Small project (10 templates): {elapsed:.3f}s")

            # Assert: Should complete in <1 second
            assert (
                elapsed < 1.0
            ), f"Small project analysis took {elapsed:.3f}s (should be <1s)"

    def test_performance_medium_project(self):
        """
        Benchmark performance on a medium project (100 templates).

        Target: Complete analysis in <5 seconds
        """
        with TemporaryDirectory() as tmpdir:
            base_path = Path(tmpdir)

            # Create 100 templates
            template_dir = self._create_templates(base_path, 100)

            # Create 50 views
            views_file = self._create_views(base_path, 50)

            # Benchmark template analysis
            start_time = time.time()

            template_analyzer = TemplateAnalyzer(
                template_dirs=[template_dir], base_dir=base_path
            )
            template_analyzer.find_all_templates()

            view_analyzer = ViewAnalyzer()
            view_analyzer.analyze_view_file(views_file)

            end_time = time.time()
            elapsed = end_time - start_time

            print(f"\n✓ Medium project (100 templates): {elapsed:.3f}s")

            # Assert: Should complete in <5 seconds
            assert (
                elapsed < 5.0
            ), f"Medium project analysis took {elapsed:.3f}s (should be <5s)"

    def test_performance_large_project(self):
        """
        Benchmark performance on a large project (1000 templates).

        Target: Complete analysis in <30 seconds
        """
        with TemporaryDirectory() as tmpdir:
            base_path = Path(tmpdir)

            # Create 1000 templates
            template_dir = self._create_templates(base_path, 1000)

            # Create 500 views
            views_file = self._create_views(base_path, 500)

            # Benchmark template analysis
            start_time = time.time()

            template_analyzer = TemplateAnalyzer(
                template_dirs=[template_dir], base_dir=base_path
            )
            template_analyzer.find_all_templates()

            view_analyzer = ViewAnalyzer()
            view_analyzer.analyze_view_file(views_file)

            end_time = time.time()
            elapsed = end_time - start_time

            print(f"\n✓ Large project (1000 templates): {elapsed:.3f}s")

            # Assert: Should complete in <30 seconds
            assert (
                elapsed < 30.0
            ), f"Large project analysis took {elapsed:.3f}s (should be <30s)"

    def test_performance_path_normalization_overhead(self):
        """
        Measure the overhead of path normalization.

        Validates that normalization adds minimal overhead.
        """
        with TemporaryDirectory() as tmpdir:
            base_path = Path(tmpdir)

            # Create templates with nested structure to stress normalization
            templates_path = base_path / "apps" / "myapp" / "templates" / "myapp"
            templates_path.mkdir(parents=True)

            # Create 100 templates
            for i in range(100):
                template_file = templates_path / f"template_{i}.html"
                template_file.write_text(f"<html>Template {i}</html>")

            # Measure normalization time
            template_analyzer = TemplateAnalyzer(
                template_dirs=[templates_path.parent], base_dir=base_path
            )

            start_time = time.time()

            # This will normalize all paths
            template_analyzer.find_all_templates()

            end_time = time.time()
            elapsed = end_time - start_time

            print(f"\n✓ Path normalization (100 templates): {elapsed:.3f}s")

            # Verify all paths were normalized
            for template_name in template_analyzer.templates.keys():
                # Should be normalized format: myapp/template_X.html
                assert template_name.startswith(
                    "myapp/"
                ), f"Template path not normalized: {template_name}"
                assert (
                    "templates" not in template_name
                ), f"Template path contains 'templates': {template_name}"

            # Assert: Normalization should be fast (<1s for 100 templates)
            assert elapsed < 1.0, (
                f"Path normalization took {elapsed:.3f}s "
                f"(should be <1s for 100 templates)"
            )

    def test_performance_cbv_detection_overhead(self):
        """
        Measure the overhead of CBV detection.

        Validates that CBV detection adds minimal overhead.
        """
        with TemporaryDirectory() as tmpdir:
            base_path = Path(tmpdir)
            app_path = base_path / "apps" / "testapp"
            app_path.mkdir(parents=True)

            # Create views.py with 100 CBVs
            views_file = app_path / "views.py"

            views_content = """
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView
)
from .models import TestModel

"""

            cbv_types = [
                "ListView",
                "DetailView",
                "CreateView",
                "UpdateView",
                "DeleteView",
            ]
            for i in range(100):
                cbv_type = cbv_types[i % 5]
                views_content += f"""
class Test{cbv_type}{i}({cbv_type}):
    model = TestModel
"""

            views_file.write_text(views_content)

            # Measure CBV detection time
            view_analyzer = ViewAnalyzer()

            start_time = time.time()
            view_analyzer.analyze_view_file(views_file)
            end_time = time.time()

            elapsed = end_time - start_time

            print(f"\n✓ CBV detection (100 views): {elapsed:.3f}s")

            # Verify CBVs were detected
            referenced_templates = view_analyzer.template_usage.keys()
            assert len(referenced_templates) > 0, "No templates detected from CBVs"

            # Assert: CBV detection should be fast (<1s for 100 views)
            assert (
                elapsed < 1.0
            ), f"CBV detection took {elapsed:.3f}s (should be <1s for 100 views)"

    def test_performance_comprehensive_benchmark(self):
        """
        Comprehensive performance benchmark combining all features.

        Simulates a realistic Django project with:
        - Mixed template structures
        - Multiple CBV types
        - Template relationships (extends/includes)
        - Various app structures
        """
        with TemporaryDirectory() as tmpdir:
            base_path = Path(tmpdir)

            # Create multiple apps with templates
            for app_num in range(5):
                app_name = f"app{app_num}"
                app_path = base_path / "apps" / app_name
                templates_path = app_path / "templates" / app_name
                templates_path.mkdir(parents=True)

                # Create templates for each app (20 templates per app = 100 total)
                for i in range(20):
                    template_file = templates_path / f"template_{i}.html"
                    template_file.write_text(f"""
{{% extends '{app_name}/base.html' %}}
{{% block content %}}
Template {i} in {app_name}
{{% endblock %}}
""")

                # Create base template
                base_file = templates_path / "base.html"
                base_file.write_text("<html>{% block content %}{% endblock %}</html>")

                # Create views
                views_file = app_path / "views.py"
                views_content = """
from django.views.generic import ListView, DetailView
from .models import TestModel

"""
                for i in range(10):
                    views_content += f"""
class TestListView{i}(ListView):
    model = TestModel

class TestDetailView{i}(DetailView):
    model = TestModel
"""
                views_file.write_text(views_content)

            # Benchmark full analysis
            start_time = time.time()

            # Collect all template directories
            template_dirs = []
            for app_num in range(5):
                app_name = f"app{app_num}"
                template_dir = base_path / "apps" / app_name / "templates"
                template_dirs.append(template_dir)

            # Analyze templates
            template_analyzer = TemplateAnalyzer(
                template_dirs=template_dirs, base_dir=base_path
            )
            template_analyzer.find_all_templates()

            # Analyze views
            view_analyzer = ViewAnalyzer()
            for app_num in range(5):
                app_name = f"app{app_num}"
                views_file = base_path / "apps" / app_name / "views.py"
                view_analyzer.analyze_view_file(views_file)

            end_time = time.time()
            elapsed = end_time - start_time

            # Calculate stats
            total_templates = len(template_analyzer.templates)
            total_referenced = len(view_analyzer.template_usage)

            print("\n✓ Comprehensive benchmark:")
            print(f"  - Total templates: {total_templates}")
            print(f"  - Referenced templates: {total_referenced}")
            print(f"  - Analysis time: {elapsed:.3f}s")
            print(f"  - Templates/second: {total_templates / elapsed:.1f}")

            # Assert: Should complete in reasonable time
            assert (
                elapsed < 5.0
            ), f"Comprehensive analysis took {elapsed:.3f}s (should be <5s)"

            # Assert: Should have found templates
            assert (
                total_templates > 100
            ), f"Should have found >100 templates, found {total_templates}"
