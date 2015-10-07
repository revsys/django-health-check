__author__ = 'philroche'
import json
import sys
from django.core.management.base import BaseCommand, CommandError
from health_check.utils import get_plugins

class Command(BaseCommand):
    help = 'Django Health Checks'


    def handle(self, *args, **options):
        plugins, working = get_plugins()

        health_check_status = {}
        for plugin in plugins:
            health_check_status[str(plugin.identifier())] = str(plugin.pretty_status())

        health_check_json = json.dumps(health_check_status)
        sys.stdout.write("No filenames given; defaulting to admin scripts\n")