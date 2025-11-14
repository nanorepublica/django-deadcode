"""Analyzer for discovering views and their template usage."""

import ast
from pathlib import Path


class ViewAnalyzer:
    """Analyzes Django views and their template references."""

    def __init__(self) -> None:
        """Initialize the view analyzer."""
        self.views: dict[str, dict] = {}
        self.view_templates: dict[str, set[str]] = {}
        self.template_usage: dict[str, set[str]] = {}

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
        except (OSError, SyntaxError, UnicodeDecodeError):
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

            # Find variable assignments containing 'template' in the name
            elif isinstance(node, ast.Assign):
                self._process_template_variable_assignment(node, file_path)

            # Find get_template_names() method definitions
            elif isinstance(node, ast.FunctionDef):
                if node.name == "get_template_names":
                    self._process_get_template_names_method(node, file_path)

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
        elif isinstance(node.func, ast.Name) and node.func.id == "render_to_response":
            if node.args and isinstance(node.args[0], ast.Constant):
                template_name = node.args[0].value
                if isinstance(template_name, str):
                    self._add_template_reference(file_path, template_name)

    def _process_cbv(self, node: ast.ClassDef, file_path: str) -> None:
        """
        Process a class-based view to extract template_name or infer default template.

        Args:
            node: AST ClassDef node
            file_path: Path to the source file
        """
        class_name = node.name
        template_name = None

        # Look for explicit template_name attribute
        for item in node.body:
            if isinstance(item, ast.Assign):
                for target in item.targets:
                    if isinstance(target, ast.Name) and target.id == "template_name":
                        if isinstance(item.value, ast.Constant):
                            template_name = item.value.value

        # If explicit template_name is set, use it
        if template_name:
            view_path = f"{file_path}:{class_name}"
            self._add_template_reference(view_path, template_name)
        else:
            # Try to detect CBV type and generate implicit template name
            cbv_type = self._detect_cbv_type(node)
            if cbv_type:
                model_name = self._extract_model_from_cbv(node)
                app_label = self._infer_app_label(file_path)

                if model_name and app_label:
                    implicit_template = self._generate_cbv_template_name(
                        cbv_type, app_label, model_name
                    )
                    if implicit_template:
                        view_path = f"{file_path}:{class_name}"
                        self._add_template_reference(view_path, implicit_template)

    def _process_template_variable_assignment(
        self, node: ast.Assign, file_path: str
    ) -> None:
        """
        Process variable assignments containing 'template' in the name.

        Args:
            node: AST Assign node
            file_path: Path to the source file
        """
        # Check each target in the assignment
        for target in node.targets:
            if isinstance(target, ast.Name):
                # Check if variable name contains 'template' (case-insensitive)
                if "template" in target.id.lower():
                    # Extract string constants from the assignment
                    template_names = self._extract_string_constants(node.value)
                    for template_name in template_names:
                        self._add_template_reference(file_path, template_name)

    def _process_get_template_names_method(
        self, node: ast.FunctionDef, file_path: str
    ) -> None:
        """
        Process get_template_names() to extract templates from returns.

        Args:
            node: AST FunctionDef node
            file_path: Path to the source file
        """
        # Walk through the method body to find return statements
        for item in ast.walk(node):
            if isinstance(item, ast.Return) and item.value:
                # Extract template names from the return value
                template_names = self._extract_string_constants(item.value)
                for template_name in template_names:
                    self._add_template_reference(file_path, template_name)

    def _extract_string_constants(self, node: ast.AST) -> list[str]:
        """
        Extract string constants from an AST node.

        Handles:
        - Direct string constants: 'template.html'
        - List literals: ['template1.html', 'template2.html']

        Args:
            node: AST node to extract strings from

        Returns:
            List of extracted template name strings
        """
        templates = []

        # Handle direct string constant
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            templates.append(node.value)

        # Handle list literal
        elif isinstance(node, ast.List):
            for element in node.elts:
                if isinstance(element, ast.Constant) and isinstance(element.value, str):
                    templates.append(element.value)

        return templates

    def _detect_cbv_type(self, class_node: ast.ClassDef) -> str | None:
        """
        Determine if class is a Django CBV and return its type.

        Args:
            class_node: AST ClassDef node

        Returns:
            CBV type name or None if not recognized
        """
        # Check base classes for Django generic views
        cbv_types = {
            "ListView",
            "DetailView",
            "CreateView",
            "UpdateView",
            "DeleteView",
            "FormView",
            "TemplateView",
        }

        for base in class_node.bases:
            # Handle simple base class names like "ListView"
            if isinstance(base, ast.Name) and base.id in cbv_types:
                return base.id

            # Handle attribute access like "generic.ListView"
            elif isinstance(base, ast.Attribute) and base.attr in cbv_types:
                return base.attr

        return None

    def _extract_model_from_cbv(self, class_node: ast.ClassDef) -> str | None:
        """
        Extract model name from CBV class definition.

        Args:
            class_node: AST ClassDef node

        Returns:
            Lowercase model name or None if not found
        """
        # Look for model or queryset attributes
        for item in class_node.body:
            if isinstance(item, ast.Assign):
                for target in item.targets:
                    if isinstance(target, ast.Name):
                        # Check for model = ModelName
                        if target.id == "model":
                            model_name = self._extract_name_from_value(item.value)
                            if model_name:
                                return model_name.lower()

                        # Check for queryset = ModelName.objects.all()
                        elif target.id == "queryset":
                            model_name = self._extract_model_from_queryset(item.value)
                            if model_name:
                                return model_name.lower()

        return None

    def _extract_name_from_value(self, value_node: ast.AST) -> str | None:
        """
        Extract name from an AST value node.

        Args:
            value_node: AST node representing a value

        Returns:
            Name as string or None
        """
        if isinstance(value_node, ast.Name):
            return value_node.id
        return None

    def _extract_model_from_queryset(self, value_node: ast.AST) -> str | None:
        """
        Extract model name from a queryset expression like ModelName.objects.all().

        Args:
            value_node: AST node representing a queryset value

        Returns:
            Model name or None
        """
        # Handle ModelName.objects.all() or ModelName.objects.filter(...)
        if isinstance(value_node, ast.Call):
            if isinstance(value_node.func, ast.Attribute):
                # Check if it's calling a method on objects (e.g., .all(), .filter())
                if isinstance(value_node.func.value, ast.Attribute):
                    # value_node.func.value should be ModelName.objects
                    if value_node.func.value.attr == "objects":
                        # value_node.func.value.value should be ModelName
                        if isinstance(value_node.func.value.value, ast.Name):
                            return value_node.func.value.value.id

        # Handle simple ModelName.objects
        elif isinstance(value_node, ast.Attribute):
            if value_node.attr == "objects":
                if isinstance(value_node.value, ast.Name):
                    return value_node.value.id

        return None

    def _infer_app_label(self, file_path: str) -> str | None:
        """
        Infer Django app label from file path.

        Args:
            file_path: Path to the source file

        Returns:
            App label (directory name) or None if cannot be inferred
        """
        path = Path(file_path)
        parts = path.parts

        # Look for common Django app structure patterns
        # Pattern 1: /path/to/apps/<app_name>/views.py
        if "apps" in parts:
            apps_index = parts.index("apps")
            if apps_index + 1 < len(parts):
                return parts[apps_index + 1]

        # Pattern 2: /path/to/<app_name>/views.py (direct app directory)
        # Get the parent directory of views.py
        if path.name in ["views.py", "views"]:
            parent_dir = path.parent.name
            # Avoid treating project root or common directory names as app labels
            if parent_dir not in ["src", "project", "django", "app", "code"]:
                return parent_dir

        # Pattern 3: Get the directory immediately containing the file
        if len(parts) >= 2:
            return parts[-2]

        return None

    def _generate_cbv_template_name(
        self, cbv_type: str, app_label: str, model_name: str
    ) -> str | None:
        """
        Generate implicit template name based on Django CBV conventions.

        Args:
            cbv_type: Type of CBV (ListView, DetailView, etc.)
            app_label: App label
            model_name: Model name (lowercase)

        Returns:
            Template name or None
        """
        # Django CBV template naming conventions
        template_suffixes = {
            "ListView": "_list.html",
            "DetailView": "_detail.html",
            "CreateView": "_form.html",
            "UpdateView": "_form.html",
            "DeleteView": "_confirm_delete.html",
        }

        suffix = template_suffixes.get(cbv_type)
        if suffix:
            return f"{app_label}/{model_name}{suffix}"

        return None

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

    def get_templates_for_view(self, view_path: str) -> set[str]:
        """
        Get all templates used by a specific view.

        Args:
            view_path: Path or identifier for the view

        Returns:
            Set of template names
        """
        return self.view_templates.get(view_path, set())

    def get_views_for_template(self, template_name: str) -> set[str]:
        """
        Get all views that use a specific template.

        Args:
            template_name: Name of the template

        Returns:
            Set of view paths
        """
        return self.template_usage.get(template_name, set())

    def get_unused_templates(self, all_templates: set[str]) -> set[str]:
        """
        Find templates that are never referenced by views.

        Args:
            all_templates: Set of all template names in the project

        Returns:
            Set of unused template names
        """
        referenced_templates = set(self.template_usage.keys())
        return all_templates - referenced_templates

    def get_all_view_templates(self) -> dict[str, set[str]]:
        """
        Get all view-to-template mappings.

        Returns:
            Dictionary mapping view paths to template sets
        """
        return self.view_templates

    def get_template_statistics(self) -> dict:
        """
        Get statistics about template usage.

        Returns:
            Dictionary with template statistics
        """
        return {
            "total_views": len(self.view_templates),
            "total_templates_referenced": len(self.template_usage),
            "templates_per_view": {
                view: len(templates) for view, templates in self.view_templates.items()
            },
        }
