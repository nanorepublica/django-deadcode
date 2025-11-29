# Spec Requirements: Improve URL Detection

## Initial Description

Improve URL detection in django-deadcode to find internal URL references anywhere in HTML template files, not just in `href` attributes. This addresses false positives where URLs referenced in JavaScript, data attributes, or other contexts are incorrectly flagged as unreferenced.

## Requirements Discussion

### First Round Questions

**Q1:** Pattern Scope - Should we focus only on internal URLs starting with `/` and exclude external URLs?
**Answer:** Correct - continue focusing only on internal URLs starting with `/` and exclude external URLs

**Q2:** Template Variable URLs - Should we detect dynamic URLs with Django template variables like `/user/{{ user.id }}/`?
**Answer:** Correct - continue detecting dynamic URLs with Django template variables like `/user/{{ user.id }}/` anywhere in the template

**Q3:** JavaScript Patterns - Should we match any string that looks like an internal URL path in JavaScript, regardless of context?
**Answer:** Yes exactly - match any string that looks like an internal URL path (starts with `/`, not `//`), regardless of context

**Q4:** False Positive Concerns - Should we exclude URLs found in comments?
**Answer:** We should try to exclude JS comments and HTML comments

**Q5:** Replacement vs Addition - Should this replace or add to the current implementation?
**Answer:** It should expand the current/replace implementation

**Q6:** Out of Scope - Is there anything that should be explicitly out of scope?
**Answer:** Nothing comes to mind

### Existing Code to Reference

**Similar Features Identified:**
- Feature: Current href detection - Path: `django_deadcode/analyzers/template_analyzer.py`
- Components to potentially reuse: `HREF_PATTERN` regex, `_analyze_template_content()` method
- Backend logic to reference: URL matching in `django_deadcode/utils/url_matching.py`

### Follow-up Questions

No follow-up questions were needed.

## Visual Assets

### Files Provided:
No visual assets provided.

## Requirements Summary

### Functional Requirements
- Detect internal URLs anywhere in template files (not just `href` attributes)
- Match URLs in JavaScript code, data attributes, inline event handlers, JSON
- Support dynamic URLs containing Django template variables (`{{ }}`)
- Exclude URLs found inside HTML comments (`<!-- ... -->`)
- Exclude URLs found inside JavaScript single-line comments (`// ...`)
- Exclude URLs found inside JavaScript multi-line comments (`/* ... */`)
- Only match internal URLs (starting with `/`, not `//`)

### Reusability Opportunities
- Existing `HREF_PATTERN` provides baseline for what needs to be detected
- `_analyze_template_content()` method is the main integration point
- URL matching utilities in `url_matching.py` for pattern comparison
- Existing tests in `test_template_href_extraction.py` as test baseline

### Scope Boundaries

**In Scope:**
- Expanding URL detection to any context in template files
- Comment exclusion (HTML, JS single-line, JS multi-line)
- Support for template variables in URLs
- Internal URLs only (starting with `/`)

**Out of Scope:**
- External URLs (http://, https://, //)
- URL validation
- Detecting URLs in Python code
- Non-URL file paths (relative paths without leading slash)

### Technical Considerations
- Must be backward compatible (detect everything current `href` approach detects)
- Comment stripping should happen before URL extraction
- Care needed with JS single-line comment regex to not match protocol-relative URLs
- Regex patterns should use `re.DOTALL` for multi-line comment matching
