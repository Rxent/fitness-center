from django.urls import path

from . import views

app_name = 'schedule'

urlpatterns = [
    path('', views.class_list, name='class_list'),
    path('my/', views.my_enrollments, name='my_enrollments'),
    path('trainer/', views.trainer_schedule, name='trainer_schedule'),
    path('classes/add/', views.class_create, name='class_create'),
    path('classes/<int:pk>/edit/', views.class_update, name='class_update'),
    path('classes/<int:pk>/enroll/', views.enroll, name='enroll'),
    path('enrollments/<int:pk>/cancel/', views.cancel_enrollment, name='cancel_enrollment'),
]
