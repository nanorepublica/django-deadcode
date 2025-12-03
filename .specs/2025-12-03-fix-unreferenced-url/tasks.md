# Tasks: Fix Unreferenced URL Detection

## Phase 1: Bug Fix - Embedded Regex Anchors

### Task 1.1: Fix normalize_path() Function
**File:** `django_deadcode/utils/url_matching.py`
**Priority:** High

- [ ] Modify `normalize_path()` to use `str.replace()` for anchor removal instead of `str.startswith()`/`str.endswith()`
- [ ] Update docstring to document the embedded anchor handling
- [ ] Preserve existing behavior for patterns without embedded anchors

**Implementation:**
```python
# Change from:
if path.startswith("^"):
    path = path[1:]
if path.endswith("$"):
    path = path[:-1]

# To:
path = path.replace("^", "")
path = path.replace("$", "")
```

### Task 1.2: Add Tests for Embedded Anchors
**File:** `tests/test_href_matching.py`
**Priority:** High

- [ ] Add `TestEmbeddedAnchors` test class
- [ ] Test `normalize_path()` with embedded `^` anchor
- [ ] Test `normalize_path()` with embedded `$` anchor
- [ ] Test `normalize_path()` with multiple embedded anchors
- [ ] Test `match_href_to_pattern()` with embedded anchor patterns
- [ ] Test `find_matching_url_patterns()` integration scenario

**Test cases:**
1. `normalize_path("prefix/^suffix/$")` → `"prefix/suffix/"`
2. `normalize_path("a/^b/^c/$")` → `"a/b/c/"`
3. `match_href_to_pattern("/nutritionist/client/mfp/", "nutritionist/^client/mfp/$")` → `True`

### Task 1.3: Verify Existing Tests Still Pass
**Priority:** High

- [ ] Run full test suite to verify no regressions
- [ ] Ensure all existing `TestPathNormalization` tests pass
- [ ] Ensure all existing `TestHrefToPatternMatching` tests pass

---

## Phase 2: Static File Scanning (Feature)

### Task 2.1: Add Static Directory Discovery
**File:** `django_deadcode/management/commands/finddeadcode.py`
**Priority:** Medium

- [ ] Add `--scan-static` command-line argument
- [ ] Add `_get_static_dirs()` method to discover static directories
- [ ] Include `STATICFILES_DIRS` from settings
- [ ] Include `static/` folders in each installed app

**Implementation:**
```python
def _get_static_dirs(self) -> list[Path]:
    """Get static directories to analyze."""
    static_dirs = []

    # Get STATICFILES_DIRS from settings
    if hasattr(settings, 'STATICFILES_DIRS'):
        for dir_path in settings.STATICFILES_DIRS:
            static_dirs.append(Path(dir_path))

    # Get static directories in each app
    from django.apps import apps
    for app_config in apps.get_app_configs():
        app_static_dir = Path(app_config.path) / "static"
        if app_static_dir.exists():
            static_dirs.append(app_static_dir)

    return static_dirs
```

### Task 2.2: Extend TemplateAnalyzer for Static Files
**File:** `django_deadcode/analyzers/template_analyzer.py`
**Priority:** Medium

- [ ] Add `static_dirs` parameter to `__init__()`
- [ ] Add `scan_static` parameter to `__init__()`
- [ ] Add `static_extensions` list: `[".js", ".mjs"]`
- [ ] Add `find_all_static_files()` method
- [ ] Add `analyze_static_file()` method

**Implementation:**
```python
def find_all_static_files(self) -> None:
    """Find and analyze all JavaScript files in static directories."""
    if not self.scan_static:
        return

    for static_dir in self.static_dirs:
        if not static_dir.exists():
            continue

        for ext in self.static_extensions:
            for static_path in static_dir.rglob(f"*{ext}"):
                # Filter by BASE_DIR if provided
                if self.base_dir:
                    try:
                        resolved = static_path.resolve()
                        if not self._is_relative_to(resolved, self.base_dir):
                            continue
                    except (ValueError, OSError):
                        continue

                self.analyze_static_file(static_path)
```

### Task 2.3: Integrate Static Scanning into Command
**File:** `django_deadcode/management/commands/finddeadcode.py`
**Priority:** Medium

- [ ] Pass `scan_static` option to `TemplateAnalyzer`
- [ ] Pass `static_dirs` to `TemplateAnalyzer`
- [ ] Update progress messages to include static file scanning

### Task 2.4: Add Tests for Static File Scanning
**File:** `tests/test_template_href_extraction.py`
**Priority:** Medium

- [ ] Add `TestStaticFileScanning` test class
- [ ] Test URL extraction from JavaScript content
- [ ] Test URL extraction from jQuery $.ajax() calls
- [ ] Test URL extraction from fetch() calls
- [ ] Test that external URLs are excluded from JS files

---

## Phase 3: Extended Detection (Feature)

### Task 3.1: Add Detection Level CLI Argument
**File:** `django_deadcode/management/commands/finddeadcode.py`
**Priority:** Low

- [ ] Add `--url-detection` argument with choices `["basic", "extended"]`
- [ ] Pass detection level to template analyzer
- [ ] Update help text to explain detection levels

### Task 3.2: Add Extended Detection Patterns
**File:** `django_deadcode/analyzers/template_analyzer.py`
**Priority:** Low

- [ ] Add `TEMPLATE_LITERAL_PATTERN` for JavaScript template literals
- [ ] Add logic to extract base paths from template literals
- [ ] Handle detection level flag in `_analyze_template_content()`

**Patterns to add:**
```python
# Template literal: `/api/${id}/edit/`
TEMPLATE_LITERAL_PATTERN = re.compile(r'`(/((?:[^`]|\\.)*?))`')

# String concatenation prefix: '/api/' + variable
# Note: Only extract the static prefix portion
```

### Task 3.3: Add Tests for Extended Detection
**File:** `tests/test_template_href_extraction.py`
**Priority:** Low

- [ ] Test detection of URLs in template literals
- [ ] Test detection of static prefixes in string concatenation
- [ ] Test that detection level flag controls behavior

### Task 3.4: Document Extended Detection
**File:** `README.md`
**Priority:** Low

- [ ] Add section explaining `--url-detection` flag
- [ ] Document what extended detection can and cannot find
- [ ] Add examples of detected patterns
- [ ] Warn about potential false positives

---

## Verification Tasks

### Task V.1: Run Full Test Suite
- [ ] `pytest tests/ -v`
- [ ] Verify all tests pass
- [ ] Check for any deprecation warnings

### Task V.2: Manual Testing
- [ ] Create test project with nested includes mixing `path()` and `re_path()`
- [ ] Verify false positive is fixed
- [ ] Test with `--scan-static` flag
- [ ] Test with `--url-detection extended` flag

### Task V.3: Update Changelog
**File:** `CHANGELOG.md`
- [ ] Add entry for bug fix
- [ ] Add entry for new features (if implemented)
- [ ] Follow existing changelog format

---

## Task Dependencies

```
1.1 ─┬─> 1.2 ─┬─> 1.3 ─> V.1
     │        │
     └────────┘

2.1 ─> 2.2 ─> 2.3 ─> 2.4 ─> V.1

3.1 ─> 3.2 ─> 3.3 ─> 3.4 ─> V.1

All phases ─> V.2 ─> V.3
```

## Estimated Effort

| Phase | Task | Effort |
|-------|------|--------|
| 1 | Bug Fix | 1-2 hours |
| 2 | Static Scanning | 3-4 hours |
| 3 | Extended Detection | 4-6 hours |
| - | Verification | 1-2 hours |

**Total:** ~10-14 hours

## Rollout Strategy

1. **Phase 1 (Bug Fix)**: Release immediately as patch version (e.g., 0.7.1)
2. **Phase 2 (Static Scanning)**: Release in next minor version (e.g., 0.8.0)
3. **Phase 3 (Extended Detection)**: Release after user feedback (e.g., 0.9.0)
