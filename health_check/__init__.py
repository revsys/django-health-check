# Used by setup.py, so minimize top-level imports.

__version_info__ = {
    'major': 1,
    'minor': 2,
    'micro': 0,
    'releaselevel': 'final',
    'serial': 0
}

default_app_config = 'health_check.apps.HealthCheckConfig'


def autodiscover():
    """
    Auto-discover INSTALLED_APPS admin.py modules and fail silently when not present.

    This forces an import on them to register any admin bits they may want.
    """
    from django.utils.module_loading import autodiscover_modules
    from health_check.plugins import plugin_dir

    autodiscover_modules('plugin_health_check', register_to=plugin_dir)


def get_version(short=False):
    assert __version_info__['releaselevel'] in ('alpha', 'beta', 'final')
    vers = ["%(major)i.%(minor)i" % __version_info__, ]
    if __version_info__['micro']:
        vers.append(".%(micro)i" % __version_info__)
    if __version_info__['releaselevel'] != 'final' and not short:
        vers.append('%s%i' % (__version_info__['releaselevel'][0], __version_info__['serial']))
    return ''.join(vers)


__version__ = get_version()
