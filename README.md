# Django Dead Code

A Django dead code analysis tool that tracks relationships between templates, URLs, and views to help identify and remove unused code.

## Features

- **Template Analysis**: Extract URL references from Django templates (href attributes and `{% url %}` tags)
- **URL Pattern Discovery**: Analyze all URL patterns defined in your Django project
- **View Tracking**: Identify which templates are used by which views
- **Relationship Mapping**: Track template inheritance (extends/includes) and relationships
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

## What It Detects

### Unreferenced URL Patterns

URL patterns that are defined in `urls.py` but never referenced in any template:

```python
# urls.py - This URL is defined
path('old-feature/', views.old_feature, name='old_feature'),

# But no template references it with {% url 'old_feature' %}
```

### Unused Templates

Templates that exist but are not referenced by any view:

```python
# views.py - No view renders 'unused_template.html'

# But the file templates/unused_template.html exists
```

### Template Relationships

Tracks which templates include or extend other templates:

```django
{# base.html is extended by page.html #}
{% extends 'base.html' %}

{# header.html is included in base.html #}
{% include 'partials/header.html' %}
```

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

1. **Template Analysis**: Scans all template files for:
   - `{% url 'name' %}` tags
   - `href="/path/"` attributes (internal links)
   - `{% include 'template' %}` tags
   - `{% extends 'template' %}` tags

2. **URL Pattern Discovery**: Inspects Django's URL configuration to find all defined URL patterns and their names

3. **View Analysis**: Parses Python files to find:
   - `render(request, 'template.html')` calls
   - `template_name = 'template.html'` in class-based views

4. **Relationship Mapping**: Connects templates ↔ URLs ↔ views to identify dead code

## Limitations

- **Static Analysis Only**: Does not execute code or track runtime behavior
- **Dynamic Templates**: Cannot detect templates loaded with dynamic names (e.g., `render(request, f'{variable}.html')`)
- **Dynamic URLs**: Cannot detect URLs generated programmatically
- **Indirect Usage**: May flag templates used only through includes/extends as "unused"
- **Third-party Packages**: Analyzes your code only, not installed packages

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
- Detection of `reverse()` and `redirect()` calls in Python code
- Multi-app analysis with cross-app relationship tracking
- Django admin integration detection
- HTML report generation with interactive UI
- CI/CD integration helpers
- IDE plugins (VS Code, PyCharm)

## Support

- **Issues**: https://github.com/nanorepublica/django-deadcode/issues
- **Discussions**: https://github.com/nanorepublica/django-deadcode/discussions
