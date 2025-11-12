# Specification: Reverse/Redirect Detection

## Goal
Implement Python AST analysis to detect `reverse()` and `redirect()` calls in view code, capturing programmatic URL references to reduce false positives in dead code detection.

## User Stories
- As a Django developer, I want django-deadcode to detect URL references in my Python code (not just templates) so that it doesn't incorrectly flag actively-used URLs as dead code
- As a developer using programmatic redirects, I want `reverse()` and `redirect()` calls to be recognized so my URL patterns aren't incorrectly reported as unreferenced
- As a project maintainer, I want to be notified about dynamic URL name patterns (like f-strings) so I can manually verify those references

## Core Requirements

### Functional Requirements
- Scan all Python files in the project (excluding migrations, __pycache__, and third-party packages)
- Detect the following patterns using AST parsing:
  - `reverse('url-name')`
  - `reverse_lazy('url-name')`
  - `redirect('url-name')`
  - `HttpResponseRedirect(reverse('url-name'))`
- Mark detected URL names as "referenced" to prevent false positives
- Detect dynamic URL name patterns (f-strings, concatenated strings) and flag them for manual investigation
- Exclude detected URLs from the "unreferenced URLs" list in analysis reports
- Track only that a URL is referenced (not where/how many times)

### Non-Functional Requirements
- Follow existing analyzer architecture patterns
- Reuse common AST parsing logic
- Handle malformed Python files gracefully (skip without crashing)
- Maintain performance similar to existing analyzers
- Integrate seamlessly with existing dead code detection workflow

## Visual Design
Not applicable - this is a backend analysis feature with no UI changes.

## Reusable Components

### Existing Code to Leverage

**ViewAnalyzer AST Patterns** (`django_deadcode/analyzers/view_analyzer.py`):
- File scanning: `Path.rglob("*.py")` to find Python files
- Skip patterns: migrations, __pycache__
- AST parsing: `ast.parse()` with error handling for IOError, SyntaxError, UnicodeDecodeError
- Tree traversal: `ast.walk(tree)` to visit all nodes
- Node matching: `isinstance(node, ast.Call)` pattern
- String extraction: `isinstance(node.args[N], ast.Constant)` with value checking

**Analyzer Architecture** (all analyzers):
- Initialize instance variables in `__init__`
- Provide `analyze_*` methods for processing
- Store results in Set/Dict structures
- Provide `get_*` query methods for retrieving data
- Example: `get_referenced_urls()` returns Set[str] in TemplateAnalyzer

**Integration Pattern** (`finddeadcode.py`):
- Initialize analyzer in command's `handle()` method
- Call analyzer's main method with appropriate paths/config
- Collect referenced URLs using `get_referenced_urls()`
- Combine with other analyzers' results in `_compile_analysis_data()`
- Pass combined referenced URLs to `url_analyzer.get_unreferenced_urls(referenced_urls)`

**Testing Patterns** (`tests/test_view_analyzer.py`):
- Use `tempfile.NamedTemporaryFile` for test files
- Test AST parsing with code snippets as strings
- Test query methods with manually added data
- Clean up temp files in try/finally blocks

### New Components Required

**ReverseAnalyzer Class** - New analyzer needed because:
- Focuses on different AST patterns (reverse/redirect calls vs template references)
- Different detection logic (function calls vs attribute assignments)
- Separate concern from ViewAnalyzer (which detects template usage)
- Allows independent evolution of each analyzer

**Dynamic URL Detection** - New capability needed for:
- Identifying f-strings: `f'namespace:{action}_list'`
- Identifying concatenated strings: `'prefix_' + suffix`
- Flagging these for manual review (can't be automatically verified)

**AST Utility Module** (optional, for refactoring) - Could extract:
- Common AST parsing setup/error handling
- File filtering logic (migrations, __pycache__)
- Shared between ViewAnalyzer and ReverseAnalyzer

## Technical Approach

### Architecture

Create `ReverseAnalyzer` class following the established analyzer pattern:
- Location: `django_deadcode/analyzers/reverse_analyzer.py`
- Import in: `django_deadcode/analyzers/__init__.py`
- Integrate in: `django_deadcode/management/commands/finddeadcode.py`

### AST Parsing Strategy

**Node Traversal:**
1. Parse Python file with `ast.parse(content, filename=str(file_path))`
2. Walk all nodes with `ast.walk(tree)`
3. Filter for `ast.Call` nodes
4. Match function names against target patterns

**Pattern Detection:**
```
reverse('url-name')          → ast.Call with func.id == 'reverse'
reverse_lazy('url-name')     → ast.Call with func.id == 'reverse_lazy'
redirect('url-name')         → ast.Call with func.id == 'redirect'
HttpResponseRedirect(reverse(...)) → nested ast.Call inspection
```

**String Extraction:**
- Static strings: `ast.Constant` nodes with string value
- F-strings: `ast.JoinedStr` nodes (mark as dynamic)
- Concatenation: `ast.BinOp` with `ast.Add` operator (mark as dynamic)

**Edge Cases to Ignore:**
- Method calls like `self.reverse()` - check that func is `ast.Name`, not `ast.Attribute`
- Calls in comments - AST parsing automatically excludes comments
- String literals containing "reverse()" - not ast.Call nodes

### Data Structures

```python
# Instance variables
self.referenced_urls: Set[str]          # URLs found in code
self.dynamic_patterns: Set[str]         # Dynamic URL references (for logging/warning)
self.url_sources: Dict[str, List[str]]  # Optional: track source files (not required for v0.2.0)
```

### Integration Points

**In `finddeadcode.py`:**
1. Initialize `ReverseAnalyzer()` alongside other analyzers
2. Call `reverse_analyzer.analyze_all_python_files(app_dir)` in the app loop
3. Get referenced URLs with `reverse_analyzer.get_referenced_urls()`
4. Combine with template references: `referenced_urls = template_refs | reverse_refs`
5. Pass combined set to `url_analyzer.get_unreferenced_urls(referenced_urls)`

### File Filtering

**Include:**
- All `.py` files in project directories
- Views, forms, models, utilities, etc.

**Exclude:**
- Migration files: `"migrations"` in file path
- Pycache: `"__pycache__"` in file path
- Third-party code: files outside analyzed app directories (handled by existing app filtering)
- JavaScript files: not scanned (only .py files)

## Implementation Details

### ReverseAnalyzer Public API

```python
class ReverseAnalyzer:
    def __init__(self) -> None
    def analyze_python_file(self, file_path: Path) -> None
    def analyze_all_python_files(self, base_path: Path) -> None
    def get_referenced_urls(self) -> Set[str]
    def get_dynamic_patterns(self) -> Set[str]
```

### AST Node Patterns to Match

**Direct reverse() call:**
```python
ast.Call(
    func=ast.Name(id='reverse'),
    args=[ast.Constant(value='url-name')]
)
```

**Nested HttpResponseRedirect(reverse()):**
```python
ast.Call(
    func=ast.Name(id='HttpResponseRedirect'),
    args=[
        ast.Call(
            func=ast.Name(id='reverse'),
            args=[ast.Constant(value='url-name')]
        )
    ]
)
```

**Dynamic f-string (detect but don't extract):**
```python
ast.Call(
    func=ast.Name(id='reverse'),
    args=[ast.JoinedStr(...)]  # f-string
)
```

### Error Handling

Follow ViewAnalyzer pattern:
```python
try:
    content = file_path.read_text(encoding="utf-8")
    tree = ast.parse(content, filename=str(file_path))
    self._process_ast(tree, str(file_path))
except (IOError, SyntaxError, UnicodeDecodeError):
    # Skip files that can't be parsed - don't crash, don't log
    pass
```

### Dynamic Pattern Handling

When detecting dynamic URL patterns:
1. Identify the pattern type (f-string, concatenation, variable)
2. Add a placeholder to `self.dynamic_patterns` for reporting
3. Log at WARNING level during analysis: "Found dynamic URL pattern, may need manual review"
4. Do NOT add to `referenced_urls` (can't verify against actual URL names)
5. Report in final output for manual investigation

## Testing Strategy

### Unit Tests

**File: `tests/test_reverse_analyzer.py`**

Test cases to implement:
1. **test_detect_reverse_call** - Basic `reverse('url-name')`
2. **test_detect_reverse_lazy_call** - `reverse_lazy('url-name')`
3. **test_detect_redirect_call** - `redirect('url-name')`
4. **test_detect_http_response_redirect** - `HttpResponseRedirect(reverse('url-name'))`
5. **test_detect_multiple_patterns** - Multiple calls in same file
6. **test_ignore_method_calls** - `self.reverse()` should be ignored
7. **test_detect_dynamic_fstring** - Detect but flag f-string patterns
8. **test_detect_dynamic_concatenation** - Detect but flag concatenated strings
9. **test_skip_malformed_file** - Handle SyntaxError gracefully
10. **test_get_referenced_urls** - Verify correct URL set returned
11. **test_namespace_urls** - `reverse('namespace:url-name')`
12. **test_skip_migration_files** - Migration files excluded from analysis
13. **test_multiple_files_analysis** - Scan multiple files, accumulate results

Use tempfile pattern from ViewAnalyzer tests:
```python
with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
    f.write(code_snippet)
    f.flush()
    temp_path = Path(f.name)
```

### Integration Tests

**File: `tests/test_integration_reverse_detection.py`**

Test the full pipeline:
1. **test_reverse_refs_prevent_false_positives** - Create URL pattern, reference with reverse(), verify not in unreferenced list
2. **test_combined_template_and_reverse_refs** - Some URLs in templates, some in reverse() calls, verify both are excluded
3. **test_finddeadcode_command_integration** - Run full command, verify ReverseAnalyzer is invoked

### Edge Cases to Test

1. **Comments with reverse()** - Should be ignored (AST excludes comments)
2. **String literals** - `my_string = "reverse('url')"` should be ignored
3. **Keyword arguments** - `reverse(viewname='url-name')` should be detected
4. **Multiple arguments** - `reverse('url-name', args=[1, 2])` should detect 'url-name'
5. **Variable references** - `reverse(url_var)` should be flagged as dynamic
6. **Imported functions** - `from django.urls import reverse` (works automatically)
7. **Empty files** - Should handle gracefully

## Acceptance Criteria

### Feature Complete When:
- [ ] ReverseAnalyzer class implemented with all public methods
- [ ] AST parsing detects all four required patterns (reverse, reverse_lazy, redirect, HttpResponseRedirect)
- [ ] Dynamic URL patterns are detected and flagged (not added to referenced set)
- [ ] Migration files and __pycache__ are excluded from analysis
- [ ] ReverseAnalyzer integrated into finddeadcode command
- [ ] Referenced URLs from ReverseAnalyzer combined with template references
- [ ] All unit tests passing (minimum 13 test cases)
- [ ] Integration test confirms false positives are reduced
- [ ] No performance degradation (analysis time increase < 20%)

### Quality Criteria:
- [ ] Code follows existing analyzer patterns
- [ ] Error handling matches ViewAnalyzer approach
- [ ] No crashes on malformed Python files
- [ ] Type hints on all public methods
- [ ] Docstrings on all public methods
- [ ] Common AST logic extracted if duplication exists (optional but recommended)

### Documentation:
- [ ] Docstrings explain AST node patterns
- [ ] Comment explaining why method calls (self.reverse) are ignored
- [ ] README updated with ReverseAnalyzer in feature list (if project has feature list)

## Out of Scope

The following are explicitly excluded from v0.2.0:

### Excluded Functions
- `resolve_url()` function detection
- Custom wrapper functions around reverse/redirect
- Any Django shortcuts not in the core four patterns

### Excluded File Types
- JavaScript files with reverse() calls
- Third-party package code (external libraries)
- Migration files
- Test files (though they can be analyzed if in app dirs)

### Excluded Edge Cases
- Comments containing "reverse()"
- String literals containing "reverse()"
- Non-Django methods named `reverse()` (e.g., `self.reverse()`, `list.reverse()`)

### Excluded Tracking Features
- Detailed tracking of WHERE reverse/redirect is called (file, line number)
- HOW MANY times each URL is referenced
- Call graph analysis
- Which view/function contains the reference
- These could be added in future versions if needed

### Excluded Runtime Analysis
- Dynamic URL name construction at runtime
- URL patterns loaded from database
- URL patterns from Django apps not in settings.INSTALLED_APPS
- Computed URL names based on user input

## Future Enhancements

Features that could be added in later versions:

### v0.3.0 Candidates:
- Support for `resolve_url()` function
- Detection of custom wrapper functions (configurable patterns)
- Confidence scoring for dynamic patterns
- File/line number tracking for each reference

### Later Versions:
- Configuration file to specify additional patterns to detect
- Machine learning to identify likely URL name patterns in f-strings
- Integration with code coverage to prioritize URL references
- Visual report showing URL reference sources (templates vs Python vs other)

## Success Criteria

### Measurable Outcomes:
1. **False Positive Reduction**: Projects with programmatic redirects should see significant reduction in unreferenced URL reports
2. **Performance**: Analysis time should increase by no more than 20% (AST parsing is fast)
3. **Reliability**: Zero crashes on production Django codebases
4. **Coverage**: Detect 100% of static reverse/redirect calls in test scenarios

### User Experience Goals:
- Developers using reverse() no longer see false positives
- Dynamic patterns are clearly flagged with actionable warnings
- Analysis remains fast enough for CI/CD integration
- Output clearly distinguishes template refs from Python refs (optional, future enhancement)
