# llm_review_project/llm_review_project/urls.py

from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static

# ❗️ 이 함수를 새로 import 해야 합니다.
from .views import CustomLogoutView 

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('editor.urls')),
    path('accounts/login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    
    # ❗️ 아래 코드로 교체해 주세요.
    # GET 요청을 허용하는 커스텀 LogoutView를 사용합니다.
    path('accounts/logout/', CustomLogoutView.as_view(), name='logout'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)