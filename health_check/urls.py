from django.urls import path

from health_check.views import MainView, ping

app_name = 'health_check'

urlpatterns = [
    path('', MainView.as_view(), name='health_check_home'),
    path('ping', ping, name='health_check_ping'),
]
