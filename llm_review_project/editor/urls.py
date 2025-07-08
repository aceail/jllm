from django.urls import path
from . import views

app_name = 'editor'

urlpatterns = [
    path('', views.main_editor_view, name='main_editor'),
    path('result/<int:result_id>/', views.main_editor_view, name='editor_with_id'),
    path('create/', views.create_inference, name='create_inference'),
    path('result/<int:result_id>/save/', views.save_edit, name='save_edit'),
    path('result/<int:result_id>/delete/', views.delete_result, name='delete_result'),
    path('upload_excel/', views.upload_excel, name='upload_excel'),
]
