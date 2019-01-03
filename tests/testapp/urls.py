from django.conf.urls import include, url

from health_check.views import JsonFirstView

urlpatterns = [
    url(r'^ht/', include('health_check.urls')),
    url(r'^ht/json', JsonFirstView.as_view(), name='health_check_home_json')
]
