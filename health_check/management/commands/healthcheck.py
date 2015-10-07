__author__ = 'philroche'
import json
import sys
from django.core.management.base import BaseCommand, CommandError
from health_check.utils import get_plugins

class Command(BaseCommand):
    help = 'Django Health Checks'

    def handle(self, *args, **options):
        plugins, working = get_plugins()
        sys.stdout.write("Running Health checks\n")
        for plugin in plugins:
            sys.stdout.write("Running Health check - %s\n" % str(plugin.identifier()))
            sys.stdout.write("Result - %s\n" % str(plugin.pretty_status()))

