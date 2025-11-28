# Spec Requirements: Fix URL Reference Detection False Positives

## Initial Description

Fix false positives in URL reference detection where valid URL patterns containing regex syntax (anchors, optional trailing slash, capture groups) are incorrectly reported as unreferenced.

## Requirements Discussion

### First Round Questions

**Q1:** How should regex anchors be handled?
**Answer:** Handle both `^` (start) and `$` (end) anchors - strip them during normalization

**Q2:** How should optional trailing slash patterns be handled?
**Answer:** Patterns like `^about/?$` should match both `/about` and `/about/` - need to handle the `/?` optional slash pattern

**Q3:** Should dynamic URLs with capture groups be skipped?
**Answer:** Do NOT skip these. Instead, for patterns with capture groups like `^user/(?P<id>\d+)/$`, look for `{{` characters in Django templates as indicators that the URL is being dynamically constructed (e.g., `href="/user/{{ user.id }}/"`)

**Q4:** What Django versions should be supported?
**Answer:** Support Django 5+ only

**Q5:** What is the scope of changes?
**Answer:** Focus on normalization logic in `url_matching.py`

### Existing Code to Reference

**Key Files Identified:**
- File: `url_matching.py` - Path: `/home/user/django-deadcode/django_deadcode/utils/url_matching.py`
- File: `url_analyzer.py` - Path: `/home/user/django-deadcode/django_deadcode/analyzers/url_analyzer.py`
- Test file: `test_href_matching.py` - Path: `/home/user/django-deadcode/tests/test_href_matching.py`

**Components to reference:**
- `normalize_path()` function - needs enhancement for regex syntax
- `match_href_to_pattern()` function - needs dynamic URL matching logic
- `find_matching_url_patterns()` function - no changes needed

## Visual Assets

No visual assets provided.

## Requirements Summary

### Functional Requirements

1. **Regex Anchor Stripping**: Strip `^` and `$` anchors from URL patterns during normalization
2. **Optional Trailing Slash**: Handle `/?` pattern to match both `/path` and `/path/`
3. **Dynamic URL Detection**: Detect capture groups in patterns and match against hrefs containing `{{` template syntax
4. **Prefix Matching**: For dynamic patterns, extract static prefix and match against dynamic hrefs

### Reusability Opportunities

- Existing `normalize_path()` function can be enhanced in-place
- Existing `match_href_to_pattern()` function can be extended
- Existing test structure in `test_href_matching.py` can be followed

### Scope Boundaries

**In Scope:**
- Enhance `normalize_path()` to strip regex anchors
- Handle optional trailing slash pattern `/?`
- Add capture group detection logic
- Add dynamic href detection (looking for `{{`)
- Add static prefix extraction for dynamic patterns
- Modify `match_href_to_pattern()` for dynamic URL matching
- Add comprehensive tests

**Out of Scope:**
- Full regex evaluation/compilation of URL patterns
- Matching static hrefs like `/user/123/` against dynamic patterns
- Support for Django versions prior to 5.0
- Changes to `url_analyzer.py` (pattern extraction is correct)
- Changes to template analyzer

### Technical Considerations

- Django 5+ only (no legacy `re_path` syntax concerns)
- All changes contained within `url_matching.py`
- Backward compatible - existing tests must continue to pass
- Use Python `re` module for capture group detection
