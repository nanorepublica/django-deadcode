# Django Dead Code

We find your buried bones (or code)!

[![PyPI version](https://badge.fury.io/py/django-deadcode.svg)](https://badge.fury.io/py/django-deadcode)
[![CI](https://github.com/nanorepublica/django-deadcode/actions/workflows/ci.yml/badge.svg)](https://github.com/nanorepublica/django-deadcode/actions/workflows/ci.yml)
[![Python versions](https://img.shields.io/pypi/pyversions/django-deadcode.svg)](https://pypi.org/project/django-deadcode/)
[![Django versions](https://img.shields.io/pypi/djversions/django-deadcode.svg)](https://pypi.org/project/django-deadcode/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Django dead code analysis tool that tracks relationships between templates, URLs, and views to help identify and remove unused code.

## Features

- **Template Analysis**: Extract URL references from Django templates (href attributes and `{% url %}` tags)
- **URL Pattern Discovery**: Analyze all URL patterns defined in your Django project
- **View Tracking**: Identify which templates are used by which views
- **Class-Based View Detection**: Automatically detects templates used by CBVs through Django's implicit naming conventions (ListView, DetailView, CreateView, UpdateView, DeleteView)
- **Template Variable Detection**: Detects templates referenced through variables containing 'template' in the name
- **Python Code Analysis**: Detect `reverse()` and `redirect()` URL references in Python code
- **Relationship Mapping**: Track template inheritance (extends/includes) and relationships
- **Smart Template Detection**: Templates referenced via `{% include %}` or `{% extends %}` are correctly marked as used
- **Path Normalization**: Consistent path handling ensures accurate template matching
- **Project Boundary Filtering**: Automatically excludes templates from installed packages (outside BASE_DIR)
- **Multiple Output Formats**: Console, JSON, and Markdown reports
- **Django Native**: Uses Django's management command structure for seamless integration

## Installation

```bash
pip install django-deadcode
```

Or install from source:

```bash
git clone https://github.com/nanorepublica/django-deadcode.git
cd django-deadcode
pip install -e .
```

## Setup

Add `django_deadcode` to your `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    # ... other apps
    'django_deadcode',
]
```

## Usage

### Basic Usage

Run the analysis on your Django project:

```bash
python manage.py finddeadcode
```

This will analyze your entire Django project and output a report to the console.

### Output Formats

**Console output (default):**
```bash
python manage.py finddeadcode
```

**JSON output:**
```bash
python manage.py finddeadcode --format json
```

**Markdown output:**
```bash
python manage.py finddeadcode --format markdown
```

### Save Report to File

```bash
python manage.py finddeadcode --format json --output report.json
```

### Analyze Specific Apps

```bash
python manage.py finddeadcode --apps myapp otherapp
```

### Custom Template Directory

```bash
python manage.py finddeadcode --templates-dir /path/to/templates
```

### Show Template Relationships

By default, template include/extends relationships are hidden in reports. To show them:

```bash
python manage.py finddeadcode --show-template-relationships
```

This is useful for understanding how templates are connected but can make reports verbose for large projects.

## What It Detects

### Unreferenced URL Patterns

URL patterns that are defined in `urls.py` but never referenced in templates or Python code:

```python
# urls.py - This URL is defined
path('old-feature/', views.old_feature, name='old_feature'),

# But no template references it with {% url 'old_feature' %}
# And no Python code uses reverse('old_feature')
```

### Class-Based View Default Templates (NEW)

Automatically detects templates used by class-based views through Django's implicit naming convention:

```python
# views.py
from django.views.generic import ListView, DetailView
from .models import Article

class ArticleListView(ListView):
    model = Article
    # Automatically detects: myapp/article_list.html

class ArticleDetailView(DetailView):
    model = Article
    # Automatically detects: myapp/article_detail.html
```

Supported CBV types:
- `ListView` → `<app_label>/<model_name>_list.html`
- `DetailView` → `<app_label>/<model_name>_detail.html`
- `CreateView` → `<app_label>/<model_name>_form.html`
- `UpdateView` → `<app_label>/<model_name>_form.html`
- `DeleteView` → `<app_label>/<model_name>_confirm_delete.html`

### Template Variable Detection (NEW)

Detects templates referenced through variables containing 'template' in the name:

```python
# Simple variable assignment
template_name = 'myapp/custom.html'

# Method returns
def get_template_names(self):
    return ['myapp/template1.html', 'myapp/template2.html']
```

### Python Code URL References

Detects URL references in Python code via:

```python
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.http import HttpResponseRedirect

# All of these are detected and marked as "referenced"
def my_view(request):
    return redirect('url-name')

def another_view(request):
    url = reverse('url-name')
    return HttpResponseRedirect(url)

class MyView(UpdateView):
    success_url = reverse_lazy('url-name')
```

### Unused Templates

Templates that exist but are not referenced by any view (directly or indirectly through includes/extends):

```python
# views.py - No view renders 'unused_template.html'
# And no other template includes or extends it

# But the file templates/unused_template.html exists
```

**Note**: Templates referenced via `{% include %}` or `{% extends %}` are now correctly identified as used, even if not directly referenced by views.

### Template Relationships

Tracks which templates include or extend other templates:

```django
{# base.html is extended by page.html #}
{% extends 'base.html' %}

{# header.html is included in base.html #}
{% include 'partials/header.html' %}
```

Use the `--show-template-relationships` flag to see these relationships in your report.

## Example Output

```
================================================================================
Django Dead Code Analysis Report
================================================================================

SUMMARY
--------------------------------------------------------------------------------
Total URL patterns: 45
Total templates analyzed: 32
Total views found: 28
Unreferenced URLs: 5
Unused templates: 3

UNREFERENCED URL PATTERNS
--------------------------------------------------------------------------------
These URL patterns are defined but never referenced in templates:

  • old_feature
    View: myapp.views.old_feature
    Pattern: /old-feature/

  • deprecated_api
    View: myapp.api.deprecated_endpoint
    Pattern: /api/v1/deprecated/

POTENTIALLY UNUSED TEMPLATES
--------------------------------------------------------------------------------
These templates are not directly referenced by views (may be included/extended):

  • old_landing.html
  • unused_email.html
  • legacy_form.html
```

## How It Works

1. **Template Analysis**: Scans all template files **within your project's BASE_DIR** for:
   - `{% url 'name' %}` tags
   - `href="/path/"` attributes (internal links)
   - `{% include 'template' %}` tags
   - `{% extends 'template' %}` tags

2. **Path Normalization**: Normalizes all template paths to Django's relative format (e.g., `app_name/template.html`) ensuring consistent matching between filesystem paths and template references.

3. **Project Boundary Filtering**: Only templates within your project's `BASE_DIR` are analyzed. Templates from installed packages (e.g., Django admin, third-party apps) are automatically excluded.

4. **URL Pattern Discovery**: Inspects Django's URL configuration to find all defined URL patterns and their names

5. **View Analysis**: Parses Python files to find:
   - `render(request, 'template.html')` calls
   - `template_name = 'template.html'` in class-based views
   - Class-based view implicit template names (ListView, DetailView, etc.)
   - Template variables containing 'template' in the name

6. **Reverse/Redirect Analysis**: Uses AST parsing to detect:
   - `reverse('url-name')` calls
   - `reverse_lazy('url-name')` calls
   - `redirect('url-name')` calls
   - `HttpResponseRedirect(reverse('url-name'))` patterns
   - Dynamic URL patterns (f-strings, concatenation) are flagged for manual review

7. **Transitive Template Detection**: Recursively traces template relationships to mark templates as used if they're referenced via `{% include %}` or `{% extends %}` from any used template

8. **Relationship Mapping**: Connects templates ↔ URLs ↔ views to identify dead code

## Limitations

### Static Analysis Only
- Does not execute code or track runtime behavior
- Cannot detect templates loaded with dynamic names (e.g., `render(request, f'{variable}.html')`)

### Dynamic Templates
The following patterns are **out of scope** and will not be detected:
- f-string template names: `f'{app_name}/template.html'`
- Concatenated variables: `template = var1 + var2`
- Complex conditional logic in `get_template_names()`

### Dynamic URLs
- Cannot automatically detect URLs generated with f-strings or concatenation
- These are flagged for manual review in the report

### Third-party Packages
- Analyzes your code only, not installed packages
- Templates outside BASE_DIR are automatically excluded

### Function-Based Template Loading
The following patterns are **not detected**:
- `get_template()` function calls
- `select_template()` function calls

These may be addressed in future enhancements based on user feedback.

## Troubleshooting

### Templates Incorrectly Flagged as Unused

**Issue**: A template that is actually used is being flagged as unused.

**Possible Causes & Solutions**:

1. **Template Outside BASE_DIR**: Templates from installed packages are automatically excluded. Verify the template is within your project's BASE_DIR.

2. **Dynamic Template Names**: If your view uses dynamic template names (f-strings, concatenation), the tool cannot detect them. Consider refactoring to use explicit template names or adding a comment to track manually.

3. **Custom Template Loaders**: If you're using custom template loaders with non-standard path resolution, the path normalization may not work correctly. Ensure templates are in standard locations.

4. **Template Name Mismatch**: Verify that the template name in your view matches the actual file path relative to the templates directory.

### Class-Based View Templates Not Detected

**Issue**: A CBV's implicit template is not being detected.

**Possible Causes & Solutions**:

1. **Non-Standard App Structure**: The tool infers app labels from file paths. If your app structure is non-standard (e.g., not in an `apps/` directory), the app label inference may fail. Use explicit `template_name` attributes.

2. **Model Not Detected**: If the model is set via a complex expression or `get_queryset()` method, the tool may not detect it. Use explicit `template_name` attributes.

3. **CBV Inheritance**: If your CBV inherits from a custom base class that inherits from Django's generic views, the tool may not detect it. Ensure the direct base class is a Django generic view.

### Path Normalization Issues

**Issue**: Templates are not being matched correctly.

**Possible Causes & Solutions**:

1. **Multiple 'templates' Directories**: If your path contains multiple directories named 'templates' (e.g., `/old_templates/templates/`), the tool uses the last occurrence. Rename directories to avoid confusion.

2. **Symlinked Templates**: Symlinks are resolved to their actual paths. Ensure symlink targets are within BASE_DIR.

3. **Windows Paths**: The tool handles both Unix and Windows path separators. If you encounter issues, please report them as a bug.

### Performance Issues

**Issue**: Analysis takes too long on large projects.

**Expected Performance**:
- Small project (10 templates): < 1 second
- Medium project (100 templates): < 5 seconds
- Large project (1000 templates): < 30 seconds

**Solutions**:
1. **Analyze Specific Apps**: Use `--apps` flag to limit analysis scope
2. **Exclude Test/Migration Files**: The tool already skips these, but ensure they're not in unusual locations
3. **Report a Bug**: If performance is significantly worse than expected, please open an issue

### False Negatives (Unused Code Not Detected)

**Issue**: Dead code exists but is not being detected.

**Possible Causes**:
1. **Template Used by Third-Party Package**: Templates used by installed packages are not tracked
2. **Dynamic Template/URL References**: Cannot be detected by static analysis
3. **Complex Template Chains**: Very complex include/extends chains may have edge cases

**Recommendations**:
- Review the report manually
- Cross-reference with code coverage reports
- Test in a staging environment before deleting templates

## Development

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/nanorepublica/django-deadcode.git
cd django-deadcode

# Install development dependencies
pip install -e ".[dev]"
```

### Running Tests

```bash
pytest
```

With coverage:

```bash
pytest --cov=django_deadcode --cov-report=html
```

### Code Quality

```bash
# Linting
ruff check .

# Type checking
mypy django_deadcode
```

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## License

MIT License - see [LICENSE](LICENSE) for details.

## Credits

Inspired by the blog post: https://softwarecrafts.co.uk/100-words/day-71

## Roadmap

See [agent-os/product/roadmap.md](agent-os/product/roadmap.md) for the full development roadmap.

### Planned Features

- Confidence scoring for dead code detection
- Multi-app analysis with cross-app relationship tracking
- Django admin integration detection
- HTML report generation with interactive UI
- CI/CD integration helpers
- IDE plugins (VS Code, PyCharm)

## Support

- **Issues**: https://github.com/nanorepublica/django-deadcode/issues
- **Discussions**: https://github.com/nanorepublica/django-deadcode/discussions

## Changelog

### v0.3.0 (Latest)

**Major Improvements: Template Detection Accuracy**

- **Path Normalization**: Fixed path format mismatch bug that caused false positives. All template paths are now normalized to Django's relative format for consistent matching.
- **Class-Based View Detection**: Automatically detects templates used by Django's generic CBVs (ListView, DetailView, CreateView, UpdateView, DeleteView) through implicit naming conventions.
- **Template Variable Detection**: Detects templates referenced through variables containing 'template' in the name, including `get_template_names()` method returns.
- **Enhanced Template Relationships**: Improved tracking of `{% extends %}` and `{% include %}` relationships with normalized paths.
- **Production Ready**: Eliminated false positives for the most common use cases. The tool is now trustworthy for identifying genuinely unused templates.

**Performance**: All improvements maintain excellent performance with minimal overhead (<10% impact on large projects).

### Previous Versions

See [CHANGELOG.md](CHANGELOG.md) for full version history.
