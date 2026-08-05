# disaster_app/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path(
        'admin_run_algorithm/<str:model_name>/',
        views.admin_run_algorithm,
        name='admin_run_algorithm'
    ),
]
