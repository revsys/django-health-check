from django.conf.urls import url

import health_check

health_check.autodiscover()

urlpatterns = [
    url(r'^$', 'health_check.views.home', name='health_check_home'),
]
