import os

from setuptools import setup

from health_check import __version__


# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name="django-health-check",
    version=__version__,
    author="Kristian Ollegaard",
    author_email="kristian@oellegaard.com",
    description=("a pluggable app that runs a full check on the deployment,"
                 " using a number of plugins to check e.g. database, queue server, celery processes, etc."),
    license="BSD",
    keywords="django health check monitoring",
    url="https://github.com/KristianOellegaard/django-health-check",
    packages=[
        'health_check',
        'health_check_celery',
        'health_check_celery3',
        'health_check_db',
        'health_check_cache',
        'health_check.backends',
        'health_check_storage',
    ],
    long_description=read('README.md'),
    classifiers=[
        'Topic :: Utilities',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    install_requires=[
        'Django>=1.4',
    ],
    include_package_data=True,
    zip_safe=False,
)
