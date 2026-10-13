from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from wagtail.admin import urls as wagtailadmin_urls
from wagtail import urls as wagtail_urls
from wagtail.documents import urls as wagtaildocs_urls

urlpatterns = [
    path("django-admin/", admin.site.urls),
    path("admin/", include(wagtailadmin_urls)),  # Wagtail's CMS admin
    path("documents/", include(wagtaildocs_urls)),
    path("subscribe/", include("subscribers.urls")),
]

if settings.DEBUG:
    from django.conf.urls.static import static

    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Wagtail's page-serving catch-all must be last.
urlpatterns += [
    path("", include(wagtail_urls)),
]
