"""Tests for href to URL pattern matching functionality."""

from django_deadcode.utils.url_matching import (
    extract_static_prefix,
    find_matching_url_patterns,
    has_capture_groups,
    is_dynamic_href,
    match_href_to_pattern,
    normalize_path,
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

    # Tests for regex anchor handling (Task 1.1)
    def test_normalize_strips_caret_anchor(self):
        """Test that leading ^ anchor is stripped from patterns."""
        assert normalize_path("^about/") == "about/"

    def test_normalize_strips_dollar_anchor(self):
        """Test that trailing $ anchor is stripped from patterns."""
        assert normalize_path("about/$") == "about/"

    def test_normalize_strips_both_anchors(self):
        """Test that both ^ and $ anchors are stripped."""
        assert normalize_path("^about/$") == "about/"

    def test_normalize_strips_anchors_multi_segment(self):
        """Test anchor stripping on multi-segment paths."""
        assert normalize_path("^users/profile/$") == "users/profile/"

    # Tests for optional trailing slash handling
    def test_normalize_optional_slash_at_end(self):
        """Test that /? optional trailing slash is converted to /."""
        assert normalize_path("^about/?$") == "about/"

    def test_normalize_optional_slash_without_anchors(self):
        """Test optional slash handling without anchors."""
        assert normalize_path("about/?") == "about/"

    # Tests for embedded regex anchors (from nested includes with mixed path/re_path)
    def test_normalize_embedded_caret_anchor(self):
        """Test that embedded ^ anchor is stripped from middle of pattern.

        This happens when using: path('prefix/', include(...)) combined with
        re_path(r'^suffix/$', ...). The accumulated pattern becomes:
        'prefix/^suffix/$'
        """
        assert normalize_path("prefix/^suffix/$") == "prefix/suffix/"

    def test_normalize_embedded_dollar_anchor(self):
        """Test that embedded $ anchor is stripped from middle of pattern."""
        assert normalize_path("prefix/$suffix/") == "prefix/suffix/"

    def test_normalize_multiple_embedded_anchors(self):
        """Test normalization with multiple embedded anchors.

        This happens with deeply nested includes mixing path() and re_path().
        """
        assert normalize_path("a/^b/^c/$") == "a/b/c/"

    def test_normalize_real_world_nested_include_pattern(self):
        """Test the exact pattern from the reported bug.

        URL config: path('nutritionist/', include(...)) combined with
        re_path(r'^client/client_mfp_code/$', ...)
        """
        assert (
            normalize_path("nutritionist/^client/client_mfp_code/$")
            == "nutritionist/client/client_mfp_code/"
        )


class TestEmbeddedAnchorMatching:
    """Test suite for matching hrefs against patterns with embedded anchors.

    These tests cover the bug where nested include() statements with mixed
    path() and re_path() produce patterns with regex anchors in the middle,
    e.g., 'nutritionist/^client/mfp/$' instead of '^nutritionist/client/mfp/$'.
    """

    def test_match_embedded_caret_anchor(self):
        """Test href matches pattern with embedded ^ anchor."""
        href = "/prefix/suffix/"
        pattern = "prefix/^suffix/$"
        assert match_href_to_pattern(href, pattern) is True

    def test_match_real_world_nested_include(self):
        """Test the exact scenario from the reported bug."""
        href = "/nutritionist/client/client_mfp_code/"
        pattern = "nutritionist/^client/client_mfp_code/$"
        assert match_href_to_pattern(href, pattern) is True

    def test_match_multiple_embedded_anchors(self):
        """Test matching with multiple embedded anchors from deep nesting."""
        href = "/a/b/c/"
        pattern = "a/^b/^c/$"
        assert match_href_to_pattern(href, pattern) is True

    def test_integration_find_matching_patterns_with_embedded_anchors(self):
        """Integration test: find_matching_url_patterns with embedded anchors."""
        hrefs = {"/nutritionist/client/client_mfp_code/"}
        url_patterns = {
            "client_mfp_code": {
                "pattern": "nutritionist/^client/client_mfp_code/$",
                "name": "client_mfp_code",
            },
            "other_url": {
                "pattern": "other/path/",
                "name": "other_url",
            },
        }
        matched = find_matching_url_patterns(hrefs, url_patterns)
        assert "client_mfp_code" in matched
        assert "other_url" not in matched

    def test_no_false_match_with_similar_patterns(self):
        """Test that embedded anchor removal doesn't cause false matches."""
        href = "/prefix/suffix/"
        pattern = "prefix/^different/$"  # Different suffix
        assert match_href_to_pattern(href, pattern) is False


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


class TestCaptureGroupHandling:
    """Test suite for capture group detection and dynamic URL matching."""

    # Tests for has_capture_groups()
    def test_has_capture_groups_named(self):
        """Test detection of named capture groups (?P<name>...)."""
        assert has_capture_groups(r"^user/(?P<id>\d+)/$") is True

    def test_has_capture_groups_unnamed(self):
        """Test detection of unnamed capture groups (...)."""
        assert has_capture_groups(r"^user/(\d+)/$") is True

    def test_has_capture_groups_none(self):
        """Test that static patterns return False."""
        assert has_capture_groups("^about/$") is False

    def test_has_capture_groups_with_non_capturing(self):
        """Test detection of non-capturing groups (?:...)."""
        assert has_capture_groups(r"^user/(?:\d+)/$") is True

    # Tests for extract_static_prefix()
    def test_extract_static_prefix_simple(self):
        """Test extracting prefix before capture group."""
        assert extract_static_prefix(r"^user/(?P<id>\d+)/$") == "user/"

    def test_extract_static_prefix_nested(self):
        """Test extracting prefix from multi-segment pattern."""
        assert extract_static_prefix(r"^api/v1/users/(?P<id>\d+)/$") == "api/v1/users/"

    def test_extract_static_prefix_no_groups(self):
        """Test that pattern without groups returns full normalized path."""
        assert extract_static_prefix("^about/$") == "about/"

    def test_extract_static_prefix_group_at_start(self):
        """Test pattern with capture group at start returns empty prefix."""
        assert extract_static_prefix(r"^(?P<lang>[a-z]{2})/about/$") == ""

    # Tests for is_dynamic_href()
    def test_is_dynamic_href_with_template_var(self):
        """Test detection of Django template variable syntax."""
        assert is_dynamic_href("/user/{{ user.id }}/") is True

    def test_is_dynamic_href_static(self):
        """Test that static hrefs return False."""
        assert is_dynamic_href("/user/123/") is False


class TestMatchHrefToPatternEnhanced:
    """Test suite for enhanced href to pattern matching with regex support."""

    # Regex anchor matching (previously failing - the original bug)
    def test_match_with_caret_anchor(self):
        """Test href matches pattern with ^ anchor."""
        assert match_href_to_pattern("/about/", "^about/") is True

    def test_match_with_dollar_anchor(self):
        """Test href matches pattern with $ anchor."""
        assert match_href_to_pattern("/about/", "about/$") is True

    def test_match_with_both_anchors(self):
        """Test href matches pattern with both ^ and $ anchors."""
        assert match_href_to_pattern("/about/", "^about/$") is True

    # Optional trailing slash matching
    def test_match_optional_slash_with_slash(self):
        """Test href with trailing slash matches /? pattern."""
        assert match_href_to_pattern("/about/", "^about/?$") is True

    def test_match_optional_slash_without_slash(self):
        """Test href without trailing slash matches /? pattern."""
        assert match_href_to_pattern("/about", "^about/?$") is True

    # Dynamic URL matching
    def test_dynamic_pattern_matches_dynamic_href(self):
        """Test dynamic pattern matches href with {{ template syntax."""
        assert (
            match_href_to_pattern("/user/{{ user.id }}/", r"^user/(?P<id>\d+)/$")
            is True
        )

    def test_dynamic_pattern_no_match_static_href(self):
        """Test dynamic pattern does NOT match static href."""
        # Static href with actual number cannot match dynamic pattern
        assert match_href_to_pattern("/user/123/", r"^user/(?P<id>\d+)/$") is False

    def test_dynamic_pattern_with_prefix(self):
        """Test dynamic pattern with longer prefix matches."""
        assert (
            match_href_to_pattern(
                "/api/users/{{ user.pk }}/edit/", r"^api/users/(?P<pk>\d+)/edit/$"
            )
            is True
        )

    def test_dynamic_pattern_wrong_prefix(self):
        """Test dynamic pattern does NOT match wrong prefix."""
        assert (
            match_href_to_pattern("/wrong/{{ user.id }}/", r"^user/(?P<id>\d+)/$")
            is False
        )

    # Edge cases
    def test_multiple_capture_groups(self):
        """Test pattern with multiple capture groups."""
        # Should match based on static prefix only
        assert (
            match_href_to_pattern(
                "/user/{{ user.id }}/posts/{{ post.id }}/",
                r"^user/(?P<user_id>\d+)/posts/(?P<post_id>\d+)/$",
            )
            is True
        )

    def test_capture_group_at_start_matches_any_dynamic(self):
        """Test pattern with capture group at start (empty prefix)."""
        # Empty prefix means any dynamic href could match
        assert (
            match_href_to_pattern("/{{ lang }}/about/", r"^(?P<lang>[a-z]{2})/about/$")
            is True
        )

    def test_character_class_not_capture_group(self):
        """Test character classes [a-z] are NOT detected as capture groups."""
        # Character class is NOT a capture group - should be static match
        assert has_capture_groups("^files/[a-z]+.pdf$") is False
        # This is a static pattern, so exact match is needed
        assert match_href_to_pattern("/files/test.pdf", "^files/[a-z]+.pdf$") is False

    def test_non_capturing_group_is_dynamic(self):
        """Test non-capturing groups (?:...) are treated as dynamic."""
        assert (
            match_href_to_pattern(
                "/articles/{{ page }}/", r"^articles/(?:page-)?(?P<num>\d+)/$"
            )
            is True
        )


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
