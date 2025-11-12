# Task Breakdown: Reverse/Redirect Detection Feature

## Overview
Implement Python AST analysis to detect `reverse()` and `redirect()` calls in view code, capturing programmatic URL references to reduce false positives in dead code detection.

**Total Tasks:** 5 major task groups
**Estimated Scope:** Large (L)
**Target Version:** v0.2.0

## Task List

### Phase 1: Foundation & AST Utilities

#### Task Group 1: Extract Common AST Logic (Optional but Recommended)
**Dependencies:** None
**Assigned to:** backend-engineer

This group is optional but recommended to reduce code duplication between ViewAnalyzer and ReverseAnalyzer.

- [ ] 1.0 Evaluate and optionally refactor common AST logic
  - [ ] 1.1 Write 2-4 focused tests for AST utility functions (if extracted)
    - Test file filtering (migrations, __pycache__ exclusion)
    - Test AST parsing error handling (SyntaxError, UnicodeDecodeError)
    - Skip exhaustive testing - focus on critical behaviors only
  - [ ] 1.2 Review ViewAnalyzer for reusable AST patterns
    - File: `/home/user/django-deadcode/django_deadcode/analyzers/view_analyzer.py`
    - Identify common patterns:
      - File scanning with `Path.rglob("*.py")`
      - Skip patterns for migrations and __pycache__
      - AST parsing with `ast.parse()` and error handling
      - Tree traversal with `ast.walk(tree)`
    - Document patterns to reuse (not necessarily extract)
  - [ ] 1.3 Decide on refactoring approach
    - **Option A:** Create `ast_utils.py` with shared functions (e.g., `parse_python_file()`, `should_skip_file()`)
    - **Option B:** Document patterns and duplicate minimal code (simpler, acceptable for v0.2.0)
    - Recommendation: Choose Option B unless significant duplication (>50 lines)
  - [ ] 1.4 If creating ast_utils.py (Option A):
    - Create: `/home/user/django-deadcode/django_deadcode/analyzers/ast_utils.py`
    - Extract: File filtering logic, AST parsing error handling
    - Update ViewAnalyzer to use utility functions
    - Run existing ViewAnalyzer tests to ensure no regression
  - [ ] 1.5 Ensure foundation tests pass (if Option A chosen)
    - Run ONLY the 2-4 tests written in 1.1
    - Verify ViewAnalyzer tests still pass
    - Do NOT run entire test suite at this stage

**Acceptance Criteria:**
- Decision documented on refactoring approach (Option A or B)
- If Option A: Common AST utilities extracted and tested (2-4 tests pass)
- If Option A: ViewAnalyzer refactored with no test regressions
- If Option B: Patterns documented for reuse in ReverseAnalyzer

---

### Phase 2: Core Implementation

#### Task Group 2: ReverseAnalyzer Class - Foundation
**Dependencies:** Task Group 1
**Assigned to:** backend-engineer

- [ ] 2.0 Implement ReverseAnalyzer foundation
  - [ ] 2.1 Write 6-8 focused tests for core ReverseAnalyzer functionality
    - Limit to 6-8 highly focused tests maximum
    - Test cases:
      1. `test_detect_reverse_call` - Basic `reverse('url-name')`
      2. `test_detect_reverse_lazy_call` - `reverse_lazy('url-name')`
      3. `test_detect_redirect_call` - `redirect('url-name')`
      4. `test_detect_http_response_redirect` - `HttpResponseRedirect(reverse('url-name'))`
      5. `test_detect_multiple_patterns` - Multiple different calls in same file
      6. `test_ignore_method_calls` - `self.reverse()` should be ignored
      7. `test_get_referenced_urls` - Verify correct URL set returned
      8. `test_namespace_urls` - `reverse('namespace:url-name')`
    - Use tempfile pattern from ViewAnalyzer tests
    - Skip exhaustive testing of edge cases at this stage
    - File: `/home/user/django-deadcode/tests/test_reverse_analyzer.py`
  - [ ] 2.2 Create ReverseAnalyzer class skeleton
    - File: `/home/user/django-deadcode/django_deadcode/analyzers/reverse_analyzer.py`
    - Class structure:
      ```python
      class ReverseAnalyzer:
          def __init__(self) -> None
          def analyze_python_file(self, file_path: Path) -> None
          def analyze_all_python_files(self, base_path: Path) -> None
          def get_referenced_urls(self) -> Set[str]
          def get_dynamic_patterns(self) -> Set[str]
      ```
    - Instance variables:
      ```python
      self.referenced_urls: Set[str]
      self.dynamic_patterns: Set[str]
      ```
    - Add type hints to all methods
    - Add docstrings to all public methods
  - [ ] 2.3 Implement file scanning logic
    - Method: `analyze_all_python_files(self, base_path: Path)`
    - Pattern: Reuse from ViewAnalyzer (lines 117-131)
    - Use `Path.rglob("*.py")` to find Python files
    - Skip migrations: `"migrations" in py_file.parts`
    - Skip __pycache__: `"__pycache__" in py_file.parts`
    - Call `analyze_python_file()` for each file
  - [ ] 2.4 Implement AST parsing foundation
    - Method: `analyze_python_file(self, file_path: Path)`
    - Follow ViewAnalyzer pattern (lines 21-34):
      - Read file with UTF-8 encoding
      - Parse with `ast.parse(content, filename=str(file_path))`
      - Call `_process_ast(tree, str(file_path))`
      - Handle exceptions: IOError, SyntaxError, UnicodeDecodeError
      - Skip unparseable files silently (don't crash, don't log)
  - [ ] 2.5 Ensure ReverseAnalyzer foundation tests pass
    - Run ONLY the 6-8 tests written in 2.1
    - Verify file scanning and AST parsing work
    - Verify basic structure is correct
    - Do NOT run entire test suite at this stage

**Acceptance Criteria:**
- ReverseAnalyzer class created with correct structure
- File scanning excludes migrations and __pycache__
- AST parsing handles errors gracefully (no crashes)
- The 6-8 tests written in 2.1 pass
- Type hints and docstrings on all public methods

---

#### Task Group 3: ReverseAnalyzer - Pattern Detection
**Dependencies:** Task Group 2
**Assigned to:** backend-engineer

- [ ] 3.0 Implement pattern detection logic
  - [ ] 3.1 Write 5-7 focused tests for pattern detection edge cases
    - Limit to 5-7 highly focused tests maximum
    - Test cases:
      1. `test_detect_dynamic_fstring` - Detect and flag f-string patterns
      2. `test_detect_dynamic_concatenation` - Detect and flag string concatenation
      3. `test_skip_malformed_file` - Handle SyntaxError gracefully
      4. `test_skip_migration_files` - Migration files excluded from analysis
      5. `test_multiple_files_analysis` - Scan multiple files, accumulate results
      6. `test_keyword_argument_reverse` - `reverse(viewname='url-name')`
      7. `test_reverse_with_multiple_args` - `reverse('url-name', args=[1, 2])`
    - Skip exhaustive edge case testing
    - File: `/home/user/django-deadcode/tests/test_reverse_analyzer.py`
  - [ ] 3.2 Implement AST node traversal
    - Method: `_process_ast(self, tree: ast.AST, file_path: str)`
    - Walk all nodes with `ast.walk(tree)`
    - Filter for `ast.Call` nodes
    - Call `_process_call_node()` for each Call node
  - [ ] 3.3 Implement reverse() and reverse_lazy() detection
    - Method: `_process_call_node(self, node: ast.Call, file_path: str)`
    - Check if `isinstance(node.func, ast.Name)` (not ast.Attribute)
    - Match `node.func.id` against: `'reverse'`, `'reverse_lazy'`
    - Extract first argument:
      - If `ast.Constant`: Add to `self.referenced_urls`
      - If `ast.JoinedStr` (f-string): Add to `self.dynamic_patterns`
      - If `ast.BinOp` (concatenation): Add to `self.dynamic_patterns`
      - If other: Add to `self.dynamic_patterns`
    - Handle keyword arguments: Check for `viewname=` keyword
    - Reference spec: Lines 103-118 for AST patterns
  - [ ] 3.4 Implement redirect() detection
    - Same method: `_process_call_node()`
    - Match `node.func.id == 'redirect'`
    - Extract first argument using same logic as 3.3
    - Note: redirect() can take URL names OR full URLs
    - Only capture if argument looks like URL name (no '/' or 'http')
  - [ ] 3.5 Implement HttpResponseRedirect(reverse()) detection
    - Same method: `_process_call_node()`
    - Match `node.func.id == 'HttpResponseRedirect'`
    - Check if first argument is another `ast.Call` node
    - If nested call is `reverse()` or `reverse_lazy()`, extract URL name
    - Reference spec: Lines 172-184 for nested pattern
  - [ ] 3.6 Implement dynamic pattern handling
    - When detecting dynamic URL (f-string, concatenation, variable):
      - Add placeholder string to `self.dynamic_patterns`
      - Format: `"<dynamic:f-string>"` or `"<dynamic:concatenation>"` or `"<dynamic:variable>"`
      - Do NOT add to `self.referenced_urls`
      - Note: Will be reported for manual investigation
    - Reference spec: Lines 207-214
  - [ ] 3.7 Ensure pattern detection tests pass
    - Run ONLY the 5-7 tests written in 3.1
    - Run the 6-8 tests from 2.1 to ensure no regression
    - Total: approximately 11-15 tests
    - Verify all four core patterns are detected
    - Verify dynamic patterns are flagged correctly
    - Do NOT run entire test suite at this stage

**Acceptance Criteria:**
- All four patterns detected: reverse(), reverse_lazy(), redirect(), HttpResponseRedirect()
- Dynamic URL patterns (f-strings, concatenation) flagged, not added to referenced_urls
- Method calls like `self.reverse()` correctly ignored
- Nested HttpResponseRedirect(reverse()) pattern detected
- The 11-15 tests from groups 2 and 3 pass
- No crashes on malformed Python files

---

### Phase 3: Integration

#### Task Group 4: Integrate with finddeadcode Command
**Dependencies:** Task Group 3
**Assigned to:** backend-engineer

- [ ] 4.0 Integrate ReverseAnalyzer into finddeadcode command
  - [ ] 4.1 Update analyzer exports
    - File: `/home/user/django-deadcode/django_deadcode/analyzers/__init__.py`
    - Add: `from .reverse_analyzer import ReverseAnalyzer`
    - Add: `"ReverseAnalyzer"` to `__all__` list
  - [ ] 4.2 Initialize ReverseAnalyzer in finddeadcode command
    - File: `/home/user/django-deadcode/django_deadcode/management/commands/finddeadcode.py`
    - Location: In `handle()` method, after line 51
    - Add: `reverse_analyzer = ReverseAnalyzer()`
    - Add import at top: Update line 9 to include ReverseAnalyzer
  - [ ] 4.3 Call ReverseAnalyzer during analysis
    - File: Same as 4.2
    - Location: After view analysis (around line 69)
    - Add analysis section:
      ```python
      # Analyze reverse/redirect references
      self.stdout.write("Analyzing reverse/redirect references...")
      for app_dir in app_dirs:
          if app_dir.exists():
              reverse_analyzer.analyze_all_python_files(app_dir)
      ```
  - [ ] 4.4 Combine referenced URLs from multiple sources
    - File: Same as 4.2
    - Method: `_compile_analysis_data()` around line 170
    - Current: `referenced_urls = template_analyzer.get_referenced_urls()`
    - Change to:
      ```python
      # Combine references from templates and Python code
      template_refs = template_analyzer.get_referenced_urls()
      reverse_refs = reverse_analyzer.get_referenced_urls()
      referenced_urls = template_refs | reverse_refs
      ```
  - [ ] 4.5 Add dynamic patterns to analysis data (optional for v0.2.0)
    - File: Same as 4.2
    - Method: `_compile_analysis_data()`
    - Add to returned dictionary:
      ```python
      "dynamic_url_patterns": list(reverse_analyzer.get_dynamic_patterns())
      ```
    - Note: This enables future reporting of dynamic patterns for manual review
  - [ ] 4.6 Manual integration test
    - Create test Django project with:
      - URL pattern: `path('test/', views.test_view, name='test-url')`
      - View using reverse: `reverse('test-url')`
      - No template references to 'test-url'
    - Run: `python manage.py finddeadcode`
    - Verify: 'test-url' is NOT in unreferenced URLs list
    - Verify: Analysis completes without errors
    - Note: This is a manual verification, not an automated test

**Acceptance Criteria:**
- ReverseAnalyzer exported in `__init__.py`
- ReverseAnalyzer initialized in finddeadcode command
- ReverseAnalyzer called for each app directory
- Referenced URLs combined from templates AND reverse/redirect calls
- Manual test confirms integration works (URLs from reverse() not reported as dead)
- No performance degradation (subjectively < 20% slower)

---

### Phase 4: Testing & Quality Assurance

#### Task Group 5: Integration Tests & Edge Cases
**Dependencies:** Task Group 4
**Assigned to:** test-engineer

- [ ] 5.0 Create integration tests and verify edge cases
  - [ ] 5.1 Review existing tests from Task Groups 2 and 3
    - Review the 6-8 tests from Task Group 2 (ReverseAnalyzer foundation)
    - Review the 5-7 tests from Task Group 3 (pattern detection)
    - Total existing: approximately 11-15 unit tests
    - Verify all tests are passing before proceeding
  - [ ] 5.2 Write 3-5 integration tests for end-to-end workflows
    - Limit to 3-5 integration tests maximum
    - File: `/home/user/django-deadcode/tests/test_integration_reverse_detection.py`
    - Test cases:
      1. `test_reverse_refs_prevent_false_positives`
         - Create URL pattern with name
         - Reference with reverse() in Python
         - Verify NOT in unreferenced URLs list
      2. `test_combined_template_and_reverse_refs`
         - Some URLs referenced in templates
         - Some URLs referenced in reverse() calls
         - Verify both sets excluded from unreferenced list
      3. `test_finddeadcode_command_integration`
         - Run full management command
         - Verify ReverseAnalyzer is invoked
         - Verify output format is correct
      4. `test_dynamic_patterns_not_marked_as_referenced` (optional)
         - Create reverse with f-string
         - Verify URL NOT added to referenced set
         - Verify pattern added to dynamic_patterns set
      5. `test_performance_acceptable` (optional)
         - Create project with 100+ Python files
         - Run analysis and time it
         - Verify time increase < 20% vs without ReverseAnalyzer
    - Focus on critical workflows, not exhaustive coverage
  - [ ] 5.3 Identify and test critical edge cases (maximum 2-4 additional tests)
    - Only add tests if critical gaps identified
    - Potential edge cases:
      - Empty Python files (should handle gracefully)
      - Python file with only comments (no code)
      - Very large Python file (performance check)
      - URL name with special characters: `'url-name-with_chars'`
    - Add ONLY if gaps found during integration testing
    - Maximum 2-4 additional tests
  - [ ] 5.4 Run feature-specific test suite
    - Run ALL tests related to ReverseAnalyzer:
      - Tests from Task Group 2 (6-8 tests)
      - Tests from Task Group 3 (5-7 tests)
      - Integration tests from 5.2 (3-5 tests)
      - Edge case tests from 5.3 (0-4 tests)
    - Expected total: approximately 14-24 tests maximum
    - Command: `pytest tests/test_reverse_analyzer.py tests/test_integration_reverse_detection.py -v`
    - Do NOT run entire application test suite
    - Verify all feature tests pass
  - [ ] 5.5 Verify no regressions in existing analyzers
    - Run ViewAnalyzer tests: `pytest tests/test_view_analyzer.py -v`
    - Run TemplateAnalyzer tests: `pytest tests/test_template_analyzer.py -v` (if exists)
    - Verify no regressions from any refactoring in Task Group 1
    - If regressions found, fix before proceeding

**Acceptance Criteria:**
- All ReverseAnalyzer tests pass (approximately 11-15 unit tests from groups 2-3)
- All integration tests pass (3-5 tests from 5.2)
- Total feature-specific tests: approximately 14-24 tests maximum
- No regressions in existing analyzer tests
- Critical user workflows covered by integration tests
- Edge cases handled gracefully (no crashes)

---

### Phase 5: Documentation & Polish

#### Task Group 6: Documentation, Logging, and Final Polish
**Dependencies:** Task Group 5
**Assigned to:** backend-engineer

- [ ] 6.0 Complete documentation and polish
  - [ ] 6.1 Add comprehensive docstrings
    - File: `/home/user/django-deadcode/django_deadcode/analyzers/reverse_analyzer.py`
    - Class docstring: Explain purpose, AST patterns detected
    - Method docstrings: All public methods (already done in 2.2, verify completeness)
    - Add internal method docstrings:
      - `_process_ast()`: Explain node traversal approach
      - `_process_call_node()`: Document AST node patterns
      - `_extract_url_name()`: Document string extraction logic (if separate method)
    - Add inline comments:
      - Why method calls (self.reverse) are ignored
      - AST node structure for each pattern
      - Dynamic pattern detection rationale
  - [ ] 6.2 Add dynamic pattern logging (optional)
    - File: Same as 6.1
    - When detecting dynamic pattern, optionally log at DEBUG level:
      ```python
      import logging
      logger = logging.getLogger(__name__)
      logger.debug(f"Found dynamic URL pattern in {file_path}: {pattern_type}")
      ```
    - Note: This is optional - dynamic patterns are already tracked in `self.dynamic_patterns`
    - Only add if useful for debugging
  - [ ] 6.3 Update README (if applicable)
    - File: `/home/user/django-deadcode/README.md` (if exists)
    - Add to features list: "Detects reverse() and redirect() URL references in Python code"
    - Update "How it works" section to mention ReverseAnalyzer
    - Add example showing reverse() detection preventing false positive
    - Note: Skip if README doesn't have feature list section
  - [ ] 6.4 Update CHANGELOG (if applicable)
    - File: `/home/user/django-deadcode/CHANGELOG.md` (if exists)
    - Add v0.2.0 section with:
      - "Added: Python AST analysis for reverse() and redirect() calls"
      - "Added: ReverseAnalyzer to detect programmatic URL references"
      - "Improved: Reduced false positives for URLs referenced in Python code"
      - "Added: Detection of dynamic URL patterns (f-strings, concatenation)"
    - Note: Skip if project doesn't maintain CHANGELOG
  - [ ] 6.5 Code review checklist
    - Verify type hints on all public methods
    - Verify docstrings on all public methods
    - Check for code duplication (DRY principle)
    - Verify error handling matches ViewAnalyzer pattern
    - Check imports are organized (standard lib, Django, local)
    - Verify no debug print statements left in code
    - Check line length (< 100 characters where reasonable)
    - Verify PEP 8 compliance (can use: `black django_deadcode/analyzers/reverse_analyzer.py`)
  - [ ] 6.6 Final verification
    - Run full feature test suite one more time
    - Run existing test suite to verify no regressions
    - Manually test with sample Django project
    - Verify performance is acceptable (< 20% slowdown subjectively)
    - Check that all acceptance criteria from spec are met

**Acceptance Criteria:**
- Comprehensive docstrings on all methods
- Inline comments explain AST patterns and edge cases
- README updated with ReverseAnalyzer feature (if applicable)
- CHANGELOG updated for v0.2.0 (if applicable)
- Code follows project style guidelines
- All tests pass (feature tests + no regressions)
- Feature ready for production use

---

## Execution Order

**Recommended implementation sequence:**

1. **Phase 1 - Foundation** (Task Group 1): Extract common AST logic [OPTIONAL]
   - Time estimate: 2-4 hours
   - Can be skipped if choosing simple duplication approach

2. **Phase 2 - Core Implementation** (Task Groups 2-3): Build ReverseAnalyzer
   - Task Group 2: Foundation (4-6 hours)
   - Task Group 3: Pattern Detection (4-6 hours)
   - Total: 8-12 hours

3. **Phase 3 - Integration** (Task Group 4): Connect to finddeadcode
   - Time estimate: 2-3 hours

4. **Phase 4 - Testing** (Task Group 5): Integration tests and edge cases
   - Time estimate: 3-5 hours

5. **Phase 5 - Documentation** (Task Group 6): Polish and document
   - Time estimate: 2-3 hours

**Total Estimated Time:** 19-27 hours (depends on whether Phase 1 is included)

---

## Testing Summary

**Test Distribution:**
- Task Group 1 (AST Utils): 2-4 tests (if refactoring)
- Task Group 2 (Foundation): 6-8 tests
- Task Group 3 (Pattern Detection): 5-7 tests
- Task Group 5 (Integration): 3-5 tests
- Task Group 5 (Edge Cases): 0-4 tests
- **Total: 16-28 tests maximum**

**Testing Philosophy:**
- Write focused tests that cover critical behaviors
- Avoid exhaustive testing of all possible scenarios
- Use test-driven approach: write tests before implementation
- Run only feature-specific tests during development
- Verify no regressions in existing tests after completion

---

## Key Technical References

**Files to Create:**
- `/home/user/django-deadcode/django_deadcode/analyzers/reverse_analyzer.py` (main implementation)
- `/home/user/django-deadcode/tests/test_reverse_analyzer.py` (unit tests)
- `/home/user/django-deadcode/tests/test_integration_reverse_detection.py` (integration tests)
- `/home/user/django-deadcode/django_deadcode/analyzers/ast_utils.py` (optional, if refactoring)

**Files to Modify:**
- `/home/user/django-deadcode/django_deadcode/analyzers/__init__.py` (add ReverseAnalyzer export)
- `/home/user/django-deadcode/django_deadcode/management/commands/finddeadcode.py` (integration)
- `/home/user/django-deadcode/README.md` (feature documentation, if applicable)
- `/home/user/django-deadcode/CHANGELOG.md` (version notes, if applicable)

**Reference Patterns:**
- ViewAnalyzer: `/home/user/django-deadcode/django_deadcode/analyzers/view_analyzer.py`
  - AST parsing: lines 21-34
  - File scanning: lines 117-131
  - Node processing: lines 36-77
- ViewAnalyzer tests: `/home/user/django-deadcode/tests/test_view_analyzer.py`
  - Tempfile pattern: lines 24-37
  - Test structure: lines 14-111

**Spec Reference:**
- Full spec: `/home/user/django-deadcode/agent-os/specs/2025-11-12-reverse-redirect-detection/spec.md`
- Requirements: `/home/user/django-deadcode/agent-os/specs/2025-11-12-reverse-redirect-detection/planning/requirements.md`
- AST patterns: spec.md lines 103-194
- Testing strategy: spec.md lines 216-263

---

## Important Constraints & Notes

**Testing Limits:**
- Maximum 6-8 tests per core implementation group
- Maximum 3-5 integration tests
- Maximum 2-4 edge case tests (only if needed)
- Total approximately 16-28 tests for entire feature
- Do NOT aim for exhaustive test coverage

**Performance Requirements:**
- Analysis time increase must be < 20% compared to v0.1.0
- AST parsing is fast, but test on projects with 100+ files
- Profile if performance degrades beyond acceptable range

**Patterns to Detect:**
1. `reverse('url-name')` - Static URL name string
2. `reverse_lazy('url-name')` - Lazy evaluation version
3. `redirect('url-name')` - Redirect to URL name
4. `HttpResponseRedirect(reverse('url-name'))` - Nested pattern

**Patterns to Flag (Dynamic):**
- F-strings: `reverse(f'app:{action}_list')`
- Concatenation: `reverse('prefix_' + suffix)`
- Variables: `reverse(url_var)`

**Files to Exclude:**
- Migration files: `"migrations"` in path
- Pycache: `"__pycache__"` in path
- Third-party code: Outside analyzed app directories

**Error Handling:**
- Skip unparseable files silently (no crash, no log)
- Handle: IOError, SyntaxError, UnicodeDecodeError
- Follow ViewAnalyzer pattern exactly

---

## Success Metrics

**Feature is complete when:**
- [ ] All task groups (1-6) completed
- [ ] All acceptance criteria met for each group
- [ ] Approximately 16-28 tests passing
- [ ] No regressions in existing tests
- [ ] Manual testing confirms false positives reduced
- [ ] Performance acceptable (< 20% slowdown)
- [ ] Code review checklist complete
- [ ] Documentation updated

**Quality indicators:**
- Clean AST pattern detection (no false positives/negatives)
- Graceful error handling (no crashes on real projects)
- Code follows existing patterns and style
- Tests are maintainable and focused
- Integration is seamless (no breaking changes)
