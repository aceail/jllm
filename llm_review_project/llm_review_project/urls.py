# ~/jllm/llm_review_project/llm_review_project/urls.py

from django.contrib import admin
from django.urls import path, include
from .views import CustomLogoutView, home_view # home_view를 임포트합니다.
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('accounts/', include('django.contrib.auth.urls')),

    # --- 루트 URL 패턴 추가 ---
    path('', home_view, name='home'), # 이 줄을 추가합니다.
    # --- 여기까지 루트 URL 패턴 추가 ---

    # 다른 URL 패턴들...
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)