from django.urls import path
from . import views

urlpatterns = [
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('pending_users/', views.pending_users, name='pending_users'),
    path('accepted_users/', views.accepted_users, name='accepted_users'),
    path('rejected_users/', views.rejected_users, name='rejected_users'),
    path('users_all/', views.all_users, name='all_users'),
    path('admin_upload_dataset/', views.upload_dataset, name='admin_upload_dataset'),
    path('admin_view_dataset/', views.view_dataset, name='admin_view_dataset'),
    path('admin_download_dataset/', views.admin_download_dataset, name='admin_download_dataset'),
    path('admin_preview_dataset/', views.admin_preview_dataset, name='admin_preview_dataset'),
    path('graph_analysis/', views.graph_analysis, name='graph_analysis'),
    path('adminlogout/', views.admin_logout, name='adminlogout'),
    path('admin_run_model/', views.admin_run_model, name='admin_run_model'),
]
