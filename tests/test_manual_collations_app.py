"""
Manual validation test for the collations app example from the spec.

This test validates that the specific false positives mentioned in the spec
are now correctly identified as used templates.

False positives from spec:
- collations/base.html (extended by other templates)
- collations/collection_detail.html (DetailView default)
- collations/collection_list.html (ListView default)
"""

from pathlib import Path
from tempfile import TemporaryDirectory

from django_deadcode.analyzers import TemplateAnalyzer, ViewAnalyzer


class TestCollationsAppExample:
    """
    Test the collations app example from the specification.

    This validates that all three example false positives are now correctly
    identified as used templates.
    """

    def test_collations_app_no_false_positives(self):
        """
        Verify collations app templates are correctly identified as used.

        Tests all three false positives mentioned in the spec:
        1. base.html - Referenced via {% extends %} in other templates
        2. collection_detail.html - Implicitly used by DetailView
        3. collection_list.html - Implicitly used by ListView
        """
        with TemporaryDirectory() as tmpdir:
            base_path = Path(tmpdir)

            # Create Django project structure
            app_path = base_path / "apps" / "collations"
            templates_path = app_path / "templates" / "collations"
            templates_path.mkdir(parents=True)

            # Create views.py with ListView and DetailView
            views_file = app_path / "views.py"
            views_file.write_text("""
from django.views.generic import ListView, DetailView
from .models import Collection

class CollectionListView(ListView):
    model = Collection
    # No template_name - should detect collations/collection_list.html

class CollectionDetailView(DetailView):
    model = Collection
    # No template_name - should detect collations/collection_detail.html
""")

            # Create base.html
            base_html = templates_path / "base.html"
            base_html.write_text("""
<!DOCTYPE html>
<html>
<head><title>{% block title %}Collations{% endblock %}</title></head>
<body>
    {% block content %}{% endblock %}
</body>
</html>
""")

            # Create collection_list.html (extends base.html)
            list_html = templates_path / "collection_list.html"
            list_html.write_text("""
{% extends 'collations/base.html' %}

{% block title %}Collections{% endblock %}

{% block content %}
<h1>Collections</h1>
<ul>
{% for collection in object_list %}
    <li>{{ collection.name }}</li>
{% endfor %}
</ul>
{% endblock %}
""")

            # Create collection_detail.html (extends base.html)
            detail_html = templates_path / "collection_detail.html"
            detail_html.write_text("""
{% extends 'collations/base.html' %}

{% block title %}{{ object.name }}{% endblock %}

{% block content %}
<h1>{{ object.name }}</h1>
<p>{{ object.description }}</p>
{% endblock %}
""")

            # Analyze templates
            template_analyzer = TemplateAnalyzer(
                template_dirs=[templates_path.parent], base_dir=base_path
            )
            template_analyzer.find_all_templates()

            # Analyze views
            view_analyzer = ViewAnalyzer()
            view_analyzer.analyze_view_file(views_file)

            # Get all templates and referenced templates
            all_templates = set(template_analyzer.templates.keys())
            directly_referenced = set(view_analyzer.template_usage.keys())

            # Get template relationships
            relationships = template_analyzer.get_template_relationships()

            # Simulate transitive closure (like in finddeadcode.py)
            transitively_referenced = set()
            to_process = list(directly_referenced)
            processed = set()

            while to_process:
                current = to_process.pop()
                if current in processed:
                    continue
                processed.add(current)

                # Add extended templates
                if current in relationships.get("extends", {}):
                    for extended in relationships["extends"][current]:
                        if extended not in transitively_referenced:
                            transitively_referenced.add(extended)
                            to_process.append(extended)

                # Add included templates
                if current in relationships.get("includes", {}):
                    for included in relationships["includes"][current]:
                        if included not in transitively_referenced:
                            transitively_referenced.add(included)
                            to_process.append(included)

            # All referenced templates (direct + transitive)
            all_referenced = directly_referenced | transitively_referenced

            # Potentially unused templates
            potentially_unused = all_templates - all_referenced

            # ASSERTIONS: Verify NO false positives

            # 1. Verify collection_list.html is NOT flagged as unused
            # (should be detected by ListView default)
            assert (
                "collations/collection_list.html" in all_templates
            ), "collection_list.html should be discovered"
            assert "collations/collection_list.html" not in potentially_unused, (
                "collection_list.html should NOT be flagged as unused "
                "(ListView default)"
            )
            assert "collations/collection_list.html" in directly_referenced, (
                "collection_list.html should be in directly_referenced " "from ListView"
            )

            # 2. Verify collection_detail.html is NOT flagged as unused
            # (should be detected by DetailView default)
            assert (
                "collations/collection_detail.html" in all_templates
            ), "collection_detail.html should be discovered"
            assert "collations/collection_detail.html" not in potentially_unused, (
                "collection_detail.html should NOT be flagged as unused "
                "(DetailView default)"
            )
            assert "collations/collection_detail.html" in directly_referenced, (
                "collection_detail.html should be in directly_referenced "
                "from DetailView"
            )

            # 3. Verify base.html is NOT flagged as unused
            # (should be detected via extends relationship)
            assert (
                "collations/base.html" in all_templates
            ), "base.html should be discovered"
            assert (
                "collations/base.html" not in potentially_unused
            ), "base.html should NOT be flagged as unused (extends relationship)"
            assert (
                "collations/base.html" in transitively_referenced
            ), "base.html should be in transitively_referenced via extends"

            # Summary assertion: NO templates should be flagged as unused
            assert len(potentially_unused) == 0, (
                f"All templates should be correctly identified as used. "
                f"Found unused: {potentially_unused}"
            )

            print("\n✓ All collations app templates correctly identified as used!")
            print(f"  - Templates discovered: {len(all_templates)}")
            print(f"  - Directly referenced: {len(directly_referenced)}")
            print(f"  - Transitively referenced: {len(transitively_referenced)}")
            print(f"  - Potentially unused: {len(potentially_unused)}")

    def test_collations_app_base_html_extends_relationship(self):
        """
        Specifically test that base.html is correctly marked as used via extends.
        """
        with TemporaryDirectory() as tmpdir:
            base_path = Path(tmpdir)
            templates_path = base_path / "templates" / "collations"
            templates_path.mkdir(parents=True)

            # Create base.html
            base_html = templates_path / "base.html"
            base_html.write_text("<html>{% block content %}{% endblock %}</html>")

            # Create child.html that extends base.html
            child_html = templates_path / "child.html"
            child_html.write_text("{% extends 'collations/base.html' %}")

            # Create a view that uses child.html
            views_path = base_path / "views.py"
            views_path.write_text("""
from django.shortcuts import render

def my_view(request):
    return render(request, 'collations/child.html')
""")

            # Analyze templates
            template_analyzer = TemplateAnalyzer(
                template_dirs=[templates_path.parent], base_dir=base_path
            )
            template_analyzer.find_all_templates()

            # Analyze views
            view_analyzer = ViewAnalyzer()
            view_analyzer.analyze_view_file(views_path)

            # Verify relationships
            relationships = template_analyzer.get_template_relationships()

            # child.html should extend base.html
            assert "collations/child.html" in relationships["extends"]
            extends_dict = relationships["extends"]["collations/child.html"]
            assert "collations/base.html" in extends_dict

            # Verify path normalization worked
            assert "collations/base.html" in template_analyzer.templates
            assert "collations/child.html" in template_analyzer.templates

            print("\n✓ Base template extends relationship correctly detected!")

    def test_collations_app_listview_implicit_template(self):
        """
        Specifically test that ListView correctly detects implicit template name.
        """
        with TemporaryDirectory() as tmpdir:
            base_path = Path(tmpdir)
            app_path = base_path / "apps" / "collations"
            app_path.mkdir(parents=True)

            # Create views.py with ListView
            views_file = app_path / "views.py"
            views_file.write_text("""
from django.views.generic import ListView
from .models import Collection

class CollectionListView(ListView):
    model = Collection
""")

            # Analyze view
            view_analyzer = ViewAnalyzer()
            view_analyzer.analyze_view_file(views_file)

            # Verify implicit template was detected
            referenced_templates = set(view_analyzer.template_usage.keys())

            assert "collations/collection_list.html" in referenced_templates, (
                "ListView should generate implicit template name: "
                "collations/collection_list.html"
            )

            print("\n✓ ListView implicit template correctly detected!")

    def test_collations_app_detailview_implicit_template(self):
        """
        Specifically test that DetailView correctly detects implicit template name.
        """
        with TemporaryDirectory() as tmpdir:
            base_path = Path(tmpdir)
            app_path = base_path / "apps" / "collations"
            app_path.mkdir(parents=True)

            # Create views.py with DetailView
            views_file = app_path / "views.py"
            views_file.write_text("""
from django.views.generic import DetailView
from .models import Collection

class CollectionDetailView(DetailView):
    model = Collection
""")

            # Analyze view
            view_analyzer = ViewAnalyzer()
            view_analyzer.analyze_view_file(views_file)

            # Verify implicit template was detected
            referenced_templates = set(view_analyzer.template_usage.keys())

            assert "collations/collection_detail.html" in referenced_templates, (
                "DetailView should generate implicit template name: "
                "collations/collection_detail.html"
            )

            print("\n✓ DetailView implicit template correctly detected!")
