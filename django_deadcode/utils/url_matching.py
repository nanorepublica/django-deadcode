"""URL pattern matching utilities for href-to-pattern matching."""

import re
from urllib.parse import urlparse

# Regex to detect capture groups in URL patterns
# Matches (?P<name>...), (?:...), or simple groups (...)
CAPTURE_GROUP_PATTERN = re.compile(r"\([^)]+\)")


def normalize_path(path: str) -> str:
    """
    Normalize a path for comparison.

    Handles both hrefs (e.g., '/about/') and URL patterns (e.g., '^about/$').
    Strips regex anchors from ANYWHERE in the pattern (not just start/end)
    and handles optional trailing slash patterns.

    This handles the case where nested include() statements with mixed path()
    and re_path() produce patterns with embedded anchors like:
    'prefix/^suffix/$' -> 'prefix/suffix/'

    Normalization steps:
    1. Strip ALL regex anchors (^ and $) from anywhere in the pattern
    2. Convert optional trailing slash (/?) to /
    3. Remove leading slash

    Args:
        path: URL path or pattern to normalize (e.g., '/about/', '^about/$',
              'prefix/^suffix/$')

    Returns:
        Normalized path suitable for comparison (e.g., 'about/')

    Examples:
        >>> normalize_path('/about/')
        'about/'
        >>> normalize_path('^about/$')
        'about/'
        >>> normalize_path('^about/?$')
        'about/'
        >>> normalize_path('/')
        ''
        >>> normalize_path('prefix/^suffix/$')
        'prefix/suffix/'
    """
    # Handle empty or root path
    if not path or path == "/":
        return ""

    # Strip ALL regex anchors (handles embedded anchors from nested includes)
    path = path.replace("^", "")
    path = path.replace("$", "")

    # Handle optional trailing slash - convert /? to /
    if path.endswith("/?"):
        path = path[:-1]  # Remove the ?, keep the /

    # Remove leading slash
    if path.startswith("/"):
        path = path[1:]

    return path


def has_capture_groups(pattern: str) -> bool:
    """
    Check if a URL pattern contains regex capture groups.

    Detects named groups (?P<name>...), non-capturing groups (?:...),
    and simple groups (...).

    Args:
        pattern: URL pattern string (may contain regex syntax)

    Returns:
        True if pattern contains capture groups, False otherwise

    Examples:
        >>> has_capture_groups(r"^user/(?P<id>\\d+)/$")
        True
        >>> has_capture_groups("^about/$")
        False
    """
    return bool(CAPTURE_GROUP_PATTERN.search(pattern))


def extract_static_prefix(pattern: str) -> str:
    """
    Extract the static prefix from a pattern before any capture group.

    The pattern is first normalized to remove regex anchors, then the
    portion before the first capture group is returned.

    Args:
        pattern: URL pattern string

    Returns:
        The static portion of the pattern before the first capture group,
        or the entire normalized pattern if no capture groups exist

    Examples:
        >>> extract_static_prefix(r"^user/(?P<id>\\d+)/$")
        'user/'
        >>> extract_static_prefix("^about/$")
        'about/'
        >>> extract_static_prefix(r"^(?P<lang>[a-z]{2})/about/$")
        ''
    """
    # First normalize the pattern to remove anchors
    normalized = normalize_path(pattern)

    # Find first capture group
    match = CAPTURE_GROUP_PATTERN.search(normalized)
    if match:
        return normalized[: match.start()]
    return normalized


def is_dynamic_href(href: str) -> bool:
    """
    Check if an href contains Django template variable syntax.

    Looks for {{ indicating template variable interpolation, which
    suggests the URL is being dynamically constructed.

    Args:
        href: Href value from a template

    Returns:
        True if href contains {{ indicating template variable interpolation

    Examples:
        >>> is_dynamic_href("/user/{{ user.id }}/")
        True
        >>> is_dynamic_href("/user/123/")
        False
    """
    return "{{" in href


def match_href_to_pattern(href: str, pattern: str) -> bool:
    """
    Check if an href matches a URL pattern.

    Uses normalized string matching. For patterns with capture groups,
    checks if dynamic hrefs (containing {{}}) match the static prefix.

    Query parameters and fragments are stripped from the href before matching.

    Args:
        href: The href from a template (e.g., '/about/', '/user/{{ id }}/')
        pattern: The URL pattern string (e.g., 'about/', '^user/(?P<id>\\d+)/$')

    Returns:
        True if the href matches the pattern, False otherwise

    Examples:
        >>> match_href_to_pattern('/about/', 'about/')
        True
        >>> match_href_to_pattern('/about/', '^about/$')
        True
        >>> match_href_to_pattern('/user/{{ user.id }}/', r'^user/(?P<id>\\d+)/$')
        True
        >>> match_href_to_pattern('/user/123/', r'^user/(?P<id>\\d+)/$')
        False
    """
    # Parse the href to remove query parameters and fragments
    parsed = urlparse(href)
    href_path = parsed.path

    # Check if pattern has capture groups (dynamic segments)
    if has_capture_groups(pattern):
        # For dynamic patterns, check if href:
        # 1. Contains template variable syntax ({{)
        # 2. Starts with the static prefix of the pattern
        if is_dynamic_href(href_path):
            static_prefix = extract_static_prefix(pattern)
            # Extract href portion before {{ and normalize it
            href_before_template = href_path.split("{{")[0]
            normalized_href = normalize_path(href_before_template)
            # Check if href starts with the static prefix
            return normalized_href.rstrip("/").startswith(static_prefix.rstrip("/"))
        # Static hrefs cannot match dynamic patterns
        return False

    # For static patterns, use exact matching
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
