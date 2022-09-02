import sys

from django.core.management.base import BaseCommand

from health_check.mixins import CheckMixin


class Command(CheckMixin, BaseCommand):
    help = "Run health checks and exit 0 if everything went well."

    def handle(self, *args, **options):
        # perform all checks
        errors = self.errors

        for plugin in self.plugins:
            style_func = self.style.SUCCESS if not plugin.errors else self.style.ERROR
            self.stdout.write(
                "{:<24} ... {}\n".format(
                    plugin.identifier(), style_func(plugin.pretty_status())
                )
            )

        if errors:
            sys.exit(1)
