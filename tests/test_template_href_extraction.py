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
