def pytest_configure():
    from django.conf import settings

    settings.configure(
        DEBUG_PROPAGATE_EXCEPTIONS=True,
        DATABASES={'default': {'ENGINE': 'django.db.backends.sqlite3',
                               'NAME': ':memory:'}},
        SECRET_KEY='not very secret in tests',
        USE_I18N=True,
        USE_L10N=True,
        STATIC_URL='/static/',
        ROOT_URLCONF='tests.urls',
        MIDDLEWARE_CLASSES=(
            'django.middleware.common.CommonMiddleware',
            'django.middleware.csrf.CsrfViewMiddleware',
            'django.contrib.sessions.middleware.SessionMiddleware',
            'django.contrib.auth.middleware.AuthenticationMiddleware',
        ),
        INSTALLED_APPS=(
            'django.contrib.auth',
            'django.contrib.contenttypes',

            'health_check',
            'health_check_cache',
        ),
        PASSWORD_HASHERS=(
            'django.contrib.auth.hashers.MD5PasswordHasher',
        ),
        REST_FRAMEWORK={
            "DEFAULT_RENDERER_CLASSES": (
                "rest_framework_json_api.renderers.JsonApiRenderer",
            ),
            "DEFAULT_PARSER_CLASSES": (
                "rest_framework_json_api.parsers.JsonApiParser",
            ),
            "TEST_REQUEST_DEFAULT_FORMAT": "json",
        },
    )
