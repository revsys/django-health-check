# -*- coding: utf-8 -*-
from django.conf.urls import url

from health_check.views import home

urlpatterns = [
    url(r'^$', home, name='health_check_home'),
]
