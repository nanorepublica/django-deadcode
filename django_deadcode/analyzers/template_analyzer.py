"""Analyzer for extracting URL references from Django templates."""

import re
from pathlib import Path


class TemplateAnalyzer:
    """Analyzes Django templates to extract URL references and relationships."""

    # Regex patterns for finding URLs
    HREF_PATTERN = re.compile(r'href=["\']([^"\']*)["\']', re.IGNORECASE)
    URL_TAG_PATTERN = re.compile(r'{%\s*url\s+["\']([^"\']+)["\']', re.MULTILINE)
    INCLUDE_PATTERN = re.compile(r'{%\s*include\s+["\']([^"\']+)["\']', re.MULTILINE)
    EXTENDS_PATTERN = re.compile(r'{%\s*extends\s+["\']([^"\']+)["\']', re.MULTILINE)

    # Comment patterns for stripping before URL extraction
    HTML_COMMENT_PATTERN = re.compile(r"<!--.*?-->", re.DOTALL)
    JS_MULTILINE_COMMENT_PATTERN = re.compile(r"/\*.*?\*/", re.DOTALL)
    JS_SINGLELINE_COMMENT_PATTERN = re.compile(r"(?<!:)//.*$", re.MULTILINE)

    # Pattern for internal URLs anywhere in content (quoted strings starting with /)
    INTERNAL_URL_PATTERN = re.compile(r'["\'](/(?!/)[^"\']*)["\']')

    # Extended pattern for template literals: `/api/${id}/edit/`
    # Matches backtick strings starting with / and extracts the static prefix
    TEMPLATE_LITERAL_PATTERN = re.compile(r"`(/[^`]*)`")

    # Pattern to extract static prefix from template literal (before ${)
    TEMPLATE_LITERAL_PREFIX_PATTERN = re.compile(r"^(/[^$`]*)")

    def __init__(
        self,
        template_dirs: list[Path] | None = None,
        base_dir: Path | None = None,
        static_dirs: list[Path] | None = None,
        scan_static: bool = False,
        url_detection: str = "basic",
    ) -> None:
        """
        Initialize the template analyzer.

        Args:
            template_dirs: List of template directories to search
            base_dir: Project BASE_DIR for filtering templates (optional)
            static_dirs: List of static directories to search for JS files (optional)
            scan_static: Whether to scan static JavaScript files for URLs
            url_detection: Detection level - 'basic' or 'extended' (default: basic)
        """
        self.template_dirs = template_dirs or []
        self.base_dir = base_dir.resolve() if base_dir else None
        self.static_dirs = static_dirs or []
        self.scan_static = scan_static
        self.url_detection = url_detection
        self.templates: dict[str, dict] = {}
        self.url_references: dict[str, set[str]] = {}
        self.template_includes: dict[str, set[str]] = {}
        self.template_extends: dict[str, set[str]] = {}
        self.template_extensions = [".html", ".txt", ".xml", ".svg"]
        self.static_extensions = [".js", ".mjs"]
        self.static_files: dict[str, dict] = {}

    def _is_relative_to(self, path: Path, parent: Path) -> bool:
        """
        Check if path is relative to parent (compatible with Python 3.8+).

        Args:
            path: Path to check
            parent: Parent path

        Returns:
            True if path is relative to parent, False otherwise
        """
        try:
            path.relative_to(parent)
            return True
        except ValueError:
            return False

    def _strip_comments(self, content: str) -> str:
        """
        Strip HTML and JavaScript comments from content.

        This removes comments before URL extraction to prevent false positives
        from URLs mentioned in commented-out code.

        Args:
            content: Template content as string

        Returns:
            Content with comments removed
        """
        # Remove HTML comments first
        content = self.HTML_COMMENT_PATTERN.sub("", content)
        # Remove JS multi-line comments
        content = self.JS_MULTILINE_COMMENT_PATTERN.sub("", content)
        # Remove JS single-line comments (but not :// in URLs)
        content = self.JS_SINGLELINE_COMMENT_PATTERN.sub("", content)
        return content

    def normalize_template_path(self, filesystem_path: Path) -> str:
        """
        Convert filesystem path to Django-relative template path.

        This method finds the 'templates/' directory in the path and returns
        everything after it, which matches Django's template resolution format.

        Args:
            filesystem_path: Full filesystem path to template

        Returns:
            Django-relative template path (e.g., 'app_name/template.html')

        Examples:
            /app/apps/collations/templates/collations/base.html
                -> collations/base.html
            /app/templates/base.html
                -> base.html
            /app/templates/partials/header.html
                -> partials/header.html
            /app/templates/old_templates/templates/base.html
                -> base.html (uses last occurrence)
        """
        path_parts = filesystem_path.parts

        # Find all occurrences of 'templates' in path
        templates_indices = [
            i for i, part in enumerate(path_parts) if part == "templates"
        ]

        if not templates_indices:
            # No 'templates' directory found, return filename
            return filesystem_path.name

        # Use the last occurrence of 'templates' directory
        last_templates_index = templates_indices[-1]

        # Get everything after 'templates/'
        relative_parts = path_parts[last_templates_index + 1 :]

        # Join with forward slashes (Django convention)
        return "/".join(relative_parts)

    def analyze_template_file(self, template_path: Path) -> dict:
        """
        Analyze a single template file.

        Args:
            template_path: Path to the template file

        Returns:
            Dictionary containing analysis results for the template
        """
        try:
            content = template_path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as e:
            return {
                "error": str(e),
                "urls": set(),
                "includes": set(),
                "extends": set(),
                "hrefs": set(),
            }

        # Normalize the template path for consistent storage
        normalized_path = self.normalize_template_path(template_path)

        return self._analyze_template_content(content, normalized_path)

    def _extract_template_literal_urls(self, content: str) -> set[str]:
        """
        Extract URL prefixes from JavaScript template literals.

        Finds template literals like `/api/${id}/edit/` and extracts the
        static prefix (e.g., '/api/').

        Args:
            content: Content to search for template literals

        Returns:
            Set of static URL prefixes extracted from template literals
        """
        urls = set()
        for match in self.TEMPLATE_LITERAL_PATTERN.findall(content):
            # Extract the static prefix before any ${...} interpolation
            prefix_match = self.TEMPLATE_LITERAL_PREFIX_PATTERN.match(match)
            if prefix_match:
                prefix = prefix_match.group(1)
                # Only include if it has a meaningful path (not just /)
                if prefix and len(prefix) > 1:
                    urls.add(prefix)
        return urls

    def _analyze_template_content(self, content: str, template_name: str) -> dict:
        """
        Analyze template content for URL references.

        Args:
            content: Template content as string
            template_name: Name or path of the template (should be normalized)

        Returns:
            Dictionary with sets of URLs, includes, extends, and hrefs
        """
        # Extract {% url %} tags
        url_tags = set(self.URL_TAG_PATTERN.findall(content))

        # Strip comments before extracting internal URLs
        # This prevents false positives from URLs in commented-out code
        cleaned_content = self._strip_comments(content)

        # Extract internal URLs from anywhere in the template (not just href)
        # This catches URLs in JavaScript, data attributes, event handlers, etc.
        internal_hrefs = set(self.INTERNAL_URL_PATTERN.findall(cleaned_content))

        # Extended detection: also extract URLs from template literals
        if self.url_detection == "extended":
            template_literal_urls = self._extract_template_literal_urls(cleaned_content)
            internal_hrefs.update(template_literal_urls)

        # Extract {% include %} tags
        includes = set(self.INCLUDE_PATTERN.findall(content))

        # Extract {% extends %} tags
        extends = set(self.EXTENDS_PATTERN.findall(content))

        result = {
            "urls": url_tags,
            "includes": includes,
            "extends": extends,
            "hrefs": internal_hrefs,
        }

        # Store in instance variables using normalized template name
        self.templates[template_name] = result
        self.url_references[template_name] = url_tags
        self.template_includes[template_name] = includes
        self.template_extends[template_name] = extends

        return result

    def find_all_templates(self) -> None:
        """
        Find all template files in configured template directories.

        Filters templates by BASE_DIR if it was provided during initialization.
        """
        for template_dir in self.template_dirs:
            if not template_dir.exists():
                continue

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

                    # Analyze template (will store with normalized path)
                    self.analyze_template_file(template_path)

    def analyze_all_templates(self, base_path: Path) -> dict[str, dict]:
        """
        Analyze all templates in a directory tree.

        Args:
            base_path: Base directory containing templates

        Returns:
            Dictionary mapping template paths to their analysis results
        """
        template_extensions = [".html", ".txt", ".xml", ".svg"]
        templates = []

        for ext in template_extensions:
            templates.extend(base_path.rglob(f"*{ext}"))

        for template_path in templates:
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

            self.analyze_template_file(template_path)

        return self.templates

    def get_url_references_by_template(self) -> dict[str, set[str]]:
        """
        Get all URL references grouped by template.

        Returns:
            Dictionary mapping template names to sets of URL references
        """
        return self.url_references

    def get_template_relationships(self) -> dict[str, dict[str, set[str]]]:
        """
        Get template inheritance and inclusion relationships.

        Returns:
            Dictionary with 'includes' and 'extends' relationships
        """
        return {"includes": self.template_includes, "extends": self.template_extends}

    def get_unused_url_names(self, defined_url_names: set[str]) -> set[str]:
        """
        Find URL names that are defined but never referenced in templates.

        Args:
            defined_url_names: Set of URL names defined in urlpatterns

        Returns:
            Set of unused URL names
        """
        referenced_urls = set()
        for urls in self.url_references.values():
            referenced_urls.update(urls)

        return defined_url_names - referenced_urls

    def get_referenced_urls(self) -> set[str]:
        """
        Get all URL names referenced across all templates.

        Returns:
            Set of all URL name references
        """
        referenced = set()
        for urls in self.url_references.values():
            referenced.update(urls)
        return referenced

    def get_all_internal_hrefs(self) -> set[str]:
        """
        Get all internal hrefs across all analyzed templates and static files.

        Returns:
            Set of all internal hrefs found in templates and static files
        """
        all_hrefs = set()
        for template_data in self.templates.values():
            hrefs = template_data.get("hrefs", set())
            all_hrefs.update(hrefs)
        # Also include hrefs from static files
        for static_data in self.static_files.values():
            hrefs = static_data.get("hrefs", set())
            all_hrefs.update(hrefs)
        return all_hrefs

    def normalize_static_path(self, filesystem_path: Path) -> str:
        """
        Convert filesystem path to a relative static file path.

        This method finds the 'static/' directory in the path and returns
        everything after it.

        Args:
            filesystem_path: Full filesystem path to static file

        Returns:
            Relative static file path (e.g., 'js/app.js')

        Examples:
            /app/myapp/static/js/app.js -> js/app.js
            /app/static/vendor/lib.js -> vendor/lib.js
        """
        path_parts = filesystem_path.parts

        # Find all occurrences of 'static' in path
        static_indices = [i for i, part in enumerate(path_parts) if part == "static"]

        if not static_indices:
            # No 'static' directory found, return filename
            return filesystem_path.name

        # Use the last occurrence of 'static' directory
        last_static_index = static_indices[-1]

        # Get everything after 'static/'
        relative_parts = path_parts[last_static_index + 1 :]

        # Join with forward slashes
        return "/".join(relative_parts)

    def analyze_static_file(self, static_path: Path) -> dict:
        """
        Analyze a single static JavaScript file for URL references.

        Args:
            static_path: Path to the static file

        Returns:
            Dictionary containing analysis results (only hrefs for static files)
        """
        try:
            content = static_path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as e:
            return {
                "error": str(e),
                "hrefs": set(),
            }

        # Normalize the static path for consistent storage
        normalized_path = self.normalize_static_path(static_path)

        return self._analyze_static_content(content, normalized_path)

    def _analyze_static_content(self, content: str, static_name: str) -> dict:
        """
        Analyze static file content for URL references.

        Unlike template analysis, this only extracts internal URLs (no {% url %} tags,
        includes, or extends since those are Django template-specific).

        Args:
            content: Static file content as string
            static_name: Name or path of the static file (should be normalized)

        Returns:
            Dictionary with set of hrefs found
        """
        # Strip comments before extracting internal URLs
        cleaned_content = self._strip_comments(content)

        # Extract internal URLs from the content
        internal_hrefs = set(self.INTERNAL_URL_PATTERN.findall(cleaned_content))

        # Extended detection: also extract URLs from template literals
        if self.url_detection == "extended":
            template_literal_urls = self._extract_template_literal_urls(cleaned_content)
            internal_hrefs.update(template_literal_urls)

        result = {
            "hrefs": internal_hrefs,
        }

        # Store in instance variable using normalized static file name
        self.static_files[static_name] = result

        return result

    def find_all_static_files(self) -> None:
        """
        Find and analyze all JavaScript files in configured static directories.

        Only runs if scan_static is True. Filters by BASE_DIR if provided.
        """
        if not self.scan_static:
            return

        for static_dir in self.static_dirs:
            if not static_dir.exists():
                continue

            for ext in self.static_extensions:
                for static_path in static_dir.rglob(f"*{ext}"):
                    # Filter by BASE_DIR if provided
                    if self.base_dir:
                        try:
                            resolved = static_path.resolve()
                            if not self._is_relative_to(resolved, self.base_dir):
                                continue
                        except (ValueError, OSError):
                            continue

                    # Skip minified files (often third-party)
                    if ".min." in static_path.name:
                        continue

                    # Skip common vendor/node_modules directories
                    path_str = str(static_path)
                    if any(
                        skip in path_str
                        for skip in ["node_modules", "vendor", "bower_components"]
                    ):
                        continue

                    self.analyze_static_file(static_path)
