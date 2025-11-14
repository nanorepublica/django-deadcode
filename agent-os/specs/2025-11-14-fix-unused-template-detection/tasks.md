# Task Breakdown: Fix Unused Template Detection

## Overview
Total Task Groups: 6
Estimated Timeline: 5 days
Critical Path: Path Normalization → Enhanced Detection → Integration → Testing

## Task List

### Phase 1: Foundation - Path Normalization Layer

#### Task Group 1: Template Path Normalization (CRITICAL - P0)
**Dependencies:** None
**Owner Role:** Backend Engineer
**Timeline:** Day 1

This is the foundational fix that resolves the core path mismatch bug. All other enhancements depend on this working correctly.

- [ ] 1.0 Complete path normalization layer
  - [ ] 1.1 Write 2-8 focused tests for path normalization
    - Limit to 2-8 highly focused tests maximum
    - Test critical normalization scenarios:
      - Standard app template path (e.g., `/app/apps/collations/templates/collations/base.html` → `collations/base.html`)
      - Project-level templates path (e.g., `/app/templates/base.html` → `base.html`)
      - Nested templates directory
      - Edge case: Multiple 'templates/' in path
    - Skip exhaustive edge case testing at this stage
    - File: `tests/test_template_analyzer.py`
  - [ ] 1.2 Implement `normalize_template_path()` method in TemplateAnalyzer
    - Location: `django_deadcode/analyzers/template_analyzer.py`
    - Method signature: `normalize_template_path(self, filesystem_path: Path) -> str`
    - Logic: Find 'templates/' in path and return everything after it
    - Handle edge case: Multiple 'templates/' directories (use last occurrence)
    - Return Django-relative path format (e.g., `app_name/template.html`)
  - [ ] 1.3 Update `analyze_template_file()` to use normalized paths
    - Change `self.templates` dictionary keys from filesystem paths to normalized paths
    - Store mapping: `{normalized_path: filesystem_path}` for debugging if needed
    - Apply normalization when storing template metadata
  - [ ] 1.4 Update template relationship tracking to use normalized paths
    - Modify `_analyze_template_content()` method
    - Normalize template names in `{% include %}` patterns
    - Normalize template names in `{% extends %}` patterns
    - Ensure relationship dictionaries use normalized paths as keys
  - [ ] 1.5 Ensure path normalization tests pass
    - Run ONLY the 2-8 tests written in 1.1
    - Verify all normalization scenarios work correctly
    - Do NOT run the entire test suite at this stage

**Acceptance Criteria:**
- The 2-8 tests written in 1.1 pass
- `normalize_template_path()` correctly converts filesystem paths to Django-relative format
- Template analyzer stores templates with normalized path keys
- Template relationships (includes/extends) use normalized paths

---

### Phase 2: Enhanced Detection - View Analysis Layer

#### Task Group 2: Class-Based View Default Template Detection (HIGH - P1)
**Dependencies:** Task Group 1
**Owner Role:** Backend Engineer
**Timeline:** Day 2

Implements Django CBV implicit template naming detection to eliminate false positives for ListView, DetailView, etc.

- [ ] 2.0 Complete CBV default template detection
  - [ ] 2.1 Write 2-8 focused tests for CBV detection
    - Limit to 2-8 highly focused tests maximum
    - Test critical CBV scenarios:
      - ListView with model attribute → detects `<app>/<model>_list.html`
      - DetailView with model attribute → detects `<app>/<model>_detail.html`
      - CreateView/UpdateView with model → detects `<app>/<model>_form.html`
      - CBV with explicit template_name (should use explicit, not default)
    - Skip exhaustive testing of all CBV types
    - File: `tests/test_view_analyzer.py`
  - [ ] 2.2 Implement `_detect_cbv_type()` method
    - Location: `django_deadcode/analyzers/view_analyzer.py`
    - Method signature: `_detect_cbv_type(self, class_node: ast.ClassDef) -> str | None`
    - Parse `class_node.bases` to find CBV inheritance
    - Detect: ListView, DetailView, CreateView, UpdateView, DeleteView
    - Return CBV type name or None if not a recognized CBV
  - [ ] 2.3 Implement `_extract_model_from_cbv()` method
    - Location: `django_deadcode/analyzers/view_analyzer.py`
    - Method signature: `_extract_model_from_cbv(self, class_node: ast.ClassDef) -> str | None`
    - Use AST to find `model = ModelName` attribute assignment
    - Also check `queryset = ModelName.objects.all()` pattern
    - Extract model name from attribute value
    - Return lowercase model name or None
  - [ ] 2.4 Implement `_infer_app_label()` method
    - Location: `django_deadcode/analyzers/view_analyzer.py`
    - Method signature: `_infer_app_label(self, file_path: str) -> str | None`
    - Parse file path to find app name
    - Pattern: `/apps/<app_name>/views.py` or `/<app_name>/views.py`
    - Return app_name directory name
    - Handle edge cases: nested apps, non-standard structures
  - [ ] 2.5 Enhance `_process_cbv()` to generate implicit template names
    - Add CBV type detection using `_detect_cbv_type()`
    - Add model extraction using `_extract_model_from_cbv()`
    - Add app label inference using `_infer_app_label()`
    - Generate template name based on Django conventions:
      - ListView → `{app_label}/{model_name}_list.html`
      - DetailView → `{app_label}/{model_name}_detail.html`
      - CreateView/UpdateView → `{app_label}/{model_name}_form.html`
      - DeleteView → `{app_label}/{model_name}_confirm_delete.html`
    - Store in `template_usage` with metadata indicating detection method
    - Only generate if no explicit `template_name` attribute exists
  - [ ] 2.6 Ensure CBV detection tests pass
    - Run ONLY the 2-8 tests written in 2.1
    - Verify ListView/DetailView/CreateView detection works
    - Do NOT run the entire test suite at this stage

**Acceptance Criteria:**
- The 2-8 tests written in 2.1 pass
- CBV type detection correctly identifies ListView, DetailView, etc.
- Model extraction works for both `model` and `queryset` attributes
- App label inference works for standard Django app structures
- Implicit template names are correctly generated and stored

---

#### Task Group 3: Template Variable Detection (MEDIUM - P2)
**Dependencies:** Task Group 1
**Owner Role:** Backend Engineer
**Timeline:** Day 3

Detects template references through variables containing 'template' in the name, including `get_template_names()` method returns.

- [ ] 3.0 Complete template variable detection
  - [ ] 3.1 Write 2-8 focused tests for template variable detection
    - Limit to 2-8 highly focused tests maximum
    - Test critical variable patterns:
      - Simple assignment: `template_name = 'app/template.html'`
      - Custom variable: `my_template = 'app/other.html'`
      - Method return: `return ['app/template.html']` in `get_template_names()`
      - List return: `return [template1, template2]`
    - Skip complex conditional logic and dynamic template names
    - File: `tests/test_view_analyzer.py`
  - [ ] 3.2 Extend `_process_ast()` for variable assignment handling
    - Location: `django_deadcode/analyzers/view_analyzer.py`
    - Add AST node visitor for `ast.Assign` nodes
    - Filter for variable names containing 'template' (case-insensitive)
    - Extract string constants from assignments
    - Store extracted template paths with metadata
  - [ ] 3.3 Add method return parsing for `get_template_names()`
    - Detect `ast.FunctionDef` nodes named `get_template_names`
    - Parse `ast.Return` statements within method body
    - Extract string constants from list literals
    - Extract string constants from simple string returns
    - Handle both single strings and list returns
    - Skip complex expressions (variables, concatenation, f-strings)
  - [ ] 3.4 Associate extracted templates with view context
    - Track parent class context when inside method
    - Associate template variables with view class when applicable
    - Store in `template_usage` with source annotation
    - Include metadata: detection method, confidence level
  - [ ] 3.5 Ensure template variable tests pass
    - Run ONLY the 2-8 tests written in 3.1
    - Verify simple assignments and method returns work
    - Do NOT run the entire test suite at this stage

**Acceptance Criteria:**
- The 2-8 tests written in 3.1 pass
- Variable assignments with 'template' in name are detected
- `get_template_names()` method returns are parsed correctly
- String constants are extracted and stored in `template_usage`
- Templates are correctly associated with their view context

---

### Phase 3: Integration & Command Updates

#### Task Group 4: Command Integration & Path Consistency
**Dependencies:** Task Groups 1, 2, 3
**Owner Role:** Backend Engineer
**Timeline:** Day 4

Ensures the command layer correctly uses normalized paths for comparison and transitive closure logic.

- [ ] 4.0 Complete command integration
  - [ ] 4.1 Write 2-8 focused integration tests
    - Limit to 2-8 highly focused tests maximum
    - Test critical integration scenarios:
      - Path matching: filesystem template matches view reference
      - CBV default: ListView template not flagged as unused
      - Extends relationship: base template not flagged as unused
      - End-to-end: real Django app structure with zero false positives
    - Skip exhaustive combinations of all features
    - File: `tests/test_command_integration.py`
  - [ ] 4.2 Update `_compile_analysis_data()` method
    - Location: `django_deadcode/management/commands/finddeadcode.py`
    - Verify `all_templates` set uses normalized paths from TemplateAnalyzer
    - Verify `directly_referenced_templates` uses normalized paths from ViewAnalyzer
    - Ensure both sets use identical path format for comparison
    - Add debug logging for path comparison (optional, helpful for troubleshooting)
  - [ ] 4.3 Verify transitive closure uses normalized paths
    - Review `_find_transitively_referenced_templates()` method
    - Ensure template relationship lookups use normalized paths
    - Verify includes/extends dictionary keys match template set keys
    - Test transitive closure: A extends B, B extends C → C marked as used
  - [ ] 4.4 Update set comparison logic
    - Location: Line 276 in `finddeadcode.py`
    - Verify `potentially_unused = all_templates - all_referenced` comparison
    - Ensure comparison works correctly with normalized paths
    - Add assertion or validation that path formats are consistent
  - [ ] 4.5 Ensure integration tests pass
    - Run ONLY the 2-8 tests written in 4.1
    - Verify end-to-end path matching works
    - Do NOT run the entire test suite at this stage

**Acceptance Criteria:**
- The 2-8 tests written in 4.1 pass
- All path comparisons use normalized format consistently
- Transitive closure correctly identifies indirectly referenced templates
- Set comparison logic works without false positives
- Example false positives from spec (collations app) are resolved

---

### Phase 4: Comprehensive Testing & Validation

#### Task Group 5: Test Review & Gap Analysis
**Dependencies:** Task Groups 1-4
**Owner Role:** QA Engineer / Test Specialist
**Timeline:** Day 5

Reviews all tests written by previous task groups and fills critical gaps to ensure production readiness.

- [ ] 5.0 Review existing tests and fill critical gaps only
  - [ ] 5.1 Review tests from Task Groups 1-4
    - Review the 2-8 tests written for path normalization (Task 1.1)
    - Review the 2-8 tests written for CBV detection (Task 2.1)
    - Review the 2-8 tests written for template variables (Task 3.1)
    - Review the 2-8 tests written for integration (Task 4.1)
    - Total existing tests: approximately 8-32 tests
  - [ ] 5.2 Analyze test coverage gaps for THIS feature only
    - Identify critical user workflows that lack test coverage
    - Focus ONLY on gaps related to template detection fix requirements
    - Do NOT assess entire application test coverage
    - Prioritize integration gaps over unit test gaps
    - Document identified gaps: edge cases, error handling, complex scenarios
  - [ ] 5.3 Write up to 10 additional strategic tests maximum
    - Add maximum of 10 new tests to fill identified critical gaps
    - Focus on:
      - Edge cases in path normalization (symlinks, custom TEMPLATES settings)
      - Complex CBV scenarios (multiple inheritance, custom queryset methods)
      - Template relationship chains (multi-level extends/includes)
      - Error handling (malformed paths, missing models, invalid CBV types)
      - Real-world Django project structures
    - Do NOT write comprehensive coverage for all scenarios
    - Skip performance tests, accessibility tests unless business-critical
    - Files: Distribute across `test_template_analyzer.py`, `test_view_analyzer.py`, `test_command_integration.py`
  - [ ] 5.4 Run feature-specific tests only
    - Run ONLY tests related to this spec's feature
    - Expected total: approximately 18-42 tests maximum
    - Verify all critical workflows pass
    - Do NOT run the entire application test suite
    - Document any remaining known limitations

**Acceptance Criteria:**
- All feature-specific tests pass (approximately 18-42 tests total)
- Critical user workflows for template detection are covered
- No more than 10 additional tests added when filling in testing gaps
- Testing focused exclusively on this spec's feature requirements
- Test coverage >90% for modified files (TemplateAnalyzer, ViewAnalyzer, finddeadcode.py)

---

#### Task Group 6: Manual Validation & Documentation
**Dependencies:** Task Group 5
**Owner Role:** Technical Lead / Product Owner
**Timeline:** Day 5 (parallel with Task Group 5)

Manual testing against real Django projects and documentation updates to ensure production readiness.

- [ ] 6.0 Complete manual validation and documentation
  - [ ] 6.1 Manual testing against example collations app
    - Run finddeadcode command against collations app from spec
    - Verify `collations/base.html` NOT flagged as unused (extends relationship)
    - Verify `collations/collection_list.html` NOT flagged as unused (ListView default)
    - Verify `collations/collection_detail.html` NOT flagged as unused (DetailView default)
    - Document results: before/after comparison
  - [ ] 6.2 Test against diverse Django project structures
    - Test with Django 2.2, 3.2, 4.2, 5.x (version compatibility)
    - Test with custom TEMPLATES settings
    - Test with non-standard app structures
    - Test with third-party app templates (should still be filtered by BASE_DIR)
    - Document any compatibility issues or limitations
  - [ ] 6.3 Performance validation
    - Benchmark against small project (10 templates)
    - Benchmark against medium project (100 templates)
    - Benchmark against large project (1000 templates)
    - Verify performance impact <10% (acceptable per spec)
    - Document performance metrics
  - [ ] 6.4 Update documentation
    - Update method docstrings for new/modified methods
    - Add inline comments for complex normalization logic
    - Update README with new capabilities (CBV detection, improved accuracy)
    - Document known limitations (out of scope items)
    - Add troubleshooting guide for path normalization issues
  - [ ] 6.5 Code review and cleanup
    - Remove debug logging if not needed
    - Ensure consistent code style
    - Verify all TODOs addressed
    - Check for unused imports
    - Final code review checklist

**Acceptance Criteria:**
- All example false positives from spec are resolved
- Performance impact <10% on benchmark projects
- Documentation is complete and accurate
- Code passes review standards
- Tool is production-ready

---

## Execution Order

Recommended implementation sequence:

**Phase 1: Foundation (Days 1)**
1. Task Group 1: Path Normalization Layer

**Phase 2: Enhanced Detection (Days 2-3)**
2. Task Group 2: CBV Default Detection
3. Task Group 3: Template Variable Detection
   - Groups 2 and 3 can be developed in parallel if desired (both depend only on Group 1)

**Phase 3: Integration (Day 4)**
4. Task Group 4: Command Integration

**Phase 4: Validation (Day 5)**
5. Task Group 5: Test Review & Gap Analysis
6. Task Group 6: Manual Validation (parallel with Group 5)

---

## Critical Dependencies

```
Task Group 1 (Path Normalization)
    ├── Task Group 2 (CBV Detection)
    ├── Task Group 3 (Template Variables)
    └── Task Group 4 (Command Integration)
            ├── Task Group 5 (Test Review)
            └── Task Group 6 (Manual Validation)
```

**Critical Path:** 1 → 2 → 4 → 5 → 6 (5 days)
**Parallel Opportunity:** Groups 2 and 3 can be done in parallel (saves 1 day if resources available)

---

## Key Files Modified

1. **`django_deadcode/analyzers/template_analyzer.py`**
   - Add `normalize_template_path()` method
   - Update `analyze_template_file()` to store normalized paths
   - Update `_analyze_template_content()` for relationship normalization

2. **`django_deadcode/analyzers/view_analyzer.py`**
   - Add `_detect_cbv_type()` method
   - Add `_extract_model_from_cbv()` method
   - Add `_infer_app_label()` method
   - Enhance `_process_cbv()` for implicit template generation
   - Extend `_process_ast()` for variable detection

3. **`django_deadcode/management/commands/finddeadcode.py`**
   - Update `_compile_analysis_data()` for normalized path comparison
   - Verify `_find_transitively_referenced_templates()` consistency

4. **Test Files:**
   - `tests/test_template_analyzer.py` - Path normalization tests
   - `tests/test_view_analyzer.py` - CBV and variable detection tests
   - `tests/test_command_integration.py` - End-to-end integration tests

---

## Success Metrics

**Functional Success:**
- Zero false positives for the collations app example
- All Django CBV types correctly detected (ListView, DetailView, CreateView, UpdateView, DeleteView)
- Template variables correctly extracted
- Template relationships correctly tracked with normalized paths

**Quality Success:**
- Test coverage >90% for modified files
- Performance impact <10% per spec benchmarks
- All tests passing (18-42 feature-specific tests)

**Production Readiness:**
- Manual testing completed against diverse Django projects
- Documentation updated and complete
- Code review approved
- Tool ready for v0.3.0 release

---

## Risk Mitigation

**RISK-1: Django Version Compatibility**
- Mitigation: Task Group 6 includes testing across Django 2.2, 3.2, 4.2, 5.x
- Fallback: Version-specific code paths if needed

**RISK-2: Complex App Structures**
- Mitigation: Task Group 6 includes non-standard structure testing
- Fallback: Make app label inference configurable

**RISK-3: Performance Impact**
- Mitigation: Task Group 6 includes performance benchmarking
- Fallback: Add caching for normalization results if needed

**RISK-4: AST Parsing Complexity**
- Mitigation: Start with simple patterns, log unhandled cases
- Fallback: Skip complex AST patterns, document limitations

---

## Out of Scope (Explicitly Excluded)

The following are **not** included in this task breakdown per spec requirements:

1. Dynamic template names (f-strings, concatenation)
2. `get_template()` function calls
3. `select_template()` function calls
4. Django admin auto-generated templates (separate feature)
5. Third-party package template analysis
6. Complex `get_template_names()` with conditional logic

These may be addressed in future features based on user feedback.

---

**Document Version:** 1.0
**Created:** 2025-11-14
**Status:** Ready for Implementation
**Estimated Effort:** 5 days (40 hours)
