from django.conf.urls import include, url

urlpatterns = [
    url(r'^ht/', include('health_check.urls')),
]
