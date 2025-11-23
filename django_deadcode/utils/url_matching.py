"""URL pattern matching utilities for href-to-pattern matching."""

from urllib.parse import urlparse


def normalize_path(path: str) -> str:
    """
    Normalize a path for comparison.

    Removes leading slash and keeps trailing slash for consistency.
    Query parameters and fragments are preserved.

    Args:
        path: URL path to normalize (e.g., '/about/', 'about/', '/about')

    Returns:
        Normalized path (e.g., 'about/')

    Examples:
        >>> normalize_path('/about/')
        'about/'
        >>> normalize_path('/users/profile/')
        'users/profile/'
        >>> normalize_path('/')
        ''
    """
    # Handle empty or root path
    if not path or path == "/":
        return ""

    # Remove leading slash
    if path.startswith("/"):
        path = path[1:]

    return path


def match_href_to_pattern(href: str, pattern: str) -> bool:
    """
    Check if an href matches a URL pattern.

    Uses simple string matching after normalizing both the href and pattern.
    Query parameters and fragments are stripped from the href before matching.

    Args:
        href: The href from a template (e.g., '/about/', '/search/?q=test')
        pattern: The URL pattern string (e.g., 'about/', 'search/')

    Returns:
        True if the href matches the pattern, False otherwise

    Examples:
        >>> match_href_to_pattern('/about/', 'about/')
        True
        >>> match_href_to_pattern('/about/', 'about')
        True
        >>> match_href_to_pattern('/about/', 'contact/')
        False
    """
    # Parse the href to remove query parameters and fragments
    parsed = urlparse(href)
    href_path = parsed.path

    # Normalize both paths
    normalized_href = normalize_path(href_path)
    normalized_pattern = normalize_path(pattern)

    # For exact matching, we need to handle trailing slashes flexibly
    # Remove trailing slashes from both for comparison
    href_clean = normalized_href.rstrip("/")
    pattern_clean = normalized_pattern.rstrip("/")

    # Match if they're equal (case-sensitive)
    return href_clean == pattern_clean


def find_matching_url_patterns(
    hrefs: set[str], url_patterns: dict[str, dict]
) -> set[str]:
    """
    Find all URL pattern names that match the given hrefs.

    Args:
        hrefs: Set of internal hrefs from templates (e.g., {'/about/', '/contact/'})
        url_patterns: Dictionary of URL patterns from URLAnalyzer
                     Keys are pattern names, values are dicts with 'pattern' field

    Returns:
        Set of URL pattern names that matched at least one href

    Examples:
        >>> hrefs = {'/about/', '/contact/'}
        >>> patterns = {
        ...     'about': {'pattern': 'about/', 'name': 'about'},
        ...     'contact': {'pattern': 'contact/', 'name': 'contact'},
        ... }
        >>> find_matching_url_patterns(hrefs, patterns)
        {'about', 'contact'}
    """
    matched_patterns = set()

    for url_name, url_info in url_patterns.items():
        pattern = url_info.get("pattern", "")

        # Check if any href matches this pattern
        for href in hrefs:
            if match_href_to_pattern(href, pattern):
                matched_patterns.add(url_name)
                break  # No need to check other hrefs for this pattern

    return matched_patterns
