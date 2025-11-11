"""Django app configuration for django_deadcode."""

from django.apps import AppConfig


class DjangoDeadcodeConfig(AppConfig):
    """Configuration for the django_deadcode app."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "django_deadcode"
    verbose_name = "Django Dead Code Analyzer"
