from django.conf.urls import patterns, include, url

import health_check
health_check.autodiscover()

urlpatterns = patterns('',
    url(r'^json/$', 'health_check.views.jsonhealthcheck', name='health_check_json'),
   url(r'^text/$', 'health_check.views.texthealthcheck', name='health_check_text'),
   url(r'^yaml/$', 'health_check.views.yamlhealthcheck', name='health_check_yaml'),
    url(r'^$', 'health_check.views.home', name='health_check_home'),
)
