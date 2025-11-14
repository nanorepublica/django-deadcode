# Specification: Fix Unused Template Detection

## Executive Summary

The django-deadcode tool's template detection feature is producing false positives by incorrectly flagging templates as unused when they are actually referenced. The root cause is a path format mismatch between template discovery (filesystem paths) and template reference detection (Django-relative paths). This specification details a comprehensive fix that includes path normalization, enhanced class-based view detection, and improved template variable parsing.

**Impact:** Eliminates false positives, making the tool production-ready and trustworthy for identifying genuinely unused templates.

**Scope:** Fix path normalization bugs and enhance template reference detection for CBV defaults and template variables.

**Timeline:** Estimated 3-5 days of development work.

## Problem Statement

### Current Behavior

Templates that are actively used in the Django project are being flagged as "potentially unused" because the tool cannot match them against their references.

### Concrete Examples of False Positives

```
/app/apps/collations/templates/collations/base.html
/app/apps/collations/templates/collations/collection_detail.html
/app/apps/collations/templates/collations/collection_list.html
```

**Why These Are False Positives:**
- `base.html` - Referenced via `{% extends 'collations/base.html' %}` in other templates
- `collection_detail.html` - Implicitly used by `DetailView` for `Collection` model
- `collection_list.html` - Implicitly used by `ListView` for `Collection` model

### User Impact

Developers cannot trust the tool's output, requiring manual verification of every "unused" template before deletion. This defeats the tool's purpose of automating dead code detection.

## Root Cause Analysis

### Primary Bug: Path Format Mismatch

**Location:** `django_deadcode/management/commands/finddeadcode.py:256-276`

**Issue:** Template paths are stored in incompatible formats:

1. **TemplateAnalyzer Output** (Line 256):
   - Format: Full filesystem paths
   - Example: `/app/apps/collations/templates/collations/base.html`
   - Source: `Path.rglob()` returns absolute paths

2. **ViewAnalyzer Output** (Line 260):
   - Format: Django-relative template names
   - Example: `collations/base.html`
   - Source: Extracted from `render()` and `template_name` attributes

3. **Set Comparison Fails** (Line 276):
   ```python
   potentially_unused = all_templates - all_referenced
   ```
   - Never matches because formats differ
   - Results in all templates being flagged as unused

### Secondary Gaps: Missing Detection Patterns

1. **Class-Based View Defaults:** CBVs use implicit naming conventions (e.g., `ListView` → `<app>/<model>_list.html`) but tool only detects explicit `template_name` attributes

2. **Template Variables:** Variables like `template_name = 'app/foo.html'` or `get_template_names()` method returns are not parsed

3. **Template Relationships:** While `{% extends %}` and `{% include %}` are extracted, they may suffer from the same path normalization issue

## Detailed Requirements

### REQ-1: Path Normalization (CRITICAL - P0)

**Objective:** Normalize all template paths to Django's relative format for consistent comparison.

**Acceptance Criteria:**
- All templates in `TemplateAnalyzer.templates` keys use relative Django paths (e.g., `app/template.html`)
- All templates in `ViewAnalyzer.template_usage` keys use the same relative format
- Template relationship keys (`includes`, `extends`) use normalized paths
- Path normalization leverages Django's template loader logic, not manual string manipulation

**Technical Requirements:**
- Add `normalize_template_path(filesystem_path: Path) -> str` method to TemplateAnalyzer
- Method should strip everything up to and including the `templates/` directory
- Handle edge cases: multiple `templates/` directories in path, symlinks, custom TEMPLATES settings
- Apply normalization consistently across all analyzers

**Example Transformation:**
```
Input:  /app/apps/collations/templates/collations/base.html
Output: collations/base.html
```

### REQ-2: Class-Based View Default Template Detection (HIGH - P1)

**Objective:** Automatically detect templates used by CBVs through Django's implicit naming convention.

**Acceptance Criteria:**
- Detect CBV inheritance (ListView, DetailView, CreateView, UpdateView, DeleteView)
- Extract model from `model` attribute or `queryset` attribute
- Determine app label from view file location or model metadata
- Generate implicit template name and mark as referenced
- Works even when `template_name` is not explicitly set

**Django CBV Naming Conventions:**
| View Type | Template Pattern |
|-----------|------------------|
| ListView | `<app_label>/<model_name>_list.html` |
| DetailView | `<app_label>/<model_name>_detail.html` |
| CreateView | `<app_label>/<model_name>_form.html` |
| UpdateView | `<app_label>/<model_name>_form.html` |
| DeleteView | `<app_label>/<model_name>_confirm_delete.html` |

**Technical Requirements:**
- Extend `ViewAnalyzer._process_cbv()` to detect base class names
- Add logic to extract model from AST (attribute assignments, queryset)
- Infer app label from file path (e.g., `/apps/collations/views.py` → `collations`)
- Generate template name using Django's conventions
- Store detected templates in `template_usage` with source annotation

### REQ-3: Template Variable Detection (MEDIUM - P2)

**Objective:** Detect template references through variables containing 'template' in the name.

**Acceptance Criteria:**
- Detect local variable assignments: `template_name = 'app/template.html'`
- Detect method returns: `return ['app/template.html']` in `get_template_names()`
- Extract string constants from these patterns
- Handle both single strings and list returns
- Associate with view class when applicable

**Patterns to Support:**

**A. Simple Assignment:**
```python
template_name = 'app/template.html'
my_template = 'app/other.html'
```

**B. Method Returns:**
```python
def get_template_names(self):
    return ['app/template.html']

def get_template_names(self):
    return [self.template_name]
```

**Technical Requirements:**
- Extend `ViewAnalyzer._process_ast()` to handle variable assignments
- Filter for variables with 'template' in name (case-insensitive)
- Extract string constants from assignments and returns
- Track context to associate with parent class if inside method

### REQ-4: Enhanced Template Relationship Tracking (MEDIUM - P2)

**Objective:** Ensure template relationships use normalized paths for correct transitive closure.

**Acceptance Criteria:**
- `{% include %}` and `{% extends %}` template names are normalized
- Transitive closure logic in `finddeadcode.py` works with normalized paths
- Templates referenced only through extends/include chains are marked as used

**Technical Requirements:**
- Apply path normalization to included/extended template names in TemplateAnalyzer
- Verify transitive closure comparison in `_find_transitively_referenced_templates()`
- Ensure all path comparisons use consistent format

## Technical Approach / Architecture

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    finddeadcode Command                      │
│                                                              │
│  1. Initialize analyzers                                    │
│  2. Collect data (with normalization)                       │
│  3. Compare using normalized paths                          │
│  4. Report genuinely unused templates                       │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────┬──────────────────────┬───────────────────┐
│                 │                      │                   │
│ TemplateAnalyzer│   ViewAnalyzer      │  ReverseAnalyzer  │
│                 │                      │                   │
│ • Find templates│ • Parse views       │  • Parse Python   │
│ • Extract       │ • Detect render()   │  • Extract refs   │
│   relationships │ • Detect CBV        │                   │
│ • NORMALIZE     │ • Detect defaults   │                   │
│   paths         │ • Detect variables  │                   │
│                 │ • NORMALIZE paths   │                   │
└─────────────────┴──────────────────────┴───────────────────┘
```

### Component Modifications

#### 1. TemplateAnalyzer (`django_deadcode/analyzers/template_analyzer.py`)

**New Method: `normalize_template_path()`**
```python
def normalize_template_path(self, filesystem_path: Path) -> str:
    """
    Convert filesystem path to Django-relative template path.

    Example:
        /app/apps/collations/templates/collations/base.html
        → collations/base.html
    """
    # Find 'templates/' in path and return everything after it
    # Handle edge cases: multiple templates dirs, symlinks
```

**Modified Method: `analyze_template_file()`**
- Store normalized path as key instead of filesystem path
- Maintain mapping for debugging if needed

**Modified Method: `_analyze_template_content()`**
- Normalize template names in `{% include %}` and `{% extends %}`

#### 2. ViewAnalyzer (`django_deadcode/analyzers/view_analyzer.py`)

**Enhanced Method: `_process_cbv()`**
- Detect CBV base classes by examining `node.bases`
- Extract model from AST attributes
- Infer app label from file path
- Generate implicit template name
- Store with metadata indicating detection method

**New Method: `_detect_cbv_type()`**
```python
def _detect_cbv_type(self, class_node: ast.ClassDef) -> str | None:
    """
    Determine if class is a Django CBV and return its type.
    Returns: 'ListView', 'DetailView', etc., or None
    """
```

**New Method: `_extract_model_from_cbv()`**
```python
def _extract_model_from_cbv(self, class_node: ast.ClassDef) -> str | None:
    """
    Extract model name from CBV class definition.
    Checks: model attribute, queryset attribute
    """
```

**New Method: `_infer_app_label()`**
```python
def _infer_app_label(self, file_path: str) -> str | None:
    """
    Infer Django app label from file path.
    Example: /project/apps/collations/views.py → collations
    """
```

**Enhanced Method: `_process_ast()`**
- Add handling for variable assignments containing 'template'
- Parse method definitions like `get_template_names()`

#### 3. Command (`django_deadcode/management/commands/finddeadcode.py`)

**Modified Method: `_compile_analysis_data()`**
- Ensure all path comparisons use normalized format
- Add debug logging for path mismatches (optional)
- Verify transitive closure works with normalized paths

### Reusable Components

**Existing Infrastructure to Leverage:**
1. **AST Parsing:** ViewAnalyzer already uses `ast.walk()` and processes ClassDef nodes
2. **Template Extraction:** TemplateAnalyzer already extracts includes/extends with regex
3. **Path Utilities:** TemplateAnalyzer already has `_is_relative_to()` helper
4. **Transitive Closure:** Command already implements graph traversal for relationships
5. **Test Framework:** Existing pytest structure with tempfile patterns

**New Components Required:**
1. Path normalization utility
2. CBV type detection logic
3. Model extraction from AST
4. App label inference
5. Template variable extraction

## Implementation Plan

### Phase 1: Path Normalization (2 days)

**Day 1: Core Implementation**
- [ ] Add `normalize_template_path()` to TemplateAnalyzer
- [ ] Update `analyze_template_file()` to store normalized paths
- [ ] Update `_analyze_template_content()` to normalize relationship paths
- [ ] Add unit tests for normalization edge cases

**Day 2: Integration & Verification**
- [ ] Verify all path comparisons in `finddeadcode.py` work correctly
- [ ] Test with real Django project to verify false positive elimination
- [ ] Add integration tests for end-to-end path normalization

**Deliverables:**
- Normalized path storage across all analyzers
- Zero false positives for explicit template references
- Test coverage for path normalization

### Phase 2: Enhanced View Detection (2 days)

**Day 3: CBV Default Detection**
- [ ] Implement `_detect_cbv_type()` method
- [ ] Implement `_extract_model_from_cbv()` method
- [ ] Implement `_infer_app_label()` method
- [ ] Update `_process_cbv()` to generate implicit template names
- [ ] Add unit tests for each CBV type (ListView, DetailView, etc.)

**Day 4: Template Variable Detection**
- [ ] Extend `_process_ast()` for variable assignment handling
- [ ] Add method return parsing for `get_template_names()`
- [ ] Filter variables by 'template' in name
- [ ] Add unit tests for variable patterns

**Deliverables:**
- CBV default templates correctly detected
- Template variables correctly parsed
- Comprehensive test coverage for new detection patterns

### Phase 3: Integration & Testing (1 day)

**Day 5: Integration & Validation**
- [ ] Run full test suite
- [ ] Test against real Django project (collations app example)
- [ ] Verify all example false positives are resolved
- [ ] Update documentation with new capabilities
- [ ] Performance testing with large projects

**Deliverables:**
- All tests passing
- Example project showing zero false positives
- Updated documentation
- Performance benchmarks

## Test Strategy

### Unit Tests

**TemplateAnalyzer Tests** (`tests/test_template_analyzer.py`):
```python
def test_normalize_template_path():
    """Test path normalization with various formats."""
    # Test standard app template
    # Test nested templates directory
    # Test symlinks
    # Test templates at project root

def test_normalized_includes_extends():
    """Test that relationships use normalized paths."""
    # Verify include/extend paths are normalized
```

**ViewAnalyzer Tests** (`tests/test_view_analyzer.py`):
```python
def test_detect_listview_default_template():
    """Test CBV default detection for ListView."""
    # ListView with model attribute
    # Verify implicit template name generated

def test_detect_detailview_default_template():
    """Test CBV default detection for DetailView."""
    # DetailView with queryset attribute
    # Verify implicit template name generated

def test_detect_template_variable():
    """Test template variable detection."""
    # Simple assignment
    # get_template_names() method

def test_infer_app_label_from_path():
    """Test app label inference."""
    # Standard app structure
    # Nested apps
    # Edge cases
```

**Integration Tests** (`tests/test_command_integration.py`):
```python
def test_no_false_positives_for_cbv_defaults():
    """Test that CBV default templates are not flagged as unused."""
    # Create ListView with model
    # Verify template not in unused list

def test_no_false_positives_for_extends():
    """Test that base templates are not flagged as unused."""
    # Create child template extending base
    # Verify base not in unused list

def test_path_normalization_integration():
    """Test end-to-end path matching."""
    # Create template with full path
    # Reference with relative path
    # Verify match succeeds
```

### Test Data

**Fixture Projects:**
1. **Minimal Django App:**
   - One ListView with implicit template
   - One DetailView with explicit template_name
   - Base template with extends relationship

2. **Complex Django App:**
   - Multiple CBV types
   - Nested template includes
   - Template variables
   - Custom template directories

### Manual Testing Checklist

- [ ] Run against example collations app
- [ ] Verify `base.html` not flagged as unused (extends relationship)
- [ ] Verify `collection_list.html` not flagged as unused (ListView default)
- [ ] Verify `collection_detail.html` not flagged as unused (DetailView default)
- [ ] Test with Django admin (should still work, admin templates filtered by BASE_DIR)
- [ ] Test with third-party packages (should still work, filtered by BASE_DIR)

## Success Criteria

### Functional Requirements

1. **Path Matching Works:**
   - Template at `/project/app/templates/app/base.html` referenced as `app/base.html` → MATCHES
   - Zero false positives for explicitly referenced templates

2. **CBV Defaults Detected:**
   - ListView for Collection model → detects `collations/collection_list.html`
   - DetailView for Collection model → detects `collations/collection_detail.html`
   - All Django generic CBV types supported

3. **Template Variables Found:**
   - `template_name = 'app/foo.html'` → DETECTED
   - `get_template_names()` returning list → DETECTED
   - Variables without 'template' in name → IGNORED (as expected)

4. **Extends/Include Work:**
   - Template extending `base.html` → `base.html` marked as USED
   - Template including `partials/header.html` → `partials/header.html` marked as USED
   - Transitive relationships work (A extends B, B extends C → C is used)

5. **Example False Positives Resolved:**
   - `collations/base.html` → NOT flagged as unused
   - `collations/collection_detail.html` → NOT flagged as unused
   - `collations/collection_list.html` → NOT flagged as unused

### Quality Requirements

1. **Test Coverage:** >90% code coverage for modified files
2. **Performance:** No significant performance degradation (<10% slower)
3. **Backward Compatibility:** Existing valid detections still work
4. **Documentation:** All new methods documented with docstrings

### Acceptance Criteria

- [ ] All unit tests passing
- [ ] All integration tests passing
- [ ] Manual test checklist completed
- [ ] Example project shows zero false positives
- [ ] Code review approved
- [ ] Documentation updated

## Out of Scope

The following are explicitly **excluded** from this implementation to maintain focus:

1. **Dynamic Template Names:**
   - f-string template names: `f'{app_name}/template.html'`
   - Concatenated variables: `template = var1 + var2`
   - **Rationale:** Requires runtime analysis or symbolic execution

2. **`get_template()` Function Calls:**
   - Direct template loader usage in view logic
   - **Rationale:** Less common pattern, requires complex AST analysis

3. **`select_template()` Function Calls:**
   - Conditional template loading with fallbacks
   - **Rationale:** Requires understanding conditional logic

4. **Django Admin Auto-Generated Templates:**
   - Admin change lists, change forms, etc.
   - **Rationale:** Separate feature (#10 in roadmap)

5. **Third-Party Package Templates:**
   - Templates from installed packages like django-allauth
   - **Rationale:** Already filtered by BASE_DIR; separate feature (#11 for confidence scoring)

6. **Template Name Override Methods:**
   - Complex `get_template_names()` with conditional logic
   - **Rationale:** Requires control flow analysis

These features may be addressed in future enhancements based on user feedback and prioritization.

## Risk Assessment

### High Risk Items

**RISK-1: Django Version Compatibility**
- **Issue:** Template loader behavior may vary across Django versions (2.2 - 5.x)
- **Mitigation:** Test against multiple Django versions; use stable APIs only
- **Contingency:** Version-specific code paths with feature detection

**RISK-2: Complex App Structures**
- **Issue:** Non-standard project layouts may break app label inference
- **Mitigation:** Make app label inference configurable; log warnings for ambiguous cases
- **Contingency:** Fall back to file-based detection only; allow manual configuration

**RISK-3: Custom Template Loaders**
- **Issue:** Projects using custom template loaders may have different path resolution
- **Mitigation:** Use Django's template settings; support multiple template directories
- **Contingency:** Provide override mechanism for path normalization logic

### Medium Risk Items

**RISK-4: Performance Impact**
- **Issue:** Path normalization adds overhead to template discovery
- **Mitigation:** Cache normalization results; optimize path parsing
- **Impact:** 5-10% slower acceptable; >20% requires optimization

**RISK-5: AST Parsing Complexity**
- **Issue:** Model extraction from AST may fail for complex expressions
- **Mitigation:** Start with simple patterns; log unhandled cases for future enhancement
- **Fallback:** Only detect explicitly set template_name if model extraction fails

### Low Risk Items

**RISK-6: Template Variable False Positives**
- **Issue:** Variables with 'template' in name might not be template paths
- **Mitigation:** Additional validation (check if value is valid path format)
- **Impact:** Minor; may detect a few non-templates (low impact)

**RISK-7: Symlink Handling**
- **Issue:** Symlinked templates may cause duplicate or missing entries
- **Mitigation:** Use resolved paths consistently; document behavior
- **Impact:** Edge case; most projects don't use symlinks for templates

### Mitigation Strategy

1. **Incremental Rollout:** Deploy path normalization first, then enhanced detection
2. **Logging:** Add debug logging for path normalization decisions
3. **Configuration:** Provide settings to disable aggressive detection if needed
4. **Validation:** Run against diverse Django projects before release
5. **Documentation:** Clearly document assumptions and limitations

## Dependencies

### Required
- Django 2.2+ (template loader APIs)
- Python 3.8+ (AST module, pathlib)
- Existing analyzer infrastructure

### Development
- pytest (testing framework)
- pytest-django (Django test utilities)
- pytest-cov (coverage reporting)
- tempfile (test fixtures)

### Optional
- Django Debug Toolbar (performance profiling)
- mypy (type checking)

## Related Work

**Current Features:**
- URL pattern analysis
- Basic template detection
- Template relationship extraction
- Reverse/redirect detection

**Future Features (Roadmap):**
- Feature #10: Django Admin Detection (reduces admin false positives)
- Feature #11: Confidence Scoring (probabilistic assessment for edge cases)
- Feature #12: Dynamic Template Detection (handles f-strings, concatenation)

**Similar Tools:**
- vulture (Python dead code detection)
- coverage.py (code coverage for templates via django-coverage-plugin)

## Appendix

### A. Example Test Case

**Test: CBV Default Template Detection**
```python
# views.py
from django.views.generic import ListView
from .models import Collection

class CollectionListView(ListView):
    model = Collection
    # No template_name specified - should detect implicit template

# Expected: Tool detects 'collations/collection_list.html' as referenced
# Actual (before fix): Template flagged as unused
# After fix: Template correctly marked as used
```

### B. Path Normalization Examples

| Filesystem Path | Normalized Path |
|-----------------|-----------------|
| `/app/templates/base.html` | `base.html` |
| `/app/apps/collations/templates/collations/list.html` | `collations/list.html` |
| `/app/templates/admin/change_form.html` | `admin/change_form.html` |
| `/app/partials/templates/partials/header.html` | `partials/header.html` |

### C. Performance Benchmarks (Target)

| Project Size | Templates | Time (Before) | Time (After) | Delta |
|--------------|-----------|---------------|--------------|-------|
| Small (10 templates) | 10 | 0.5s | 0.55s | +10% |
| Medium (100 templates) | 100 | 2.0s | 2.15s | +7.5% |
| Large (1000 templates) | 1000 | 15s | 16.2s | +8% |

**Acceptable:** <10% performance impact
**Warning:** 10-20% impact requires optimization
**Blocker:** >20% impact requires redesign

---

**Document Version:** 1.0
**Last Updated:** 2025-11-14
**Author:** Agent OS Spec Writer
**Status:** Ready for Implementation
