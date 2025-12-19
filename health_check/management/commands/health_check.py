import sys

from django.core.management.base import BaseCommand
from django.http import Http404

from health_check.mixins import CheckMixin


class Command(CheckMixin, BaseCommand):
    help = "Run health checks and exit 0 if everything went well."

    def add_arguments(self, parser):
        parser.add_argument("-s", "--subset", type=str, nargs=1)

    def handle(self, *args, **options):
        # perform all checks
        subset = options.get("subset", [])
        subset = subset[0] if subset else None
        try:
            errors = self.check(subset=subset)
        except Http404 as e:
            self.stdout.write(str(e))
            sys.exit(1)

        for plugin_identifier, plugin in self.filter_plugins(subset=subset).items():
            style_func = self.style.SUCCESS if not plugin.errors else self.style.ERROR
            self.stdout.write(f"{plugin_identifier:<24} ... {style_func(plugin.pretty_status())}\n")

        if errors:
            sys.exit(1)
