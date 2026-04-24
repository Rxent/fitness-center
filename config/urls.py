from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from users.views import home

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('users/', include('users.urls', namespace='users')),
    path('clients/', include('clients.urls', namespace='clients')),
    path('trainers/', include('trainers.urls', namespace='trainers')),
    path('subscriptions/', include('subscriptions.urls', namespace='subscriptions')),
    path('schedule/', include('schedule.urls', namespace='schedule')),
    path('reports/', include('reports.urls', namespace='reports')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
