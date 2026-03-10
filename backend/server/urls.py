"""
Main URL mapping configuration file.

Include other URLConfs from external apps using method `include()`.

It is also a good practice to keep a single URL to the root index page.

This examples uses Django's default media
files serving technique in development.
"""

from django.conf import settings
from django.contrib import admin
from django.contrib.admindocs import urls as admindocs_urls
from django.urls import include, path
from django.views.generic import TemplateView
from health_check.views import HealthCheckView
from ninja import NinjaAPI

from server.apps.main import urls as main_urls
from server.apps.main.views import index
from server.apps.users.api import router as users_router
from server.common.auth import BasicAuth

admin.autodiscover()
django_ninja_api = NinjaAPI(
    docs_url="/docs/",
    title="Powerbank API",
    description="API for Powerbank project",
    auth=BasicAuth(),
)
# TODO: add API routers here

django_ninja_api.add_router("", users_router)


urlpatterns = [
    # Apps:
    path("main/", include(main_urls, namespace="main")),
    # DjangoNinja routers
    path("api/", django_ninja_api.urls),
    # Health checks:
    path(
        "health/",
        HealthCheckView.as_view(
            checks=[
                "health_check.Cache",
                "health_check.Database",
                "health_check.Storage",
            ]
        ),
        name="health_check",
    ),
    # django-admin:
    path("admin/doc/", include(admindocs_urls)),
    path("admin/", admin.site.urls),
    # Text and xml static files:
    path(
        "robots.txt",
        TemplateView.as_view(
            template_name="common/txt/robots.txt",
            content_type="text/plain",
        ),
        name="robots_txt",
    ),
    path(
        "humans.txt",
        TemplateView.as_view(
            template_name="common/txt/humans.txt",
            content_type="text/plain",
        ),
        name="humans_txt",
    ),
    # It is a good practice to have explicit index view:
    path("", index, name="index"),
]
if settings.DEBUG:  # pragma: no cover
    from django.conf.urls.static import static

    urlpatterns = [
        *urlpatterns,
        # Serving media files in development only:
        *static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT),
    ]
