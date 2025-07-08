# ~/jllm/llm_review_project/llm_review_project/views.py

from django.contrib.auth.views import LogoutView
from django.urls import reverse_lazy
from django.shortcuts import redirect, render # render를 임포트합니다.

class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('home')

    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        return response

# --- 새로운 뷰 추가: 홈페이지 뷰 ---
def home_view(request):
    """
    홈페이지를 렌더링하는 뷰.
    """
    return render(request, 'home.html') # 'home.html' 템플릿을 렌더링합니다.