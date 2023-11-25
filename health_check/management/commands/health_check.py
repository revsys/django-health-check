import sys

from django.core.management.base import BaseCommand

from health_check.mixins import CheckMixin


class Command(CheckMixin, BaseCommand):
    help = "Run health checks and exit 0 if everything went well."

    def add_arguments(self, parser):
        parser.add_argument("--subset", type=str, default=None, nargs=1)

    def handle(self, *args, **options):
        # perform all checks
        subset = options.get("subset", [])
        subset = subset[0] if subset else None
        errors = self.check(subset=subset)

        for plugin_identifier, plugin in self.filter_plugins(subset=subset).items():
            style_func = self.style.SUCCESS if not plugin.errors else self.style.ERROR
            self.stdout.write(
                "{:<24} ... {}\n".format(
                    plugin_identifier, style_func(plugin.pretty_status())
                )
            )

        if errors:
            sys.exit(1)
