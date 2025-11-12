"""Analyzer for discovering reverse() and redirect() URL references in Python code."""

import ast
from pathlib import Path


class ReverseAnalyzer:
    """
    Analyzes Python files to detect URL references via reverse() and redirect() calls.

    This analyzer uses AST parsing to find programmatic URL references in Django code,
    including:
    - reverse('url-name')
    - reverse_lazy('url-name')
    - redirect('url-name')
    - HttpResponseRedirect(reverse('url-name'))

    Dynamic URL patterns (f-strings, concatenation, variables) are detected but
    flagged separately for manual review rather than being added to referenced URLs.
    """

    def __init__(self) -> None:
        """Initialize the reverse analyzer."""
        self.referenced_urls: set[str] = set()
        self.dynamic_patterns: set[str] = set()

    def analyze_python_file(self, file_path: Path) -> None:
        """
        Analyze a Python file for reverse/redirect URL references.

        This method parses the Python file using AST and extracts URL names from
        reverse(), reverse_lazy(), redirect(), and HttpResponseRedirect() calls.

        Files that cannot be parsed (due to syntax errors, encoding issues, or I/O
        errors) are silently skipped to avoid crashing the analysis.

        Args:
            file_path: Path to the Python file to analyze
        """
        try:
            content = file_path.read_text(encoding="utf-8")
            tree = ast.parse(content, filename=str(file_path))
            self._process_ast(tree, str(file_path))
        except (OSError, SyntaxError, UnicodeDecodeError):
            # Skip files that can't be parsed - don't crash, don't log
            pass

    def analyze_all_python_files(self, base_path: Path) -> None:
        """
        Analyze all Python files in a directory tree for URL references.

        This method recursively scans for .py files and analyzes each one,
        excluding migration files and __pycache__ directories.

        Args:
            base_path: Base directory to search for Python files
        """
        # Find all Python files recursively
        python_files = list(base_path.rglob("*.py"))

        for py_file in python_files:
            # Skip migrations and __pycache__
            if "migrations" in py_file.parts or "__pycache__" in py_file.parts:
                continue
            self.analyze_python_file(py_file)

    def get_referenced_urls(self) -> set[str]:
        """
        Get all URL names referenced in the analyzed Python files.

        Returns:
            Set of URL name strings found in reverse/redirect calls
        """
        return self.referenced_urls

    def get_dynamic_patterns(self) -> set[str]:
        """
        Get all dynamic URL patterns that need manual review.

        Dynamic patterns include f-strings, concatenated strings, and variables
        where the URL name cannot be statically determined.

        Returns:
            Set of dynamic pattern descriptions
        """
        return self.dynamic_patterns

    def _process_ast(self, tree: ast.AST, file_path: str) -> None:
        """
        Process an AST tree to find reverse/redirect calls.

        This method walks all nodes in the AST and processes Call nodes to
        extract URL names from Django's URL reversal functions.

        Args:
            tree: AST tree from parsed Python file
            file_path: Path to the source file (for debugging)
        """
        for node in ast.walk(tree):
            # Find function calls
            if isinstance(node, ast.Call):
                self._process_call_node(node, file_path)

    def _process_call_node(self, node: ast.Call, file_path: str) -> None:
        """
        Process a Call node to extract URL names from reverse/redirect calls.

        This method handles several patterns:
        1. reverse('url-name') - Direct reverse call
        2. reverse_lazy('url-name') - Lazy reverse call
        3. redirect('url-name') - Redirect shortcut
        4. HttpResponseRedirect(reverse('url-name')) - Nested pattern
        5. reverse(viewname='url-name') - Keyword argument

        Method calls like self.reverse() are ignored by checking that the
        function is an ast.Name node (not ast.Attribute).

        Args:
            node: AST Call node to process
            file_path: Path to the source file (for debugging)
        """
        # Only process direct function calls, not method calls
        # This ignores self.reverse(), list.reverse(), etc.
        if not isinstance(node.func, ast.Name):
            return

        func_name = node.func.id

        # Check for reverse(), reverse_lazy(), or redirect()
        if func_name in ("reverse", "reverse_lazy", "redirect"):
            self._extract_url_from_call(node)

        # Check for HttpResponseRedirect(reverse(...))
        elif func_name == "HttpResponseRedirect":
            self._extract_url_from_http_response_redirect(node)

    def _extract_url_from_call(self, node: ast.Call) -> None:
        """
        Extract URL name from reverse/redirect call arguments.

        This handles both positional and keyword arguments:
        - reverse('url-name') - First positional argument
        - reverse(viewname='url-name') - viewname keyword argument

        Args:
            node: AST Call node for reverse/reverse_lazy/redirect
        """
        url_name = None

        # Check positional arguments (first argument is the URL name)
        if node.args and len(node.args) > 0:
            url_name = self._extract_string_value(node.args[0])

        # Check keyword arguments (viewname= keyword)
        if url_name is None:
            for keyword in node.keywords:
                if keyword.arg == "viewname":
                    url_name = self._extract_string_value(keyword.value)
                    break

        # Add to referenced URLs if we found a static string
        if url_name is not None:
            if isinstance(url_name, str):
                self.referenced_urls.add(url_name)
            # If it's a marker for dynamic pattern, it was already added to
            # dynamic_patterns

    def _extract_url_from_http_response_redirect(self, node: ast.Call) -> None:
        """
        Extract URL name from HttpResponseRedirect(reverse(...)) pattern.

        This handles the nested pattern where reverse() is called inside
        HttpResponseRedirect():
        - HttpResponseRedirect(reverse('url-name'))
        - HttpResponseRedirect(reverse_lazy('url-name'))

        Args:
            node: AST Call node for HttpResponseRedirect
        """
        # Check if the first argument is a reverse() or reverse_lazy() call
        if node.args and len(node.args) > 0:
            first_arg = node.args[0]

            # Check if it's a nested Call node
            if isinstance(first_arg, ast.Call):
                # Check if it's a reverse or reverse_lazy call
                if isinstance(first_arg.func, ast.Name) and first_arg.func.id in (
                    "reverse",
                    "reverse_lazy",
                ):
                    # Extract the URL name from the nested call
                    self._extract_url_from_call(first_arg)

    def _extract_string_value(self, node: ast.AST) -> str | None:
        """
        Extract a string value from an AST node.

        This handles:
        - ast.Constant: Static string literals ('url-name')
        - ast.JoinedStr: F-strings (f'app:{action}') - flagged as dynamic
        - ast.BinOp: String concatenation ('prefix_' + var) - flagged as dynamic
        - Other: Variables, function calls, etc. - flagged as dynamic

        Args:
            node: AST node that might contain a string value

        Returns:
            String value if it's a static constant, None if dynamic
            (dynamic patterns are added to self.dynamic_patterns)
        """
        # Static string constant
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            return node.value

        # F-string (dynamic)
        elif isinstance(node, ast.JoinedStr):
            self.dynamic_patterns.add("<dynamic:f-string>")
            return None

        # String concatenation (dynamic)
        elif isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
            self.dynamic_patterns.add("<dynamic:concatenation>")
            return None

        # Variable or other dynamic reference
        else:
            self.dynamic_patterns.add("<dynamic:variable>")
            return None
