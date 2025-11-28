# Task Breakdown: Fix URL Reference Detection False Positives

## Overview
Total Tasks: 3 Task Groups with 16 Sub-tasks

This feature enhances the URL pattern matching logic in `django_deadcode/utils/url_matching.py` to properly handle Django URL patterns containing regex syntax (anchors, optional trailing slash, capture groups).

## Files to Modify

| File | Purpose |
|------|---------|
| `django_deadcode/utils/url_matching.py` | Primary implementation - all code changes |
| `tests/test_href_matching.py` | Add new test cases for enhanced functionality |

## Task List

### Core Utilities Layer

#### Task Group 1: Path Normalization Enhancement
**Dependencies:** None
**Specialist:** Python Backend Engineer

- [ ] 1.0 Complete path normalization enhancement for regex syntax
  - [ ] 1.1 Write 6 focused tests for enhanced `normalize_path()` functionality
    - Test stripping `^` anchor from start of pattern
    - Test stripping `$` anchor from end of pattern
    - Test stripping both anchors together (e.g., `^about/$`)
    - Test optional trailing slash `/?` conversion to `/`
    - Test combined anchors with optional slash (e.g., `^about/?$`)
    - Test multi-segment patterns with anchors (e.g., `^users/profile/$`)
    - Add tests to existing `TestPathNormalization` class in `tests/test_href_matching.py`
  - [ ] 1.2 Add regex anchor stripping to `normalize_path()`
    - Strip leading `^` anchor if present
    - Strip trailing `$` anchor if present
    - Maintain existing behavior for paths without anchors
    - Location: `django_deadcode/utils/url_matching.py`
  - [ ] 1.3 Add optional trailing slash handling to `normalize_path()`
    - Detect `/?` at end of path (before `$` stripping)
    - Convert `/?` to `/` for consistent comparison
    - Handle edge case: `/?$` should become `/`
  - [ ] 1.4 Update `normalize_path()` docstring
    - Document new behavior for regex syntax
    - Add examples showing anchor stripping
    - Document optional trailing slash handling
  - [ ] 1.5 Ensure normalization tests pass
    - Run ONLY the 6 tests written in 1.1 plus existing normalization tests
    - Verify all existing `TestPathNormalization` tests still pass (backward compatibility)
    - Command: `pytest tests/test_href_matching.py::TestPathNormalization -v`

**Acceptance Criteria:**
- `normalize_path("^about/$")` returns `"about/"`
- `normalize_path("^about/?$")` returns `"about/"`
- `normalize_path("^users/profile/$")` returns `"users/profile/"`
- All existing normalization tests continue to pass
- The 6 new tests from 1.1 pass

---

#### Task Group 2: Dynamic URL Pattern Matching
**Dependencies:** Task Group 1
**Specialist:** Python Backend Engineer

- [ ] 2.0 Complete dynamic URL pattern matching with capture group support
  - [ ] 2.1 Write 8 focused tests for capture group detection and dynamic matching
    - Test `has_capture_groups()` with named group `(?P<id>\d+)`
    - Test `has_capture_groups()` with unnamed group `(\d+)`
    - Test `has_capture_groups()` returns False for static patterns
    - Test `extract_static_prefix()` extracts prefix before capture group
    - Test `extract_static_prefix()` handles capture group at start (empty prefix)
    - Test `is_dynamic_href()` detects `{{` in href
    - Test `is_dynamic_href()` returns False for static href
    - Test integration: dynamic pattern matches dynamic href
    - Add new test class `TestCaptureGroupHandling` in `tests/test_href_matching.py`
  - [ ] 2.2 Add `CAPTURE_GROUP_PATTERN` regex constant
    - Pattern: `re.compile(r'\([^)]+\)')`
    - Add `import re` at top of file if not present
    - Location: Top of `django_deadcode/utils/url_matching.py`
  - [ ] 2.3 Implement `has_capture_groups()` helper function
    - Accept pattern string as input
    - Return True if pattern contains `(...)` groups
    - Use `CAPTURE_GROUP_PATTERN.search()` for detection
    - Add comprehensive docstring with examples
  - [ ] 2.4 Implement `extract_static_prefix()` helper function
    - Normalize the pattern first (using enhanced `normalize_path()`)
    - Find first capture group position
    - Return substring before first capture group
    - Return full normalized pattern if no capture groups
    - Add docstring with examples
  - [ ] 2.5 Implement `is_dynamic_href()` helper function
    - Check if href contains `{{` (Django template variable syntax)
    - Return boolean result
    - Add docstring explaining purpose
  - [ ] 2.6 Ensure helper function tests pass
    - Run ONLY tests for the new helper functions
    - Command: `pytest tests/test_href_matching.py::TestCaptureGroupHandling -v`

**Acceptance Criteria:**
- `has_capture_groups("^user/(?P<id>\d+)/$")` returns `True`
- `has_capture_groups("^about/$")` returns `False`
- `extract_static_prefix("^user/(?P<id>\d+)/$")` returns `"user/"`
- `is_dynamic_href("/user/{{ user.id }}/")` returns `True`
- `is_dynamic_href("/user/123/")` returns `False`
- All 8 tests from 2.1 pass

---

#### Task Group 3: Integration and Match Function Enhancement
**Dependencies:** Task Groups 1 and 2
**Specialist:** Python Backend Engineer

- [ ] 3.0 Complete `match_href_to_pattern()` enhancement and integration testing
  - [ ] 3.1 Write 8 focused integration tests for enhanced matching
    - Test static pattern with `^` anchor matches href (e.g., `^about/` matches `/about/`)
    - Test static pattern with `$` anchor matches href
    - Test static pattern with both anchors matches href
    - Test optional slash pattern matches href with slash
    - Test optional slash pattern matches href without slash
    - Test dynamic pattern matches dynamic href with `{{}}`
    - Test dynamic pattern does NOT match static href (important false negative prevention)
    - Test dynamic pattern with wrong prefix does NOT match
    - Add new test class `TestMatchHrefToPatternEnhanced` in `tests/test_href_matching.py`
  - [ ] 3.2 Modify `match_href_to_pattern()` for dynamic patterns
    - Check if pattern has capture groups using `has_capture_groups()`
    - If dynamic pattern:
      - Check if href contains `{{` using `is_dynamic_href()`
      - Extract static prefix using `extract_static_prefix()`
      - Extract href portion before `{{`
      - Compare normalized prefixes (startswith check)
      - Return False for static hrefs against dynamic patterns
    - If static pattern: use existing exact matching logic
  - [ ] 3.3 Update `match_href_to_pattern()` docstring
    - Document new dynamic URL matching behavior
    - Add examples for dynamic pattern matching
    - Explain why static hrefs don't match dynamic patterns
  - [ ] 3.4 Update module exports
    - Add new functions to module `__all__` if present
    - Ensure new functions are importable from the module
  - [ ] 3.5 Ensure all integration tests pass
    - Run ONLY the integration tests for enhanced matching
    - Verify existing `TestHrefToPatternMatching` tests still pass
    - Command: `pytest tests/test_href_matching.py::TestMatchHrefToPatternEnhanced tests/test_href_matching.py::TestHrefToPatternMatching -v`

**Acceptance Criteria:**
- `match_href_to_pattern("/about/", "^about/$")` returns `True`
- `match_href_to_pattern("/about/", "^about/?$")` returns `True`
- `match_href_to_pattern("/about", "^about/?$")` returns `True`
- `match_href_to_pattern("/user/{{ user.id }}/", "^user/(?P<id>\d+)/$")` returns `True`
- `match_href_to_pattern("/user/123/", "^user/(?P<id>\d+)/$")` returns `False`
- All existing `TestHrefToPatternMatching` tests pass (backward compatibility)
- All 8 tests from 3.1 pass

---

### Testing

#### Task Group 4: Final Verification and Edge Cases
**Dependencies:** Task Groups 1-3
**Specialist:** Python Backend Engineer / QA

- [ ] 4.0 Complete final verification and edge case coverage
  - [ ] 4.1 Review all tests from Task Groups 1-3
    - Verify 6 tests from Task 1.1 (normalization)
    - Verify 8 tests from Task 2.1 (helper functions)
    - Verify 8 tests from Task 3.1 (integration)
    - Total existing new tests: 22 tests
  - [ ] 4.2 Identify critical edge case gaps
    - Multiple capture groups in one pattern
    - Capture group at start of pattern (empty prefix)
    - Non-capturing groups `(?:...)`
    - Character classes `[a-z]` (should NOT be detected as capture groups)
    - Patterns with both leading slash and anchors
  - [ ] 4.3 Write up to 6 additional edge case tests
    - Test pattern with multiple capture groups
    - Test pattern with capture group at start
    - Test non-capturing group detection
    - Test character class is NOT detected as capture group
    - Test `find_matching_url_patterns()` works with new matching logic
    - Add to appropriate test classes in `tests/test_href_matching.py`
  - [ ] 4.4 Run complete test suite for this feature
    - Run ALL tests in `tests/test_href_matching.py`
    - Verify no regressions in existing functionality
    - Command: `pytest tests/test_href_matching.py -v`
  - [ ] 4.5 Run related integration tests
    - Run URL analyzer tests to ensure no regressions
    - Command: `pytest tests/test_url_analyzer.py tests/test_integration_url_enhancements.py -v`

**Acceptance Criteria:**
- All tests in `tests/test_href_matching.py` pass (approximately 28-30 total tests)
- All edge cases identified in 4.2 are covered
- No regressions in existing URL matching functionality
- Related integration tests pass

---

## Execution Order

Recommended implementation sequence:

```
Task Group 1: Path Normalization Enhancement
     |
     v
Task Group 2: Dynamic URL Pattern Matching
     |
     v
Task Group 3: Integration and Match Function Enhancement
     |
     v
Task Group 4: Final Verification and Edge Cases
```

**Notes:**
- All task groups can be completed by a single Python backend engineer
- Each group builds on the previous one
- Tests are written first in each group (TDD approach)
- Backward compatibility is verified at each stage

## Implementation Reference

### Key Code Snippets from Spec

**Enhanced normalize_path():**
```python
def normalize_path(path: str) -> str:
    if not path or path == "/":
        return ""

    # Strip regex anchors
    if path.startswith("^"):
        path = path[1:]
    if path.endswith("$"):
        path = path[:-1]

    # Handle optional trailing slash
    if path.endswith("/?"):
        path = path[:-1]  # Remove ?, keep /

    # Remove leading slash
    if path.startswith("/"):
        path = path[1:]

    return path
```

**Helper functions:**
```python
CAPTURE_GROUP_PATTERN = re.compile(r'\([^)]+\)')

def has_capture_groups(pattern: str) -> bool:
    return bool(CAPTURE_GROUP_PATTERN.search(pattern))

def extract_static_prefix(pattern: str) -> str:
    normalized = normalize_path(pattern)
    match = CAPTURE_GROUP_PATTERN.search(normalized)
    if match:
        return normalized[:match.start()]
    return normalized

def is_dynamic_href(href: str) -> bool:
    return "{{" in href
```

## Success Criteria Summary

1. Patterns with `^` and `$` anchors correctly match corresponding hrefs
2. Patterns with `/?` optional trailing slash match hrefs both with and without trailing slash
3. Dynamic patterns with capture groups match hrefs containing `{{` template syntax
4. Static hrefs do NOT match dynamic patterns (avoiding false negatives)
5. All existing tests pass (backward compatibility)
6. No regression in detection accuracy for static URL patterns
