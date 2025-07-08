# llm_review_project/llm_review_project/urls.py
from django.contrib import admin
from django.urls import path, include
from django.views.generic.base import RedirectView # RedirectView를 임포트합니다.
# from . import views # home_view를 사용하지 않으므로 이 임포트 줄은 제거하거나 주석 처리할 수 있습니다.

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    # 루트 URL을 /editor/로 리디렉션합니다.
    path('', RedirectView.as_view(url='/editor/', permanent=False), name='home'), # name='home'은 기존 next_page 등에 사용될 수 있어 유지합니다.
    path('editor/', include('editor.urls')),
]