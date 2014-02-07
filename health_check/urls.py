from django.conf.urls import patterns, include, url

import health_check
health_check.autodiscover()

urlpatterns = patterns('',
    url(r'^json/$', 'health_check.views.jsonhealthcheck', name='health_check_json'),
    url(r'^$', 'health_check.views.home', name='health_check_home'),
)
