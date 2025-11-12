"""Django management command for finding dead code."""

from pathlib import Path
from typing import Any

from django.conf import settings
from django.core.management.base import BaseCommand, CommandParser

from django_deadcode.analyzers import (
    ReverseAnalyzer,
    TemplateAnalyzer,
    URLAnalyzer,
    ViewAnalyzer,
)
from django_deadcode.reporters import ConsoleReporter, JSONReporter, MarkdownReporter


class Command(BaseCommand):
    """Django management command to analyze dead code in a Django project."""

    help = "Analyze Django project for dead code (unused URLs, views, and templates)"

    def add_arguments(self, parser: CommandParser) -> None:
        """Add command arguments."""
        parser.add_argument(
            "--format",
            type=str,
            choices=["console", "json", "markdown"],
            default="console",
            help="Output format for the report (default: console)",
        )
        parser.add_argument(
            "--output",
            type=str,
            help="Output file path (default: print to stdout)",
        )
        parser.add_argument(
            "--templates-dir",
            type=str,
            help="Directory to search for templates (default: all TEMPLATES dirs)",
        )
        parser.add_argument(
            "--apps",
            type=str,
            nargs="+",
            help="Specific apps to analyze (default: all installed apps)",
        )

    def handle(self, *args: Any, **options: Any) -> None:
        """Execute the command."""
        self.stdout.write(self.style.SUCCESS("Starting dead code analysis..."))

        # Initialize analyzers
        template_analyzer = TemplateAnalyzer()
        url_analyzer = URLAnalyzer()
        view_analyzer = ViewAnalyzer()
        reverse_analyzer = ReverseAnalyzer()

        # Analyze templates
        self.stdout.write("Analyzing templates...")
        template_dirs = self._get_template_dirs(options.get("templates_dir"))
        for template_dir in template_dirs:
            if template_dir.exists():
                template_analyzer.analyze_all_templates(template_dir)

        # Analyze URLs
        self.stdout.write("Analyzing URL patterns...")
        url_analyzer.analyze_url_patterns()

        # Analyze views
        self.stdout.write("Analyzing views...")
        app_dirs = self._get_app_dirs(options.get("apps"))
        for app_dir in app_dirs:
            if app_dir.exists():
                view_analyzer.analyze_all_views(app_dir)

        # Analyze reverse/redirect references
        self.stdout.write("Analyzing reverse/redirect references...")
        for app_dir in app_dirs:
            if app_dir.exists():
                reverse_analyzer.analyze_all_python_files(app_dir)

        # Compile analysis data
        self.stdout.write("Compiling analysis results...")
        analysis_data = self._compile_analysis_data(
            template_analyzer, url_analyzer, view_analyzer, reverse_analyzer
        )

        # Generate report
        report_format = options.get("format", "console")
        report = self._generate_report(analysis_data, report_format)

        # Output report
        output_file = options.get("output")
        if output_file:
            Path(output_file).write_text(report, encoding="utf-8")
            self.stdout.write(self.style.SUCCESS(f"Report written to: {output_file}"))
        else:
            self.stdout.write("\n" + report)

        # Print summary
        self._print_summary(analysis_data)

    def _get_template_dirs(self, custom_dir: str = None) -> list[Path]:
        """
        Get template directories to analyze.

        Args:
            custom_dir: Custom directory path

        Returns:
            List of Path objects for template directories
        """
        if custom_dir:
            return [Path(custom_dir)]

        template_dirs = []
        for template_config in settings.TEMPLATES:
            dirs = template_config.get("DIRS", [])
            for dir_path in dirs:
                template_dirs.append(Path(dir_path))

        # Also check for templates directories in each app
        if hasattr(settings, "INSTALLED_APPS"):
            from django.apps import apps

            for app_config in apps.get_app_configs():
                app_template_dir = Path(app_config.path) / "templates"
                if app_template_dir.exists():
                    template_dirs.append(app_template_dir)

        return template_dirs

    def _get_app_dirs(self, app_names: list[str] = None) -> list[Path]:
        """
        Get application directories to analyze.

        Args:
            app_names: List of specific app names to analyze

        Returns:
            List of Path objects for app directories
        """
        from django.apps import apps

        app_dirs = []
        app_configs = apps.get_app_configs()

        for app_config in app_configs:
            # Skip Django's built-in apps unless specifically requested
            if not app_names and app_config.name.startswith("django."):
                continue

            if app_names and app_config.name not in app_names:
                continue

            app_dirs.append(Path(app_config.path))

        return app_dirs

    def _compile_analysis_data(
        self,
        template_analyzer: TemplateAnalyzer,
        url_analyzer: URLAnalyzer,
        view_analyzer: ViewAnalyzer,
        reverse_analyzer: ReverseAnalyzer,
    ) -> dict[str, Any]:
        """
        Compile analysis data from all analyzers.

        Args:
            template_analyzer: Template analyzer instance
            url_analyzer: URL analyzer instance
            view_analyzer: View analyzer instance
            reverse_analyzer: Reverse analyzer instance

        Returns:
            Dictionary containing compiled analysis data
        """
        # Get all URL names and combine referenced URLs from templates and Python code
        all_url_names = url_analyzer.get_all_url_names()
        template_refs = template_analyzer.get_referenced_urls()
        reverse_refs = reverse_analyzer.get_referenced_urls()
        referenced_urls = template_refs | reverse_refs
        unreferenced_urls = url_analyzer.get_unreferenced_urls(referenced_urls)

        # Get template data
        all_templates = set(template_analyzer.templates.keys())
        template_usage = view_analyzer.get_all_view_templates()

        # Get potentially unused templates (not referenced by views)
        directly_referenced_templates = set(view_analyzer.template_usage.keys())
        potentially_unused = all_templates - directly_referenced_templates

        # Get template relationships
        template_relationships = template_analyzer.get_template_relationships()

        # Compile data
        analysis_data = {
            "summary": {
                "total_urls": len(all_url_names),
                "total_templates": len(all_templates),
                "total_views": len(template_usage),
                "unreferenced_urls_count": len(unreferenced_urls),
                "unused_templates_count": len(potentially_unused),
            },
            "unreferenced_urls": list(unreferenced_urls),
            "url_details": url_analyzer.url_patterns,
            "url_references": template_analyzer.get_url_references_by_template(),
            "template_usage": {k: list(v) for k, v in template_usage.items()},
            "unused_templates": list(potentially_unused),
            "template_relationships": template_relationships,
            "all_urls": list(all_url_names),
            "referenced_urls": list(referenced_urls),
            "dynamic_url_patterns": list(reverse_analyzer.get_dynamic_patterns()),
        }

        return analysis_data

    def _generate_report(self, analysis_data: dict[str, Any], format: str) -> str:
        """
        Generate report in specified format.

        Args:
            analysis_data: Compiled analysis data
            format: Output format

        Returns:
            Formatted report string
        """
        if format == "json":
            reporter = JSONReporter()
        elif format == "markdown":
            reporter = MarkdownReporter()
        else:
            reporter = ConsoleReporter()

        return reporter.generate_report(analysis_data)

    def _print_summary(self, analysis_data: dict[str, Any]) -> None:
        """
        Print a summary of the analysis.

        Args:
            analysis_data: Compiled analysis data
        """
        summary = analysis_data.get("summary", {})

        self.stdout.write("\n" + "=" * 60)
        self.stdout.write(self.style.SUCCESS("Analysis Complete!"))
        self.stdout.write("=" * 60)

        # Highlight potential issues
        unreferenced_count = summary.get("unreferenced_urls_count", 0)
        unused_templates_count = summary.get("unused_templates_count", 0)

        if unreferenced_count > 0:
            self.stdout.write(
                self.style.WARNING(
                    f"⚠ Found {unreferenced_count} unreferenced URL pattern(s)"
                )
            )

        if unused_templates_count > 0:
            self.stdout.write(
                self.style.WARNING(
                    f"⚠ Found {unused_templates_count} potentially unused template(s)"
                )
            )

        if unreferenced_count == 0 and unused_templates_count == 0:
            self.stdout.write(self.style.SUCCESS("✓ No obvious dead code detected!"))
