"""Analyzer for discovering views and their template usage."""

import ast
import inspect
from pathlib import Path
from typing import Dict, List, Optional, Set

from django.apps import apps
from django.views.generic import TemplateView


class ViewAnalyzer:
    """Analyzes Django views and their template references."""

    def __init__(self) -> None:
        """Initialize the view analyzer."""
        self.views: Dict[str, Dict] = {}
        self.view_templates: Dict[str, Set[str]] = {}
        self.template_usage: Dict[str, Set[str]] = {}

    def analyze_view_file(self, file_path: Path) -> None:
        """
        Analyze a Python file containing views.

        Args:
            file_path: Path to the Python file
        """
        try:
            content = file_path.read_text(encoding="utf-8")
            tree = ast.parse(content, filename=str(file_path))
            self._process_ast(tree, str(file_path))
        except (IOError, SyntaxError, UnicodeDecodeError):
            # Skip files that can't be parsed
            pass

    def _process_ast(self, tree: ast.AST, file_path: str) -> None:
        """
        Process an AST to find template references.

        Args:
            tree: AST tree
            file_path: Path to the source file
        """
        for node in ast.walk(tree):
            # Find render() calls
            if isinstance(node, ast.Call):
                self._process_render_call(node, file_path)

            # Find class-based views with template_name
            elif isinstance(node, ast.ClassDef):
                self._process_cbv(node, file_path)

    def _process_render_call(self, node: ast.Call, file_path: str) -> None:
        """
        Process a render() function call to extract template name.

        Args:
            node: AST Call node
            file_path: Path to the source file
        """
        # Check if this is a render call
        if isinstance(node.func, ast.Name) and node.func.id == "render":
            # The second argument is usually the template name
            if len(node.args) >= 2 and isinstance(node.args[1], ast.Constant):
                template_name = node.args[1].value
                if isinstance(template_name, str):
                    self._add_template_reference(file_path, template_name)

        # Also check for render_to_response
        elif (
            isinstance(node.func, ast.Name) and node.func.id == "render_to_response"
        ):
            if node.args and isinstance(node.args[0], ast.Constant):
                template_name = node.args[0].value
                if isinstance(template_name, str):
                    self._add_template_reference(file_path, template_name)

    def _process_cbv(self, node: ast.ClassDef, file_path: str) -> None:
        """
        Process a class-based view to extract template_name.

        Args:
            node: AST ClassDef node
            file_path: Path to the source file
        """
        class_name = node.name
        template_name = None

        # Look for template_name attribute
        for item in node.body:
            if isinstance(item, ast.Assign):
                for target in item.targets:
                    if isinstance(target, ast.Name) and target.id == "template_name":
                        if isinstance(item.value, ast.Constant):
                            template_name = item.value.value

        if template_name:
            view_path = f"{file_path}:{class_name}"
            self._add_template_reference(view_path, template_name)

    def _add_template_reference(self, view_path: str, template_name: str) -> None:
        """
        Add a template reference for a view.

        Args:
            view_path: Path or identifier for the view
            template_name: Name of the template
        """
        if view_path not in self.view_templates:
            self.view_templates[view_path] = set()
        self.view_templates[view_path].add(template_name)

        if template_name not in self.template_usage:
            self.template_usage[template_name] = set()
        self.template_usage[template_name].add(view_path)

    def analyze_all_views(self, base_path: Path) -> None:
        """
        Analyze all Python files in a directory for views.

        Args:
            base_path: Base directory to search
        """
        # Find all Python files (typically in views.py or views/ directory)
        python_files = list(base_path.rglob("*.py"))

        for py_file in python_files:
            # Skip migrations and __pycache__
            if "migrations" in py_file.parts or "__pycache__" in py_file.parts:
                continue
            self.analyze_view_file(py_file)

    def get_templates_for_view(self, view_path: str) -> Set[str]:
        """
        Get all templates used by a specific view.

        Args:
            view_path: Path or identifier for the view

        Returns:
            Set of template names
        """
        return self.view_templates.get(view_path, set())

    def get_views_for_template(self, template_name: str) -> Set[str]:
        """
        Get all views that use a specific template.

        Args:
            template_name: Name of the template

        Returns:
            Set of view paths
        """
        return self.template_usage.get(template_name, set())

    def get_unused_templates(self, all_templates: Set[str]) -> Set[str]:
        """
        Find templates that are never referenced by views.

        Args:
            all_templates: Set of all template names in the project

        Returns:
            Set of unused template names
        """
        referenced_templates = set(self.template_usage.keys())
        return all_templates - referenced_templates

    def get_all_view_templates(self) -> Dict[str, Set[str]]:
        """
        Get all view-to-template mappings.

        Returns:
            Dictionary mapping view paths to template sets
        """
        return self.view_templates

    def get_template_statistics(self) -> Dict:
        """
        Get statistics about template usage.

        Returns:
            Dictionary with template statistics
        """
        return {
            "total_views": len(self.view_templates),
            "total_templates_referenced": len(self.template_usage),
            "templates_per_view": {
                view: len(templates)
                for view, templates in self.view_templates.items()
            },
        }
