from django.conf.urls import url

import health_check
from health_check.views import home

health_check.autodiscover()

urlpatterns = [
    url(r'^$', home, name='health_check_home'),
]
