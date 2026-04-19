from django.urls import path

from . import views

app_name = 'reports'

urlpatterns = [
    path('', views.report_index, name='index'),
    path('attendance/', views.attendance, name='attendance'),
    path('revenue/', views.revenue, name='revenue'),
    path('trainer-load/', views.trainer_load, name='trainer_load'),
]
