"""Test URL configuration."""

from django.urls import path


def test_view(request):
    """Test view."""
    pass


urlpatterns = [
    path("test/", test_view, name="test_url"),
    path("unused/", test_view, name="unused_url"),
]
