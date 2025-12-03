# Raw Idea: Fix Unreferenced URL Detection

## Problem
URLs used inside JavaScript in Django HTML templates are being reported as "unreferenced URLs" even when they're clearly being used.

Example of false positive:
```
• client_mfp_code
    View: FMP.nutritionist.views.views.client_mfp_code
    Pattern: ^nutritionist/client/client_mfp_code/$
```

But the URL IS being used in inline JavaScript:
```javascript
function saveMFPCode(){
  code = $('#client_mfp_code').val()
  $.ajax({
            url: '/nutritionist/client/client_mfp_code/',
            ...
        });
}
```

## Root Cause
When using nested `include()` with mixed `path()` and `re_path()`, regex anchors (`^` and `$`) end up embedded in the MIDDLE of the accumulated pattern string, not at the start/end. The current `normalize_path()` only strips anchors from start/end.

Example:
- URL config: `path('nutritionist/', include(...))` + `re_path(r'^client/client_mfp_code/$', ...)`
- Accumulated pattern: `nutritionist/^client/client_mfp_code/$`
- After normalization: `nutritionist/^client/client_mfp_code/` (embedded ^ NOT stripped!)
- Href: `/nutritionist/client/client_mfp_code/`
- Match: FALSE (should be TRUE)

## Additional Requirements
1. **External JS file scanning**: Scan `.js` files in static directories for URL references
2. **Aggressiveness flag**: Command-line flag for URL detection aggressiveness:
   - Default: Static string URLs only
   - Aggressive: Also detect string concatenations and template literals

## User Answers to Clarifying Questions
1. Location of JS: Inline in HTML template
2. Template location: Standard .html extension, findable by Django loader
3. Approach: Debug existing detection (option A)
4. Edge cases: String concat and template literals with aggressiveness flag
5. External JS: Yes, should scan
6. Exclusions: None
