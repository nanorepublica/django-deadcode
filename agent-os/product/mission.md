# Product Mission

## Pitch
django-deadcode is a static analysis tool that helps Django developers understand and clean up legacy codebases by providing a comprehensive view of relationships between templates, URLs, and views - making it easy to identify and remove unused code that accumulates over time.

## Users

### Primary Customers
- **Individual Django Developers**: Working on legacy codebases that have accumulated cruft over multiple years and development cycles
- **Development Teams**: Managing large Django projects where understanding the full codebase structure has become difficult
- **Tech Leads & Architects**: Responsible for reducing technical debt and maintaining code quality across Django applications

### User Personas

**Senior Django Developer** (28-45)
- **Role:** Lead developer or technical lead on legacy Django projects
- **Context:** Inherited a 3+ year old Django codebase with 50+ views, 100+ URL patterns, and 200+ templates
- **Pain Points:** Unable to confidently identify which code is safe to remove; spends hours manually tracing template/URL/view relationships; fears breaking production by removing "dead" code that might actually be used
- **Goals:** Safely reduce codebase size by 20-30%; understand the full scope of changes before refactoring; confidently remove unused code without breaking functionality

**Development Team Lead** (30-50)
- **Role:** Engineering manager or technical lead overseeing Django application maintenance
- **Context:** Managing a team working on multiple Django projects with varying levels of technical debt
- **Pain Points:** Cannot get a clear picture of codebase health; onboarding new developers takes weeks due to cruft; unclear which parts of the application are actually active
- **Goals:** Provide team with clear visibility into codebase structure; reduce time spent on code archaeology; establish a baseline for technical debt reduction

**Refactoring Specialist** (25-40)
- **Role:** Developer tasked with modernizing or cleaning up Django applications
- **Context:** Preparing for Django version upgrades, architecture changes, or codebase consolidation
- **Pain Points:** Must manually trace every URL, view, and template relationship; no automated way to identify orphaned code; risky to remove code without comprehensive analysis
- **Goals:** Complete refactoring projects 50% faster; eliminate dead code before migration; confidently identify safe-to-remove components

## The Problem

### Invisible Technical Debt
Django codebases accumulate unused code over time - URL patterns pointing to deleted views, templates never rendered, views never called. This "dead code" can represent 20-40% of a mature codebase, making it harder to maintain, slower to understand, and riskier to modify. Developers waste hours manually tracing relationships between components to understand what's actually in use.

**Our Solution:** Automated static analysis that maps all relationships between templates, URLs, and views, providing a complete birds-eye view of the codebase and highlighting potentially unused components in minutes instead of days.

### Lack of Codebase Visibility
In large Django projects, the relationships between templates, URLs, and views become opaque. Developers cannot easily answer questions like "Which views are never called?" or "Which templates reference this URL?" This lack of visibility leads to fear-based development where nobody dares to remove code.

**Our Solution:** Comprehensive reporting showing exactly how every template, URL, and view connects to the rest of the codebase, with reference counts and usage patterns that give developers confidence in their refactoring decisions.

### Risky Refactoring
Without automated analysis, refactoring Django applications is high-risk. Developers must manually grep through code, trace URL patterns, and hope they've found all references. This manual process is error-prone and incomplete, leading to broken links in production or abandoned refactoring efforts.

**Our Solution:** Complete relationship mapping that shows all direct and indirect references, including Django-specific patterns like `{% url %}` tags, `reverse()` calls, and `redirect()` functions, giving developers a safety net for refactoring work.

## Differentiators

### Django-Native Analysis
Unlike generic dead code detectors or grep-based searches, django-deadcode understands Django's URL routing system, template language, and view conventions. We parse `{% url %}` tags, `reverse()` calls, template inheritance, and URL patterns as first-class citizens, providing accurate results that generic tools miss.

This results in actionable insights specific to Django architecture, not just generic "unused function" warnings.

### Relationship Mapping Focus
While other tools focus on finding unused code, we focus on mapping relationships. We show not just what's unused, but how everything connects - which templates include which other templates, which views render which templates, which URLs map to which views.

This results in a comprehensive understanding of codebase structure, enabling informed decisions rather than just deletion suggestions.

### Zero Configuration Analysis
Unlike tools that require complex setup, configuration files, or code instrumentation, django-deadcode works out of the box on any Django project. Point it at your codebase and get immediate results without modifying your application, adding decorators, or configuring analysis rules.

This results in developers getting value in minutes, not hours, with no risk to existing code.

## Key Features

### Core Analysis Features
- **Template Link Extraction:** Automatically identify all internal links in templates, including plain href attributes and Django `{% url %}` template tags
- **URL Pattern Matching:** Match extracted URLs against all defined urlpatterns in your Django project, showing which URLs are defined but never referenced
- **View Reference Tracking:** Link URL patterns to their corresponding views and count how many times each view is referenced across the codebase
- **Template Usage Analysis:** Track which templates are referenced by views through render() calls, TemplateView declarations, and other Django patterns

### Advanced Analysis Features
- **Template Inheritance Mapping:** Follow `{% include %}` and `{% extends %}` tags to build a complete template dependency graph
- **Reverse Reference Detection:** Find all uses of `reverse()` and `redirect()` in Python code to capture programmatic URL references
- **Django Admin Integration:** Detect URLs generated by Django admin and third-party packages to avoid false positives
- **Multi-App Analysis:** Analyze projects with multiple Django apps, showing cross-app dependencies and app-specific dead code

### Reporting Features
- **Reference Count Reports:** See how many times each view, URL, and template is referenced, helping prioritize cleanup efforts
- **Orphaned Code Identification:** Clearly identify views with zero references, templates never rendered, and URLs never called
- **Relationship Visualization:** Understand the full graph of template->URL->view relationships in an easy-to-scan format
- **Confidence Scoring:** Get confidence levels on dead code detection, accounting for dynamic URLs and runtime-generated paths

## Success Metrics

### Adoption Metrics
- **Active Users:** 1,000+ Django developers using the tool within 6 months of launch
- **Project Analysis:** 5,000+ Django projects analyzed in the first year
- **Community Engagement:** 500+ GitHub stars, active issue discussions, and pull requests from community

### Impact Metrics
- **Code Cleanup:** Users successfully remove an average of 15-25% of unused code from analyzed projects
- **Time Savings:** Reduce dead code analysis time from days to minutes (95%+ time savings)
- **Confidence:** 80%+ of users report increased confidence in refactoring decisions

### Quality Metrics
- **Accuracy:** 95%+ accuracy in identifying unused code (minimizing false positives)
- **Performance:** Analyze medium-sized Django projects (100 files) in under 60 seconds
- **User Satisfaction:** Net Promoter Score of 40+ from Django developer community
