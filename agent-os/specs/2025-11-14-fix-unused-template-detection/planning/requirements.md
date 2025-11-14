# Requirements: Fix Unused Template Detection

## Problem Statement

The unused template detection feature is incorrectly flagging templates as unreferenced when they are actually used. This results in false positives that undermine the tool's reliability.

### Example False Positives

```
/app/apps/collations/templates/collations/base.html
/app/apps/collations/templates/collations/collection_detail.html
/app/apps/collations/templates/collations/collection_list.html
```

- `base.html` is referenced via `{% extends %}` in other templates
- `collection_detail.html` and `collection_list.html` are used by class-based view defaults (implicit references)

## Root Cause Analysis

### Core Bug: Path Mismatch

**Location:** `django_deadcode/management/commands/finddeadcode.py:256-276`

**Issue:** Template paths are stored in different formats and cannot be matched:

1. **`all_templates`** (from `TemplateAnalyzer`) contains full filesystem paths:
   - Example: `/app/apps/collations/templates/collations/base.html`

2. **`directly_referenced_templates`** (from `ViewAnalyzer`) contains relative template names:
   - Example: `collations/base.html`

3. **Comparison fails:** When computing `potentially_unused = all_templates - all_referenced`, the sets never intersect because the path formats don't match.

### Current Code Flow

```python
# Line 256: Full paths from TemplateAnalyzer
all_templates = set(template_analyzer.templates.keys())

# Line 260: Relative paths from ViewAnalyzer
directly_referenced_templates = set(view_analyzer.template_usage.keys())

# Line 276: Comparison fails due to format mismatch
potentially_unused = all_templates - all_referenced
```

## Requirements

### 1. Fix Path Normalization (CRITICAL)

**Requirement:** Normalize template paths to use consistent relative format that matches Django's template resolution.

**Approach:**
- Use Django's template loaders to determine the correct relative path format
- Normalize full filesystem paths to Django's relative template paths (e.g., strip everything before and including `templates/`)
- Ensure both `TemplateAnalyzer` and `ViewAnalyzer` produce comparable path formats

**Implementation Notes:**
- Leverage Django's `django.template.loaders` to get canonical template names
- The relative path should match what developers write in code (e.g., `app_name/template.html`)

**Files to Modify:**
- `django_deadcode/analyzers/template_analyzer.py` - Add path normalization method
- `django_deadcode/management/commands/finddeadcode.py` - Ensure consistent comparison

### 2. Detect Class-Based View Default Templates

**Requirement:** Automatically detect templates used by CBVs through Django's implicit naming convention.

**Django CBV Template Naming Convention:**
- `ListView` → `<app_label>/<model_name>_list.html`
- `DetailView` → `<app_label>/<model_name>_detail.html`
- `CreateView` → `<app_label>/<model_name>_form.html`
- `UpdateView` → `<app_label>/<model_name>_form.html`
- `DeleteView` → `<app_label>/<model_name>_confirm_delete.html`
- `TemplateView` → uses explicit `template_name` (already handled)

**Implementation Notes:**
- Detect CBV inheritance (ListView, DetailView, etc.)
- Extract model name from `model` attribute or `queryset`
- Determine app label from file location or model
- Generate implicit template name based on CBV type
- Mark these as referenced templates

**Files to Modify:**
- `django_deadcode/analyzers/view_analyzer.py` - Add CBV default detection

### 3. Detect Template Name Variables

**Requirement:** Detect templates referenced through string variables containing 'template' in the variable name.

**Patterns to Detect:**

**A. Local Variables:**
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

**Implementation Notes:**
- Use AST analysis to find variable assignments with 'template' in the name
- Extract string constants assigned to these variables
- Handle both simple assignments and method returns
- Track context to associate with view class if applicable

**Files to Modify:**
- `django_deadcode/analyzers/view_analyzer.py` - Expand AST analysis

### 4. Enhanced Template Relationship Tracking

**Requirement:** Ensure `{% extends %}` and `{% include %}` relationships use normalized paths.

**Current State:**
- Already extracting `{% include %}` and `{% extends %}` tags
- Already doing transitive closure to find indirectly referenced templates
- **BUT:** May suffer from same path normalization issue

**Implementation Notes:**
- Apply same path normalization to included/extended template names
- Ensure transitive closure comparison works with normalized paths

**Files to Verify/Update:**
- `django_deadcode/analyzers/template_analyzer.py` - Verify pattern extraction
- `django_deadcode/management/commands/finddeadcode.py` - Verify transitive closure logic

## Out of Scope (For Now)

The following are explicitly **not** included in this fix to maintain focus:

1. **Dynamic template names** - e.g., `f'{app_name}/template.html'`, `template = var1 + var2`
2. **`get_template()` function calls** - Direct template loader usage
3. **`select_template()` function calls** - Conditional template loading
4. **Django admin auto-generated templates** - Covered by separate feature (Feature 10 in roadmap)
5. **Third-party package templates** - Will be addressed in confidence scoring (Feature 11)

These may be addressed in future enhancements.

## Success Criteria

1. **Path Matching Works:** Templates with explicit references (render, template_name attribute) are correctly matched and not flagged as unused
2. **CBV Defaults Detected:** Templates used by CBV implicit naming are recognized as referenced
3. **Template Variables Found:** Variables containing 'template' in the name are parsed and templates extracted
4. **Extends/Include Work:** Templates referenced through `{% extends %}` and `{% include %}` are correctly identified
5. **No False Positives:** The example false positives from collations app are correctly identified as used
6. **Django Template Loader Used:** Leverage Django's built-in template resolution rather than manual path manipulation

## Test Cases Required

1. **Path Normalization:**
   - Template at `/project/app/templates/app/base.html` referenced as `app/base.html` → should match

2. **CBV Defaults:**
   - `ListView` for `Collection` model in `collations` app → should detect `collations/collection_list.html`
   - `DetailView` for `Collection` model → should detect `collations/collection_detail.html`

3. **Template Variables:**
   - `template_name = 'app/foo.html'` → should detect reference
   - `get_template_names()` returning list → should detect references

4. **Template Relationships:**
   - Template extending `base.html` → `base.html` marked as used
   - Template including `partials/header.html` → `partials/header.html` marked as used

5. **End-to-End:**
   - Run on real Django project with known template usage
   - Verify zero false positives for correctly referenced templates

## Technical Approach

### Phase 1: Path Normalization
1. Add method to convert filesystem paths to Django template loader paths
2. Use `django.template.loaders.app_directories.Loader` logic as reference
3. Update `TemplateAnalyzer` to store normalized paths
4. Update comparison logic in `finddeadcode.py`

### Phase 2: Enhanced View Detection
1. Add CBV default template detection to `ViewAnalyzer`
2. Add template variable detection to AST parsing
3. Update tests to cover new detection patterns

### Phase 3: Integration & Testing
1. Ensure all path formats are consistent
2. Run against test projects
3. Verify false positive elimination

## Dependencies

- Django's template loading system (`django.template.loaders`)
- Python AST module (already in use)
- Existing analyzer infrastructure

## Risks & Considerations

1. **Django Version Compatibility:** Template loader behavior may vary across Django versions
2. **Complex Template Directories:** Projects with custom TEMPLATES settings may need special handling
3. **Performance:** Path normalization adds processing overhead - should be optimized
4. **App Label Detection:** Determining app label for CBV defaults may be non-trivial

## Related Features

- **Feature 10: Django Admin Detection** - Will reduce admin-related false positives
- **Feature 11: Confidence Scoring** - Will provide probabilistic assessment for edge cases
