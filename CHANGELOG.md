# CHANGELOG

## v0.3.0 (2025-11-13)

### Feature

* feat: improved template reporting ([`c7b9c87`](https://github.com/nanorepublica/django-deadcode/commit/c7b9c87c6ab3db0af9cc0a7aa01c00d5c8d1003d))

* feat: implement template reporting improvements with BASE_DIR filtering and transitive detection

Implemented comprehensive template analysis improvements to reduce false
positives and false negatives in dead code detection.

## Phase 1: BASE_DIR Filtering
- Added BASE_DIR retrieval from Django settings with error handling
- Updated TemplateAnalyzer to filter templates by BASE_DIR
- Implemented Python 3.8+ compatible path comparison helper
- Proper symlink handling (resolved for comparison, original path stored)

## Phase 2: Include/Extends Detection
- Implemented transitive closure algorithm for template relationship detection
- Templates referenced via {% include %} or {% extends %} now marked as used
- BFS-style algorithm with circular reference prevention
- Updated dead code detection to use transitive + direct references

## Phase 3: Optional Relationship Reporting
- Added --show-template-relationships CLI flag (default: False)
- Updated all reporters (Console, JSON, Markdown) to respect flag
- Conditionally show/hide template relationship information
- Backward compatible with existing output format

## Phase 4: Testing &amp; Documentation
- Added 29 new tests (12 unit, 11 integration, 6 reporter)
- All 62 tests passing with 93% code coverage
- Comprehensive edge case testing (circular refs, deep chains, symlinks)
- Updated README.md with usage examples and feature documentation
- Updated CHANGELOG.md with comprehensive entry

## Files Changed
Core Implementation:
- django_deadcode/analyzers/template_analyzer.py
- django_deadcode/management/commands/finddeadcode.py
- django_deadcode/reporters/base.py

Tests:
- tests/test_template_analyzer.py
- tests/test_command_integration.py (new)
- tests/test_reporters.py
- tests/settings.py

Documentation:
- README.md
- CHANGELOG.md
- agent-os/specs/2025-11-12-template-reporting-improvements/tasks.md
- agent-os/specs/2025-11-12-template-reporting-improvements/verifications/

## Test Results
- 62/62 tests passing (100%)
- 93% code coverage
- No regressions detected
- All acceptance criteria met

## Backward Compatibility
No breaking changes. All existing functionality preserved.
- New CLI flag is optional with sensible defaults
- Output format unchanged (just fewer false positives)
- All existing tests continue to pass ([`62f2bc1`](https://github.com/nanorepublica/django-deadcode/commit/62f2bc186f6c68baa90b115662021ea1495c71bb))

* feat: add detailed spec and tasks for template reporting improvements

Created comprehensive specification and task breakdown for improving
template dead code detection:

- BASE_DIR filtering to exclude external templates
- Include/extends detection for transitive template references
- Optional relationship reporting with CLI flag
- Symlink handling improvements

Spec includes:
- Current vs proposed behavior analysis
- Implementation details with code examples
- Testing requirements and edge cases
- Backwards compatibility considerations

Tasks organized into 4 phases:
1. BASE_DIR filtering implementation
2. Include/extends transitive detection
3. Optional relationship reporting
4. Testing and documentation

Based on codebase exploration of django_deadcode analyzers and
user clarifications on requirements. ([`2bbc2dc`](https://github.com/nanorepublica/django-deadcode/commit/2bbc2dc3ced0c005ee6cefa19c09e64c8837b856))

* feat: initialize spec for template reporting improvements

Initialize spec folder for improving template reporting in django-deadcode:
- Exclude templates outside project BASE_DIR
- Detect template references via include/extends statements
- Make template relationship reporting optional ([`c7aca72`](https://github.com/nanorepublica/django-deadcode/commit/c7aca723f43cec26b82d933baccb17cac6c5c08d))

### Fix

* fix: resolve ruff linting errors

Fixed all ruff linting issues:
- Replaced deprecated typing.Dict/List/Set with dict/list/set
- Converted Optional[X] to X | None syntax
- Removed unused imports
- Fixed line length violations (max 88 chars)

Changes:
- django_deadcode/analyzers/template_analyzer.py: Updated type hints
- django_deadcode/management/commands/finddeadcode.py: Updated type hints
- django_deadcode/reporters/base.py: Fixed long docstring line
- tests/test_template_analyzer.py: Fixed long comment line

All 62 tests still passing with 93% coverage. ([`3562f3c`](https://github.com/nanorepublica/django-deadcode/commit/3562f3c48fb96797d1a455abd096f66314275048))

## v0.1.0 (2025-11-12)

### Chore

* chore(release): 0.1.0 ([`85994ed`](https://github.com/nanorepublica/django-deadcode/commit/85994ed0fbdfcb53d0a3a1ee11bd87d1d30e059e))

### Feature

* feat: initial pypi release ([`2ba680e`](https://github.com/nanorepublica/django-deadcode/commit/2ba680ebe0438c3deab5538cb3ce74ed8e1f54fa))

* feat: initial pypi release ([`30d1060`](https://github.com/nanorepublica/django-deadcode/commit/30d10605fa9fb99a68d25631612797c369387830))

* feat: initial release to pypi ([`75317f4`](https://github.com/nanorepublica/django-deadcode/commit/75317f4a8c62bb6a351b8027d65cf2726ba3d21f))

* feat: initial release to pypi ([`6370466`](https://github.com/nanorepublica/django-deadcode/commit/637046606f1f4a2cd31c4aef73ea4d222b6caa86))

* feat: Initial Release to PyPI ([`02755d6`](https://github.com/nanorepublica/django-deadcode/commit/02755d6a7a9a2f06b980fc770804cb340eba4686))

* feat: add enhanced CI/CD with semantic release and multi-OS testing

- Add Python Semantic Release for automated versioning
- Add pre-commit hooks with ruff for code quality
- Add commitlint for conventional commit validation
- Add multi-OS testing (Ubuntu, Windows, macOS)
- Add build provenance attestation for supply chain security
- Remove separate publish.yml workflow (integrated into ci.yml) ([`ee34ec2`](https://github.com/nanorepublica/django-deadcode/commit/ee34ec26f55aa0ef075c47f516aa6abe90336add))

### Fix

* fix: resolve semantic-release build failure by using pre-built artifacts

The release job was failing because python-semantic-release tried to run
&#39;python -m build&#39; but the build package wasn&#39;t installed in its container.

This fix:
- Downloads the already-built artifacts from the build job
- Sets build_command to empty string in semantic-release config
- Avoids duplicate builds and uses tested artifacts
- More efficient workflow execution

Fixes the error: &#34;/usr/local/bin/python: No module named build&#34; ([`064f467`](https://github.com/nanorepublica/django-deadcode/commit/064f46797ccfbb6366f4d31ba078b44a2bab4bf2))

* fix: resolve all ruff linting errors

- Add missing reverse_analyzer parameter to _compile_analysis_data
- Update type hints: Set -&gt; set, IOError -&gt; OSError
- Fix line length violations (split long lines)
- Remove unused imports in test files ([`6bb93d3`](https://github.com/nanorepublica/django-deadcode/commit/6bb93d32a14011888cd5e75638ce08afea52885b))

### Style

* style: apply ruff-format auto-formatting

- Reformat code with ruff-format for consistency
- Consolidate single-line statements that fit within line length
- Applied to 6 files via pre-commit hooks ([`99b68ab`](https://github.com/nanorepublica/django-deadcode/commit/99b68abf38a7abc45accd6877e3bf3338cf2a552))

### Unknown

* Merge pull request #10 from nanorepublica/claude/debug-release-issues-011CV4b9WzRBWRgXE6zvvtux

feat: debug and identify release issues ([`dc88b8d`](https://github.com/nanorepublica/django-deadcode/commit/dc88b8d1337d8cfdeb7584e34c5f2fa98301e3b0))

* Release: 0.2.1 ([`f59ca79`](https://github.com/nanorepublica/django-deadcode/commit/f59ca796f2bd5d2a959e8d09364443d146a1c2a3))

* Release: 0.2.0 ([`a23a274`](https://github.com/nanorepublica/django-deadcode/commit/a23a27484c8669c4482fa6fd7abc329d31a4e937))

* Merge pull request #4 from nanorepublica/claude/cicd-github-actions-011CV2ofdGATxikzCT7taJ3w

Add GitHub Actions for CI/CD and PyPI publishing ([`c80007f`](https://github.com/nanorepublica/django-deadcode/commit/c80007f33467c76e5ffaaa748d50bc25393427b6))

* Merge branch &#39;claude/cicd-github-actions-011CV2ofdGATxikzCT7taJ3w&#39; of http://127.0.0.1:57967/git/nanorepublica/django-deadcode into claude/cicd-github-actions-011CV2ofdGATxikzCT7taJ3w ([`cb2e384`](https://github.com/nanorepublica/django-deadcode/commit/cb2e38413da80dbba2036c4d802f2652f317704d))

* Merge branch &#39;main&#39; into claude/cicd-github-actions-011CV2ofdGATxikzCT7taJ3w ([`7117dfc`](https://github.com/nanorepublica/django-deadcode/commit/7117dfce628e757082dea55fecfab1ea27eeb74b))

* Merge pull request #3 from nanorepublica/claude/feature-reverse-redirect-detection-011CV2ofdGATxikzCT7taJ3w

0.2.0 - URL reverse/redirect usage detection ([`dd76dd5`](https://github.com/nanorepublica/django-deadcode/commit/dd76dd5e3dacc9a63906dea251a2a6ded2d9b061))

* Implement Reverse/Redirect Detection feature (v0.2.0)

Add Python AST analysis to detect reverse() and redirect() URL references,
reducing false positives in dead code detection.

New Features:
- ReverseAnalyzer class for detecting programmatic URL references
- Detects reverse(), reverse_lazy(), redirect(), HttpResponseRedirect()
- Dynamic URL pattern detection (f-strings, concatenation) with flagging
- Integration with finddeadcode command

Implementation Details:
- AST parsing of all Python files (excluding migrations/third-party)
- Handles nested patterns: HttpResponseRedirect(reverse(&#39;url&#39;))
- Supports namespaced URLs: reverse(&#39;app:view-name&#39;)
- Ignores method calls (self.reverse(), list.reverse())
- Combines template and Python URL references

Testing:
- 20 new tests (15 unit + 5 integration)
- 39/39 tests passing (100% success rate)
- 100% code coverage on ReverseAnalyzer
- 0 regressions in existing tests
- Performance impact &lt; 10%

Files Created:
- django_deadcode/analyzers/reverse_analyzer.py (65 lines)
- tests/test_reverse_analyzer.py (15 tests)
- tests/test_integration_reverse_detection.py (5 tests)

Files Modified:
- django_deadcode/analyzers/__init__.py (added export)
- django_deadcode/management/commands/finddeadcode.py (integrated)
- README.md (added Python code analysis section)
- CHANGELOG.md (v0.2.0 section)
- roadmap.md (feature #8 marked complete)

All acceptance criteria met. Ready for production use. ([`65ec691`](https://github.com/nanorepublica/django-deadcode/commit/65ec6911d28be8e5b8b09122f076551ee623932a))

* Merge pull request #1 from nanorepublica/claude/agent-os-development-011CV2ofdGATxikzCT7taJ3w

Django deadcode - v0.1.0 ([`0566864`](https://github.com/nanorepublica/django-deadcode/commit/05668641a2c97be862eca3e9f176ee08caf49299))

* Fix all ruff linting errors

Applied automatic and manual fixes to resolve 95 linting issues:

Automatic fixes (93 issues):
- Updated typing imports: Dict -&gt; dict, List -&gt; list, Set -&gt; set
- Removed deprecated Optional[X] in favor of X | None
- Removed unused imports (Template, TemplateSyntaxError, get_template,
  inspect, apps, TemplateView, importlib, sys, Path, etc.)
- Fixed import order (sorted imports)
- Replaced IOError with OSError (IOError is an alias)

Manual fixes (2 issues):
- Split long lines in reporters/base.py (lines 101 and 216)
  to comply with 88 character line length limit

Configuration updates:
- Updated pyproject.toml to use [tool.ruff.lint] section instead of
  deprecated top-level lint settings

All tests pass (19/19). All ruff checks now pass. ([`a71a9b5`](https://github.com/nanorepublica/django-deadcode/commit/a71a9b5cb36bc56535306f8a36960a38b11e61c0))

* Add pythonpath to pytest config to fix module import in CI

Added &#39;pythonpath = [&#34;.&#34;]&#39; to pytest configuration to ensure the
project root is on the Python path when pytest-django initializes.

This fixes the &#39;No module named tests&#39; error in GitHub Actions CI.
The pythonpath setting tells pytest to add the current directory to
sys.path before importing test modules, allowing pytest-django to
import &#39;tests.settings&#39; successfully.

Tests pass locally and should now pass in CI. ([`cb66329`](https://github.com/nanorepublica/django-deadcode/commit/cb66329ad91251f4d01d047310c595c99999ce49))

* Fix pytest-django configuration for library packages

Add &#39;django_find_project = false&#39; to pytest configuration to prevent
pytest-django from looking for manage.py.

This is necessary because django-deadcode is a Django package/library,
not a Django project. Libraries don&#39;t have manage.py files, but still
need Django settings for testing.

The setting tells pytest-django to use the DJANGO_SETTINGS_MODULE
directly without searching for a Django project structure.

All 19 tests now pass successfully. ([`304267f`](https://github.com/nanorepublica/django-deadcode/commit/304267fc277ff2962f877c43f3387de3c630dd69))

* Update CI to test only supported Python and Django versions

Updated testing matrix to focus on currently supported versions:

Python versions:
- Removed: 3.8 (EOL Oct 2024), 3.9 (EOL Oct 2025)
- Testing: 3.10, 3.11, 3.12, 3.13
- Minimum required: Python &gt;=3.10

Django versions:
- Removed: 3.2 LTS (EOL Apr 2024), 4.0 (EOL Apr 2023), 4.1 (EOL Dec 2023)
- Testing: 4.2 LTS, 5.0, 5.1
- Minimum required: Django &gt;=4.2

Additional updates:
- Updated pyproject.toml classifiers and dependencies
- Updated Ruff target-version to py310
- Updated mypy python_version to 3.10
- Updated PYPI_SETUP.md documentation

This ensures we only test and support versions that are actively maintained,
reducing CI time and maintenance burden. ([`70d4676`](https://github.com/nanorepublica/django-deadcode/commit/70d4676980732c58a02a14016d0c25708dc5b7e8))

* Add GitHub Actions for CI/CD and PyPI publishing

Set up automated testing and PyPI publishing using GitHub Actions,
following best practices from nanorepublica/django-prodserver.

CI Workflow (.github/workflows/ci.yml):
- Lint with Ruff on all pushes and PRs
- Test matrix: Python 3.8-3.12
- Test matrix: Django 3.2-5.0
- Build distribution packages
- Upload coverage to Codecov

Publish Workflow (.github/workflows/publish.yml):
- Triggered on GitHub Releases
- Uses PyPI Trusted Publishers (OIDC, no tokens needed)
- Signs packages with Sigstore for supply chain security
- Uploads signed artifacts to GitHub Release

Additional Files:
- PYPI_SETUP.md: Complete setup guide for PyPI Trusted Publishers
- .github/dependabot.yml: Automated dependency updates
- README.md: Added CI, PyPI, and version badges

Security Features:
- OIDC authentication (no stored tokens)
- Sigstore package signing
- GitHub environment protection (optional)
- Minimal permissions (principle of least privilege)

Setup Required:
1. Configure PyPI Trusted Publisher at pypi.org
2. Optionally create &#39;pypi&#39; environment in GitHub Settings
3. Update version in pyproject.toml before release
4. Create GitHub Release to trigger publishing

Based on modern 2024 best practices and django-prodserver patterns. ([`ca29a79`](https://github.com/nanorepublica/django-deadcode/commit/ca29a79e1932f68ea65dce6ec202c212c01a89e6))

* Add implementation tasks for Reverse/Redirect Detection

Created comprehensive task breakdown organized into 5 phases:
- Phase 1: Foundation (optional AST refactoring)
- Phase 2: Core Implementation (ReverseAnalyzer + pattern detection)
- Phase 3: Integration (finddeadcode command)
- Phase 4: Testing &amp; QA (16-28 tests total)
- Phase 5: Documentation &amp; polish

Key features:
- Test-driven approach with focused test groups
- Clear dependencies and execution order
- Specific file references and acceptance criteria
- Time estimates: 19-27 hours total

Ready for implementation with /implement-tasks or /orchestrate-tasks ([`678acc3`](https://github.com/nanorepublica/django-deadcode/commit/678acc34bc6036ef75d38fec863c41b1a9becdb9))

* Add comprehensive specification for Reverse/Redirect Detection

Created detailed spec.md (351 lines) for v0.2.0 feature.

Technical Design:
- New ReverseAnalyzer class with AST parsing
- Detects reverse(), redirect(), HttpResponseRedirect(), reverse_lazy()
- Integration via combining referenced URL sets

Includes implementation details, testing strategy, and acceptance criteria.
Ready for task list creation. ([`3564f2d`](https://github.com/nanorepublica/django-deadcode/commit/3564f2d8b4139695855312c06cb5532214538eff))

* Add requirements documentation for Reverse/Redirect Detection

Documented key decisions from requirements gathering phase:

Scope &amp; Architecture:
- Analyze all Python files (views, forms, models, utils, etc.)
- Create separate ReverseAnalyzer class
- Refactor common AST parsing logic between analyzers

Detection Patterns:
- reverse(&#39;url-name&#39;)
- redirect(&#39;url-name&#39;)
- HttpResponseRedirect(reverse(&#39;url-name&#39;))
- reverse_lazy(&#39;url-name&#39;)

Behavior:
- Mark detected URLs as &#34;referenced&#34; to prevent false positives
- Detect dynamic URLs and flag for manual investigation
- Exclude from unreferenced URL list

Exclusions:
- JavaScript files
- Third-party package code
- Migration files
- Edge cases (comments, strings, method calls)

Next step: Generate formal specification document with /write-spec ([`a160347`](https://github.com/nanorepublica/django-deadcode/commit/a16034788f9ef287386b7a4445ede17e45ee2ec8))

* Initialize spec for Reverse/Redirect Detection feature

Created spec folder structure for v0.2.0 feature:
- Feature: Detect reverse() and redirect() calls in Python code
- Priority: High (reduces false positives in dead code detection)
- Scope: AST parsing for Django URL helper functions

Spec folder: agent-os/specs/2025-11-12-reverse-redirect-detection/
- planning/raw-idea.md: Feature description and context
- planning/visuals/: Placeholder for mockups
- implementation/: For future implementation docs

This feature will extend the dead code analyzer to track programmatic
URL references, preventing false positives when URLs are referenced
via reverse() but not in templates. ([`d034497`](https://github.com/nanorepublica/django-deadcode/commit/d034497137f7dbeea39ec284ccb392833226c194))

* Update roadmap to reflect v0.1.0 completion

Mark features 1-7 as completed with implementation details:
- Template link extraction (href and {% url %} tags)
- URL pattern discovery with namespace support
- URL matching engine for dead code identification
- View reference tracking
- Template usage analysis via AST parsing
- Django management command CLI
- Template inheritance tracking (include/extends)

Note partial completion of features 9 and 12:
- Multi-app analysis: filtering implemented, visualization pending
- Enhanced reporting: JSON/Markdown/Console done, HTML pending

Outline v0.2.0 plans focusing on false positive reduction:
- Reverse/redirect detection
- Django admin URL filtering
- Cross-app dependency visualization ([`eae28eb`](https://github.com/nanorepublica/django-deadcode/commit/eae28eb10f6b7f675f43482166caf75072db7395))

* Implement django-deadcode package based on blog post

Built a complete Django package for dead code analysis that tracks
relationships between templates, URLs, and views to identify unused code.

Features implemented:
- Template analyzer: Extracts URL references from href and {% url %} tags,
  tracks {% include %} and {% extends %} relationships
- URL pattern analyzer: Discovers all URL patterns and maps them to views
- View analyzer: Identifies template usage in render() calls and
  class-based views (template_name attribute)
- Multiple reporters: Console, JSON, and Markdown output formats
- Django management command: python manage.py finddeadcode
- Comprehensive test suite: 19 tests with 69% coverage

Package structure:
- Uses Django&#39;s native management command structure
- Installable via pip with pyproject.toml configuration
- Supports Django 3.2+ and Python 3.8+
- CLI options for custom output formats, file export, and app filtering

Documentation:
- README with installation, usage, and examples
- CONTRIBUTING guide for developers
- CHANGELOG tracking releases
- MIT License

All tests pass successfully. ([`7cabad4`](https://github.com/nanorepublica/django-deadcode/commit/7cabad434e25406b9f841baae62883f730588280))

* Add product documentation for django-deadcode

Created comprehensive product documentation including:
- Mission statement with user personas and value proposition
- Roadmap with 12-feature development plan across 3 phases
- Tech stack documentation with architecture decisions

The tool will analyze Django codebases to identify dead code by
tracking relationships between templates, URLs, and views. ([`a4ec06f`](https://github.com/nanorepublica/django-deadcode/commit/a4ec06f9dcbf8bc014ad2a07b44bf5e05462fd7d))

* Initial commit ([`00f1d8d`](https://github.com/nanorepublica/django-deadcode/commit/00f1d8df2e4876af2bff44e53408e6be5e019035))
