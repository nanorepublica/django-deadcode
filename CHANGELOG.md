# CHANGELOG

## v0.6.0 (2025-11-29)

### Chore

* chore: fix trailing whitespace in CHANGELOG.md ([`a9461e6`](https://github.com/nanorepublica/django-deadcode/commit/a9461e644aa943f107160defe46e050ee62aeb50))

### Documentation

* docs: add task list for URL detection implementation

Break down implementation into 3 task groups with 15 sub-tasks:
- Task Group 1: Comment stripping (4 tests + implementation)
- Task Group 2: URL pattern enhancement (6 tests + implementation)
- Task Group 3: Test coverage review and gap analysis ([`527fd4b`](https://github.com/nanorepublica/django-deadcode/commit/527fd4b981e6537505baf5c1d812c1948a7f818e))

* docs: add spec for expanded URL detection in templates

Add specification to detect internal URLs anywhere in HTML templates,
not just in href attributes. Includes requirements to:
- Match URLs in JS code, data attributes, event handlers
- Exclude URLs inside HTML and JS comments
- Support dynamic URLs with Django template variables ([`6747e6b`](https://github.com/nanorepublica/django-deadcode/commit/6747e6b207881e7d51c9eaf084c59c4d747d4c25))

### Feature

* feat: release ([`ec03b3a`](https://github.com/nanorepublica/django-deadcode/commit/ec03b3aa7eb586505fd2dd14507d82a7c2c60dec))

* feat: Reduce false positives in URL detection ([`2500e5e`](https://github.com/nanorepublica/django-deadcode/commit/2500e5ea4ef58c1f2ccdbe16700ffb75977914af))

* feat: expand URL detection to find URLs anywhere in templates

Instead of only detecting URLs in href attributes, now detect internal
URL strings anywhere in HTML template files. This catches URLs in:
- JavaScript code (fetch, const url = ...)
- Data attributes (data-url=&#34;/api/...&#34;)
- Inline event handlers (onclick=&#34;location.href=&#39;...&#39;&#34;)
- JSON configs embedded in templates

Also excludes URLs inside comments:
- HTML comments (&lt;!-- ... --&gt;)
- JS single-line comments (// ...)
- JS multi-line comments (/* ... */)

Added 10 new tests covering the expanded detection and comment stripping.
All 211 existing tests continue to pass. ([`88f418e`](https://github.com/nanorepublica/django-deadcode/commit/88f418e3c9c117e828d0c6a35982211b0c0b1fee))

## v0.5.1 (2025-11-28)

### Chore

* chore(release): 0.5.1 ([`31e50a7`](https://github.com/nanorepublica/django-deadcode/commit/31e50a700b2569e54ea1259d9e4949a809dad231))

### Documentation

* docs: add task list for URL reference detection fix

Break down implementation into 4 task groups with 16 sub-tasks:
- Task Group 1: Path normalization enhancement (strip ^, $, handle /?)
- Task Group 2: Dynamic URL pattern matching (helper functions)
- Task Group 3: Integration and match function enhancement
- Task Group 4: Final verification and edge cases

Follows TDD approach with ~28-30 new tests planned. ([`26df666`](https://github.com/nanorepublica/django-deadcode/commit/26df6666d3b79d8ee4343cace43ebc51613a23e5))

* docs: add spec for fixing URL reference detection false positives

Add specification for fixing false positives when detecting unreferenced
URLs. The issue occurs because regex anchors (^ and $) and optional
trailing slashes (/?) in URL patterns aren&#39;t being stripped during
normalization, causing pattern-to-href comparison to fail.

The spec covers:
- Enhanced normalize_path() to strip regex syntax
- Helper functions for detecting capture groups
- Dynamic URL matching for patterns with template variables ({{)
- Comprehensive test cases for edge cases ([`1767e5e`](https://github.com/nanorepublica/django-deadcode/commit/1767e5e88a7a9ad12b4f05d2f06164aa489bc3e4))

### Fix

* fix: fix false positives on unreferenced urls

Fix false positives in URL reference detection ([`ae491df`](https://github.com/nanorepublica/django-deadcode/commit/ae491dfb84c14f70649e5cbac92c98f7e7a04e16))

* fix: handle regex anchors and dynamic URLs in pattern matching

Fix false positives when detecting unreferenced URLs by properly handling
regex syntax in Django URL patterns.

Changes to url_matching.py:
- Enhanced normalize_path() to strip ^ and $ regex anchors
- Added support for /? optional trailing slash patterns
- Added has_capture_groups() to detect dynamic URL patterns
- Added extract_static_prefix() to get static portion before capture groups
- Added is_dynamic_href() to detect {{ template syntax in hrefs
- Modified match_href_to_pattern() to match dynamic hrefs against patterns
  with capture groups by comparing static prefixes

This fixes the issue where patterns like ^my/url$ were not matching
hrefs like /my/url, and enables matching dynamic hrefs like
/user/{{ user.id }}/ against patterns like ^user/(?P&lt;id&gt;\d+)/$

Added 35 new tests covering:
- Regex anchor stripping (^, $, both)
- Optional trailing slash handling (/?)
- Capture group detection and prefix extraction
- Dynamic href matching
- Edge cases (multiple groups, groups at start, character classes)

All 201 tests pass with 100% coverage on url_matching.py. ([`28ba411`](https://github.com/nanorepublica/django-deadcode/commit/28ba4119a1eb140af21c0dcfce688dacfe36f833))

### Style

* style: apply pre-commit formatting fixes ([`875cac7`](https://github.com/nanorepublica/django-deadcode/commit/875cac7c0409a9d6b41b889387c9a441c48d6ae7))

## v0.5.0 (2025-11-26)

### Chore

* chore(release): 0.5.0 ([`9f959cd`](https://github.com/nanorepublica/django-deadcode/commit/9f959cd9ccc2e5629d832caaff10493ada3ecaad))

### Feature

* feat: release ([`2f24270`](https://github.com/nanorepublica/django-deadcode/commit/2f242704e7eb9f616edfe2fb68bbd1a635ae7766))

* feat: release ([`4acaeeb`](https://github.com/nanorepublica/django-deadcode/commit/4acaeeb3217c43a16f4288cf1927825a7379615c))

* feat: release ([`64db357`](https://github.com/nanorepublica/django-deadcode/commit/64db357ea4a68869fee5152217a06e9268eae881))

## v0.4.0 (2025-11-26)

### Chore

* chore(release): 0.4.0 ([`7f792b6`](https://github.com/nanorepublica/django-deadcode/commit/7f792b6c038725a0b12a82b7f7dbfc81a539a088))

### Feature

* feat: release ([`002ccdf`](https://github.com/nanorepublica/django-deadcode/commit/002ccdf9e9915aa77f6e151924bdcb18940b6dd2))

* feat: release ([`9392c88`](https://github.com/nanorepublica/django-deadcode/commit/9392c88ac55ff00420552d8406c8ec19d75915f9))

* feat: release ([`d5e209c`](https://github.com/nanorepublica/django-deadcode/commit/d5e209c56e8cb7d5e897a9dfb86c1a34e63203f0))

* feat: release ([`13b1caa`](https://github.com/nanorepublica/django-deadcode/commit/13b1caaed9496c1d821f79f687f0c28a91c81595))

* feat: release ([`d5144dd`](https://github.com/nanorepublica/django-deadcode/commit/d5144dd795547b7f528c5e235c5f3c0486251508))

* feat: release ([`3afaf91`](https://github.com/nanorepublica/django-deadcode/commit/3afaf91663fba206c68d3b2fa5b58c3df3d939e2))

### Fix

* fix: release ([`89f7de2`](https://github.com/nanorepublica/django-deadcode/commit/89f7de2126e4904abb4029a386152a9c44156d4b))

### Unknown

* patch: release ([`55a3e21`](https://github.com/nanorepublica/django-deadcode/commit/55a3e21046f477d652aa155d6cea9d2f3fe7dbfd))

## v0.3.0 (2025-11-26)

### Chore

* chore(release): 0.3.0 ([`4697f88`](https://github.com/nanorepublica/django-deadcode/commit/4697f887baa9fe222ff1212338a341b86d33e31a))

* chore: release fix ([`c98af15`](https://github.com/nanorepublica/django-deadcode/commit/c98af15720a5919aa6fe7b82b0adc3b947f98a4e))

* chore(release): 0.4.0 ([`565ef70`](https://github.com/nanorepublica/django-deadcode/commit/565ef705023d700cbc8d18171ac70fe7c4d08878))

* chore: update ruff-pre-commit version to v0.8.4 ([`cf66b6d`](https://github.com/nanorepublica/django-deadcode/commit/cf66b6d0addc9915fa9803ff41bc0c2b7d2e1e7f))

* chore: fix trailing whitespace in CHANGELOG.md

Applied pre-commit hook to remove trailing whitespace. ([`e096722`](https://github.com/nanorepublica/django-deadcode/commit/e096722607d74a29a03828f28d76f95d21730024))

* chore(release): 0.3.0 ([`d3f9631`](https://github.com/nanorepublica/django-deadcode/commit/d3f96312478432307329f8bade337dd92f246122))

* chore: remove trailing whitespace from CHANGELOG.md ([`af4f702`](https://github.com/nanorepublica/django-deadcode/commit/af4f70210c445ea30be09643e36b607598eaea22))

* chore: initialize spec for template detection fix

Initialize spec folder for fixing unused template detection feature
where templates are incorrectly flagged as unreferenced due to
relative path handling issues. ([`1124d74`](https://github.com/nanorepublica/django-deadcode/commit/1124d744d8f87f25fa905fdffb800df09aad3ca7))

### Documentation

* docs: add final verification report for URL pattern enhancements ([`c13edbc`](https://github.com/nanorepublica/django-deadcode/commit/c13edbc113acfe1e1a7807fdab02c5fc5853adfc))

* docs: add tasks breakdown for URL pattern enhancements ([`2a6b53c`](https://github.com/nanorepublica/django-deadcode/commit/2a6b53c98bee0370d4d2f41178c83b5e94d7ec96))

* docs: add spec for URL pattern enhancements ([`b8732c9`](https://github.com/nanorepublica/django-deadcode/commit/b8732c9d22b1f8c2ed4fe0deda0abc8b8b045ffc))

* docs: add tasks breakdown for template detection fix

Create comprehensive tasks list with 36 tasks across 4 phases:
- Phase 1: Path normalization foundation (5 tasks, CRITICAL)
- Phase 2: Enhanced detection - CBV defaults and template variables (11 tasks)
- Phase 3: Command integration (5 tasks)
- Phase 4: Testing and validation (15 tasks)

Strategic organization respects dependencies, includes test-driven
approach with 18-42 targeted tests, and targets 5-day implementation. ([`a4bc4f9`](https://github.com/nanorepublica/django-deadcode/commit/a4bc4f9d685f092cd0c149fed152325662dddf58))

* docs: add comprehensive specification for template detection fix

Create detailed specification document covering:
- Problem statement with concrete examples
- Root cause analysis of path mismatch bug
- Four prioritized requirements (path normalization, CBV defaults, template variables, relationships)
- Technical approach with architecture diagrams
- 5-day phased implementation plan
- Comprehensive test strategy
- Success criteria and risk assessment ([`3bb6a89`](https://github.com/nanorepublica/django-deadcode/commit/3bb6a898a7c9b2ce3ed89840f78600fdfdee6a63))

* docs: add requirements for template detection fix

Document comprehensive requirements for fixing unused template detection:
- Core bug: path mismatch between full paths and relative names
- Need path normalization using Django&#39;s template loaders
- CBV default template detection (ListView, DetailView, etc.)
- Template variable detection (variables with &#39;template&#39; in name)
- Enhanced relationship tracking for extends/include

Success criteria and test cases included. ([`b12f2bb`](https://github.com/nanorepublica/django-deadcode/commit/b12f2bbcbf1432940eab8ea15fb73dec38f7f07a))

### Feature

* feat: release ([`47fd562`](https://github.com/nanorepublica/django-deadcode/commit/47fd562fee38b68bce62636aff093bb3cacc9674))

* feat: fix unreferenced URL patterns for internal links ([`c369b60`](https://github.com/nanorepublica/django-deadcode/commit/c369b601e984e75e142184795a5ff2ae5d1cd7fa))

* feat: implement URL pattern enhancements with href matching and third-party exclusion

Implement two major enhancements to django-deadcode&#39;s URL pattern detection:

1. Raw URL Pattern Matching
   - Extract internal hrefs from templates (e.g., &lt;a href=&#34;/about/&#34;&gt;)
   - Match hrefs against URL patterns using simple string matching
   - Mark matched URL patterns as referenced to reduce false positives
   - Properly handle path normalization (leading/trailing slashes)
   - Filter external protocols (http://, https://, mailto:, tel:, etc.)

2. Third-Party URL Exclusion
   - Auto-detect third-party namespaces by checking if view modules are outside BASE_DIR
   - Exclude entire namespaces if any pattern is third-party
   - Support manual exclusions via DEADCODE_EXCLUDE_NAMESPACES setting
   - Add informational note to reports listing excluded namespaces
   - Silently remove third-party URLs from unreferenced list

Implementation Details:
- Created utils module with module_detection, url_matching, and config utilities
- Enhanced URLAnalyzer to store module_path and is_third_party for each pattern
- Updated get_unreferenced_urls() to return tuple: (unreferenced, excluded_namespaces)
- Added get_all_internal_hrefs() method to TemplateAnalyzer
- Updated management command to integrate href matching and namespace exclusion
- Enhanced all reporters (Console, JSON, Markdown) to show exclusion notes
- Maintained full backwards compatibility with existing functionality

Tests:
- Added 74 new tests across 5 new test files
- All 172 tests pass including existing tests
- Tests cover: third-party detection, href extraction, pattern matching,
  configuration handling, and end-to-end integration

Configuration:
Users can now configure:
  DEADCODE_EXCLUDE_NAMESPACES = [&#39;admin&#39;, &#39;debug_toolbar&#39;]

This addresses the common issue of third-party URLs (like Django admin)
appearing as unreferenced, and improves detection by matching raw hrefs
in templates. ([`ab0c5c8`](https://github.com/nanorepublica/django-deadcode/commit/ab0c5c89b86e62c79915409f1290c987d9f93909))

* feat: path normalization for templates and cbv detection

Path Normalization for templates and CBV detection ([`84bd028`](https://github.com/nanorepublica/django-deadcode/commit/84bd028cbb4b04101f85850eb9955aa756985259))

* feat: fix unused template detection with path normalization and enhanced detection

Implement comprehensive fix for template detection false positives across 6 task groups:

PHASE 1: Path Normalization (CRITICAL)
- Add normalize_template_path() to convert filesystem paths to Django-relative format
- Update TemplateAnalyzer to store templates with normalized paths
- Ensure template relationships (extends/includes) use normalized paths
- 8 focused tests added, all passing

PHASE 2: Enhanced Detection
- Task Group 2: CBV Default Template Detection
  * Detect ListView, DetailView, CreateView, UpdateView, DeleteView implicit templates
  * Extract models from &#39;model&#39; attribute and &#39;queryset&#39; patterns
  * Infer app labels from file paths
  * Generate implicit template names following Django conventions
  * 8 focused tests added, all passing

- Task Group 3: Template Variable Detection
  * Detect variables containing &#39;template&#39; in name (case-insensitive)
  * Parse get_template_names() method returns
  * Extract string constants from assignments and returns
  * 7 focused tests added, all passing

PHASE 3: Integration
- Task Group 4: Command Integration &amp; Path Consistency
  * Verify _compile_analysis_data() uses normalized paths
  * Confirm transitive closure works with normalized paths
  * Validate set comparison logic eliminates false positives
  * 7 integration tests added, all passing

PHASE 4: Validation
- Task Group 5: Test Review &amp; Gap Analysis
  * Review 51 existing tests from Task Groups 1-4
  * Add 10 strategic tests for edge cases and error handling
  * Achieve 93% code coverage (exceeds 90% target)

- Task Group 6: Manual Validation &amp; Documentation
  * Create collations app validation tests (4 tests)
  * Add performance benchmarks (6 tests, &lt;1% impact vs 10% target)
  * Update README with features, troubleshooting, changelog
  * Code cleanup and linting fixes

RESULTS:
- 102/102 tests passing (92 original + 10 new)
- 93% code coverage (target: &gt;90%)
- &lt;1% performance impact (target: &lt;10%)
- Zero false positives for collations app example
- Production-ready for v0.3.0 release

Fixes: Template detection false positives
Resolves: collations/base.html, collection_list.html, collection_detail.html incorrectly flagged ([`76ddd8b`](https://github.com/nanorepublica/django-deadcode/commit/76ddd8b4f06b3800a10cc1f86510022caff6c566))

### Refactor

* refactor: remove URL REFERENCES BY TEMPLATE and TEMPLATE USAGE BY VIEWS sections

Remove these reporting sections from ConsoleReporter as they are no longer needed:
- URL REFERENCES BY TEMPLATE
- TEMPLATE USAGE BY VIEWS

This streamlines the console output to focus on the most important information. ([`c8fb0a9`](https://github.com/nanorepublica/django-deadcode/commit/c8fb0a969fa0cb39be1c33ded6ac61ad750ec6b6))

### Style

* style: apply ruff-format v0.8.4 to test files ([`f041320`](https://github.com/nanorepublica/django-deadcode/commit/f041320def33f0cb42e445a81d1e2df3f434384c))

* style: apply ruff-format to all files ([`27a670d`](https://github.com/nanorepublica/django-deadcode/commit/27a670db117b0a5bfe7116e6c8c72365ab98d2a6))

* style: fix ruff linting errors (line length and imports) ([`743fd0d`](https://github.com/nanorepublica/django-deadcode/commit/743fd0de9b8c8ed53a51624cfeff7203584000eb))

* style: apply ruff-format to test files

Apply ruff formatting improvements:
- Consolidate function arguments on single line when they fit
- Reformat assertion statements for better readability
- Standardize string concatenation formatting ([`05b822c`](https://github.com/nanorepublica/django-deadcode/commit/05b822c170f78f29a1ad18c1f8e6cc2eeb717010))

* style: fix ruff lint issues (line length violations)

Fix all E501 (line too long) and F541 (unused f-string) violations:
- Shorten docstring in test_manual_collations_app.py
- Split long assertion messages across multiple lines
- Break long imports into parenthesized groups
- Extract dict lookups to separate variables
- Reformat long comments to fit within 88 character limit

All 102 tests still passing. ([`807580e`](https://github.com/nanorepublica/django-deadcode/commit/807580e4efe9e52d7028b7e1334271e1d55fda80))

### Unknown

* Merge pull request #17 from nanorepublica/claude/remove-reporting-sections-01YTxtgpotVnM33V7bWjk9D6

Remove unused reporting sections from dashboard ([`7ee6a27`](https://github.com/nanorepublica/django-deadcode/commit/7ee6a27bd7e3d260e8405bce62055f046fef42c8))

## v0.2.1 (2025-11-13)

### Chore

* chore(release): 0.2.1 ([`58a9266`](https://github.com/nanorepublica/django-deadcode/commit/58a9266ce7ea78f567907bca66be333ebf8b001e))

* chore: set version to 0.3.0 for PyPI release 

Update package version to 0.2.3 ([`9cef729`](https://github.com/nanorepublica/django-deadcode/commit/9cef729b4f465cb717b9a54cbbb5bb20ca03c3cd))

* chore: set version to 0.3.0 for PyPI release

Update version to 0.3.0 in both pyproject.toml and __init__.py to
prepare for publishing to PyPI. ([`4bc9f91`](https://github.com/nanorepublica/django-deadcode/commit/4bc9f91f60ca8a9cd92ea2f1af98c7f4a41b5a0c))

* chore(release): 0.3.1 ([`3b6e019`](https://github.com/nanorepublica/django-deadcode/commit/3b6e01996dc83e1d170e154e92e5f4fdbac5f241))

* chore(release): 0.3.0 ([`2ad1f74`](https://github.com/nanorepublica/django-deadcode/commit/2ad1f74365f96bd7b41094cf1fe5d87c9592edf0))

### Ci

* ci: trigger CI workflow

Trigger CI workflow to verify and publish version 0.3.0 to PyPI. ([`69b14c4`](https://github.com/nanorepublica/django-deadcode/commit/69b14c4b0f4f845c357fe828b2921cadbd353b16))

### Fix

* fix: update README for production readiness

Claude/update pypi version 01 kxyyzljhtm6 bp8r sx vypd s ([`07a56a0`](https://github.com/nanorepublica/django-deadcode/commit/07a56a01a690b5722db8a89d23b24bd1e535a0c6))

* fix: update README for production readiness

Remove experimental warning as the package has been thoroughly tested
with 62 passing tests and 93% code coverage. ([`89cac28`](https://github.com/nanorepublica/django-deadcode/commit/89cac288d3b0dc0149028eeded034dbc97f5d002))

### Unknown

* Merge pull request #13 from nanorepublica/claude/agent-os-development-011CV4fE968vXyiH6k8T9hCU

chore(release): 0.3.1 ([`cab09da`](https://github.com/nanorepublica/django-deadcode/commit/cab09dab9ca4ad65d5d643994a35df265bd74f9c))

* Merge branch &#39;main&#39; into claude/agent-os-development-011CV4fE968vXyiH6k8T9hCU ([`7669602`](https://github.com/nanorepublica/django-deadcode/commit/7669602585f1a8fb57adef99ece8a0b3354fda11))

## v0.2.0 (2025-11-13)

### Chore

* chore(release): 0.2.0 ([`409e1d1`](https://github.com/nanorepublica/django-deadcode/commit/409e1d1ef118e6c856bd162de2557273d3eb7455))

* chore(release): 0.3.0 ([`57ced8d`](https://github.com/nanorepublica/django-deadcode/commit/57ced8d6748eb1179ac2bc27e5fecdb6062dbd75))

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
