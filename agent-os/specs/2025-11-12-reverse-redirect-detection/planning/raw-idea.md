# Reverse/Redirect Detection Feature

## Feature Description
Implement Python AST analysis to find all reverse() and redirect() calls in view code, capturing programmatic URL references beyond templates. This is a high priority feature for reducing false positives in dead code detection.

## Detailed Context
From the v0.2.0 roadmap, this feature should:
- Add AST parsing for `reverse()` calls
- Detect `redirect()` to URL names
- Track `HttpResponseRedirect(reverse(...))`

## Project Context
- Project: django-deadcode (Django dead code analysis tool)
- Current version: v0.1.0 (MVP complete)
- This feature is planned for v0.2.0
- Priority: High (reduces false positives)
- Size estimate: Large (L)

## Date Initiated
2025-11-12
