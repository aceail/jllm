from django.contrib import admin
from django.urls import path, include, re_path
from django.views.generic.base import RedirectView
from django.views import static as django_static
from django.conf import settings
import os

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('', RedirectView.as_view(url='/editor/', permanent=False), name='home'),
    path('editor/', include('editor.urls')),
]

# DEBUG일 때 media 경로를 디버그 로그와 함께 처리
if settings.DEBUG:
    def debug_serve(request, path, document_root=None, show_indexes=False):
        full_path = os.path.join(document_root, path)
        print("=" * 60)
        print(f"요청 URL Path: {path}")
        print(f"MEDIA_ROOT: {document_root}")
        print(f"실제 찾는 경로: {full_path}")
        print("=" * 60)
        return django_static.serve(request, path, document_root=document_root, show_indexes=show_indexes)

    urlpatterns += [
        re_path(
            r'^media/(?P<path>.*)$',
            debug_serve,
            {'document_root': settings.MEDIA_ROOT},
        ),
    ]
