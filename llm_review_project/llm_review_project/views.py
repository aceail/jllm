# ~/jllm/llm_review_project/llm_review_project/views.py

from django.contrib.auth.views import LogoutView, LoginView
from django.urls import reverse_lazy
from django.shortcuts import redirect

class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('home')

    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        return response

class CustomLoginView(LoginView):
    """사용자 로그인을 처리하는 뷰."""

    redirect_authenticated_user = True
    template_name = 'registration/login.html'
    # get_success_url 메서드를 제거하여 settings.LOGIN_REDIRECT_URL을 따르도록 합니다.
    # def get_success_url(self):
    #     return reverse_lazy('home')