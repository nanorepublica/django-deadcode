# Tasks: Template Reporting Improvements

## Phase 1: BASE_DIR Filtering

### Task 1.1: Add BASE_DIR Retrieval
**File**: `django_deadcode/management/commands/finddeadcode.py`

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
- Test with project that has BASE_DIR
- Test with project missing BASE_DIR (should raise CommandError)

### Task 1.2: Filter Templates by BASE_DIR
**File**: `django_deadcode/analyzers/template_analyzer.py`

**Changes**:
1. Update `__init__` to accept `base_dir` parameter:
```python
def __init__(self, template_dirs: List[Path], base_dir: Optional[Path] = None):
    self.template_dirs = template_dirs
    self.base_dir = base_dir.resolve() if base_dir else None
    # ... rest of init
```

2. Update `find_all_templates()` to filter by BASE_DIR:
```python
def find_all_templates(self) -> None:
    """Find all template files in template directories."""
    for template_dir in self.template_dirs:
        for ext in self.template_extensions:
            for template_path in template_dir.rglob(f"*{ext}"):
                # Filter by BASE_DIR if provided
                if self.base_dir:
                    try:
                        # Use resolved path for comparison
                        resolved = template_path.resolve()
                        if not self._is_relative_to(resolved, self.base_dir):
                            continue
                    except (ValueError, OSError):
                        # Skip templates that can't be resolved
                        continue

                # Store original path (not resolved)
                self.templates[str(template_path)] = TemplateInfo(template_path)
```

3. Add helper method for compatibility with Python < 3.9:
```python
def _is_relative_to(self, path: Path, parent: Path) -> bool:
    """Check if path is relative to parent (compatible with Python 3.8+)."""
    try:
        path.relative_to(parent)
        return True
    except ValueError:
        return False
```

**Testing**:
- Test with templates inside BASE_DIR (should be included)
- Test with templates outside BASE_DIR (should be excluded)
- Test with symlinked templates (should use resolved path for check but keep original)

### Task 1.3: Update Command to Pass BASE_DIR
**File**: `django_deadcode/management/commands/finddeadcode.py`

**Changes**:
1. Get BASE_DIR in `handle()` method
2. Pass to TemplateAnalyzer:
```python
base_dir = self._get_base_dir()
template_analyzer = TemplateAnalyzer(template_dirs, base_dir=base_dir)
```

**Testing**:
- Integration test: full command run with templates in/out of BASE_DIR

---

## Phase 2: Include/Extends Detection

### Task 2.1: Implement Transitive Closure Algorithm
**File**: `django_deadcode/management/commands/finddeadcode.py`

**Changes**:
1. Add new method after `handle()`:
```python
def _find_transitively_referenced_templates(
    self,
    directly_referenced: Set[str],
    template_includes: Dict[str, List[str]],
    template_extends: Dict[str, str]
) -> Set[str]:
    """
    Find all templates transitively referenced through include/extends.

    Args:
        directly_referenced: Templates directly referenced by views
        template_includes: Map of template -> list of included templates
        template_extends: Map of template -> extended template

    Returns:
        Set of all transitively referenced templates
    """
    transitively_referenced = set()
    to_process = list(directly_referenced)
    processed = set()

    while to_process:
        current = to_process.pop()

        # Skip if already processed to avoid infinite loops
        if current in processed:
            continue
        processed.add(current)

        # Add included templates
        if current in template_includes:
            for included in template_includes[current]:
                if included not in transitively_referenced:
                    transitively_referenced.add(included)
                    to_process.append(included)

        # Add extended template
        if current in template_extends:
            extended = template_extends[current]
            if extended not in transitively_referenced:
                transitively_referenced.add(extended)
                to_process.append(extended)

    return transitively_referenced
```

**Testing**:
- Test simple chain: view → template1 → includes template2
- Test extends: view → child → extends base
- Test complex: view → template1 → includes template2, extends base
- Test circular reference: template1 includes template2, template2 includes template1

### Task 2.2: Update Dead Code Detection Logic
**File**: `django_deadcode/management/commands/finddeadcode.py`

**Changes**:
Update the logic in `handle()` around lines 187-193:
```python
# Find all templates
all_templates = set(template_analyzer.templates.keys())

# Find directly referenced templates (from views)
directly_referenced_templates = set(view_analyzer.template_usage.keys())

# Find transitively referenced templates (via include/extends)
transitively_referenced = self._find_transitively_referenced_templates(
    directly_referenced_templates,
    template_analyzer.template_includes,
    template_analyzer.template_extends
)

# All referenced templates
all_referenced = directly_referenced_templates | transitively_referenced

# Potentially unused templates
potentially_unused_templates = all_templates - all_referenced
```

**Testing**:
- Integration test: templates only used via includes are not reported as unused
- Integration test: base templates only used via extends are not reported as unused

---

## Phase 3: Optional Relationship Reporting

### Task 3.1: Add CLI Flag
**File**: `django_deadcode/management/commands/finddeadcode.py`

**Changes**:
1. Add argument in `add_arguments()` method:
```python
def add_arguments(self, parser):
    # ... existing arguments ...
    parser.add_argument(
        '--show-template-relationships',
        action='store_true',
        default=False,
        help='Show template include/extends relationships in output'
    )
```

2. Store flag value in `handle()`:
```python
show_relationships = options['show_template_relationships']
```

**Testing**:
- Test flag parsing: command with/without flag

### Task 3.2: Update Reporter Base Class
**File**: `django_deadcode/reporters/base.py`

**Changes**:
1. Add parameter to reporter `__init__`:
```python
def __init__(self, show_template_relationships: bool = False):
    self.show_template_relationships = show_template_relationships
```

2. Update each `generate()` method signature to include the parameter

**Testing**:
- Unit test: verify flag is stored correctly

### Task 3.3: Update Console Reporter
**File**: `django_deadcode/reporters/console_reporter.py`

**Changes**:
Update `generate()` method to conditionally show relationships:
```python
def generate(
    self,
    # ... existing params ...
) -> str:
    # ... existing output generation ...

    # Only show relationships if flag is enabled
    if self.show_template_relationships and (template_includes or template_extends):
        output.append(Fore.CYAN + "\nTemplate Relationships:" + Style.RESET_ALL)
        # ... existing relationship output ...
```

**Testing**:
- Test with flag=True: relationships shown
- Test with flag=False: relationships not shown

### Task 3.4: Update JSON Reporter
**File**: `django_deadcode/reporters/json_reporter.py`

**Changes**:
Update `generate()` method to conditionally include relationships:
```python
def generate(
    self,
    # ... existing params ...
) -> str:
    result = {
        # ... existing fields ...
    }

    # Only include relationships if flag is enabled
    if self.show_template_relationships:
        result["template_relationships"] = {
            "includes": template_includes,
            "extends": template_extends
        }

    return json.dumps(result, indent=2, default=str)
```

**Testing**:
- Test with flag=True: JSON includes template_relationships
- Test with flag=False: JSON excludes template_relationships

### Task 3.5: Update Markdown Reporter
**File**: `django_deadcode/reporters/markdown_reporter.py`

**Changes**:
Update `generate()` method to conditionally show relationships:
```python
def generate(
    self,
    # ... existing params ...
) -> str:
    # ... existing output generation ...

    # Only show relationships if flag is enabled
    if self.show_template_relationships and (template_includes or template_extends):
        output.append("\n## Template Relationships\n")
        # ... existing relationship output ...
```

**Testing**:
- Test with flag=True: markdown includes relationships section
- Test with flag=False: markdown excludes relationships section

### Task 3.6: Update Command to Pass Flag to Reporters
**File**: `django_deadcode/management/commands/finddeadcode.py`

**Changes**:
Update reporter instantiation in `handle()`:
```python
show_relationships = options['show_template_relationships']

if output_format == "console":
    reporter = ConsoleReporter(show_template_relationships=show_relationships)
elif output_format == "json":
    reporter = JSONReporter(show_template_relationships=show_relationships)
elif output_format == "markdown":
    reporter = MarkdownReporter(show_template_relationships=show_relationships)
```

**Testing**:
- Integration test: full command with --show-template-relationships

---

## Phase 4: Testing & Documentation

### Task 4.1: Add Unit Tests
**File**: `tests/test_template_analyzer.py` (new/existing)

**Test Cases**:
1. `test_base_dir_filtering_includes_templates_inside()`
2. `test_base_dir_filtering_excludes_templates_outside()`
3. `test_symlink_preserves_original_path()`
4. `test_transitive_includes_detection()`
5. `test_transitive_extends_detection()`
6. `test_circular_include_detection()`
7. `test_complex_template_chain()`

### Task 4.2: Add Integration Tests
**File**: `tests/test_integration.py` (new/existing)

**Test Cases**:
1. `test_full_workflow_with_base_dir_filtering()`
2. `test_templates_used_via_includes_not_reported_as_unused()`
3. `test_show_template_relationships_flag()`
4. `test_hide_template_relationships_by_default()`

### Task 4.3: Update Documentation
**Files**:
- `README.md`: Add section on BASE_DIR filtering and --show-template-relationships flag
- `CHANGELOG.md`: Add entry for this feature

**Content**:
```markdown
## Template Detection Improvements

### BASE_DIR Filtering
Django-deadcode now only analyzes templates within your project's `BASE_DIR`.
Templates from installed packages are automatically excluded.

### Include/Extends Detection
Templates referenced via `{% include %}` or `{% extends %}` are now correctly
marked as used, even if not directly referenced by views.

### Optional Relationship Reporting
Use `--show-template-relationships` to see template include/extends relationships:

    python manage.py finddeadcode --show-template-relationships

By default, relationships are not shown in the output.
```

---

## Acceptance Criteria

### Phase 1: BASE_DIR Filtering
- [ ] Templates outside BASE_DIR are not discovered
- [ ] Templates inside BASE_DIR are discovered normally
- [ ] Symlinks are handled correctly (resolved for comparison, original path stored)
- [ ] Tests pass for all BASE_DIR scenarios

### Phase 2: Include/Extends Detection
- [ ] Templates used via `{% include %}` are marked as used
- [ ] Templates used via `{% extends %}` are marked as used
- [ ] Transitive references work (template1 → template2 → template3)
- [ ] Circular references don't cause infinite loops
- [ ] Tests pass for all include/extends scenarios

### Phase 3: Optional Relationship Reporting
- [ ] `--show-template-relationships` flag is available
- [ ] Flag=True shows relationships in all output formats
- [ ] Flag=False (default) hides relationships in all output formats
- [ ] Tests pass for all reporter scenarios

### Phase 4: Testing & Documentation
- [ ] All unit tests pass
- [ ] All integration tests pass
- [ ] README.md updated with new behavior
- [ ] CHANGELOG.md updated

---

## Risk Assessment

### Low Risk
- BASE_DIR filtering: Simply excludes templates during discovery
- CLI flag: Additive feature, no impact on existing behavior

### Medium Risk
- Include/extends detection: Changes core logic for determining unused templates
  - Mitigation: Extensive testing with various template chains
  - Mitigation: Keep old logic commented for comparison during testing

### Edge Cases to Test
1. Circular includes: A includes B, B includes A
2. Missing templates: A includes B, but B doesn't exist
3. Symlinked template directories
4. Template names with special characters
5. Very deep inheritance chains (10+ levels)

---

## Development Notes

### Python Version Compatibility
- Target: Python 3.8+
- Use `try/except ValueError` for `is_relative_to` equivalent (Python 3.9+ has native support)

### Performance Considerations
- Transitive closure algorithm is O(N) where N = number of templates
- Should be negligible for typical Django projects (<1000 templates)

### Backwards Compatibility
- No breaking changes
- Output format unchanged (just fewer false positives)
- All existing tests should continue to pass
