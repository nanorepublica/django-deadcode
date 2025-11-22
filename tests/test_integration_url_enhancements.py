"""Integration tests for URL pattern enhancements feature."""

from django.test import override_settings

from django_deadcode.analyzers import TemplateAnalyzer, URLAnalyzer
from django_deadcode.reporters import ConsoleReporter, MarkdownReporter
from django_deadcode.utils import find_matching_url_patterns, get_excluded_namespaces


class TestHrefToURLMatching:
    """Integration tests for href-to-URL pattern matching."""

    def test_href_in_template_matches_url_pattern(self):
        """Test template href matches URL pattern and marks it as referenced."""
        # Create URL analyzer with a simple pattern
        url_analyzer = URLAnalyzer()
        url_analyzer.url_patterns = {
            "about": {"pattern": "about/", "name": "about"},
            "contact": {"pattern": "contact/", "name": "contact"},
        }
        url_analyzer.url_names = {"about", "contact"}

        # Create template analyzer with internal hrefs
        template_analyzer = TemplateAnalyzer()
        template_content = '<a href="/about/">About Us</a>'
        template_analyzer._analyze_template_content(template_content, "test.html")

        # Get hrefs and match to patterns
        hrefs = template_analyzer.get_all_internal_hrefs()
        matched_urls = find_matching_url_patterns(hrefs, url_analyzer.url_patterns)

        # Verify the href matched the pattern
        assert "/about/" in hrefs
        assert "about" in matched_urls
        assert "contact" not in matched_urls

    def test_multiple_hrefs_match_multiple_patterns(self):
        """Test that multiple hrefs match multiple URL patterns."""
        url_analyzer = URLAnalyzer()
        url_analyzer.url_patterns = {
            "home": {"pattern": "", "name": "home"},
            "about": {"pattern": "about/", "name": "about"},
            "contact": {"pattern": "contact/", "name": "contact"},
        }
        url_analyzer.url_names = {"home", "about", "contact"}

        template_analyzer = TemplateAnalyzer()
        template_content = """
            <a href="/">Home</a>
            <a href="/about/">About</a>
        """
        template_analyzer._analyze_template_content(template_content, "test.html")

        hrefs = template_analyzer.get_all_internal_hrefs()
        matched_urls = find_matching_url_patterns(hrefs, url_analyzer.url_patterns)

        assert "home" in matched_urls
        assert "about" in matched_urls
        assert "contact" not in matched_urls

    def test_href_matching_reduces_unreferenced_urls(self):
        """Test that href matching reduces unreferenced URL count."""
        url_analyzer = URLAnalyzer()
        url_analyzer.url_patterns = {
            "about": {
                "pattern": "about/",
                "name": "about",
                "namespace": None,
                "is_third_party": False,
            },
            "contact": {
                "pattern": "contact/",
                "name": "contact",
                "namespace": None,
                "is_third_party": False,
            },
        }
        url_analyzer.url_names = {"about", "contact"}

        # Before href matching: both URLs unreferenced
        unreferenced, _ = url_analyzer.get_unreferenced_urls(set())
        assert len(unreferenced) == 2

        # After href matching: only contact is unreferenced
        template_analyzer = TemplateAnalyzer()
        template_content = '<a href="/about/">About</a>'
        template_analyzer._analyze_template_content(template_content, "test.html")

        hrefs = template_analyzer.get_all_internal_hrefs()
        matched_urls = find_matching_url_patterns(hrefs, url_analyzer.url_patterns)

        unreferenced, _ = url_analyzer.get_unreferenced_urls(matched_urls)
        assert len(unreferenced) == 1
        assert "contact" in unreferenced
        assert "about" not in unreferenced


class TestThirdPartyExclusion:
    """Integration tests for third-party namespace exclusion."""

    def test_third_party_urls_excluded_from_report(self):
        """Test that third-party URLs are excluded from unreferenced report."""
        url_analyzer = URLAnalyzer()
        url_analyzer.url_patterns = {
            "admin:index": {
                "pattern": "admin/",
                "name": "admin:index",
                "namespace": "admin",
                "is_third_party": True,
            },
            "admin:login": {
                "pattern": "admin/login/",
                "name": "admin:login",
                "namespace": "admin",
                "is_third_party": True,
            },
            "myapp:home": {
                "pattern": "home/",
                "name": "myapp:home",
                "namespace": "myapp",
                "is_third_party": False,
            },
        }
        url_analyzer.url_names = {"admin:index", "admin:login", "myapp:home"}

        # Get third-party namespaces
        third_party = url_analyzer.get_third_party_namespaces()
        assert "admin" in third_party

        # Exclude third-party namespaces
        unreferenced, excluded = url_analyzer.get_unreferenced_urls(set(), third_party)

        # Admin URLs should be excluded
        assert "admin:index" not in unreferenced
        assert "admin:login" not in unreferenced
        # App URLs should be present
        assert "myapp:home" in unreferenced
        # Admin namespace should be reported as excluded
        assert "admin" in excluded

    @override_settings(DEADCODE_EXCLUDE_NAMESPACES=["api", "debug"])
    def test_manual_exclusions_combined_with_auto_detect(self):
        """Test that manual exclusions are combined with auto-detected ones."""
        url_analyzer = URLAnalyzer()
        url_analyzer.url_patterns = {
            "admin:index": {
                "pattern": "admin/",
                "name": "admin:index",
                "namespace": "admin",
                "is_third_party": True,
            },
            "api:list": {
                "pattern": "api/list/",
                "name": "api:list",
                "namespace": "api",
                "is_third_party": False,
            },
        }
        url_analyzer.url_names = {"admin:index", "api:list"}

        # Get auto-detected third-party
        auto_detected = url_analyzer.get_third_party_namespaces()
        assert "admin" in auto_detected

        # Get manual exclusions
        manual = get_excluded_namespaces()
        assert "api" in manual
        assert "debug" in manual

        # Combine them
        all_excluded = auto_detected | manual

        # Exclude all
        unreferenced, excluded = url_analyzer.get_unreferenced_urls(set(), all_excluded)

        # Both should be excluded
        assert "admin:index" not in unreferenced
        assert "api:list" not in unreferenced
        # Both namespaces should be reported
        assert "admin" in excluded
        assert "api" in excluded

    def test_exclusion_note_in_console_report(self):
        """Test that exclusion note appears in console report."""
        analysis_data = {
            "summary": {
                "total_urls": 3,
                "unreferenced_urls_count": 1,
            },
            "unreferenced_urls": ["myapp:home"],
            "url_details": {
                "myapp:home": {
                    "pattern": "home/",
                    "view": "myapp.views.home",
                }
            },
            "excluded_namespaces": ["admin", "api"],
        }

        reporter = ConsoleReporter()
        report = reporter.generate_report(analysis_data)

        # Check that exclusion note is present
        assert "Note: Third-party namespaces excluded: admin, api" in report

    def test_exclusion_note_in_markdown_report(self):
        """Test that exclusion note appears in markdown report."""
        analysis_data = {
            "summary": {
                "total_urls": 3,
                "unreferenced_urls_count": 1,
            },
            "unreferenced_urls": ["myapp:home"],
            "url_details": {
                "myapp:home": {
                    "pattern": "home/",
                    "view": "myapp.views.home",
                }
            },
            "excluded_namespaces": ["admin", "rest_framework"],
        }

        reporter = MarkdownReporter()
        report = reporter.generate_report(analysis_data)

        # Check that exclusion note is present
        expected_note = (
            "**Note:** Third-party namespaces excluded: admin, rest_framework"
        )
        assert expected_note in report

    def test_no_exclusion_note_when_no_exclusions(self):
        """Test that exclusion note does not appear when there are no exclusions."""
        analysis_data = {
            "summary": {
                "total_urls": 2,
                "unreferenced_urls_count": 1,
            },
            "unreferenced_urls": ["myapp:home"],
            "url_details": {
                "myapp:home": {
                    "pattern": "home/",
                    "view": "myapp.views.home",
                }
            },
            "excluded_namespaces": [],
        }

        reporter = ConsoleReporter()
        report = reporter.generate_report(analysis_data)

        # Check that exclusion note is NOT present
        assert "Note: Third-party namespaces excluded:" not in report


class TestEndToEndWorkflow:
    """End-to-end integration tests for complete workflow."""

    def test_complete_analysis_workflow(self):
        """Test the complete analysis workflow with all features."""
        # Set up URL analyzer
        url_analyzer = URLAnalyzer()
        url_analyzer.url_patterns = {
            "admin:index": {
                "pattern": "admin/",
                "name": "admin:index",
                "namespace": "admin",
                "is_third_party": True,
                "view": "django.contrib.admin.index",
                "module_path": "django.contrib.admin.sites",
            },
            "about": {
                "pattern": "about/",
                "name": "about",
                "namespace": None,
                "is_third_party": False,
                "view": "myapp.views.about",
                "module_path": "myapp.views",
            },
            "contact": {
                "pattern": "contact/",
                "name": "contact",
                "namespace": None,
                "is_third_party": False,
                "view": "myapp.views.contact",
                "module_path": "myapp.views",
            },
        }
        url_analyzer.url_names = {"admin:index", "about", "contact"}

        # Set up template analyzer with hrefs
        template_analyzer = TemplateAnalyzer()
        template_content = """
            <a href="/about/">About</a>
            {% url 'contact' %}
        """
        template_analyzer._analyze_template_content(template_content, "test.html")

        # Step 1: Get references from {% url %} tags
        url_tag_refs = template_analyzer.get_referenced_urls()
        assert "contact" in url_tag_refs

        # Step 2: Get references from hrefs
        hrefs = template_analyzer.get_all_internal_hrefs()
        href_refs = find_matching_url_patterns(hrefs, url_analyzer.url_patterns)
        assert "about" in href_refs

        # Step 3: Combine all references
        all_refs = url_tag_refs | href_refs

        # Step 4: Get third-party namespaces
        third_party = url_analyzer.get_third_party_namespaces()
        assert "admin" in third_party

        # Step 5: Get unreferenced URLs with exclusions
        unreferenced, excluded = url_analyzer.get_unreferenced_urls(
            all_refs, third_party
        )

        # Verify results:
        # - admin:index is excluded (third-party)
        # - about is referenced (href)
        # - contact is referenced ({% url %} tag)
        # - No URLs should be unreferenced!
        assert len(unreferenced) == 0
        assert "admin" in excluded

    def test_existing_functionality_still_works(self):
        """Test that existing {% url %} tag detection still works."""
        template_analyzer = TemplateAnalyzer()
        template_content = """
            {% url 'home' %}
            {% url 'about' %}
            {% url 'contact' %}
        """
        template_analyzer._analyze_template_content(template_content, "test.html")

        url_refs = template_analyzer.get_referenced_urls()

        assert "home" in url_refs
        assert "about" in url_refs
        assert "contact" in url_refs
        assert len(url_refs) == 3
