# Specification: Fix Unreferenced URL Detection

## Overview

This spec addresses two issues with URL reference detection in django-deadcode:

1. **Bug Fix**: Embedded regex anchors in accumulated URL patterns cause false positives
2. **Feature Enhancement**: Add support for scanning external JavaScript files and configurable detection aggressiveness

## Problem Description

### Issue 1: Embedded Regex Anchors (Bug)

When using nested `include()` statements that mix `path()` and `re_path()`, regex anchors (`^` and `$`) end up embedded in the middle of the accumulated pattern string. The current `normalize_path()` function only strips anchors from the start and end of patterns.

**Example URL configuration:**
```python
# project/urls.py
urlpatterns = [
    path('nutritionist/', include('nutritionist.urls')),
]

# nutritionist/urls.py
urlpatterns = [
    re_path(r'^client/client_mfp_code/$', views.client_mfp_code, name='client_mfp_code'),
]
```

**Pattern accumulation in URLAnalyzer (url_analyzer.py:83):**
```python
full_pattern = prefix + pattern_str
# prefix = "nutritionist/" (from path())
# pattern_str = "^client/client_mfp_code/$" (from re_path regex)
# full_pattern = "nutritionist/^client/client_mfp_code/$"
```

**Current normalization (url_matching.py:44-47):**
```python
if path.startswith("^"):  # NOT TRUE - starts with 'n'
    path = path[1:]
if path.endswith("$"):    # TRUE - strip trailing $
    path = path[:-1]
# Result: "nutritionist/^client/client_mfp_code/" (embedded ^ remains!)
```

**Consequence:**
- Normalized pattern: `nutritionist/^client/client_mfp_code/`
- Normalized href: `nutritionist/client/client_mfp_code/`
- Match result: **FALSE** (should be TRUE)

### Issue 2: External JavaScript Files Not Scanned

Currently, django-deadcode only scans template files (`.html`, `.txt`, `.xml`, `.svg`) for URL references. JavaScript files in static directories that contain hardcoded URLs are not scanned.

### Issue 3: Limited URL Detection Patterns

The current detection only finds static string URLs. More complex patterns like string concatenation or template literals are not detected.

## Proposed Solutions

### Solution 1: Enhanced Pattern Normalization (Bug Fix)

Modify `normalize_path()` to strip all occurrences of `^` and `$` anchors, not just at start/end.

**New normalization logic:**
```python
def normalize_path(path: str) -> str:
    """
    Normalize a path for comparison.

    Removes regex anchors (^ and $) from ANYWHERE in the pattern,
    not just at the start/end.
    """
    if not path or path == "/":
        return ""

    # Strip ALL regex anchors (handles embedded anchors from nested includes)
    path = path.replace("^", "")
    path = path.replace("$", "")

    # Handle optional trailing slash - convert /? to /
    if path.endswith("/?"):
        path = path[:-1]

    # Remove leading slash
    if path.startswith("/"):
        path = path[1:]

    return path
```

### Solution 2: Static File Scanning (Feature)

Add support for scanning JavaScript files in Django's static directories.

**Implementation approach:**
1. Add `StaticFileAnalyzer` class (or extend `TemplateAnalyzer`)
2. Scan files with `.js` extension in directories from `STATICFILES_DIRS` and app static folders
3. Use the existing `INTERNAL_URL_PATTERN` regex to extract URLs
4. Add command-line option `--scan-static` to enable this feature

**New file extensions:**
- `.js` - JavaScript files
- `.mjs` - ES modules
- `.jsx` - React JSX files (optional)
- `.ts` / `.tsx` - TypeScript files (optional)

### Solution 3: Aggressiveness Flag (Feature)

Add a command-line flag to control URL detection aggressiveness.

**Proposed flags:**
```
--url-detection [basic|extended]
```

**Detection levels:**
1. `basic` (default): Static string URLs only
   - Pattern: `r'["\'](/(?!/)[^"\']*)["\']'`
   - Matches: `'/api/endpoint/'`, `"/user/profile/"`

2. `extended`: Also detect dynamic URL construction
   - String concatenation: `'/api/' + id + '/edit/'`
   - Template literals: `` `/api/${id}/edit/` ``
   - Jinja2/Django templates: `'/api/{{ id }}/edit/'`

**Extended patterns:**
```python
# String concatenation (partial match)
CONCAT_URL_PATTERN = re.compile(r'["\']/([\w/]+)["\']')

# Template literals
TEMPLATE_LITERAL_PATTERN = re.compile(r'`(/((?:[^`]|\\.)*?))`')
```

## Implementation Details

### File Changes

#### 1. `django_deadcode/utils/url_matching.py`

**Modify `normalize_path()`:**

```python
def normalize_path(path: str) -> str:
    """
    Normalize a path for comparison.

    Handles both hrefs (e.g., '/about/') and URL patterns (e.g., '^about/$').
    Strips regex anchors from ANYWHERE in the pattern to handle nested includes
    that mix path() and re_path().

    Normalization steps:
    1. Strip ALL regex anchors (^ and $)
    2. Convert optional trailing slash (/?) to /
    3. Remove leading slash

    Args:
        path: URL path or pattern to normalize (e.g., '/about/', '^about/$',
              'prefix/^suffix/$')

    Returns:
        Normalized path suitable for comparison (e.g., 'about/')
    """
    # Handle empty or root path
    if not path or path == "/":
        return ""

    # Strip ALL regex anchors (handles embedded anchors from nested includes)
    path = path.replace("^", "")
    path = path.replace("$", "")

    # Handle optional trailing slash - convert /? to /
    if path.endswith("/?"):
        path = path[:-1]  # Remove the ?, keep the /

    # Remove leading slash
    if path.startswith("/"):
        path = path[1:]

    return path
```

#### 2. `django_deadcode/analyzers/template_analyzer.py`

**Add static file extensions (optional feature):**

```python
class TemplateAnalyzer:
    def __init__(
        self,
        template_dirs: list[Path] | None = None,
        base_dir: Path | None = None,
        static_dirs: list[Path] | None = None,  # NEW
        scan_static: bool = False,  # NEW
    ) -> None:
        # ... existing code ...
        self.static_dirs = static_dirs or []
        self.scan_static = scan_static
        self.static_extensions = [".js", ".mjs"]  # NEW
```

#### 3. `django_deadcode/management/commands/finddeadcode.py`

**Add new command-line arguments:**

```python
def add_arguments(self, parser: CommandParser) -> None:
    # ... existing arguments ...
    parser.add_argument(
        "--scan-static",
        action="store_true",
        default=False,
        help="Also scan JavaScript files in static directories for URL references",
    )
    parser.add_argument(
        "--url-detection",
        type=str,
        choices=["basic", "extended"],
        default="basic",
        help="URL detection level: 'basic' for static strings only, "
             "'extended' for dynamic URL patterns (default: basic)",
    )
```

### Test Cases

#### Test: Embedded Regex Anchors (Bug Fix)

```python
class TestEmbeddedAnchors:
    """Test for embedded regex anchors in accumulated patterns."""

    def test_normalize_embedded_caret(self):
        """Test normalization of pattern with embedded ^ anchor."""
        # Pattern from: path('prefix/', include(...)) + re_path(r'^suffix/$', ...)
        assert normalize_path("prefix/^suffix/$") == "prefix/suffix/"

    def test_normalize_multiple_embedded_anchors(self):
        """Test normalization of pattern with multiple embedded anchors."""
        # Deeply nested includes with multiple re_path() calls
        assert normalize_path("a/^b/^c/$") == "a/b/c/"

    def test_match_embedded_anchor_pattern(self):
        """Test matching href against pattern with embedded anchor."""
        href = "/nutritionist/client/client_mfp_code/"
        pattern = "nutritionist/^client/client_mfp_code/$"
        assert match_href_to_pattern(href, pattern) is True

    def test_integration_nested_includes(self):
        """Integration test simulating real nested include scenario."""
        # Simulates: path('nutritionist/', include([
        #     re_path(r'^client/client_mfp_code/$', view, name='client_mfp_code')
        # ]))
        hrefs = {"/nutritionist/client/client_mfp_code/"}
        patterns = {
            "client_mfp_code": {
                "pattern": "nutritionist/^client/client_mfp_code/$",
                "name": "client_mfp_code",
            }
        }
        matched = find_matching_url_patterns(hrefs, patterns)
        assert "client_mfp_code" in matched
```

#### Test: Static File Scanning

```python
class TestStaticFileScanning:
    """Tests for JavaScript file scanning."""

    def test_extract_url_from_js_file(self):
        """Test URL extraction from JavaScript content."""
        js_content = """
            function saveData() {
                $.ajax({
                    url: '/api/save/',
                    method: 'POST'
                });
            }
        """
        # Test that '/api/save/' is extracted

    def test_extract_url_from_fetch_call(self):
        """Test URL extraction from fetch() calls."""
        js_content = """
            fetch('/api/users/')
                .then(response => response.json());
        """
        # Test that '/api/users/' is extracted
```

## Migration / Compatibility

### Backward Compatibility

- The bug fix is fully backward compatible
- All existing tests continue to pass
- Static file scanning is opt-in via `--scan-static` flag
- Extended detection is opt-in via `--url-detection extended`

### Potential Breaking Changes

None - all changes are either bug fixes or opt-in features.

## Success Criteria

1. Patterns with embedded `^` and `$` anchors correctly match corresponding hrefs
2. `--scan-static` flag enables JavaScript file scanning
3. `--url-detection extended` enables detection of dynamic URL patterns
4. All existing tests pass
5. No regression in detection accuracy for static URL patterns

## Files to Modify

1. `django_deadcode/utils/url_matching.py` - Bug fix for `normalize_path()`
2. `django_deadcode/analyzers/template_analyzer.py` - Static file scanning (feature)
3. `django_deadcode/management/commands/finddeadcode.py` - New CLI arguments
4. `tests/test_href_matching.py` - New test cases for bug fix
5. `tests/test_template_href_extraction.py` - Tests for static file scanning

## Implementation Phases

### Phase 1: Bug Fix (Priority: High)
- Fix `normalize_path()` to handle embedded anchors
- Add tests for embedded anchor scenarios
- Estimated effort: Small

### Phase 2: Static File Scanning (Priority: Medium)
- Add `--scan-static` flag
- Implement static directory discovery
- Add JavaScript file scanning
- Estimated effort: Medium

### Phase 3: Extended Detection (Priority: Low)
- Add `--url-detection` flag
- Implement extended detection patterns
- Document limitations and false positive risks
- Estimated effort: Medium

## Out of Scope

- Full regex evaluation of URL patterns against hrefs
- Scanning minified JavaScript (would need source maps)
- Scanning JavaScript in node_modules or vendor directories
- Real-time/watch mode scanning
