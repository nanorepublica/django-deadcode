"""Tests for template href extraction functionality."""

from django_deadcode.analyzers import TemplateAnalyzer


class TestTemplateHrefExtraction:
    """Test suite for href extraction from templates."""

    def test_extract_internal_href(self):
        """Test extraction of internal href like /about/."""
        content = '<a href="/about/">About</a>'
        analyzer = TemplateAnalyzer()
        result = analyzer._analyze_template_content(content, "test.html")

        assert "/about/" in result["hrefs"]

    def test_exclude_external_https_href(self):
        """Test that external https:// hrefs are excluded."""
        content = '<a href="https://example.com">External</a>'
        analyzer = TemplateAnalyzer()
        result = analyzer._analyze_template_content(content, "test.html")

        assert "https://example.com" not in result["hrefs"]
        assert len(result["hrefs"]) == 0

    def test_exclude_external_http_href(self):
        """Test that external http:// hrefs are excluded."""
        content = '<a href="http://example.com">External</a>'
        analyzer = TemplateAnalyzer()
        result = analyzer._analyze_template_content(content, "test.html")

        assert "http://example.com" not in result["hrefs"]
        assert len(result["hrefs"]) == 0

    def test_exclude_protocol_relative_href(self):
        """Test that protocol-relative // hrefs are excluded."""
        content = '<a href="//cdn.example.com/script.js">CDN</a>'
        analyzer = TemplateAnalyzer()
        result = analyzer._analyze_template_content(content, "test.html")

        assert "//cdn.example.com/script.js" not in result["hrefs"]
        assert len(result["hrefs"]) == 0

    def test_exclude_mailto_href(self):
        """Test that mailto: hrefs are excluded."""
        content = '<a href="mailto:test@example.com">Email</a>'
        analyzer = TemplateAnalyzer()
        result = analyzer._analyze_template_content(content, "test.html")

        assert "mailto:test@example.com" not in result["hrefs"]
        assert len(result["hrefs"]) == 0

    def test_exclude_tel_href(self):
        """Test that tel: hrefs are excluded."""
        content = '<a href="tel:+1234567890">Call</a>'
        analyzer = TemplateAnalyzer()
        result = analyzer._analyze_template_content(content, "test.html")

        assert "tel:+1234567890" not in result["hrefs"]
        assert len(result["hrefs"]) == 0

    def test_exclude_javascript_href(self):
        """Test that javascript: hrefs are excluded."""
        content = '<a href="javascript:void(0)">Click</a>'
        analyzer = TemplateAnalyzer()
        result = analyzer._analyze_template_content(content, "test.html")

        assert "javascript:void(0)" not in result["hrefs"]
        assert len(result["hrefs"]) == 0

    def test_exclude_hash_href(self):
        """Test that # hrefs are excluded."""
        content = '<a href="#">Anchor</a>'
        analyzer = TemplateAnalyzer()
        result = analyzer._analyze_template_content(content, "test.html")

        assert "#" not in result["hrefs"]
        assert len(result["hrefs"]) == 0

    def test_extract_multiple_internal_hrefs(self):
        """Test extraction of multiple internal hrefs from one template."""
        content = """
            <a href="/home/">Home</a>
            <a href="/about/">About</a>
            <a href="/contact/">Contact</a>
        """
        analyzer = TemplateAnalyzer()
        result = analyzer._analyze_template_content(content, "test.html")

        assert "/home/" in result["hrefs"]
        assert "/about/" in result["hrefs"]
        assert "/contact/" in result["hrefs"]
        assert len(result["hrefs"]) == 3

    def test_mixed_internal_and_external_hrefs(self):
        """Test that only internal hrefs are extracted from mixed content."""
        content = """
            <a href="/internal/">Internal</a>
            <a href="https://example.com">External</a>
            <a href="/another/">Another</a>
            <a href="mailto:test@example.com">Email</a>
        """
        analyzer = TemplateAnalyzer()
        result = analyzer._analyze_template_content(content, "test.html")

        assert "/internal/" in result["hrefs"]
        assert "/another/" in result["hrefs"]
        assert "https://example.com" not in result["hrefs"]
        assert "mailto:test@example.com" not in result["hrefs"]
        assert len(result["hrefs"]) == 2

    def test_href_with_query_parameters(self):
        """Test extraction of href with query parameters."""
        content = '<a href="/search/?q=test">Search</a>'
        analyzer = TemplateAnalyzer()
        result = analyzer._analyze_template_content(content, "test.html")

        assert "/search/?q=test" in result["hrefs"]

    def test_href_with_fragment(self):
        """Test extraction of href with fragment identifier."""
        content = '<a href="/page/#section">Section</a>'
        analyzer = TemplateAnalyzer()
        result = analyzer._analyze_template_content(content, "test.html")

        assert "/page/#section" in result["hrefs"]

    def test_empty_href(self):
        """Test handling of empty href."""
        content = '<a href="">Empty</a>'
        analyzer = TemplateAnalyzer()
        result = analyzer._analyze_template_content(content, "test.html")

        # Empty hrefs should be excluded
        assert "" not in result["hrefs"]

    def test_href_without_leading_slash(self):
        """Test that relative hrefs without leading slash are excluded."""
        content = '<a href="relative/path">Relative</a>'
        analyzer = TemplateAnalyzer()
        result = analyzer._analyze_template_content(content, "test.html")

        # Only hrefs starting with / should be included
        assert "relative/path" not in result["hrefs"]
        assert len(result["hrefs"]) == 0

    def test_href_case_insensitive_attribute(self):
        """Test that HREF attribute is case-insensitive."""
        content = '<a HREF="/uppercase/">Link</a>'
        analyzer = TemplateAnalyzer()
        result = analyzer._analyze_template_content(content, "test.html")

        assert "/uppercase/" in result["hrefs"]


class TestCommentStripping:
    """Test suite for comment stripping before URL extraction."""

    def test_url_in_html_comment_excluded(self):
        """Test that URLs inside HTML comments are NOT extracted."""
        content = """
            <!-- Old link: /deprecated/path/ -->
            <a href="/active/">Active</a>
        """
        analyzer = TemplateAnalyzer()
        result = analyzer._analyze_template_content(content, "test.html")

        assert "/active/" in result["hrefs"]
        assert "/deprecated/path/" not in result["hrefs"]

    def test_url_in_js_multiline_comment_excluded(self):
        """Test that URLs inside JS multi-line comments are NOT extracted."""
        content = """
            <script>
            /*
             * Old endpoints:
             * /api/v1/old/
             * /api/v1/deprecated/
             */
            const url = "/api/v2/current/";
            </script>
        """
        analyzer = TemplateAnalyzer()
        result = analyzer._analyze_template_content(content, "test.html")

        assert "/api/v2/current/" in result["hrefs"]
        assert "/api/v1/old/" not in result["hrefs"]
        assert "/api/v1/deprecated/" not in result["hrefs"]

    def test_url_in_js_singleline_comment_excluded(self):
        """Test that URLs inside JS single-line comments are NOT extracted."""
        content = """
            <script>
            // const oldUrl = "/old/endpoint/";
            const newUrl = "/new/endpoint/";
            </script>
        """
        analyzer = TemplateAnalyzer()
        result = analyzer._analyze_template_content(content, "test.html")

        assert "/new/endpoint/" in result["hrefs"]
        assert "/old/endpoint/" not in result["hrefs"]

    def test_protocol_urls_not_affected_by_comment_stripping(self):
        """Test that protocol URLs (https://) are NOT mistaken for comments."""
        content = """
            <a href="https://example.com">External</a>
            <script>const url = "/internal/";</script>
        """
        analyzer = TemplateAnalyzer()
        result = analyzer._analyze_template_content(content, "test.html")

        # Internal URL should be extracted
        assert "/internal/" in result["hrefs"]
        # External URL should be excluded (not starting with /)
        assert "https://example.com" not in result["hrefs"]


class TestExpandedUrlDetection:
    """Test suite for expanded URL detection beyond href attributes."""

    def test_url_in_data_attribute(self):
        """Test URL extraction from data-* attributes."""
        content = '<div data-url="/api/users/"></div>'
        analyzer = TemplateAnalyzer()
        result = analyzer._analyze_template_content(content, "test.html")

        assert "/api/users/" in result["hrefs"]

    def test_url_in_javascript_string(self):
        """Test URL extraction from JavaScript strings."""
        content = """
            <script>
            const url = "/api/endpoint/";
            fetch("/api/data/");
            </script>
        """
        analyzer = TemplateAnalyzer()
        result = analyzer._analyze_template_content(content, "test.html")

        assert "/api/endpoint/" in result["hrefs"]
        assert "/api/data/" in result["hrefs"]

    def test_url_in_inline_event_handler(self):
        """Test URL extraction from inline event handlers."""
        content = """<button onclick="location.href='/dashboard/'">Go</button>"""
        analyzer = TemplateAnalyzer()
        result = analyzer._analyze_template_content(content, "test.html")

        assert "/dashboard/" in result["hrefs"]

    def test_url_in_json_config(self):
        """Test URL extraction from JSON embedded in templates."""
        content = """
            <script>
            const config = {
                "apiUrl": "/api/v1/",
                "dashboardUrl": "/dashboard/"
            };
            </script>
        """
        analyzer = TemplateAnalyzer()
        result = analyzer._analyze_template_content(content, "test.html")

        assert "/api/v1/" in result["hrefs"]
        assert "/dashboard/" in result["hrefs"]

    def test_dynamic_url_with_template_variable(self):
        """Test URL extraction with Django template variables."""
        content = """
            <a href="/user/{{ user.id }}/">Profile</a>
            <script>const url = "/items/{{ item.pk }}/edit/";</script>
        """
        analyzer = TemplateAnalyzer()
        result = analyzer._analyze_template_content(content, "test.html")

        assert "/user/{{ user.id }}/" in result["hrefs"]
        assert "/items/{{ item.pk }}/edit/" in result["hrefs"]

    def test_urls_in_comments_not_extracted(self):
        """Test that URLs inside any type of comment are NOT extracted."""
        content = """
            <!-- /html/comment/url/ -->
            <script>
            // /singleline/comment/url/
            /* /multiline/comment/url/ */
            const activeUrl = "/active/url/";
            </script>
        """
        analyzer = TemplateAnalyzer()
        result = analyzer._analyze_template_content(content, "test.html")

        assert "/active/url/" in result["hrefs"]
        assert "/html/comment/url/" not in result["hrefs"]
        assert "/singleline/comment/url/" not in result["hrefs"]
        assert "/multiline/comment/url/" not in result["hrefs"]


class TestStaticFileScanning:
    """Test suite for JavaScript static file scanning."""

    def test_extract_url_from_js_content(self):
        """Test URL extraction from JavaScript content."""
        js_content = """
            function saveData() {
                $.ajax({
                    url: '/api/save/',
                    method: 'POST'
                });
            }
        """
        analyzer = TemplateAnalyzer()
        result = analyzer._analyze_static_content(js_content, "app.js")

        assert "/api/save/" in result["hrefs"]

    def test_extract_url_from_fetch_call(self):
        """Test URL extraction from fetch() calls."""
        js_content = """
            fetch('/api/users/')
                .then(response => response.json());
        """
        analyzer = TemplateAnalyzer()
        result = analyzer._analyze_static_content(js_content, "api.js")

        assert "/api/users/" in result["hrefs"]

    def test_extract_multiple_urls_from_js(self):
        """Test extraction of multiple URLs from JavaScript."""
        js_content = """
            const API = {
                users: '/api/users/',
                posts: '/api/posts/',
                comments: '/api/comments/'
            };
        """
        analyzer = TemplateAnalyzer()
        result = analyzer._analyze_static_content(js_content, "config.js")

        assert "/api/users/" in result["hrefs"]
        assert "/api/posts/" in result["hrefs"]
        assert "/api/comments/" in result["hrefs"]
        assert len(result["hrefs"]) == 3

    def test_exclude_external_urls_from_js(self):
        """Test that external URLs are excluded from JavaScript files."""
        js_content = """
            const external = "https://example.com/api/";
            const internal = "/api/internal/";
        """
        analyzer = TemplateAnalyzer()
        result = analyzer._analyze_static_content(js_content, "urls.js")

        assert "/api/internal/" in result["hrefs"]
        assert "https://example.com/api/" not in result["hrefs"]

    def test_urls_in_js_comments_excluded(self):
        """Test that URLs in JavaScript comments are excluded."""
        js_content = """
            // Old endpoint: /api/v1/deprecated/
            /* Also deprecated: /api/v1/old/ */
            const url = '/api/v2/current/';
        """
        analyzer = TemplateAnalyzer()
        result = analyzer._analyze_static_content(js_content, "api.js")

        assert "/api/v2/current/" in result["hrefs"]
        assert "/api/v1/deprecated/" not in result["hrefs"]
        assert "/api/v1/old/" not in result["hrefs"]

    def test_static_files_included_in_all_hrefs(self):
        """Test that static file hrefs are included in get_all_internal_hrefs()."""
        analyzer = TemplateAnalyzer()

        # Add a template
        analyzer._analyze_template_content(
            '<a href="/template/url/">Link</a>', "test.html"
        )

        # Add a static file
        analyzer._analyze_static_content('const url = "/static/url/";', "app.js")

        all_hrefs = analyzer.get_all_internal_hrefs()

        assert "/template/url/" in all_hrefs
        assert "/static/url/" in all_hrefs
        assert len(all_hrefs) == 2

    def test_normalize_static_path(self):
        """Test normalization of static file paths."""
        from pathlib import Path

        analyzer = TemplateAnalyzer()

        # Test typical static path
        path1 = Path("/app/myapp/static/js/app.js")
        assert analyzer.normalize_static_path(path1) == "js/app.js"

        # Test nested static path
        path2 = Path("/project/static/vendor/lib.js")
        assert analyzer.normalize_static_path(path2) == "vendor/lib.js"

        # Test path without 'static' directory
        path3 = Path("/app/scripts/main.js")
        assert analyzer.normalize_static_path(path3) == "main.js"

    def test_scan_static_disabled_by_default(self):
        """Test that static scanning is disabled by default."""
        analyzer = TemplateAnalyzer()
        assert analyzer.scan_static is False
        assert analyzer.static_files == {}

    def test_scan_static_enabled(self):
        """Test that static scanning can be enabled."""
        analyzer = TemplateAnalyzer(scan_static=True)
        assert analyzer.scan_static is True

    def test_jquery_ajax_url_extraction(self):
        """Test URL extraction from jQuery AJAX patterns (the original use case)."""
        js_content = """
            function saveMFPCode(){
              code = $('#client_mfp_code').val()
              $.ajax({
                        url: '/nutritionist/client/client_mfp_code/',
                        data: {
                        'client_id': clientId,
                        'code': code,
                        },
                        success: function (data) {
                          location.reload()
                        }
                    });
            }
        """
        analyzer = TemplateAnalyzer()
        result = analyzer._analyze_static_content(js_content, "nutritionist.js")

        assert "/nutritionist/client/client_mfp_code/" in result["hrefs"]


class TestExtendedUrlDetection:
    """Test suite for extended URL detection (template literals)."""

    def test_template_literal_basic(self):
        """Test URL extraction from basic template literal."""
        js_content = """
            const url = `/api/users/`;
        """
        analyzer = TemplateAnalyzer(url_detection="extended")
        result = analyzer._analyze_static_content(js_content, "app.js")

        assert "/api/users/" in result["hrefs"]

    def test_template_literal_with_interpolation(self):
        """Test URL prefix extraction from template literal with ${...}."""
        js_content = """
            const url = `/api/users/${userId}/edit/`;
        """
        analyzer = TemplateAnalyzer(url_detection="extended")
        result = analyzer._analyze_static_content(js_content, "app.js")

        # Should extract the prefix before ${
        assert "/api/users/" in result["hrefs"]

    def test_template_literal_multiple_interpolations(self):
        """Test URL prefix extraction with multiple interpolations."""
        js_content = """
            const url = `/api/${resource}/${id}/`;
        """
        analyzer = TemplateAnalyzer(url_detection="extended")
        result = analyzer._analyze_static_content(js_content, "app.js")

        # Should extract only up to first ${
        assert "/api/" in result["hrefs"]

    def test_template_literal_not_detected_in_basic_mode(self):
        """Test that template literals are NOT detected in basic mode."""
        js_content = """
            const url = `/api/users/${userId}/`;
        """
        analyzer = TemplateAnalyzer(url_detection="basic")
        result = analyzer._analyze_static_content(js_content, "app.js")

        # Should NOT find template literal URLs in basic mode
        assert "/api/users/" not in result["hrefs"]
        assert len(result["hrefs"]) == 0

    def test_template_literal_in_template(self):
        """Test template literal detection in HTML template content."""
        content = """
            <script>
            const apiUrl = `/api/data/${id}/`;
            fetch(apiUrl);
            </script>
        """
        analyzer = TemplateAnalyzer(url_detection="extended")
        result = analyzer._analyze_template_content(content, "test.html")

        assert "/api/data/" in result["hrefs"]

    def test_extended_detection_combines_with_basic(self):
        """Test that extended mode also detects basic quoted URLs."""
        js_content = """
            const url1 = '/api/basic/';
            const url2 = `/api/template/${id}/`;
        """
        analyzer = TemplateAnalyzer(url_detection="extended")
        result = analyzer._analyze_static_content(js_content, "app.js")

        # Should find both basic and template literal URLs
        assert "/api/basic/" in result["hrefs"]
        assert "/api/template/" in result["hrefs"]

    def test_template_literal_with_expressions(self):
        """Test template literal with complex expressions."""
        js_content = """
            const url = `/api/items/${item.id + 1}/details/`;
        """
        analyzer = TemplateAnalyzer(url_detection="extended")
        result = analyzer._analyze_static_content(js_content, "app.js")

        # Should extract prefix before ${
        assert "/api/items/" in result["hrefs"]

    def test_template_literal_ignores_non_url_strings(self):
        """Test that template literals not starting with / are ignored."""
        js_content = """
            const msg = `Hello ${name}!`;
            const path = `relative/path/${id}`;
        """
        analyzer = TemplateAnalyzer(url_detection="extended")
        result = analyzer._analyze_static_content(js_content, "app.js")

        # Should not find any URLs (no leading /)
        assert len(result["hrefs"]) == 0

    def test_url_detection_default_is_basic(self):
        """Test that default url_detection is 'basic'."""
        analyzer = TemplateAnalyzer()
        assert analyzer.url_detection == "basic"

    def test_url_detection_can_be_set_to_extended(self):
        """Test that url_detection can be set to 'extended'."""
        analyzer = TemplateAnalyzer(url_detection="extended")
        assert analyzer.url_detection == "extended"

    def test_template_literal_in_fetch_call(self):
        """Test template literal in fetch() call (common pattern)."""
        js_content = """
            fetch(`/api/users/${userId}`)
                .then(response => response.json());
        """
        analyzer = TemplateAnalyzer(url_detection="extended")
        result = analyzer._analyze_static_content(js_content, "api.js")

        assert "/api/users/" in result["hrefs"]

    def test_template_literal_excludes_just_slash(self):
        """Test that template literals with just / are excluded."""
        js_content = """
            const root = `/`;
            const url = `/${page}`;
        """
        analyzer = TemplateAnalyzer(url_detection="extended")
        result = analyzer._analyze_static_content(js_content, "app.js")

        # Should not include just "/" - needs a meaningful prefix
        assert "/" not in result["hrefs"]
