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

    def __init__(self) -> None:
        """Initialize the template analyzer."""
        self.templates: dict[str, dict] = {}
        self.url_references: dict[str, set[str]] = {}
        self.template_includes: dict[str, set[str]] = {}
        self.template_extends: dict[str, set[str]] = {}

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

        return self._analyze_template_content(content, str(template_path))

    def _analyze_template_content(self, content: str, template_name: str) -> dict:
        """
        Analyze template content for URL references.

        Args:
            content: Template content as string
            template_name: Name or path of the template

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

        # Store in instance variables
        self.templates[template_name] = result
        self.url_references[template_name] = url_tags
        self.template_includes[template_name] = includes
        self.template_extends[template_name] = extends

        return result

    def find_all_templates(self, base_path: Path) -> list[Path]:
        """
        Find all Django template files in a directory.

        Args:
            base_path: Base directory to search

        Returns:
            List of Path objects for template files
        """
        template_extensions = [".html", ".txt", ".xml", ".svg"]
        templates = []

        for ext in template_extensions:
            templates.extend(base_path.rglob(f"*{ext}"))

        return templates

    def analyze_all_templates(self, base_path: Path) -> dict[str, dict]:
        """
        Analyze all templates in a directory tree.

        Args:
            base_path: Base directory containing templates

        Returns:
            Dictionary mapping template paths to their analysis results
        """
        templates = self.find_all_templates(base_path)

        for template_path in templates:
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
