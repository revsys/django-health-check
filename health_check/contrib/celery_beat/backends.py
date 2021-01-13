from django.conf import settings
from django.utils.module_loading import import_string

from health_check.backends import BaseHealthCheckBackend
from health_check.exceptions import (
    ServiceReturnedUnexpectedResult, ServiceUnavailable
)


class CeleryBeatHealthCheck(BaseHealthCheckBackend):

    def check_status(self):

        try:
            current_app = import_string('celery.current_app')
        except ImportError:
            self.add_error(ServiceUnavailable("No found module name 'celery.current_app'"))
            return

        try:
            Service = import_string('celery.beat.Service')
        except ImportError:
            self.add_error(ServiceUnavailable("No found module name 'celery.beat.Service'"))
            return

        scheduler_module_cls = getattr(settings, 'HEALTHCHECK_CELERY_SCHEDULER', 'celery.beat.PersistentScheduler')
        try:
            scheduler_cls = import_string(scheduler_module_cls)
        except ImportError:
            self.add_error(ServiceUnavailable("No found module name '{cls}'".format(cls=scheduler_module_cls)))
            return

        try:
            schedule = Service(current_app, scheduler_cls=scheduler_cls).get_scheduler().schedule
            due_tasks = {}
            for key, entry in schedule.items():
                # entry.is_due() returns (is_due, time_in_seconds_for_next_execution)
                is_due_tpl = entry.is_due()
                due_tasks[key] = is_due_tpl[0]
            if any(due_tasks.values()):
                self.add_error(ServiceReturnedUnexpectedResult("Some entries are due"))
        except BaseException as e:
            self.add_error(ServiceUnavailable("Unknown error"), e)
