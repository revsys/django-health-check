from django.urls import path

from health_check.views import DRFView, MainView

app_name = 'health_check'

urlpatterns = [
    path('', MainView.as_view(), name='health_check_home'),
    path('v2', DRFView.as_view(), name="health_check_home_v2")
]
