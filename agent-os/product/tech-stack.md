# Tech Stack

## Framework & Runtime
- **Application Framework:** Django
- **Language/Runtime:** Python 3.10+
- **Package Manager:** uv then pip

## Static Analysis & Code Parsing
- **Python AST Parser:** Built-in `ast` module for analyzing Python source code
- **Template Parser:** Django template engine for parsing template syntax
- **Regular Expressions:** Python `re` module for pattern matching in templates
- **Django URL Resolver:** Django's `django.urls` module for introspecting URL configurations

## Core Analysis Libraries
- **File System Analysis:** Python `pathlib` for navigating Django project structure
- **Code Introspection:** Python `inspect` module for analyzing view functions and classes
- **Import Analysis:** `importlib` for discovering Django apps and configurations

## Frontend (if web dashboard is built)
- **JavaScript Framework:** HTMX, Alpine, vanilla JS
- **CSS Framework:** Tailwind CSS
- **UI Components:** Tailwind UI, custom library

## Database & Storage
- **Database:** PostgreSQL (for storing analysis results in web version)
- **ORM/Query Builder:** Django ORM
- **Caching:** Redis (for caching analysis results)

## Report Generation
- **Output Formats:** JSON, HTML, Markdown, plain text
- **CLI Framework:** Python `argparse` or `click` for command-line interface
- **Console Output:** `rich` library for formatted terminal output

## Testing & Quality
- **Test Framework:** pytest with pytest-django
- **Test Coverage:** pytest-cov for measuring code coverage
- **Linting/Formatting:** ruff, precommit
- **Type Checking:** mypy for static type analysis

## Development Tools
- **Virtual Environment:** Python venv or virtualenv
- **Dependency Management:** uv for fast package installation, pip for compatibility
- **Version Control:** Git with conventional commit messages

## Deployment & Infrastructure
- **Package Distribution:** PyPI for distributing the CLI tool
- **Hosting:** dokku on AWS EC2 (for optional web dashboard)
- **CI/CD:** GitHub Actions for testing, linting, and publishing

## Third-Party Services
- **Monitoring:** Sentry for error tracking
- **Documentation:** Sphinx or MkDocs for generating package documentation

## Architecture Decisions

### CLI-First Approach
The tool is primarily a command-line utility that can be installed via pip/uv and run directly on Django projects. This ensures zero configuration and immediate value for developers.

### Static Analysis Only
All analysis is performed through static code analysis without running the Django application. This avoids dependencies on database setup, environment configuration, or runtime state.

### Django Version Compatibility
Support Django 3.2+ (LTS versions) to cover the majority of active Django projects while maintaining reasonable compatibility scope.

### Incremental Analysis
Design the analysis engine to support incremental updates, allowing for fast re-analysis when only portions of the codebase change (important for web dashboard and IDE integration).

### Pluggable Architecture
Build core analysis engine as separate modules (template analyzer, URL analyzer, view analyzer) that can be extended with custom analyzers for project-specific patterns.
