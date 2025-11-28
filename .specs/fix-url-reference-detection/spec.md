# Specification: Fix URL Reference Detection False Positives

## Overview

This spec addresses false positives in URL reference detection where valid URL patterns are incorrectly reported as unreferenced because the pattern normalization logic does not properly handle regex syntax commonly found in Django URL patterns.

## Problem Description

The current `normalize_path()` function in `django_deadcode/utils/url_matching.py` performs basic path normalization (removing leading slashes) but fails to account for regex syntax that Django uses in URL patterns. This causes the href-to-pattern matching to fail for patterns containing:

1. **Regex anchors** (`^` and `$`) - Patterns like `^about/$` don't match hrefs like `/about/`
2. **Optional trailing slash** (`/?`) - Patterns like `^about/?$` should match both `/about` and `/about/`
3. **Dynamic capture groups** - Patterns like `^user/(?P<id>\d+)/$` contain dynamic segments that cannot be matched with static hrefs alone

### Current Behavior

```python
# Current normalize_path implementation
def normalize_path(path: str) -> str:
    if not path or path == "/":
        return ""
    if path.startswith("/"):
        path = path[1:]
    return path
```

**Example failures:**
```python
# Pattern from RegexPattern: ^about/$
# Href from template: /about/
normalize_path("/about/")  # Returns "about/"
normalize_path("^about/$")  # Returns "^about/$" (unchanged!)
# Result: No match - FALSE POSITIVE
```

### Root Cause

The `_process_url_pattern()` method in `url_analyzer.py` extracts the raw regex pattern string for `RegexPattern` objects:

```python
elif isinstance(pattern.pattern, RegexPattern):
    pattern_str = pattern.pattern.regex.pattern  # e.g., "^about/$"
```

This raw regex string is stored and later compared against normalized hrefs, but the regex syntax is never stripped.

## Proposed Solution

### 1. Enhanced Pattern Normalization

Modify `normalize_path()` to handle URL patterns containing regex syntax by stripping regex-specific characters during normalization.

**New function signature and behavior:**

```python
def normalize_path(path: str) -> str:
    """
    Normalize a path for comparison.

    Handles both hrefs (e.g., '/about/') and URL patterns (e.g., '^about/$').
    Strips regex anchors and handles optional trailing slash patterns.
    """
```

**Normalization steps:**
1. Strip leading `^` anchor if present
2. Strip trailing `$` anchor if present
3. Handle optional trailing slash `/?` - convert to `/` for consistent comparison
4. Remove leading `/` if present
5. Return normalized path

### 2. Optional Trailing Slash Handling

For patterns using `/?$` (optional trailing slash):
- Pattern `^about/?$` should match both `/about` and `/about/`
- During normalization, convert `/?` to `/` for consistent matching
- The existing `match_href_to_pattern()` already strips trailing slashes during comparison, so this handles both cases

### 3. Dynamic URL Detection with Capture Groups

For patterns containing regex capture groups (e.g., `(?P<id>\d+)`):
- **Do NOT skip these patterns** - they represent real URLs that may be referenced
- Instead, look for Django template syntax indicators (`{{`) in hrefs that suggest dynamic URL construction
- If an href contains `{{`, it indicates a dynamically constructed URL

**Detection logic:**

```python
def has_capture_groups(pattern: str) -> bool:
    """Check if pattern contains regex capture groups."""
    # Match (?P<name>...) or (?:...) or simple groups (...)
    return bool(re.search(r'\([^)]+\)', pattern))

def extract_static_prefix(pattern: str) -> str:
    """Extract the static prefix before any capture group."""
    # Find the position of the first capture group
    match = re.search(r'\([^)]+\)', pattern)
    if match:
        return pattern[:match.start()]
    return pattern
```

**Matching strategy for dynamic patterns:**
1. If pattern has capture groups, extract the static prefix
2. Look for hrefs that:
   - Start with the static prefix AND
   - Contain `{{` (indicating Django template variable interpolation)
3. Example: Pattern `^user/(?P<id>\d+)/$` with static prefix `user/`
   - Matches href: `/user/{{ user.id }}/`
   - Does NOT match: `/user/123/` (static ID, would need exact regex matching)

## Implementation Details

### File: `django_deadcode/utils/url_matching.py`

#### Modified `normalize_path()` function:

```python
import re

# Regex to detect capture groups in URL patterns
CAPTURE_GROUP_PATTERN = re.compile(r'\([^)]+\)')

def normalize_path(path: str) -> str:
    """
    Normalize a path for comparison.

    Handles both hrefs (e.g., '/about/') and URL patterns (e.g., '^about/$').

    Normalization steps:
    1. Strip regex anchors (^ and $)
    2. Convert optional trailing slash (/?) to /
    3. Remove leading slash

    Args:
        path: URL path or pattern to normalize

    Returns:
        Normalized path suitable for comparison
    """
    if not path or path == "/":
        return ""

    # Strip regex anchors
    if path.startswith("^"):
        path = path[1:]
    if path.endswith("$"):
        path = path[:-1]

    # Handle optional trailing slash - convert /? to /
    if path.endswith("/?"):
        path = path[:-1]  # Remove the ?, keep the /

    # Remove leading slash
    if path.startswith("/"):
        path = path[1:]

    return path
```

#### New helper functions for dynamic URL matching:

```python
def has_capture_groups(pattern: str) -> bool:
    """
    Check if a URL pattern contains regex capture groups.

    Args:
        pattern: URL pattern string (may contain regex syntax)

    Returns:
        True if pattern contains capture groups like (?P<name>...) or (...)
    """
    return bool(CAPTURE_GROUP_PATTERN.search(pattern))


def extract_static_prefix(pattern: str) -> str:
    """
    Extract the static prefix from a pattern before any capture group.

    Args:
        pattern: URL pattern string

    Returns:
        The static portion of the pattern before the first capture group,
        or the entire pattern if no capture groups exist

    Examples:
        >>> extract_static_prefix("^user/(?P<id>\\d+)/$")
        'user/'
        >>> extract_static_prefix("^about/$")
        'about/'
    """
    # First normalize the pattern to remove anchors
    normalized = normalize_path(pattern)

    # Find first capture group
    match = CAPTURE_GROUP_PATTERN.search(normalized)
    if match:
        return normalized[:match.start()]
    return normalized


def is_dynamic_href(href: str) -> bool:
    """
    Check if an href contains Django template variable syntax.

    Args:
        href: Href value from a template

    Returns:
        True if href contains {{ indicating template variable interpolation
    """
    return "{{" in href
```

#### Modified `match_href_to_pattern()` function:

```python
def match_href_to_pattern(href: str, pattern: str) -> bool:
    """
    Check if an href matches a URL pattern.

    Uses normalized string matching. For patterns with capture groups,
    checks if dynamic hrefs (containing {{}}) match the static prefix.

    Args:
        href: The href from a template (e.g., '/about/', '/user/{{ id }}/')
        pattern: The URL pattern string (e.g., 'about/', '^user/(?P<id>\\d+)/$')

    Returns:
        True if the href matches the pattern, False otherwise
    """
    # Parse the href to extract path (remove query params and fragments)
    parsed = urlparse(href)
    href_path = parsed.path

    # Check if pattern has capture groups (dynamic segments)
    if has_capture_groups(pattern):
        # For dynamic patterns, check if href:
        # 1. Contains template variable syntax ({{)
        # 2. Starts with the static prefix of the pattern
        if is_dynamic_href(href_path):
            static_prefix = extract_static_prefix(pattern)
            normalized_href = normalize_path(href_path.split("{{")[0])
            # Check if href starts with the static prefix
            return normalized_href.rstrip("/").startswith(static_prefix.rstrip("/"))
        # Static hrefs cannot match dynamic patterns
        return False

    # For static patterns, use exact matching
    normalized_href = normalize_path(href_path)
    normalized_pattern = normalize_path(pattern)

    # Handle trailing slashes flexibly
    href_clean = normalized_href.rstrip("/")
    pattern_clean = normalized_pattern.rstrip("/")

    return href_clean == pattern_clean
```

## Test Cases

### Unit Tests for `normalize_path()`

```python
class TestNormalizePath:
    """Tests for enhanced normalize_path function."""

    # Existing behavior (should still pass)
    def test_normalize_removes_leading_slash(self):
        assert normalize_path("/about/") == "about/"

    def test_normalize_handles_root_path(self):
        assert normalize_path("/") == ""

    def test_normalize_handles_empty_string(self):
        assert normalize_path("") == ""

    # New: Regex anchor handling
    def test_normalize_strips_caret_anchor(self):
        assert normalize_path("^about/") == "about/"

    def test_normalize_strips_dollar_anchor(self):
        assert normalize_path("about/$") == "about/"

    def test_normalize_strips_both_anchors(self):
        assert normalize_path("^about/$") == "about/"

    def test_normalize_strips_anchors_multi_segment(self):
        assert normalize_path("^users/profile/$") == "users/profile/"

    # New: Optional trailing slash handling
    def test_normalize_optional_slash_at_end(self):
        assert normalize_path("^about/?$") == "about/"

    def test_normalize_optional_slash_without_anchors(self):
        assert normalize_path("about/?") == "about/"

    # Combined scenarios
    def test_normalize_leading_slash_and_anchors(self):
        # Pattern shouldn't have leading slash, but handle gracefully
        assert normalize_path("^/about/$") == "about/"
```

### Unit Tests for Capture Group Detection

```python
class TestCaptureGroupHandling:
    """Tests for dynamic URL pattern handling."""

    def test_has_capture_groups_named(self):
        assert has_capture_groups("^user/(?P<id>\\d+)/$") is True

    def test_has_capture_groups_unnamed(self):
        assert has_capture_groups("^user/(\\d+)/$") is True

    def test_has_capture_groups_none(self):
        assert has_capture_groups("^about/$") is False

    def test_has_capture_groups_with_non_capturing(self):
        assert has_capture_groups("^user/(?:\\d+)/$") is True

    def test_extract_static_prefix_simple(self):
        assert extract_static_prefix("^user/(?P<id>\\d+)/$") == "user/"

    def test_extract_static_prefix_nested(self):
        assert extract_static_prefix("^api/v1/users/(?P<id>\\d+)/$") == "api/v1/users/"

    def test_extract_static_prefix_no_groups(self):
        assert extract_static_prefix("^about/$") == "about/"

    def test_extract_static_prefix_group_at_start(self):
        assert extract_static_prefix("^(?P<lang>[a-z]{2})/about/$") == ""

    def test_is_dynamic_href_with_template_var(self):
        assert is_dynamic_href("/user/{{ user.id }}/") is True

    def test_is_dynamic_href_static(self):
        assert is_dynamic_href("/user/123/") is False
```

### Integration Tests for `match_href_to_pattern()`

```python
class TestMatchHrefToPatternEnhanced:
    """Tests for enhanced href to pattern matching."""

    # Regex anchor matching (previously failing)
    def test_match_with_caret_anchor(self):
        assert match_href_to_pattern("/about/", "^about/") is True

    def test_match_with_dollar_anchor(self):
        assert match_href_to_pattern("/about/", "about/$") is True

    def test_match_with_both_anchors(self):
        assert match_href_to_pattern("/about/", "^about/$") is True

    # Optional trailing slash matching
    def test_match_optional_slash_with_slash(self):
        assert match_href_to_pattern("/about/", "^about/?$") is True

    def test_match_optional_slash_without_slash(self):
        assert match_href_to_pattern("/about", "^about/?$") is True

    # Dynamic URL matching
    def test_dynamic_pattern_matches_dynamic_href(self):
        assert match_href_to_pattern(
            "/user/{{ user.id }}/",
            "^user/(?P<id>\\d+)/$"
        ) is True

    def test_dynamic_pattern_no_match_static_href(self):
        # Static href with actual number cannot match dynamic pattern
        assert match_href_to_pattern(
            "/user/123/",
            "^user/(?P<id>\\d+)/$"
        ) is False

    def test_dynamic_pattern_with_prefix(self):
        assert match_href_to_pattern(
            "/api/users/{{ user.pk }}/edit/",
            "^api/users/(?P<pk>\\d+)/edit/$"
        ) is True

    def test_dynamic_pattern_wrong_prefix(self):
        assert match_href_to_pattern(
            "/wrong/{{ user.id }}/",
            "^user/(?P<id>\\d+)/$"
        ) is False

    # Existing tests should still pass
    def test_simple_static_match(self):
        assert match_href_to_pattern("/about/", "about/") is True

    def test_no_match_different_paths(self):
        assert match_href_to_pattern("/about/", "contact/") is False
```

## Edge Cases

### 1. Patterns with Multiple Capture Groups

```python
# Pattern: ^user/(?P<user_id>\d+)/posts/(?P<post_id>\d+)/$
# Static prefix: user/
# Href: /user/{{ user.id }}/posts/{{ post.id }}/
# Should match: Yes (starts with "user/" and contains {{)
```

### 2. Capture Group at Start of Pattern

```python
# Pattern: ^(?P<lang>[a-z]{2})/about/$
# Static prefix: "" (empty)
# Href: /{{ lang }}/about/
# Should match: Yes (empty prefix always matches, and contains {{)
```

### 3. Non-Capturing Groups

```python
# Pattern: ^articles/(?:page-)?(?P<num>\d+)/$
# This contains both non-capturing (?:...) and capturing (?P<>...) groups
# Static prefix: articles/
# Should detect as dynamic pattern
```

### 4. Character Classes (Not Capture Groups)

```python
# Pattern: ^files/[a-z]+\.pdf$
# This is NOT a capture group - [a-z] is a character class
# Should NOT be detected as dynamic
# Current regex will correctly not match this as a capture group
```

### 5. Escaped Parentheses

```python
# Pattern: ^search/\(term\)/$
# Escaped parens should not be detected as capture groups
# Note: In practice, this is rare in Django URL patterns
```

## Migration / Compatibility

### Backward Compatibility

- All existing tests should continue to pass
- Static URL patterns without regex syntax work exactly as before
- The change is additive - patterns that previously matched will still match

### Django Version

- Target: Django 5.0+ only
- No need to support older `re_path` patterns from Django 1.x/2.x that used different syntax

## Success Criteria

1. Patterns with `^` and `$` anchors correctly match corresponding hrefs
2. Patterns with `/?` optional trailing slash match hrefs both with and without trailing slash
3. Dynamic patterns with capture groups match hrefs containing `{{` template syntax
4. Static hrefs (without `{{`) do NOT match dynamic patterns (avoiding false negatives)
5. All existing tests pass
6. No regression in detection accuracy for static URL patterns

## Files to Modify

1. `django_deadcode/utils/url_matching.py` - Primary changes
   - Enhance `normalize_path()`
   - Add `has_capture_groups()`, `extract_static_prefix()`, `is_dynamic_href()`
   - Modify `match_href_to_pattern()`

2. `tests/test_href_matching.py` - Add new test cases
   - Tests for regex anchor stripping
   - Tests for optional trailing slash
   - Tests for dynamic URL matching

## Out of Scope

- Full regex evaluation/compilation of URL patterns
- Matching static hrefs like `/user/123/` against dynamic patterns (would require regex evaluation)
- Support for Django versions prior to 5.0
- Changes to `url_analyzer.py` (pattern extraction is correct, only matching needs fixing)
