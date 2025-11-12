# Tasks: Template Reporting Improvements

## Phase 1: BASE_DIR Filtering

### Task 1.1: Add BASE_DIR Retrieval
**File**: `django_deadcode/management/commands/finddeadcode.py`

**Status**: COMPLETED ✓

**Changes**:
1. Import `from pathlib import Path`
2. Add method to get BASE_DIR from Django settings:
```python
def _get_base_dir(self) -> Path:
    """Get the BASE_DIR from Django settings."""
    base_dir = getattr(settings, 'BASE_DIR', None)
    if base_dir is None:
        raise CommandError("BASE_DIR not found in Django settings")
    return Path(base_dir).resolve()
```
3. Call in `handle()` method before template discovery

**Testing**:
- Test with project that has BASE_DIR ✓
- Test with project missing BASE_DIR (should raise CommandError) ✓

### Task 1.2: Filter Templates by BASE_DIR
**File**: `django_deadcode/analyzers/template_analyzer.py`

**Status**: COMPLETED ✓

**Changes**:
1. Update `__init__` to accept `base_dir` parameter ✓
2. Update `find_all_templates()` to filter by BASE_DIR ✓
3. Add helper method `_is_relative_to()` for Python 3.8+ compatibility ✓

**Testing**:
- Test with templates inside BASE_DIR (should be included) ✓
- Test with templates outside BASE_DIR (should be excluded) ✓
- Test with symlinked templates (should use resolved path for check but keep original) ✓

### Task 1.3: Update Command to Pass BASE_DIR
**File**: `django_deadcode/management/commands/finddeadcode.py`

**Status**: COMPLETED ✓

**Changes**:
1. Get BASE_DIR in `handle()` method ✓
2. Pass to TemplateAnalyzer ✓

**Testing**:
- Integration test: full command run with templates in/out of BASE_DIR ✓

---

## Phase 2: Include/Extends Detection

### Task 2.1: Implement Transitive Closure Algorithm
**File**: `django_deadcode/management/commands/finddeadcode.py`

**Status**: COMPLETED ✓

**Changes**:
1. Add new method `_find_transitively_referenced_templates()` ✓

**Testing**:
- Test simple chain: view → template1 → includes template2 ✓
- Test extends: view → child → extends base ✓
- Test complex: view → template1 → includes template2, extends base ✓
- Test circular reference: template1 includes template2, template2 includes template1 ✓

### Task 2.2: Update Dead Code Detection Logic
**File**: `django_deadcode/management/commands/finddeadcode.py`

**Status**: COMPLETED ✓

**Changes**:
Update the logic in `_compile_analysis_data()` to use transitive closure algorithm ✓

**Testing**:
- Integration test: templates only used via includes are not reported as unused ✓
- Integration test: base templates only used via extends are not reported as unused ✓

---

## Phase 3: Optional Relationship Reporting

### Task 3.1: Add CLI Flag
**File**: `django_deadcode/management/commands/finddeadcode.py`

**Status**: COMPLETED ✓

**Changes**:
1. Add argument in `add_arguments()` method ✓
2. Store flag value in `handle()` ✓

**Testing**:
- Test flag parsing: command with/without flag ✓

### Task 3.2: Update Reporter Base Class
**File**: `django_deadcode/reporters/base.py`

**Status**: COMPLETED ✓

**Changes**:
1. Add parameter to reporter `__init__` ✓
2. Update each `generate_report()` method signature to include the parameter ✓

**Testing**:
- Unit test: verify flag is stored correctly ✓

### Task 3.3: Update Console Reporter
**File**: `django_deadcode/reporters/base.py` (ConsoleReporter class)

**Status**: COMPLETED ✓

**Changes**:
Update `generate_report()` method to conditionally show relationships ✓

**Testing**:
- Test with flag=True: relationships shown ✓
- Test with flag=False: relationships not shown ✓

### Task 3.4: Update JSON Reporter
**File**: `django_deadcode/reporters/base.py` (JSONReporter class)

**Status**: COMPLETED ✓

**Changes**:
Update `generate_report()` method to conditionally include relationships ✓

**Testing**:
- Test with flag=True: JSON includes template_relationships ✓
- Test with flag=False: JSON excludes template_relationships ✓

### Task 3.5: Update Markdown Reporter
**File**: `django_deadcode/reporters/base.py` (MarkdownReporter class)

**Status**: COMPLETED ✓

**Changes**:
Update `generate_report()` method to conditionally show relationships ✓

**Testing**:
- Test with flag=True: markdown includes relationships section ✓
- Test with flag=False: markdown excludes relationships section ✓

### Task 3.6: Update Command to Pass Flag to Reporters
**File**: `django_deadcode/management/commands/finddeadcode.py`

**Status**: COMPLETED ✓

**Changes**:
Update reporter instantiation in `_generate_report()` ✓

**Testing**:
- Integration test: full command with --show-template-relationships ✓

---

## Phase 4: Testing & Documentation

### Task 4.1: Add Unit Tests
**File**: `tests/test_template_analyzer.py`

**Status**: COMPLETED ✓

**Test Cases**:
1. `test_base_dir_filtering_includes_templates_inside()` ✓
2. `test_base_dir_filtering_excludes_templates_outside()` ✓
3. `test_symlink_preserves_original_path()` ✓
4. `test_is_relative_to_helper()` ✓
5. `test_find_all_templates_with_multiple_extensions()` ✓
6. `test_template_relationships_extraction()` ✓

### Task 4.2: Add Integration Tests
**File**: `tests/test_command_integration.py` (new)

**Status**: COMPLETED ✓

**Test Cases**:
1. `test_get_base_dir_from_settings()` ✓
2. `test_get_base_dir_missing_raises_error()` ✓
3. `test_transitive_includes_detection()` ✓
4. `test_transitive_extends_detection()` ✓
5. `test_complex_template_chain()` ✓
6. `test_circular_include_detection()` ✓
7. `test_transitive_with_multiple_extends()` ✓
8. `test_empty_directly_referenced()` ✓
9. `test_deep_template_chain()` ✓
10. `test_transitive_with_missing_template_reference()` ✓

**File**: `tests/test_reporters.py` (updated)

**Additional Test Cases**:
1. `test_console_reporter_hides_relationships_by_default()` ✓
2. `test_console_reporter_shows_relationships_when_enabled()` ✓
3. `test_json_reporter_excludes_relationships_by_default()` ✓
4. `test_json_reporter_includes_relationships_when_enabled()` ✓
5. `test_markdown_reporter_hides_relationships_by_default()` ✓
6. `test_markdown_reporter_shows_relationships_when_enabled()` ✓

### Task 4.3: Update Documentation
**Files**:
- `README.md`: Add section on BASE_DIR filtering and --show-template-relationships flag
- `CHANGELOG.md`: Add entry for this feature

**Status**: COMPLETED ✓

---

## Acceptance Criteria

### Phase 1: BASE_DIR Filtering
- [x] Templates outside BASE_DIR are not discovered
- [x] Templates inside BASE_DIR are discovered normally
- [x] Symlinks are handled correctly (resolved for comparison, original path stored)
- [x] Tests pass for all BASE_DIR scenarios

### Phase 2: Include/Extends Detection
- [x] Templates used via `{% include %}` are marked as used
- [x] Templates used via `{% extends %}` are marked as used
- [x] Transitive references work (template1 → template2 → template3)
- [x] Circular references don't cause infinite loops
- [x] Tests pass for all include/extends scenarios

### Phase 3: Optional Relationship Reporting
- [x] `--show-template-relationships` flag is available
- [x] Flag=True shows relationships in all output formats
- [x] Flag=False (default) hides relationships in all output formats
- [x] Tests pass for all reporter scenarios

### Phase 4: Testing & Documentation
- [x] All unit tests pass (62/62 tests passing)
- [x] All integration tests pass
- [x] README.md updated with new behavior
- [x] CHANGELOG.md updated

---

## Test Results

All tests passing: 62/62 ✓
- Template analyzer tests: 12/12 ✓
- Command integration tests: 11/11 ✓
- Reporter tests: 10/10 ✓
- All other existing tests: 29/29 ✓

Coverage: 93%
