from django.conf.urls.defaults import patterns, include, url

import health_check
health_check.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'health_check.views.home', name='health_check_home'),
)
