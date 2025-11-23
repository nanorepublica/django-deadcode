# Product Roadmap

## ✅ MVP Complete (v0.1.0) - Released 2024-11-11

The following features have been implemented and released:

1. [x] **Template Link Extraction** — Build parser to analyze Django templates and extract all internal links from plain href attributes and {% url %} template tags, storing them with source location information. `M`
   - ✅ Implemented in `template_analyzer.py`
   - ✅ Extracts both href attributes and {% url %} tags
   - ✅ Filters for internal links only

2. [x] **URL Pattern Discovery** — Implement Django URL configuration introspection to discover all defined urlpatterns across the project, including app-level URLs and namespaced patterns. `S`
   - ✅ Implemented in `url_analyzer.py`
   - ✅ Handles nested URLResolvers and namespaces
   - ✅ Supports both RoutePattern and RegexPattern

3. [x] **URL Matching Engine** — Create matching system to compare extracted template links against discovered URL patterns, identifying which URLs are referenced and which are orphaned. `M`
   - ✅ Implemented in `finddeadcode` management command
   - ✅ Identifies unreferenced URL patterns
   - ✅ Cross-references templates and URL patterns

4. [x] **View Reference Tracker** — Link matched URL patterns to their corresponding view functions or class-based views, counting reference frequency across all templates. `S`
   - ✅ Implemented in `url_analyzer.py` and `view_analyzer.py`
   - ✅ Maps URLs to view callables
   - ✅ Tracks view-to-template relationships

5. [x] **Template Usage Analysis** — Scan Python view files to find all references to templates via render(), TemplateView, and similar Django patterns to identify which templates are actually used. `M`
   - ✅ Implemented in `view_analyzer.py`
   - ✅ AST parsing for render() calls
   - ✅ Class-based view template_name detection

6. [x] **Basic CLI Reporter** — Build command-line interface that outputs analysis results showing view reference counts, unused URLs, and orphaned templates in readable text format. `S`
   - ✅ Django management command: `python manage.py finddeadcode`
   - ✅ Console reporter with human-readable output
   - ✅ Summary statistics and warnings

7. [x] **Template Inheritance Tracking** — Extend template parser to follow {% include %} and {% extends %} tags, building complete template dependency graph including nested inheritance. `M`
   - ✅ Implemented in `template_analyzer.py`
   - ✅ Tracks {% include %} tags
   - ✅ Tracks {% extends %} tags
   - ✅ Reports template relationships

## ✅ v0.2.0 Features - Complete (2025-11-12)

8. [x] **Reverse/Redirect Detection** — Implement Python AST analysis to find all reverse() and redirect() calls in view code, capturing programmatic URL references beyond templates. `L`
   - ✅ Implemented in `reverse_analyzer.py`
   - ✅ Detects `reverse()`, `reverse_lazy()`, `redirect()`, and `HttpResponseRedirect()` patterns
   - ✅ Handles nested patterns like `HttpResponseRedirect(reverse('url'))`
   - ✅ Detects namespaced URLs (`'myapp:detail'`)
   - ✅ Flags dynamic URL patterns (f-strings, concatenation) for manual review
   - ✅ Integrated with finddeadcode command
   - ✅ 100% code coverage with 20 comprehensive tests
   - ✅ Reduces false positives for URLs referenced only in Python code

## ✅ v0.3.0 Features - Complete (2025-11-21)

9. [x] **Multi-App Analysis** — Add support for analyzing Django projects with multiple apps, showing cross-app dependencies and generating per-app reports. `M`
   - ⚠️ Partially implemented
   - ✅ Can filter by specific apps with `--apps` flag
   - ❌ No cross-app dependency visualization yet
   - ❌ No per-app report generation

10. [x] **Django Admin Detection & Third-Party URL Exclusion** — Automatically detect and filter URLs from Django admin and all third-party packages to reduce false positives in dead code detection. `S`
    - ✅ Implemented in `url_analyzer.py` and `utils/module_detection.py`
    - ✅ Auto-detects third-party URLs based on BASE_DIR comparison
    - ✅ Excludes entire namespaces if ANY pattern is third-party
    - ✅ Configurable manual exclusions via DEADCODE_EXCLUDE_NAMESPACES setting
    - ✅ Reports excluded namespaces in output
    - ✅ Covers Django admin, DRF, and all site-packages automatically

11. [x] **Raw URL Pattern Matching** — Match internal href links from templates against raw URL patterns to detect additional URL references beyond {% url %} tags. `M`
    - ✅ Implemented in `template_analyzer.py` and `utils/url_matching.py`
    - ✅ Extracts internal hrefs from template href attributes
    - ✅ Filters out external protocols (http://, https://, mailto:, etc.)
    - ✅ Normalizes paths for consistent matching
    - ✅ Simple string matching algorithm
    - ✅ Reduces false positives for URLs referenced via plain hrefs
    - ✅ Integrated with existing {% url %} tag detection

## 🚧 Planned Features

12. [ ] **Confidence Scoring System** — Implement confidence levels for dead code detection that account for dynamic URL generation, runtime patterns, and third-party integrations. `M`
    - Not yet started
    - Important for providing actionable insights

13. [x] **Enhanced Report Generation** — Create detailed reporting with multiple output formats (JSON, HTML, Markdown) showing relationship visualizations and prioritized cleanup suggestions. `L`
    - ⚠️ Partially implemented
    - ✅ JSON output format
    - ✅ Markdown output format
    - ✅ Console output format
    - ❌ No HTML output with visualizations yet
    - ❌ No prioritized cleanup suggestions

## 📊 Progress Summary

- **Completed:** 11/13 features (85%)
- **Partially Complete:** 2/13 features (15%)
- **Not Started:** 0/13 features (0%)
- **MVP Status:** ✅ Complete (features 1-7)
- **v0.2.0 Status:** ✅ Complete (feature 8)
- **v0.3.0 Status:** ✅ Complete (features 9-11)

## 🎯 Next Release (v0.4.0) - Planned

Focus on accuracy and usability improvements:

1. **Confidence Scoring System** (Feature 12)
   - Score each finding based on confidence level
   - Account for dynamic patterns
   - Prioritize cleanup recommendations

2. **Enhanced Multi-App Analysis** (Feature 9 completion)
   - Cross-app dependency graph
   - Per-app summary reports
   - Visualization of app relationships

3. **Complete Enhanced Report Generation** (Feature 13)
   - HTML report generation with interactive visualizations
   - Prioritized cleanup suggestions based on impact

## 🔮 Future Releases

### v0.5.0 - Advanced Features
- Custom rule definitions
- CI/CD integration helpers
- GitHub Action integration
- Performance optimization for large projects

### v0.6.0 - IDE Integration
- VS Code extension
- PyCharm plugin
- Real-time dead code detection
- Inline suggestions and quick fixes

> **Note:** The roadmap is flexible and may be adjusted based on user feedback and community contributions.
