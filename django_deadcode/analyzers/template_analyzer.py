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

    def __init__(
        self, template_dirs: list[Path] | None = None, base_dir: Path | None = None
    ) -> None:
        """
        Initialize the template analyzer.

        Args:
            template_dirs: List of template directories to search
            base_dir: Project BASE_DIR for filtering templates (optional)
        """
        self.template_dirs = template_dirs or []
        self.base_dir = base_dir.resolve() if base_dir else None
        self.templates: dict[str, dict] = {}
        self.url_references: dict[str, set[str]] = {}
        self.template_includes: dict[str, set[str]] = {}
        self.template_extends: dict[str, set[str]] = {}
        self.template_extensions = [".html", ".txt", ".xml", ".svg"]

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

        # Extract href attributes (filter for internal URLs starting with /)
        all_hrefs = self.HREF_PATTERN.findall(content)
        internal_hrefs = {
            href
            for href in all_hrefs
            if href.startswith("/") and not href.startswith("//")
        }

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
