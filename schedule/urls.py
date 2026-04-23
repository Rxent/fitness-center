from django.urls import path

from . import views

app_name = 'schedule'

urlpatterns = [
    path('', views.class_list, name='class_list'),
    path('my/', views.my_enrollments, name='my_enrollments'),
    path('trainer/', views.trainer_classes, name='trainer_classes'),
    path('trainer/<int:pk>/', views.trainer_class_detail, name='trainer_class_detail'),
    path('trainer/<int:pk>/status/', views.mark_class_status, name='mark_class_status'),
    path(
        'trainer/enrollment/<int:enrollment_id>/',
        views.mark_enrollment_status,
        name='mark_enrollment_status',
    ),
    path('<int:pk>/', views.class_detail, name='class_detail'),
    path('<int:pk>/enroll/', views.enroll, name='enroll'),
    path('<int:pk>/cancel/', views.cancel_enrollment, name='cancel'),
]
