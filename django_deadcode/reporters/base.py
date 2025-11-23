"""Base reporters for generating analysis output."""

import json
from abc import ABC, abstractmethod
from typing import Any


class BaseReporter(ABC):
    """Base class for all reporters."""

    def __init__(self, show_template_relationships: bool = False):
        """
        Initialize the reporter.

        Args:
            show_template_relationships: Whether to show template
                relationships in output
        """
        self.show_template_relationships = show_template_relationships

    @abstractmethod
    def generate_report(self, analysis_data: dict[str, Any]) -> str:
        """
        Generate a report from analysis data.

        Args:
            analysis_data: Dictionary containing analysis results

        Returns:
            Formatted report as string
        """
        pass


class ConsoleReporter(BaseReporter):
    """Reporter that outputs to console in human-readable format."""

    def generate_report(self, analysis_data: dict[str, Any]) -> str:
        """Generate a console-friendly report."""
        lines = []
        lines.append("=" * 80)
        lines.append("Django Dead Code Analysis Report")
        lines.append("=" * 80)
        lines.append("")

        # Summary
        lines.append("SUMMARY")
        lines.append("-" * 80)
        summary = analysis_data.get("summary", {})
        lines.append(f"Total URL patterns: {summary.get('total_urls', 0)}")
        lines.append(f"Total templates analyzed: {summary.get('total_templates', 0)}")
        lines.append(f"Total views found: {summary.get('total_views', 0)}")
        lines.append(f"Unreferenced URLs: {summary.get('unreferenced_urls_count', 0)}")
        lines.append(f"Unused templates: {summary.get('unused_templates_count', 0)}")
        lines.append("")

        # Unreferenced URLs
        unreferenced_urls = analysis_data.get("unreferenced_urls", [])
        excluded_namespaces = analysis_data.get("excluded_namespaces", [])

        if unreferenced_urls or excluded_namespaces:
            lines.append("UNREFERENCED URL PATTERNS")
            lines.append("-" * 80)

            # Add exclusion note if there are excluded namespaces
            if excluded_namespaces:
                # Filter out None values and format the list
                excluded_list = [ns for ns in excluded_namespaces if ns is not None]
                if excluded_list:
                    note = (
                        f"Note: Third-party namespaces excluded: "
                        f"{', '.join(excluded_list)}"
                    )
                    lines.append(note)
                    lines.append("")

            if unreferenced_urls:
                lines.append(
                    "These URL patterns are defined but never referenced in templates:"
                )
                lines.append("")
                for url_name in sorted(unreferenced_urls):
                    url_info = analysis_data.get("url_details", {}).get(url_name, {})
                    view = url_info.get("view", "Unknown")
                    pattern = url_info.get("pattern", "Unknown")
                    lines.append(f"  • {url_name}")
                    lines.append(f"    View: {view}")
                    lines.append(f"    Pattern: {pattern}")
                    lines.append("")
            elif excluded_namespaces:
                lines.append("All unreferenced URLs were from excluded namespaces.")
                lines.append("")

        # Unused templates
        unused_templates = analysis_data.get("unused_templates", [])
        if unused_templates:
            lines.append("POTENTIALLY UNUSED TEMPLATES")
            lines.append("-" * 80)
            lines.append(
                "These templates are not directly referenced by views "
                "(may be included/extended):"
            )
            lines.append("")
            for template in sorted(unused_templates):
                lines.append(f"  • {template}")
            lines.append("")

        # Template relationships - only show if flag is enabled
        if self.show_template_relationships:
            template_relationships = analysis_data.get("template_relationships", {})
            includes = template_relationships.get("includes", {})
            extends = template_relationships.get("extends", {})

            if includes or extends:
                lines.append("TEMPLATE RELATIONSHIPS")
                lines.append("-" * 80)

                if extends:
                    lines.append("Extends:")
                    for template, parents in sorted(extends.items()):
                        if parents:
                            for parent in sorted(parents):
                                lines.append(f"  {template} → {parent}")
                    lines.append("")

                if includes:
                    lines.append("Includes:")
                    for template, included in sorted(includes.items()):
                        if included:
                            for inc in sorted(included):
                                lines.append(f"  {template} → {inc}")
                    lines.append("")

        lines.append("=" * 80)
        return "\n".join(lines)


class JSONReporter(BaseReporter):
    """Reporter that outputs JSON format."""

    def generate_report(self, analysis_data: dict[str, Any]) -> str:
        """Generate a JSON report."""
        # Convert sets to lists for JSON serialization
        serializable_data = self._make_serializable(analysis_data)

        # Only include relationships if flag is enabled
        if not self.show_template_relationships:
            serializable_data.pop("template_relationships", None)

        return json.dumps(serializable_data, indent=2)

    def _make_serializable(self, obj: Any) -> Any:
        """
        Convert sets to lists for JSON serialization.

        Args:
            obj: Object to make serializable

        Returns:
            Serializable version of the object
        """
        if isinstance(obj, set):
            return sorted(list(obj))
        elif isinstance(obj, dict):
            return {key: self._make_serializable(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self._make_serializable(item) for item in obj]
        else:
            return obj


class MarkdownReporter(BaseReporter):
    """Reporter that outputs Markdown format."""

    def generate_report(self, analysis_data: dict[str, Any]) -> str:
        """Generate a Markdown report."""
        lines = []
        lines.append("# Django Dead Code Analysis Report")
        lines.append("")

        # Summary
        lines.append("## Summary")
        lines.append("")
        summary = analysis_data.get("summary", {})
        lines.append(f"- **Total URL patterns:** {summary.get('total_urls', 0)}")
        lines.append(
            f"- **Total templates analyzed:** {summary.get('total_templates', 0)}"
        )
        lines.append(f"- **Total views found:** {summary.get('total_views', 0)}")
        lines.append(
            f"- **Unreferenced URLs:** {summary.get('unreferenced_urls_count', 0)}"
        )
        lines.append(
            f"- **Unused templates:** {summary.get('unused_templates_count', 0)}"
        )
        lines.append("")

        # Unreferenced URLs
        unreferenced_urls = analysis_data.get("unreferenced_urls", [])
        excluded_namespaces = analysis_data.get("excluded_namespaces", [])

        if unreferenced_urls or excluded_namespaces:
            lines.append("## Unreferenced URL Patterns")
            lines.append("")

            # Add exclusion note if there are excluded namespaces
            if excluded_namespaces:
                # Filter out None values and format the list
                excluded_list = [ns for ns in excluded_namespaces if ns is not None]
                if excluded_list:
                    note = (
                        f"**Note:** Third-party namespaces excluded: "
                        f"{', '.join(excluded_list)}"
                    )
                    lines.append(note)
                    lines.append("")

            if unreferenced_urls:
                lines.append(
                    "These URL patterns are defined but never referenced in templates:"
                )
                lines.append("")
                for url_name in sorted(unreferenced_urls):
                    url_info = analysis_data.get("url_details", {}).get(url_name, {})
                    view = url_info.get("view", "Unknown")
                    pattern = url_info.get("pattern", "Unknown")
                    lines.append(f"### `{url_name}`")
                    lines.append(f"- **View:** `{view}`")
                    lines.append(f"- **Pattern:** `{pattern}`")
                    lines.append("")
            elif excluded_namespaces:
                lines.append("All unreferenced URLs were from excluded namespaces.")
                lines.append("")

        # Unused templates
        unused_templates = analysis_data.get("unused_templates", [])
        if unused_templates:
            lines.append("## Potentially Unused Templates")
            lines.append("")
            lines.append(
                "These templates are not directly referenced by views "
                "(may be included/extended):"
            )
            lines.append("")
            for template in sorted(unused_templates):
                lines.append(f"- `{template}`")
            lines.append("")

        # Template relationships - only show if flag is enabled
        if self.show_template_relationships:
            template_relationships = analysis_data.get("template_relationships", {})
            includes = template_relationships.get("includes", {})
            extends = template_relationships.get("extends", {})

            if includes or extends:
                lines.append("## Template Relationships")
                lines.append("")

                if extends:
                    lines.append("### Extends")
                    lines.append("")
                    for template, parents in sorted(extends.items()):
                        if parents:
                            for parent in sorted(parents):
                                lines.append(f"- `{template}` → `{parent}`")
                    lines.append("")

                if includes:
                    lines.append("### Includes")
                    lines.append("")
                    for template, included in sorted(includes.items()):
                        if included:
                            for inc in sorted(included):
                                lines.append(f"- `{template}` → `{inc}`")
                    lines.append("")

        return "\n".join(lines)
