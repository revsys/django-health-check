from django.conf.urls import include
from django.urls import path

urlpatterns = [
    path('ht/', include('health_check.urls')),
]
