# -*- coding: utf-8 -*-
from django.test import TestCase
from health_check.backends.base import BaseHealthCheckBackend


class TestBaseHealthCheckBackend(TestCase):

    def test_status(self):
        self.assertIsNone(BaseHealthCheckBackend().status)
