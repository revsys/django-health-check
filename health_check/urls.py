from django.conf.urls import url
from health_check.views import home

import health_check

health_check.autodiscover()

urlpatterns = [
    url(r'^$', home, name='health_check_home'),
]
