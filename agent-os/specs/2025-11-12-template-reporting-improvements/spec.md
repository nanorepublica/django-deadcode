# Template Reporting Improvements

## Overview

Improve template dead code detection in django-deadcode to:
1. Exclude templates outside the project BASE_DIR
2. Mark templates referenced via include/extends as used
3. Handle symlinks properly in template paths

## Current Behavior

### Template Discovery
- Templates are discovered from `SETTINGS.TEMPLATES[].DIRS` and app template directories
- All templates with extensions `.html`, `.txt`, `.xml`, `.svg` are collected
- No filtering based on project boundaries

### Dead Template Detection
Currently, a template is marked as "potentially unused" if:
```python
all_templates - directly_referenced_templates = potentially_unused
```

Where `directly_referenced_templates` only includes templates referenced in view code via:
- `render(request, 'template.html')` calls
- `template_name = 'template.html'` attributes in class-based views

### Template Relationships
- `{% include 'template' %}` and `{% extends 'template' %}` are tracked but NOT used in dead code detection
- Template relationships are always reported in output

## Proposed Changes

### 1. BASE_DIR Filtering

**Requirement**: Exclude templates outside project BASE_DIR

**Implementation**:
- Get BASE_DIR from Django settings
- During template discovery, only include templates where `template_path.is_relative_to(BASE_DIR)`
- Templates outside BASE_DIR are completely ignored (not discovered)

**Rationale**: Templates from installed packages or system-wide templates aren't part of the project and shouldn't be analyzed for dead code

### 2. Include/Extends Detection

**Requirement**: Templates referenced via include/extends should be marked as used

**Current State**:
- `TemplateAnalyzer.template_includes`: Dict mapping template → list of included templates
- `TemplateAnalyzer.template_extends`: Dict mapping template → extended template
- These are tracked but not used in dead code calculation

**Implementation**:
```python
# Step 1: Find all templates referenced by views
directly_referenced = set(view_analyzer.template_usage.keys())

# Step 2: Recursively find templates referenced via include/extends
transitively_referenced = set()
to_process = list(directly_referenced)

while to_process:
    current = to_process.pop()

    # Add included templates
    if current in template_analyzer.template_includes:
        for included in template_analyzer.template_includes[current]:
            if included not in transitively_referenced:
                transitively_referenced.add(included)
                to_process.append(included)

    # Add extended templates
    if current in template_analyzer.template_extends:
        extended = template_analyzer.template_extends[current]
        if extended not in transitively_referenced:
            transitively_referenced.add(extended)
            to_process.append(extended)

# Step 3: All referenced templates (direct + transitive)
all_referenced = directly_referenced | transitively_referenced

# Step 4: Unused templates
potentially_unused = all_templates - all_referenced
```

**Edge Cases**:
1. **Template extends template outside project**: If `child.html` extends `base.html` from an installed package (outside BASE_DIR):
   - `child.html` can still be reported as unused if not referenced
   - The external `base.html` is never discovered (due to BASE_DIR filtering)

2. **Both templates in project**: If both `child.html` and `base.html` are in project:
   - If `child.html` is referenced by a view → both are marked as used
   - If neither is referenced by any view → both are reported as unused

3. **Templates that are only included/extended**: These templates are now marked as used if any template in the reference chain is used by a view

### 3. Template Relationship Reporting

**Requirement**: Don't report includes/extends by default

**Implementation**:
- Add optional flag `--show-template-relationships` (default: False)
- Only include template relationships section in output when flag is enabled
- Applies to all output formats (console, JSON, markdown)

### 4. Symlink Handling

**Requirement**: Report the symlink path, not the resolved target

**Implementation**:
- Use `Path.resolve()` sparingly - only when needed for comparison
- Store and report the original symlink path as discovered
- When checking if path is relative to BASE_DIR, resolve both for comparison but keep original path

Example:
```python
# During discovery
original_path = Path("/path/to/template.html")  # might be symlink
resolved_path = original_path.resolve()

# Check if in project
if resolved_path.is_relative_to(BASE_DIR.resolve()):
    # Store the original path
    templates[str(original_path)] = TemplateInfo(...)
```

## Implementation Plan

### Phase 1: BASE_DIR Filtering
1. Add BASE_DIR retrieval from Django settings
2. Filter templates during discovery in `find_all_templates()`
3. Add tests for templates inside/outside BASE_DIR

### Phase 2: Include/Extends Detection
1. Implement recursive transitive closure algorithm
2. Update dead code detection logic in `finddeadcode.py`
3. Add tests for various include/extends scenarios

### Phase 3: Optional Relationship Reporting
1. Add `--show-template-relationships` CLI flag
2. Update all reporters (console, JSON, markdown) to respect flag
3. Update tests to verify flag behavior

### Phase 4: Symlink Handling
1. Preserve original paths during template discovery
2. Use resolved paths only for BASE_DIR comparison
3. Add tests with symlinked templates

## Testing Requirements

### Unit Tests
- Template discovery with/without BASE_DIR filtering
- Recursive include/extends detection
- Symlink path preservation
- CLI flag parsing

### Integration Tests
- Full workflow with mixed templates (in/out of project)
- Complex template inheritance chains
- Circular include detection (edge case)
- Symlinked template directories

## Backwards Compatibility

**Breaking Changes**: None
- New behavior is more accurate (fewer false positives)
- CLI flags are additive (opt-in for relationship reporting)
- Output format remains the same (just fewer unused templates reported)

**Migration**: None required

## Configuration

No new Django settings required. Uses existing:
- `settings.BASE_DIR`: Project root directory
- `settings.TEMPLATES`: Template directory configuration

CLI flags:
- `--show-template-relationships`: Show template include/extends relationships (default: False)

## Documentation Updates

1. README.md: Document new BASE_DIR filtering behavior
2. README.md: Document `--show-template-relationships` flag
3. CHANGELOG.md: Add entry for improved template detection
