# Spec Requirements: Reverse/Redirect Detection

## Initial Description
Implement Python AST analysis to find all reverse() and redirect() calls in view code, capturing programmatic URL references beyond templates. This is a high priority feature for reducing false positives in dead code detection.

From the v0.2.0 roadmap, this feature should:
- Add AST parsing for `reverse()` calls
- Detect `redirect()` to URL names
- Track `HttpResponseRedirect(reverse(...))`

Project Context:
- Project: django-deadcode (Django dead code analysis tool)
- Current version: v0.1.0 (MVP complete)
- This feature is planned for v0.2.0
- Priority: High (reduces false positives)
- Size estimate: Large (L)

## Requirements Discussion

### First Round Questions

**Q1:** Should we scan all Python files in the project, or limit to specific file types (views.py, viewsets.py, etc.)?
**Answer:** All Python files (not limited to specific types)

**Q2:** What detection patterns should we support? I'm assuming we should detect:
- `reverse('url-name')`
- `redirect('url-name')`
- `HttpResponseRedirect(reverse('url-name'))`
- `reverse_lazy('url-name')`

Should we also detect: `resolve_url()`, custom wrappers around reverse/redirect?
**Answer:** Stick to the core patterns for now:
   - `reverse('url-name')`
   - `redirect('url-name')`
   - `HttpResponseRedirect(reverse('url-name'))`
   - `reverse_lazy('url-name')`
   - Do NOT include: resolve_url() or custom wrappers (for now)

**Q3:** For tracking URL references, should we track WHERE the reverse/redirect was called from (file, line number), or just mark the URL as "referenced"?
**Answer:** Just mark URLs as "referenced" - focus on preventing false positives, not detailed tracking of where they're called from

**Q4:** How should we handle dynamic URL names like `reverse(f'namespace:{action}_list')`?
**Answer:** Detect them but mark for humans to investigate further

**Q5:** For the architecture, should we create a separate `ReverseAnalyzer` class similar to the existing analyzers, or add this to the existing `ViewAnalyzer`?
**Answer:** Create a SEPARATE ReverseAnalyzer class, but refactor out any common AST parsing logic between it and ViewAnalyzer

**Q6:** For the reporting output, should reverse/redirect URLs be shown in a separate section, or should they simply be excluded from the "unreferenced URLs" list?
**Answer:** Exclude reverse/redirect URLs from the unreferenced list

**Q7:** Should we handle edge cases like:
- Comments containing reverse() in them
- Strings that contain "reverse()" but aren't actual calls
- Method calls like `self.reverse()` that aren't the Django reverse function
**Answer:** Ignore all of these for now:
   - Comments with reverse() in them
   - Strings containing reverse()
   - Method calls like self.reverse()

**Q8:** Are there any specific things we should explicitly NOT include? For example:
- JavaScript files with reverse() calls
- Third-party package code
- Migration files
- Runtime URL generation
**Answer:** Yes, exclude all of these:
   - JavaScript files
   - Third-party package code
   - Migration files
   - Runtime URL generation

### Existing Code to Reference

No similar existing features identified for reference by user.

### Follow-up Questions

No follow-up questions were needed. All requirements are clear and comprehensive.

## Visual Assets

### Files Provided:
No visual assets provided.

### Visual Insights:
Not applicable - no visual assets provided.

## Requirements Summary

### Functional Requirements
- Scan all Python files in the project for URL reference patterns
- Detect the following patterns using AST parsing:
  - `reverse('url-name')`
  - `redirect('url-name')`
  - `HttpResponseRedirect(reverse('url-name'))`
  - `reverse_lazy('url-name')`
- Mark detected URLs as "referenced" to prevent false positives in dead code detection
- Detect dynamic URL names (e.g., f-strings, concatenated strings) and flag them for manual investigation
- Exclude detected URLs from the "unreferenced URLs" list in reports

### Reusability Opportunities
- Extract common AST parsing logic shared between ReverseAnalyzer and ViewAnalyzer
- Reuse existing analyzer patterns and architecture from the codebase

### Scope Boundaries
**In Scope:**
- Python file AST analysis for reverse/redirect patterns
- Core Django URL reference functions (reverse, redirect, reverse_lazy, HttpResponseRedirect)
- Detection of dynamic URL name patterns
- Integration with existing dead code detection to reduce false positives
- Basic pattern matching for URL name strings

**Out of Scope:**
- JavaScript files with reverse() calls
- Third-party package code analysis
- Migration files
- Runtime URL generation detection
- `resolve_url()` function detection
- Custom wrapper functions around reverse/redirect
- Edge cases:
  - Comments containing reverse() text
  - String literals containing "reverse()"
  - Non-Django reverse methods (e.g., `self.reverse()`)
- Detailed tracking of WHERE reverse/redirect is called from (file/line numbers)

### Technical Considerations
- Create a separate `ReverseAnalyzer` class following existing analyzer patterns
- Refactor common AST parsing logic to avoid duplication between analyzers
- Use Python AST parsing for accurate detection
- Exclude the following file types from analysis:
  - JavaScript files
  - Third-party packages
  - Migration files (Django migrations)
- Handle dynamic URL names gracefully (detect but flag for manual review)
- Focus on preventing false positives in dead code detection rather than comprehensive tracking
