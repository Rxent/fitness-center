from django.urls import path

from . import views

app_name = 'subscriptions'

urlpatterns = [
    path('', views.plan_list, name='plan_list'),
    path('my/', views.my_subscriptions, name='my'),
    path('<int:pk>/', views.plan_detail, name='plan_detail'),
    path('<int:pk>/purchase/', views.purchase_plan, name='purchase'),
]
