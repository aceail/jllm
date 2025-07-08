# llm_review_project/llm_review_project/urls.py

from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    # 기존 'editor/' 경로를 비워둬서 메인 페이지로 만듭니다.
    path('', include('editor.urls')), 
    path('accounts/login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
]

# media 파일 URL 설정 추가
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# 개발 환경에서 미디어 파일을 서빙하기 위한 설정
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

