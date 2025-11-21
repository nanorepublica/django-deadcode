# Task Breakdown: URL Pattern Enhancements

## Overview
Total Task Groups: 6
Estimated Tasks: ~35

## Task List

### Phase 1: Analysis & Preparation

#### Task Group 1: Code Analysis
**Dependencies:** None

- [ ] 1.0 Analyze existing codebase structure
  - [ ] 1.1 Review URLAnalyzer implementation
    - Locate: `django_deadcode/analyzers/urls.py` or similar
    - Understand current `_process_url_pattern()` method
    - Identify where URL references are tracked
    - Document data structures used for URL storage
  - [ ] 1.2 Review TemplateAnalyzer implementation
    - Locate: `django_deadcode/analyzers/templates.py` or similar
    - Understand current template parsing logic
    - Identify existing href/link extraction (if any)
    - Note HTML parsing library in use (likely BeautifulSoup or regex)
  - [ ] 1.3 Review main analyzer/orchestrator
    - Locate main entry point that combines results
    - Understand how URLAnalyzer and TemplateAnalyzer are integrated
    - Identify where unreferenced URLs report is generated
    - Document current reference matching logic
  - [ ] 1.4 Review settings and configuration handling
    - Check if settings module exists for django-deadcode
    - Understand current configuration pattern
    - Identify where to add DEADCODE_EXCLUDE_NAMESPACES

**Acceptance Criteria:**
- Clear understanding of URLAnalyzer structure and data flow
- Clear understanding of TemplateAnalyzer parsing approach
- Identified exact locations for each required change
- Documented integration points between components

### Phase 2: Third-Party Detection Infrastructure

#### Task Group 2: Third-Party Detection Utility
**Dependencies:** Task Group 1

- [ ] 2.0 Implement third-party detection infrastructure
  - [ ] 2.1 Write 2-8 focused tests for third-party detection
    - Test: Module under BASE_DIR returns False
    - Test: Module outside BASE_DIR returns True
    - Test: Django built-in module (django.contrib.*) returns True
    - Test: Site-packages module returns True
    - Test: Module without __file__ attribute (edge case)
    - Limit to critical scenarios only
  - [ ] 2.2 Create utility function `is_third_party_module()`
    - Location: New file `django_deadcode/utils/module_detection.py` or in existing utils
    - Parameters: `module_path: str` or `view_callback: callable`
    - Logic: Get module's file path, compare against settings.BASE_DIR
    - Return: `bool` indicating if module is third-party
    - Handle edge cases: Built-in modules, modules without __file__
  - [ ] 2.3 Add helper to determine module file path from view callback
    - Extract module from view function or class
    - Get __file__ attribute safely
    - Convert to absolute Path
    - Handle CBVs (class-based views) vs FBVs (function-based views)
  - [ ] 2.4 Ensure third-party detection tests pass
    - Run ONLY the 2-8 tests written in 2.1
    - Verify correct detection for project vs third-party modules
    - Do NOT run entire test suite at this stage

**Acceptance Criteria:**
- The 2-8 tests written in 2.1 pass
- Function correctly identifies third-party vs project modules
- Handles edge cases gracefully (built-ins, no __file__, etc.)
- Works with both function and class-based views

### Phase 3: URL Analyzer Enhancements

#### Task Group 3: URLAnalyzer Third-Party Support
**Dependencies:** Task Group 2

- [ ] 3.0 Enhance URLAnalyzer for third-party detection
  - [ ] 3.1 Write 2-8 focused tests for URLAnalyzer enhancements
    - Test: URL pattern with third-party view is marked as third-party
    - Test: URL pattern with project view is marked as project code
    - Test: Namespace with mixed patterns is detected as third-party if any pattern is third-party
    - Test: get_unreferenced_urls() excludes specified namespaces
    - Test: get_unreferenced_urls() returns excluded_namespaces set
    - Limit to critical URLAnalyzer functionality
  - [ ] 3.2 Extend URL pattern data structure
    - Add `module_path: str` field to store view's module path
    - Add `is_third_party: bool` field
    - Ensure backwards compatibility with existing code
  - [ ] 3.3 Update `_process_url_pattern()` method
    - Extract module path from view callback
    - Call `is_third_party_module()` utility
    - Store both module_path and is_third_party flag
    - Handle include() patterns appropriately
  - [ ] 3.4 Implement namespace-level third-party detection
    - Add method `_detect_third_party_namespaces()` or similar
    - Logic: If ANY pattern in a namespace is third-party, mark entire namespace
    - Return: `set[str]` of third-party namespace names
  - [ ] 3.5 Update `get_unreferenced_urls()` method signature
    - Add parameter: `excluded_namespaces: Optional[set[str]] = None`
    - Filter out URL patterns whose namespace is in excluded_namespaces
    - Return tuple: `(unreferenced_urls, excluded_namespaces_found)`
    - Maintain backwards compatibility
  - [ ] 3.6 Ensure URLAnalyzer enhancement tests pass
    - Run ONLY the 2-8 tests written in 3.1
    - Verify third-party detection works correctly
    - Verify namespace exclusion works correctly
    - Do NOT run entire test suite at this stage

**Acceptance Criteria:**
- The 2-8 tests written in 3.1 pass
- URL patterns store module path and third-party status
- Namespace-level detection correctly identifies third-party namespaces
- get_unreferenced_urls() properly filters excluded namespaces
- Returns information about which namespaces were excluded

### Phase 4: Template Href Extraction

#### Task Group 4: TemplateAnalyzer Href Support
**Dependencies:** Task Group 1

- [ ] 4.0 Add href extraction to TemplateAnalyzer
  - [ ] 4.1 Write 2-8 focused tests for href extraction
    - Test: Extract internal href like `/about/`
    - Test: Exclude external href like `https://example.com`
    - Test: Exclude protocol-relative href like `//cdn.example.com`
    - Test: Exclude mailto:, tel:, javascript:, # hrefs
    - Test: Normalize hrefs (handle with/without leading/trailing slashes)
    - Test: Handle multiple hrefs in one template
    - Limit to critical extraction scenarios
  - [ ] 4.2 Implement href extraction method
    - Add method: `extract_internal_hrefs()` or similar
    - Parse HTML/template content for href attributes
    - Use existing parsing approach (BeautifulSoup, regex, or template parser)
    - Filter out external protocols: http://, https://, mailto:, tel:, javascript:, #, //
    - Return: `set[str]` of internal href paths
  - [ ] 4.3 Implement href normalization
    - Add utility function: `normalize_href(href: str) -> str`
    - Strip leading and trailing slashes for comparison
    - Handle empty hrefs and invalid values
    - Make comparison consistent with URL pattern format
  - [ ] 4.4 Integrate href extraction into main analyze() flow
    - Call extract_internal_hrefs() during template analysis
    - Store extracted hrefs in TemplateAnalyzer results
    - Ensure existing template analysis ({% url %} tags) still works
  - [ ] 4.5 Ensure href extraction tests pass
    - Run ONLY the 2-8 tests written in 4.1
    - Verify internal hrefs extracted correctly
    - Verify external hrefs excluded properly
    - Do NOT run entire test suite at this stage

**Acceptance Criteria:**
- The 2-8 tests written in 4.1 pass
- Internal hrefs correctly extracted from templates
- External protocols properly filtered out
- Href normalization works consistently
- Integration with existing template analysis maintained

### Phase 5: URL Pattern Matching Logic

#### Task Group 5: Href to URL Pattern Matching
**Dependencies:** Task Groups 3, 4

- [ ] 5.0 Implement href-to-pattern matching
  - [ ] 5.1 Write 2-8 focused tests for matching logic
    - Test: `/about/` matches pattern `about/`
    - Test: `/users/profile/` matches pattern `users/profile/`
    - Test: Href with trailing slash matches pattern without (and vice versa)
    - Test: Partial matches don't incorrectly match (e.g., `/user/` shouldn't match `users/`)
    - Test: Matched patterns are added to referenced URL set
    - Test: Integration: Href in template marks URL as referenced
    - Limit to critical matching scenarios
  - [ ] 5.2 Create URL pattern matching utility
    - Add function: `match_href_to_pattern(href: str, pattern: str) -> bool`
    - Normalize both href and pattern before comparison
    - Use simple string matching (not regex evaluation)
    - Handle leading/trailing slash variations
    - Return True if href matches pattern
  - [ ] 5.3 Implement bulk matching function
    - Add function: `find_matching_url_patterns(hrefs: set[str], url_patterns: dict) -> set[str]`
    - Iterate through hrefs and URL patterns
    - Use match_href_to_pattern() for comparison
    - Return: `set[str]` of URL pattern names that matched
  - [ ] 5.4 Integrate matching into main analyzer
    - Get internal hrefs from TemplateAnalyzer
    - Get URL patterns from URLAnalyzer
    - Call find_matching_url_patterns()
    - Add matched URL names to the referenced URLs set
    - Ensure this happens before generating unreferenced report
  - [ ] 5.5 Ensure matching logic tests pass
    - Run ONLY the 2-8 tests written in 5.1
    - Verify hrefs correctly match URL patterns
    - Verify matched URLs marked as referenced
    - Do NOT run entire test suite at this stage

**Acceptance Criteria:**
- The 2-8 tests written in 5.1 pass
- Hrefs correctly match against URL patterns
- Normalization handles slash variations
- Matched URLs properly added to referenced set
- Integration with existing reference detection works

### Phase 6: Configuration & Reporting

#### Task Group 6: Settings and Report Output
**Dependencies:** Task Groups 3, 5

- [ ] 6.0 Implement configuration and reporting
  - [ ] 6.1 Write 2-8 focused tests for configuration and reporting
    - Test: DEADCODE_EXCLUDE_NAMESPACES setting is read correctly
    - Test: Manual exclusions combined with auto-detected third-party namespaces
    - Test: Report includes "Note: Third-party namespaces excluded: ..." line
    - Test: Note only appears when namespaces actually excluded
    - Test: Excluded namespaces listed alphabetically
    - Limit to critical configuration scenarios
  - [ ] 6.2 Add settings support for DEADCODE_EXCLUDE_NAMESPACES
    - Check if settings handler exists, otherwise create one
    - Add function: `get_excluded_namespaces() -> set[str]`
    - Read from Django settings: `settings.DEADCODE_EXCLUDE_NAMESPACES`
    - Return empty set if not configured
    - Validate that value is iterable of strings
  - [ ] 6.3 Combine exclusion sources
    - In main analyzer, get auto-detected third-party namespaces from URLAnalyzer
    - Get manual exclusions from settings: get_excluded_namespaces()
    - Combine both sets: `excluded = auto_detected | manual_exclusions`
    - Pass combined set to get_unreferenced_urls()
  - [ ] 6.4 Update unreferenced URLs report format
    - Locate report generation code (likely in management command or main analyzer)
    - After "UNREFERENCED URL PATTERNS" heading, add informational note
    - Format: "Note: Third-party namespaces excluded: {', '.join(sorted(excluded_namespaces))}"
    - Only show note if excluded_namespaces is non-empty
    - Maintain existing report format for the URL list itself
  - [ ] 6.5 Ensure configuration and reporting tests pass
    - Run ONLY the 2-8 tests written in 6.1
    - Verify settings read correctly
    - Verify report note appears correctly
    - Do NOT run entire test suite at this stage

**Acceptance Criteria:**
- The 2-8 tests written in 6.1 pass
- DEADCODE_EXCLUDE_NAMESPACES setting properly read and applied
- Auto-detected and manual exclusions combined correctly
- Report shows informational note with excluded namespaces
- Note only appears when namespaces were actually excluded
- Existing report format maintained

### Phase 7: Integration Testing & Validation

#### Task Group 7: End-to-End Testing
**Dependencies:** All previous task groups (1-6)

- [ ] 7.0 Validate complete feature integration
  - [ ] 7.1 Review all existing tests
    - Count tests from Task Groups 2-6 (approximately 10-40 tests)
    - Verify each test group's tests are passing
    - Document any test failures or gaps
  - [ ] 7.2 Analyze test coverage gaps for URL pattern enhancements only
    - Identify critical workflows lacking coverage:
      - End-to-end: href in template → matched → excluded from unreferenced report
      - End-to-end: third-party URL → auto-detected → excluded from report
      - Edge case: URL with namespace in both auto-detect and manual exclusions
      - Edge case: href matches multiple URL patterns
      - Integration: All features work together with real Django project structure
    - Focus ONLY on this feature's integration points
    - Prioritize end-to-end workflows over unit test gaps
  - [ ] 7.3 Write up to 10 additional integration tests maximum
    - Add maximum of 10 new tests to fill critical gaps identified
    - Focus on end-to-end scenarios and integration points
    - Test complete workflows:
      - Template with internal href → URL pattern matched → excluded from unreferenced
      - Third-party app URLs → auto-detected → excluded → note in report
      - Manual exclusion via settings → combined with auto-detect → all excluded
      - Existing functionality still works ({% url %}, reverse() detection)
    - DO NOT write exhaustive coverage for all edge cases
    - Skip performance tests and non-critical edge cases
  - [ ] 7.4 Run all feature-specific tests
    - Run all tests from Task Groups 2-6 plus new tests from 7.3
    - Expected total: approximately 20-50 tests maximum
    - Verify all tests pass
    - Fix any integration issues discovered
    - Do NOT run entire application test suite (if this is part of larger project)
  - [ ] 7.5 Manual validation with sample Django project
    - Create or use test Django project with:
      - Project URLs under BASE_DIR
      - Third-party URLs (e.g., Django admin, DRF)
      - Templates with internal hrefs
      - Templates with {% url %} tags
    - Run django-deadcode analyzer
    - Verify: Internal hrefs match URL patterns correctly
    - Verify: Third-party URLs excluded from unreferenced report
    - Verify: Report note shows excluded namespaces
    - Verify: Existing functionality ({% url %} detection) still works
  - [ ] 7.6 Update documentation
    - Update README.md or main documentation with new features:
      - Explain internal href matching capability
      - Explain automatic third-party exclusion
      - Document DEADCODE_EXCLUDE_NAMESPACES setting
      - Provide configuration examples
    - Update CHANGELOG.md with new feature entries
    - Add inline code documentation/docstrings where missing

**Acceptance Criteria:**
- All feature-specific tests pass (approximately 20-50 tests total)
- End-to-end workflows validated with integration tests
- Manual validation confirms features work with real Django project
- No more than 10 additional tests added when filling gaps
- Existing functionality unaffected (backwards compatible)
- Documentation updated with new features and configuration options

## Execution Order

Recommended implementation sequence:

1. **Phase 1: Analysis & Preparation** (Task Group 1)
   - Understand existing codebase before making changes

2. **Phase 2: Third-Party Detection** (Task Group 2)
   - Build foundational utility for detecting third-party modules
   - This is used by both URLAnalyzer and matching logic

3. **Phase 3 & 4: Parallel Implementation** (Task Groups 3, 4)
   - Task Group 3: URLAnalyzer Enhancements (depends on Task Group 2)
   - Task Group 4: TemplateAnalyzer Href Extraction (independent)
   - These can be implemented in parallel or in either order

4. **Phase 5: Matching Logic** (Task Group 5)
   - Depends on Task Groups 3 & 4 being complete
   - Connects hrefs to URL patterns

5. **Phase 6: Configuration & Reporting** (Task Group 6)
   - Depends on Task Groups 3 & 5
   - Adds user-facing settings and output formatting

6. **Phase 7: Integration Testing** (Task Group 7)
   - Final validation after all components complete
   - Ensures everything works together correctly

## Notes

- **Test Strategy**: Each implementation task group (2-6) writes 2-8 focused tests and runs only those tests. Final integration testing (Group 7) adds up to 10 more tests for end-to-end validation.

- **Backwards Compatibility**: Ensure all changes maintain backwards compatibility with existing django-deadcode functionality. Existing reference detection ({% url %} tags, reverse() calls) must continue to work unchanged.

- **Path Normalization**: Pay careful attention to path normalization throughout - Django URL patterns, template hrefs, and file paths all handle slashes differently.

- **Edge Cases to Consider**:
  - URL patterns with regex or path converters (may not match simple hrefs)
  - Namespaced URLs (namespace:name format)
  - Include() patterns that add prefixes
  - URLs with query parameters or fragments in templates
  - Dynamic hrefs built with template variables

- **Performance Considerations**: If the Django project has many templates and many URL patterns, the matching logic could be O(n*m). Consider optimizing if performance issues arise, but start with simple implementation.
