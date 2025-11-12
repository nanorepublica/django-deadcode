"""Analyzer for discovering and analyzing Django URL patterns."""

from django.conf import settings
from django.urls import URLPattern, URLResolver, get_resolver
from django.urls.resolvers import RegexPattern, RoutePattern


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
        else:
            view_name = "Unknown"

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

    def get_unreferenced_urls(self, referenced_urls: set[str]) -> set[str]:
        """
        Find URL patterns that are never referenced.

        Args:
            referenced_urls: Set of URL names that are referenced

        Returns:
            Set of unreferenced URL names
        """
        return self.url_names - referenced_urls

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
