# -*- coding: utf-8 -*-
# Used by setup.py, so minimize top-level imports.

VERSION = (1, 3, 0)

default_app_config = 'health_check.apps.HealthCheckConfig'


def autodiscover():
    """
    Auto-discover INSTALLED_APPS admin.py modules and fail silently when not present.

    This forces an import on them to register any admin bits they may want.
    """
    from django.utils.module_loading import autodiscover_modules
    from health_check.plugins import plugin_dir

    autodiscover_modules('plugin_health_check', register_to=plugin_dir)


__version__ = ".".join(str(i) for i in VERSION)
