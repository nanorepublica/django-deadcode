# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2024-11-11

### Added
- Initial release of django-deadcode
- Template analyzer for extracting URL references (href and {% url %} tags)
- URL pattern analyzer for discovering all URL patterns
- View analyzer for tracking template usage in views
- Template relationship tracking (extends/includes)
- Multiple output formats (console, JSON, Markdown)
- Django management command: `finddeadcode`
- Comprehensive test suite with pytest
- Full documentation and examples

### Features
- Detect unreferenced URL patterns
- Find unused templates
- Track template-to-view relationships
- Report template inheritance and inclusion
- Filter analysis by specific apps
- Custom template directory support
- Export reports to files

[0.1.0]: https://github.com/nanorepublica/django-deadcode/releases/tag/v0.1.0
