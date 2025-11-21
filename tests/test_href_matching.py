"""Tests for href to URL pattern matching functionality."""

import pytest
from django_deadcode.utils.url_matching import (
    normalize_path,
    match_href_to_pattern,
    find_matching_url_patterns,
)


class TestPathNormalization:
    """Test suite for path normalization."""

    def test_normalize_removes_leading_slash(self):
        """Test that leading slash is removed."""
        assert normalize_path("/about/") == "about/"

    def test_normalize_keeps_trailing_slash(self):
        """Test that trailing slash is kept."""
        assert normalize_path("/about/") == "about/"

    def test_normalize_handles_no_slashes(self):
        """Test normalization of path without slashes."""
        assert normalize_path("about") == "about"

    def test_normalize_handles_multiple_segments(self):
        """Test normalization of multi-segment path."""
        assert normalize_path("/users/profile/") == "users/profile/"

    def test_normalize_empty_path(self):
        """Test normalization of empty path."""
        assert normalize_path("") == ""

    def test_normalize_root_path(self):
        """Test normalization of root path /."""
        assert normalize_path("/") == ""


class TestHrefToPatternMatching:
    """Test suite for matching hrefs to URL patterns."""

    def test_simple_match(self):
        """Test /about/ matches pattern about/."""
        assert match_href_to_pattern("/about/", "about/")

    def test_multi_segment_match(self):
        """Test /users/profile/ matches pattern users/profile/."""
        assert match_href_to_pattern("/users/profile/", "users/profile/")

    def test_match_with_trailing_slash_difference(self):
        """Test /about/ matches pattern about (without trailing slash)."""
        assert match_href_to_pattern("/about/", "about")

    def test_match_without_trailing_slash(self):
        """Test /about matches pattern about/."""
        assert match_href_to_pattern("/about", "about/")

    def test_no_match_different_paths(self):
        """Test that /about/ does not match /contact/."""
        assert not match_href_to_pattern("/about/", "contact/")

    def test_no_match_partial_path(self):
        """Test that /user/ does not match users/ (partial match)."""
        assert not match_href_to_pattern("/user/", "users/")

    def test_no_match_substring(self):
        """Test that /user/ does not match /users/profile/."""
        assert not match_href_to_pattern("/user/", "users/profile/")

    def test_match_root_path(self):
        """Test / matches empty pattern."""
        assert match_href_to_pattern("/", "")

    def test_match_with_query_parameters(self):
        """Test that query parameters don't affect matching."""
        # Query params should be stripped before matching
        assert match_href_to_pattern("/search/?q=test", "search/")

    def test_match_with_fragment(self):
        """Test that fragments don't affect matching."""
        # Fragments should be stripped before matching
        assert match_href_to_pattern("/page/#section", "page/")

    def test_case_sensitive_match(self):
        """Test that matching is case-sensitive."""
        assert not match_href_to_pattern("/About/", "about/")


class TestFindMatchingPatterns:
    """Test suite for finding matching URL patterns from hrefs."""

    def test_find_single_match(self):
        """Test finding a single matching URL pattern."""
        hrefs = {"/about/"}
        url_patterns = {
            "about": {"pattern": "about/", "name": "about"},
            "contact": {"pattern": "contact/", "name": "contact"},
        }

        matches = find_matching_url_patterns(hrefs, url_patterns)
        assert "about" in matches
        assert "contact" not in matches

    def test_find_multiple_matches(self):
        """Test finding multiple matching URL patterns."""
        hrefs = {"/about/", "/contact/"}
        url_patterns = {
            "about": {"pattern": "about/", "name": "about"},
            "contact": {"pattern": "contact/", "name": "contact"},
            "services": {"pattern": "services/", "name": "services"},
        }

        matches = find_matching_url_patterns(hrefs, url_patterns)
        assert "about" in matches
        assert "contact" in matches
        assert "services" not in matches
        assert len(matches) == 2

    def test_no_matches(self):
        """Test when no hrefs match any patterns."""
        hrefs = {"/unknown/"}
        url_patterns = {
            "about": {"pattern": "about/", "name": "about"},
            "contact": {"pattern": "contact/", "name": "contact"},
        }

        matches = find_matching_url_patterns(hrefs, url_patterns)
        assert len(matches) == 0

    def test_empty_hrefs(self):
        """Test with empty hrefs set."""
        hrefs = set()
        url_patterns = {
            "about": {"pattern": "about/", "name": "about"},
        }

        matches = find_matching_url_patterns(hrefs, url_patterns)
        assert len(matches) == 0

    def test_empty_patterns(self):
        """Test with empty URL patterns dict."""
        hrefs = {"/about/"}
        url_patterns = {}

        matches = find_matching_url_patterns(hrefs, url_patterns)
        assert len(matches) == 0

    def test_match_with_namespace(self):
        """Test matching namespaced URL patterns."""
        hrefs = {"/admin/login/"}
        url_patterns = {
            "admin:login": {"pattern": "admin/login/", "name": "admin:login"},
            "admin:logout": {"pattern": "admin/logout/", "name": "admin:logout"},
        }

        matches = find_matching_url_patterns(hrefs, url_patterns)
        assert "admin:login" in matches
        assert "admin:logout" not in matches

    def test_one_href_matches_multiple_patterns(self):
        """Test that one href can match multiple patterns (rare but possible)."""
        hrefs = {"/api/v1/"}
        url_patterns = {
            "api_v1": {"pattern": "api/v1/", "name": "api_v1"},
            "api_v1_alt": {"pattern": "api/v1/", "name": "api_v1_alt"},
        }

        matches = find_matching_url_patterns(hrefs, url_patterns)
        # Both patterns have the same path, so both should match
        assert "api_v1" in matches
        assert "api_v1_alt" in matches
        assert len(matches) == 2
