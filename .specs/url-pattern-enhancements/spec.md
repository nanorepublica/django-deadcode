# Specification: URL Pattern Enhancements

## Overview

Enhance the unreferenced URL patterns detection in django-deadcode with two new capabilities:
1. Raw URL pattern matching against internal href links in templates
2. Automatic exclusion of third-party URL namespaces from the unreferenced report

## Requirements

### 1. Raw URL Pattern Matching

Detect URL pattern references by matching internal href links found in templates against raw URL patterns.

**Matching Logic:**
- Extract href values from templates that do NOT start with: `http://`, `https://`, `mailto:`, `tel:`, `javascript:`, `#`, `//`
- Compare these internal links against raw URL patterns (the pattern string, not the name)
- If a template href matches a URL pattern string, mark that URL pattern as referenced
- Use simple string matching (not regex resolution)

**Example:**
- Template has `<a href="/about/">`
- URL pattern exists: `path('about/', views.about, name='about')`
- The `/about/` href matches the `about/` pattern -> mark `about` URL as referenced

### 2. Third-Party URL Exclusion

Automatically detect and exclude URL patterns from third-party packages.

**Detection Logic:**
- A URL is third-party if its view module path is NOT under `settings.BASE_DIR`
- Detect at the namespace level, not individual pattern level
- If any pattern in a namespace is third-party, exclude the entire namespace

**Configurable Allowlist:**
- Setting: `DEADCODE_EXCLUDE_NAMESPACES` (list of namespace strings)
- Allows users to explicitly exclude additional namespaces
- Example: `DEADCODE_EXCLUDE_NAMESPACES = ['admin', 'rest_framework']`

### 3. Reporting Changes

**Silent Exclusion:**
- Third-party URLs should not appear in the unreferenced URL list
- No separate section for excluded URLs

**Informational Note:**
- Add a sentence under the "UNREFERENCED URL PATTERNS" section title
- Format: "Note: Third-party namespaces excluded: admin, rest_framework, drf_spectacular"
- Only show if namespaces were actually excluded

## Implementation Details

### URLAnalyzer Changes

Extend `_process_url_pattern()` to store:
- Module path of the view callback
- Whether the pattern is third-party (view module not under BASE_DIR)

Add new method `get_unreferenced_urls()` parameters:
- Accept `excluded_namespaces: set[str]` to filter results

### Template Analyzer Changes

Add href extraction in `TemplateAnalyzer`:
- Parse templates for href attributes
- Filter to internal links only (exclude external protocols)
- Normalize paths (handle leading/trailing slashes)
- Return set of internal href paths

### Reference Matching

In the main analyzer or a new matcher module:
- Compare extracted hrefs against URL pattern strings
- Handle path normalization (e.g., `/about/` matches `about/`)
- Add matched URL names to the referenced set

### Third-Party Detection

New utility function `is_third_party_module(module_path: str) -> bool`:
- Get `settings.BASE_DIR` as Path
- Check if module's file path starts with BASE_DIR
- Return True if external

## Configuration

```python
# settings.py

# Optional: Additional namespaces to exclude from unreferenced report
DEADCODE_EXCLUDE_NAMESPACES = ['admin', 'debug_toolbar']
```

Default behavior without configuration:
- Auto-detect third-party namespaces based on BASE_DIR
- No manual exclusions

## Acceptance Criteria

1. Internal hrefs in templates (e.g., `/about/`, `/users/profile/`) that match URL patterns mark those patterns as referenced

2. URL patterns from packages installed outside BASE_DIR are automatically excluded from the unreferenced report

3. Users can configure `DEADCODE_EXCLUDE_NAMESPACES` to exclude additional namespaces

4. The report shows an informational note listing excluded third-party namespaces

5. External links (http://, https://, mailto:, etc.) are ignored during href matching

6. Existing functionality (reverse() detection, url tag detection) continues to work unchanged
