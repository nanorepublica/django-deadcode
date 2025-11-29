# Spec: Improve URL Detection in Templates

## Overview

Expand the URL detection capability in `TemplateAnalyzer` to find internal URL references anywhere in HTML template files, not just in `href` attributes. This will reduce false positives when reporting unreferenced URLs.

## Problem Statement

The current implementation only extracts URLs from `href` attributes using the pattern:
```python
HREF_PATTERN = re.compile(r'href=["\']([^"\']*)["\']', re.IGNORECASE)
```

This misses URLs that appear in other contexts within templates:
- JavaScript code (inline or in `<script>` tags)
- Data attributes (e.g., `data-url="/api/endpoint/"`)
- Inline event handlers (e.g., `onclick="redirect('/path/')"`)
- JSON embedded in templates
- Other HTML attributes

As a result, URLs that ARE referenced in templates get incorrectly flagged as "unreferenced" because they appear outside of `href` attributes.

## Requirements

### Functional Requirements

1. **Detect internal URLs anywhere in template content**
   - Match any string that looks like an internal URL path
   - Internal URL criteria: starts with `/` but NOT `//` (to exclude protocol-relative URLs)
   - Should work regardless of context (JavaScript, data attributes, JSON, etc.)

2. **Support dynamic URLs with template variables**
   - Detect URLs containing Django template variables like `/user/{{ user.id }}/`
   - These should be matched and extracted for URL pattern matching

3. **Exclude URLs inside comments**
   - HTML comments: `<!-- ... -->`
   - JavaScript single-line comments: `// ...`
   - JavaScript multi-line comments: `/* ... */`

4. **Replace/expand current implementation**
   - This should replace the current `href`-only approach
   - The new implementation should be a superset (catch everything `href` did plus more)

### Out of Scope

- External URLs (URLs starting with `http://`, `https://`, or `//`)
- URL validation (checking if URLs are syntactically correct)
- Detecting URLs in Python code (only template files)

## Technical Approach

### Implementation Location

Modify `django_deadcode/analyzers/template_analyzer.py`:
- Update or replace `HREF_PATTERN` with a more comprehensive pattern
- Modify `_analyze_template_content()` to use the new detection approach

### Detection Strategy

1. **Pre-process**: Strip out comment blocks from content before URL extraction
   - Remove HTML comments: `<!-- ... -->`
   - Remove JS multi-line comments: `/* ... */`
   - Remove JS single-line comments: `// ...` (to end of line)

2. **Extract URLs**: Find all internal URL patterns in the cleaned content
   - Pattern should match strings starting with `/` (but not `//`)
   - Should handle quoted strings (`"..."` or `'...'`)
   - Should capture the URL path including any template variables

### URL Pattern Matching

The URL pattern should match paths like:
- `/` (root)
- `/path/`
- `/path/to/resource/`
- `/api/v1/users/`
- `/user/{{ user.id }}/`
- `/items/{{ item.pk }}/edit/`

### Comment Removal Patterns

```python
# HTML comments
HTML_COMMENT = re.compile(r'<!--.*?-->', re.DOTALL)

# JS multi-line comments
JS_MULTILINE_COMMENT = re.compile(r'/\*.*?\*/', re.DOTALL)

# JS single-line comments (be careful not to match URLs starting with //)
JS_SINGLELINE_COMMENT = re.compile(r'(?<!:)//.*$', re.MULTILINE)
```

Note: The single-line comment pattern uses a negative lookbehind `(?<!:)` to avoid matching protocol-relative URLs like `https://...` while still matching `// comment`.

## Test Cases

### Should Detect

1. Basic href (existing functionality):
   ```html
   <a href="/about/">About</a>
   ```

2. Data attributes:
   ```html
   <div data-url="/api/users/"></div>
   ```

3. JavaScript strings:
   ```html
   <script>
   const url = "/api/endpoint/";
   fetch("/api/data/");
   </script>
   ```

4. Inline event handlers:
   ```html
   <button onclick="location.href='/dashboard/'">Go</button>
   ```

5. Dynamic URLs with template variables:
   ```html
   <a href="/user/{{ user.id }}/">Profile</a>
   <script>const url = "/items/{{ item.pk }}/edit/";</script>
   ```

6. JSON in templates:
   ```html
   <script>
   const config = {
     "apiUrl": "/api/v1/",
     "dashboardUrl": "/dashboard/"
   };
   </script>
   ```

### Should NOT Detect

1. URLs inside HTML comments:
   ```html
   <!-- Old link: /deprecated/path/ -->
   ```

2. URLs inside JS single-line comments:
   ```html
   <script>
   // const oldUrl = "/old/endpoint/";
   const newUrl = "/new/endpoint/";
   </script>
   ```

3. URLs inside JS multi-line comments:
   ```html
   <script>
   /*
    * Old endpoints:
    * /api/v1/old/
    * /api/v1/deprecated/
    */
   const url = "/api/v2/current/";
   </script>
   ```

4. External URLs:
   ```html
   <a href="https://example.com/path/">External</a>
   <a href="//cdn.example.com/resource/">Protocol-relative</a>
   ```

5. Non-URL paths (CSS, file paths without leading slash):
   ```html
   <link rel="stylesheet" href="styles/main.css">
   <img src="images/logo.png">
   ```

## Acceptance Criteria

1. All URLs currently detected by `href` pattern continue to be detected
2. URLs in JavaScript code, data attributes, and other contexts are detected
3. URLs inside HTML comments are NOT detected
4. URLs inside JS comments (single-line and multi-line) are NOT detected
5. External URLs (http://, https://, //) are NOT detected
6. Dynamic URLs with Django template variables ({{ }}) are detected
7. Existing tests continue to pass
8. New tests cover the expanded detection scenarios

## Files to Modify

- `django_deadcode/analyzers/template_analyzer.py` - Main implementation
- `tests/test_template_href_extraction.py` - Update/expand tests

## Related Files for Reference

- `django_deadcode/utils/url_matching.py` - URL pattern matching utilities
- `tests/test_href_matching.py` - Tests for URL matching
