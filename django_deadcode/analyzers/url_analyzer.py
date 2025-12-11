"""Analyzer for discovering and analyzing Django URL patterns."""

from django.conf import settings
from django.urls import URLPattern, URLResolver, get_resolver
from django.urls.resolvers import RegexPattern, RoutePattern

from django_deadcode.utils import get_module_path, is_third_party_module


class URLAnalyzer:
    """Analyzes Django URL patterns and their relationships."""

    def __init__(self) -> None:
        """Initialize the URL analyzer."""
        self.url_patterns: dict[str, dict] = {}
        self.url_names: set[str] = set()
        self.url_to_view: dict[str, str] = {}

    def analyze_url_patterns(self, urlconf: str | None = None) -> dict[str, dict]:
        """
        Analyze all URL patterns in the project.

        Args:
            urlconf: URLconf module path (defaults to settings.ROOT_URLCONF)

        Returns:
            Dictionary mapping URL names to their details
        """
        if urlconf is None:
            urlconf = settings.ROOT_URLCONF

        resolver = get_resolver(urlconf)
        self._process_url_patterns(resolver.url_patterns, prefix="")

        return self.url_patterns

    def _process_url_patterns(
        self, patterns: list, prefix: str = "", namespace: str | None = None
    ) -> None:
        """
        Recursively process URL patterns.

        Args:
            patterns: List of URLPattern or URLResolver objects
            prefix: URL prefix from parent resolvers
            namespace: Current namespace
        """
        for pattern in patterns:
            if isinstance(pattern, URLResolver):
                # Handle included URL patterns
                new_prefix = prefix + str(pattern.pattern)
                new_namespace = (
                    f"{namespace}:{pattern.namespace}"
                    if namespace and pattern.namespace
                    else pattern.namespace or namespace
                )
                self._process_url_patterns(
                    pattern.url_patterns, prefix=new_prefix, namespace=new_namespace
                )
            elif isinstance(pattern, URLPattern):
                # Handle individual URL pattern
                self._process_url_pattern(pattern, prefix, namespace)

    def _process_url_pattern(
        self, pattern: URLPattern, prefix: str, namespace: str | None
    ) -> None:
        """
        Process a single URL pattern.

        Args:
            pattern: URLPattern object
            prefix: URL prefix
            namespace: Current namespace
        """
        # Get the pattern string
        if isinstance(pattern.pattern, RoutePattern):
            pattern_str = str(pattern.pattern)
        elif isinstance(pattern.pattern, RegexPattern):
            pattern_str = pattern.pattern.regex.pattern
        else:
            pattern_str = str(pattern.pattern)

        full_pattern = prefix + pattern_str

        # Get the view callable
        view = pattern.callback
        if view:
            view_name = f"{view.__module__}.{view.__name__}"
            module_path = get_module_path(view)
            is_third_party = is_third_party_module(view)
        else:
            view_name = "Unknown"
            module_path = "Unknown"
            is_third_party = False

        # Get the URL name
        url_name = pattern.name
        if url_name:
            if namespace:
                full_name = f"{namespace}:{url_name}"
            else:
                full_name = url_name

            self.url_names.add(full_name)
            self.url_to_view[full_name] = view_name

            self.url_patterns[full_name] = {
                "name": full_name,
                "pattern": full_pattern,
                "view": view_name,
                "namespace": namespace,
                "module_path": module_path,
                "is_third_party": is_third_party,
            }

    def get_all_url_names(self) -> set[str]:
        """
        Get all URL names defined in the project.

        Returns:
            Set of URL names
        """
        return self.url_names

    def get_view_for_url(self, url_name: str) -> str | None:
        """
        Get the view callable for a given URL name.

        Args:
            url_name: Name of the URL pattern

        Returns:
            View callable path or None
        """
        return self.url_to_view.get(url_name)

    def get_urls_for_view(self, view_name: str) -> list[str]:
        """
        Get all URL names that point to a specific view.

        Args:
            view_name: Full path to the view callable

        Returns:
            List of URL names
        """
        return [
            url_name for url_name, view in self.url_to_view.items() if view == view_name
        ]

    def get_third_party_namespaces(self) -> set[str]:
        """
        Get all namespaces that contain at least one third-party URL pattern.

        A namespace is considered third-party if ANY of its patterns
        are from third-party code.

        Returns:
            Set of third-party namespace names
        """
        third_party_namespaces = set()

        for url_name, details in self.url_patterns.items():
            if details.get("is_third_party", False):
                namespace = details.get("namespace")
                if namespace:
                    third_party_namespaces.add(namespace)

        return third_party_namespaces

    def get_unreferenced_urls(
        self, referenced_urls: set[str], excluded_namespaces: set[str] | None = None
    ) -> tuple[set[str], set[str]]:
        """
        Find URL patterns that are never referenced.

        Args:
            referenced_urls: Set of URL names that are referenced
            excluded_namespaces: Optional set of namespaces to exclude from results

        Returns:
            Tuple of (unreferenced_urls, excluded_namespaces_found)
            - unreferenced_urls: Set of unreferenced URL names
            - excluded_namespaces_found: Set of namespaces that were actually excluded
        """
        if excluded_namespaces is None:
            excluded_namespaces = set()

        # Find unreferenced URLs
        unreferenced = self.url_names - referenced_urls

        # Track which excluded namespaces actually had URLs removed
        excluded_namespaces_found = set()

        # Filter out URLs from excluded namespaces
        filtered_unreferenced = set()
        for url_name in unreferenced:
            url_details = self.url_patterns.get(url_name, {})
            namespace = url_details.get("namespace")
            module_path = url_details.get("module_path")

            # Check if URL should be excluded
            if namespace and namespace in excluded_namespaces:
                excluded_namespaces_found.add(namespace)
                continue

            # Check if URL without namespace should be excluded
            # (None in excluded_namespaces)
            if not namespace and None in excluded_namespaces:
                excluded_namespaces_found.add(None)
                continue

            if not namespace and module_path:
                if any(
                    module_path.startswith(excluded) for excluded in excluded_namespaces
                ):
                    excluded_namespaces_found.add(module_path)
                    continue

            filtered_unreferenced.add(url_name)

        return filtered_unreferenced, excluded_namespaces_found

    def get_url_statistics(self) -> dict:
        """
        Get statistics about URL patterns.

        Returns:
            Dictionary with URL statistics
        """
        view_counts: dict[str, int] = {}
        for view_name in self.url_to_view.values():
            view_counts[view_name] = view_counts.get(view_name, 0) + 1

        return {
            "total_urls": len(self.url_patterns),
            "total_views": len(set(self.url_to_view.values())),
            "urls_per_view": view_counts,
        }
