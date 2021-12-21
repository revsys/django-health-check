import sys
import json

from django.core.management.base import BaseCommand

from health_check.conf import HEALTH_CHECK
from health_check.mixins import CheckMixin


class Command(CheckMixin, BaseCommand):
    help = "Run health checks and exit 0 if everything went well."

    def add_arguments(self, parser):
        parser.add_argument("--json-output", action="store_true", required=False)
        parser.add_argument("--verbose", action="store_true", required=False)

    def handle(self, *args, **options):
        if not options["verbose"]:
            HEALTH_CHECK["VERBOSE"] = False

        # perform all checks
        errors = self.errors
        if options["json_output"]:

            self.json_output()
        else:
            self.plain_output()
            if errors:
                sys.exit(1)

    def plain_output(self):
        for plugin in self.plugins:
            style_func = self.style.SUCCESS if not plugin.errors else self.style.ERROR
            self.stdout.write(
                "{:<24} ... {}\n".format(
                    plugin.identifier(),
                    style_func(plugin.pretty_status())
                )
            )

    def json_output(self):
        metrics = {
            p.identifier(): p.status
            for p in self.plugins
        }
        self.stdout.write(json.dumps(metrics))
