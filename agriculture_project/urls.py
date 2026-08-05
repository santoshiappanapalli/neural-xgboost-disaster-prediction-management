from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static
from users import views as user_views
from admins import views as admin_views

urlpatterns = [
    # Django admin
    path('dj-admin/', admin.site.urls),
    path('', include('disaster_app.urls')),
    # Admin app
    path('admins/', include('admins.urls')),
    # -------- Public Pages --------
    path('', user_views.home_page, name='home'),
    path('about/', user_views.about_page, name='about'),
    path('service/', user_views.service_page, name='service'),
    path('causes/', user_views.causes_page, name='causes'),
    path('events/', user_views.events_page, name='events'),
    path('contact/', user_views.contact_page, name='contact'),

    # -------- User Auth --------
    path('user_login/', user_views.user_login_page, name='userLogin'),
    path('user/check-login/', user_views.check_user_credentials),
    path('user/check-register/', user_views.check_register_fields),

    path('user/send-otp/', user_views.user_send_otp, name='user_send_otp'),
    path('user/verify-otp/', user_views.user_verify_otp, name='user_verify_otp'),
    path('user/login/', user_views.user_login, name='user_login'),
    path('user/register/', user_views.user_register, name='user_register'),

    # -------- Admin Auth --------
    path('adminLogin/', admin_views.admin_login_page, name='adminLogin'),
    path('admin/send-otp/', admin_views.send_otp, name='send_otp'),
    path('admin/verify-otp/', admin_views.verify_otp, name='verify_otp'),
    path('admin/check-credentials/', admin_views.check_admin_credentials, name='check_admin_credentials'),
    path('admin/login/', admin_views.admin_login, name='admin_login'),
    path('admindashboard/', admin_views.admin_dashboard),

    # -------- Admin User Management --------
    path('pending_users/', admin_views.pending_users, name='pending_users'),
    path('accepted_users/', admin_views.accepted_users, name='accepted_users'),
    path('rejected_users/', admin_views.rejected_users, name='rejected_users'),

    path('accept_user/<int:user_id>/', admin_views.accept_user, name='accept_user'),
    path('reject_user/<int:user_id>/', admin_views.reject_user, name='reject_user'),

    # -------- Admin Other Pages --------
    path('users_all/', admin_views.all_users, name='all_users'),
    path('admin_upload_dataset/', admin_views.upload_dataset, name='admin_upload_dataset'),
    path('admin_view_dataset/', admin_views.view_dataset, name='admin_view_dataset'),
    path('admin_download_dataset/', admin_views.admin_download_dataset, name='admin_download_dataset'),
    path('admin_preview_dataset/', admin_views.admin_preview_dataset, name='admin_preview_dataset'),
    path('graph_analysis/', admin_views.graph_analysis, name='graph_analysis'),
    path('adminlogout/', admin_views.admin_logout, name='adminlogout'),
    path('admin_run_model/', admin_views.admin_run_model, name='admin_run_model'),
    path('run_rf_model/', admin_views.run_rf_model, name='run_rf_model'),
    path('run_lr_model/', admin_views.run_lr_model, name='run_lr_model'),
    path('run_svm_model/', admin_views.run_svm_model, name='run_svm_model'),
    path('run_knn_model/', admin_views.run_knn_model, name='run_knn_model'),
    # -------- User Dashboard --------
    path('user-dashboard/', user_views.user_dashboard, name='user-dashboard'),
    path('userprofile/', user_views.user_profile, name='userprofile'),
    path('userlogout/', user_views.user_logout, name='userlogout'),
    path('user_disaster_predict/', user_views.disaster_predict, name='user_disaster_predict'),
    path('prediction_result/', user_views.predict_result, name='prediction_result'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
