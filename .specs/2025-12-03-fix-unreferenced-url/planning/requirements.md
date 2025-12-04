# Requirements: Fix Unreferenced URL Detection

## Initial Description

Fix false positives in URL reference detection where URLs used inside JavaScript in Django HTML templates are incorrectly reported as "unreferenced URLs".

## User-Reported Issue

**Example from report:**
```
• client_mfp_code
    View: FMP.nutritionist.views.views.client_mfp_code
    Pattern: ^nutritionist/client/client_mfp_code/$
```

**The URL IS being used in inline JavaScript:**
```javascript
function saveMFPCode(){
  code = $('#client_mfp_code').val()
  $.ajax({
            url: '/nutritionist/client/client_mfp_code/',
            data: {
            'client_id': {{ client.pk }},
            'code': code,
            },
            success: function (data) {
              location.reload()
            }
        });
}
```

## Requirements Discussion

### Clarifying Questions and Answers

**Q1:** Is the JavaScript code inline in the Django HTML template, or in a separate `.js` file?
**A1:** Inline

**Q2:** Is the template file in a standard Django templates directory with `.html` extension?
**A2:** Yes, it has a `.html` extension and is findable by the Django Template loader

**Q3:** Should we debug why existing detection isn't working (A), or add a more robust solution (B)?
**A3:** A - Debug why existing detection isn't working

**Q4:** Should we also consider string concatenation and template literals?
**A4:** Yes, these could be considered. Perhaps with a flag on the command line in terms of aggressiveness.

**Q5:** Should django-deadcode also scan `.js` files in static directories?
**A5:** Yes

**Q6:** Are there any specific scenarios to exclude from detection?
**A6:** Nope

## Root Cause Analysis

### Investigation Results

The core detection logic (regex extraction, pattern matching, normalization) is correctly implemented and tested. The bug is in how patterns are accumulated when using nested `include()` statements.

### The Bug

When using nested `include()` with mixed `path()` and `re_path()`:

1. `path('nutritionist/', include(...))` produces prefix: `nutritionist/`
2. `re_path(r'^client/client_mfp_code/$', ...)` produces pattern: `^client/client_mfp_code/$`
3. URLAnalyzer concatenates them: `nutritionist/^client/client_mfp_code/$`
4. `normalize_path()` only strips `^` from start and `$` from end
5. Result: `nutritionist/^client/client_mfp_code/` (embedded `^` remains!)
6. This never matches the href `nutritionist/client/client_mfp_code/`

### Code Location

**File:** `django_deadcode/utils/url_matching.py`
**Lines:** 44-47

```python
# Current (buggy) implementation:
if path.startswith("^"):  # NOT TRUE for "nutritionist/^..."
    path = path[1:]
if path.endswith("$"):    # TRUE, strips trailing $
    path = path[:-1]
```

**Fix:**
```python
# Replace with:
path = path.replace("^", "")
path = path.replace("$", "")
```

## Existing Code Reference

### Key Files

| File | Purpose | Path |
|------|---------|------|
| url_matching.py | Pattern normalization and matching | `django_deadcode/utils/url_matching.py` |
| url_analyzer.py | URL pattern discovery and accumulation | `django_deadcode/analyzers/url_analyzer.py` |
| template_analyzer.py | Template and href extraction | `django_deadcode/analyzers/template_analyzer.py` |
| finddeadcode.py | Management command | `django_deadcode/management/commands/finddeadcode.py` |
| test_href_matching.py | Tests for pattern matching | `tests/test_href_matching.py` |

### Existing Patterns to Reuse

- `INTERNAL_URL_PATTERN` in template_analyzer.py: `r'["\'](/(?!/)[^"\']*)["\']'`
- `normalize_path()` function structure
- `match_href_to_pattern()` function structure
- Test class organization in test_href_matching.py

## Visual Assets

No visual assets provided.

## Requirements Summary

### Functional Requirements

1. **Bug Fix: Embedded Anchors**
   - Strip all `^` and `$` characters from URL patterns, not just at start/end
   - Must handle patterns like `prefix/^middle/suffix/$`
   - Must handle deeply nested includes with multiple embedded anchors

2. **Feature: Static File Scanning**
   - Add `--scan-static` CLI flag to enable JavaScript file scanning
   - Scan `.js` and `.mjs` files in `STATICFILES_DIRS` and app static folders
   - Use existing URL extraction patterns
   - Filter by `BASE_DIR` to exclude third-party code

3. **Feature: Detection Aggressiveness**
   - Add `--url-detection [basic|extended]` CLI flag
   - `basic` (default): Static string URLs only
   - `extended`: Also detect template literals and string concatenation prefixes

### Non-Functional Requirements

1. **Backward Compatibility**
   - All existing tests must pass
   - New features are opt-in via CLI flags
   - No breaking changes to existing behavior

2. **Performance**
   - Static file scanning should be lazy (only when flag is set)
   - Extended detection should not significantly slow down analysis

3. **Testing**
   - All bug fixes must have corresponding test cases
   - New features must have unit and integration tests
   - Test coverage should not decrease

### Scope Boundaries

**In Scope:**
- Fix `normalize_path()` for embedded anchors
- Add static file scanning capability
- Add detection aggressiveness flag
- Add comprehensive tests

**Out of Scope:**
- Full regex evaluation of URL patterns
- Scanning minified JavaScript
- Scanning node_modules/vendor directories
- Source map support
- Real-time/watch mode

## Technical Considerations

- Target Django 4.2+ and Django 5.x
- Python 3.10+ required
- No new dependencies needed
- All changes contained within existing file structure
