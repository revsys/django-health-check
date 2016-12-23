# -*- coding: utf-8 -*-
from django.conf.urls import url

import health_check
from health_check.views import home, json_view

health_check.autodiscover()

urlpatterns = [
    url(r'^$', home, name='health_check_home'),
    url(r'^json/?$', json_view, name='health_check_json_view')
]
