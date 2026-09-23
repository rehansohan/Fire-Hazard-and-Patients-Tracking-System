"""
URL configuration for hazard_management project.
"""

from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('Core.urls')),
]

handler404 = 'Core.views.page_not_found'
handler403 = 'Core.views.permission_denied'
handler500 = 'Core.views.server_error'


# Serve media files
if settings.DEBUG:

    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )

else:

    urlpatterns += [
        re_path(
            r'^media/(?P<path>.*)$',
            serve,
            {
                'document_root': settings.MEDIA_ROOT,
            },
        ),
    ]