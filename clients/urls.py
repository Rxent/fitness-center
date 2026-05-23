from django.urls import path

from . import views

app_name = 'clients'

urlpatterns = [
    path('', views.client_list, name='client_list'),
    path('<int:pk>/edit/', views.client_update, name='client_update'),
]
