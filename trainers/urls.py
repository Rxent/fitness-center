from django.urls import path

from . import views

app_name = 'trainers'

urlpatterns = [
    path('', views.trainer_list, name='trainer_list'),
    path('<int:pk>/edit/', views.trainer_update, name='trainer_update'),
]
