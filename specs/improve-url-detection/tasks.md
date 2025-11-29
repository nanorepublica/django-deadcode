# Task Breakdown: Improve URL Detection in Templates

## Overview
Total Tasks: 15 sub-tasks across 3 task groups

This implementation expands the URL detection capability in `TemplateAnalyzer` to find internal URL references anywhere in HTML template files, not just in `href` attributes. The key changes involve adding comment-stripping patterns and a comprehensive URL detection pattern.

## Files to Modify
- `/home/user/django-deadcode/django_deadcode/analyzers/template_analyzer.py` - Main implementation
- `/home/user/django-deadcode/tests/test_template_href_extraction.py` - Update/expand tests

## Task List

### Analyzer Enhancement

#### Task Group 1: Comment Stripping Implementation
**Dependencies:** None

- [ ] 1.0 Complete comment stripping functionality
  - [ ] 1.1 Write 4 focused tests for comment stripping behavior
    - Test HTML comment removal: `<!-- /path/ -->` should be stripped
    - Test JS multi-line comment removal: `/* /path/ */` should be stripped
    - Test JS single-line comment removal: `// /path/` should be stripped
    - Test that protocol URLs like `https://example.com` are NOT affected by single-line comment stripping
  - [ ] 1.2 Add comment pattern constants to TemplateAnalyzer
    - Add `HTML_COMMENT_PATTERN = re.compile(r'<!--.*?-->', re.DOTALL)`
    - Add `JS_MULTILINE_COMMENT_PATTERN = re.compile(r'/\*.*?\*/', re.DOTALL)`
    - Add `JS_SINGLELINE_COMMENT_PATTERN = re.compile(r'(?<!:)//.*$', re.MULTILINE)`
    - Place after existing pattern definitions (line 14)
  - [ ] 1.3 Create `_strip_comments()` helper method
    - Accept content string as parameter
    - Apply HTML comment pattern first
    - Apply JS multi-line comment pattern second
    - Apply JS single-line comment pattern last
    - Return cleaned content string
    - Add after line 50 (after `_is_relative_to` method)
  - [ ] 1.4 Ensure comment stripping tests pass
    - Run ONLY the 4 tests written in 1.1
    - Verify comments are properly stripped
    - Verify protocol URLs are preserved

**Acceptance Criteria:**
- The 4 tests written in 1.1 pass
- HTML comments are fully removed (including multi-line)
- JS multi-line comments are fully removed
- JS single-line comments are removed without affecting `://` in URLs
- Method returns cleaned content ready for URL extraction

---

#### Task Group 2: URL Pattern Enhancement
**Dependencies:** Task Group 1

- [ ] 2.0 Complete URL pattern enhancement
  - [ ] 2.1 Write 6 focused tests for expanded URL detection
    - Test URL in data attribute: `<div data-url="/api/users/">` extracts `/api/users/`
    - Test URL in JavaScript string: `const url = "/api/endpoint/";` extracts `/api/endpoint/`
    - Test URL in inline event handler: `onclick="location.href='/dashboard/'"` extracts `/dashboard/`
    - Test URL in JSON config: `"apiUrl": "/api/v1/"` extracts `/api/v1/`
    - Test dynamic URL with template variable: `/user/{{ user.id }}/` is extracted
    - Test that URLs inside stripped comments are NOT extracted
  - [ ] 2.2 Add comprehensive URL pattern constant
    - Create `INTERNAL_URL_PATTERN` to match quoted internal URL paths
    - Pattern should match strings starting with `/` (not `//`)
    - Pattern should handle both single and double quotes
    - Pattern should capture Django template variables: `{{ ... }}`
    - Suggested pattern: `re.compile(r'["\'](/(?!/)[^"\']*)["\']')`
    - Place after comment pattern definitions
  - [ ] 2.3 Update `_analyze_template_content()` method
    - Call `_strip_comments()` on content first (before any extraction)
    - Replace `HREF_PATTERN.findall()` usage with `INTERNAL_URL_PATTERN.findall()`
    - Keep existing filtering logic for internal URLs (starts with `/`, not `//`)
    - Update on lines 131-140
  - [ ] 2.4 Ensure URL pattern tests pass
    - Run ONLY the 6 tests written in 2.1
    - Verify URLs are extracted from various contexts
    - Verify commented URLs are NOT extracted

**Acceptance Criteria:**
- The 6 tests written in 2.1 pass
- URLs in `href`, `data-*`, JavaScript, and JSON are all detected
- URLs with Django template variables are detected
- External URLs (http://, https://, //) are excluded
- URLs inside any type of comment are excluded

---

### Testing

#### Task Group 3: Test Coverage Review and Gap Analysis
**Dependencies:** Task Groups 1-2

- [ ] 3.0 Review existing tests and fill critical gaps
  - [ ] 3.1 Review tests from Task Groups 1-2
    - Review the 4 tests from Task 1.1 (comment stripping)
    - Review the 6 tests from Task 2.1 (URL pattern)
    - Total new tests: 10 tests
  - [ ] 3.2 Verify existing tests still pass
    - Run all tests in `test_template_href_extraction.py`
    - Existing tests (15 tests) must continue to pass
    - This validates backward compatibility
  - [ ] 3.3 Analyze test coverage gaps for this feature
    - Identify any critical scenarios not covered by Tasks 1.1, 2.1, or existing tests
    - Focus on edge cases specific to the new functionality
    - Prioritize integration scenarios
  - [ ] 3.4 Write up to 5 additional tests if needed
    - Add maximum 5 new tests to fill identified gaps
    - Suggested gap areas:
      - Multi-line HTML comment with URLs
      - Mixed commented and non-commented URLs in same content
      - Edge case: URL at very start of content
      - Edge case: Nested quotes in JavaScript
      - Integration: `get_all_internal_hrefs()` returns expanded results
  - [ ] 3.5 Run complete feature test suite
    - Run all tests in `test_template_href_extraction.py`
    - Expected: ~25-30 total tests pass
    - Verify no regressions in existing functionality

**Acceptance Criteria:**
- All 15 existing tests continue to pass (backward compatibility)
- All 10 new tests from Task Groups 1-2 pass
- Up to 5 additional gap tests pass (if added)
- No regressions in URL detection for `href` attributes
- Expanded detection works for all specified contexts

---

## Execution Order

Recommended implementation sequence:

1. **Task Group 1: Comment Stripping** (Foundation)
   - Must be completed first as URL detection depends on clean content
   - Introduces new regex patterns and helper method
   - Low risk, isolated functionality

2. **Task Group 2: URL Pattern Enhancement** (Core Feature)
   - Builds on comment stripping from Task Group 1
   - Modifies the main detection logic
   - Higher risk, requires careful testing

3. **Task Group 3: Test Coverage Review** (Validation)
   - Validates all changes work together
   - Ensures backward compatibility
   - Fills any remaining gaps

## Implementation Notes

### Key Code Locations

**Pattern Definitions (add new patterns here):**
```python
# Line 11-14 in template_analyzer.py
HREF_PATTERN = re.compile(r'href=["\']([^"\']*)["\']', re.IGNORECASE)
URL_TAG_PATTERN = re.compile(r'{%\s*url\s+["\']([^"\']+)["\']', re.MULTILINE)
# Add comment patterns and INTERNAL_URL_PATTERN after line 14
```

**Content Analysis Method (modify this):**
```python
# Lines 120-161 in template_analyzer.py
def _analyze_template_content(self, content: str, template_name: str) -> dict:
    # Add comment stripping call at start
    # Replace HREF_PATTERN usage with INTERNAL_URL_PATTERN
```

### Pattern Specifications

**Comment Patterns:**
```python
HTML_COMMENT_PATTERN = re.compile(r'<!--.*?-->', re.DOTALL)
JS_MULTILINE_COMMENT_PATTERN = re.compile(r'/\*.*?\*/', re.DOTALL)
JS_SINGLELINE_COMMENT_PATTERN = re.compile(r'(?<!:)//.*$', re.MULTILINE)
```

**URL Pattern:**
```python
INTERNAL_URL_PATTERN = re.compile(r'["\'](/(?!/)[^"\']*)["\']')
```

### Backward Compatibility Considerations

- The `hrefs` key in the result dictionary must continue to work
- Existing tests filter for internal URLs (starts with `/`, not `//`)
- The `get_all_internal_hrefs()` method must return expanded results
- All existing test assertions must remain valid

## Risk Assessment

| Task Group | Risk Level | Mitigation |
|------------|------------|------------|
| 1. Comment Stripping | Low | Isolated helper method, easy to test |
| 2. URL Pattern | Medium | Comprehensive pattern testing, backward compat checks |
| 3. Test Coverage | Low | Validation only, no code changes |

## Definition of Done

- [ ] All comment types are properly stripped before URL extraction
- [ ] URLs are detected in all specified contexts (href, data-*, JS, JSON)
- [ ] URLs inside comments are NOT detected
- [ ] Dynamic URLs with Django template variables are detected
- [ ] External URLs are excluded
- [ ] All existing tests pass (backward compatibility)
- [ ] All new tests pass
- [ ] Code follows existing patterns in the codebase
