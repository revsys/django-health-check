from datetime import timedelta
from typing import Any, Dict, List, Union

from celery.beat import Service
from celery.schedules import crontab, solar, schedule
from django.conf import settings
from django.utils.module_loading import import_string
from django_celery_beat.models import CrontabSchedule, IntervalSchedule, SolarSchedule
from django_celery_beat.schedulers import ModelEntry
from health_check.backends import BaseHealthCheckBackend
from health_check.exceptions import ServiceReturnedUnexpectedResult, ServiceUnavailable


class CeleryBeatHealthCheck(BaseHealthCheckBackend):
    def check_status(self):
        """
        Checks for overdue tasks in a celery beat scheduler.
        Uses the scheduler module dotted path that is specified in settings.py with `CELERY_BEAT_SCHEDULER`.
        If not specified, defaults to `django_celery_beat`'s `django_celery_beat.schedulers.DatabaseScheduler`.
        Allows a custom buffer to be set using `BEAT_HEALTH_CHECK_BUFFER_SECONDS` in settings.py. The buffer
        defaults to 30 seconds if not defined. The buffer will offset the scheduler interval for when due
        tasks are processed. Using a buffer avoids false positives, such as the case where a task is
        technically due according to the scheduler, but that's only because the scheduler has not hit its
        interval to check and process due tasks.
        """
        from celery.app import default_app as celery_app

        # Dotted path to the Celery beat scheduler. Uses django_celery_beat scheduler at default.
        scheduler_module_path = getattr(settings, "CELERY_BEAT_SCHEDULER", "django_celery_beat.schedulers.DatabaseScheduler")
        scheduler = import_string(scheduler_module_path)
        try:
            # Get the celery scheduler for the current app and scheduler class via a beat Service
            schedule: Dict = (
                Service(app=celery_app, scheduler_cls=scheduler).get_scheduler().schedule
            )

            schedule_tasks: Union[ModelEntry, Any] = schedule.values()
            tasks_due: List[Union[ModelEntry, Any]] = []

            for task in schedule_tasks:
                if self.is_overdue(task):
                    tasks_due.append(task)

            if tasks_due:
                self.add_error(
                    ServiceReturnedUnexpectedResult(
                        f"{len(tasks_due)} task(s) due:{[task.name for task in tasks_due]} "
                    )
                )
        except BaseException as e:
            self.add_error(
                ServiceUnavailable("Encountered unexpected error while checking Beat Tasks"), e
            )

    @staticmethod
    def is_overdue(task: ModelEntry) -> bool:
        """Determines if a task is overdue by checking if a task is overdue more than x seconds.
        Use BEAT_HEALTH_CHECK_BUFFER_SECONDS or defaults to 30 second, when checking if a task should
        be considered overdue.
        Uses the ScheduleEntry.last run at, and the task's schedule in seconds to calculate the
        next time the task is due. If the time that the task is due is less than the current time
        plus the buffer, we say it's overdue. Otherwise, it's not.

        See celery.schedules.schedule.is_due for celery's implementation of determining when a
        entry is due.

        Args:
            task: ScheduleEntry

        Returns:
            bool: If the task is overdue by at least the buffer.
        """
        EXPECTED_SCHEDULE_CLASSES = [solar, crontab, schedule]
        DEFAULT_DUE_BUFFER_SECONDS = 30
        buffer_seconds = getattr(
            settings, "BEAT_HEALTH_CHECK_BUFFER_SECONDS", DEFAULT_DUE_BUFFER_SECONDS
        )
        # django_celery_beat.schedulers.ModelEntry.to_model_schedule returns a Tuple: model_schedule, model_field
        task_schedule: Union[
            CrontabSchedule, IntervalSchedule, SolarSchedule
        ] = task.to_model_schedule(task.schedule)[0]

        # Get the celery schedule from the Modelentry.
        celery_scheduler = task_schedule.schedule
        if celery_scheduler.__class__ not in EXPECTED_SCHEDULE_CLASSES:
            raise ServiceUnavailable(
                f"Encountered unexpected celery schedule class: {celery_scheduler}"
            )
        try:
            celery_schedule: Union[solar, crontab, schedule] = task_schedule.schedule
            due_in = celery_schedule.remaining_estimate(task.last_run_at)
        except BaseException:
            raise ServiceUnavailable("Encountered an error when determining if a task is overdue.")

        next_due_buffered_seconds = (due_in + timedelta(seconds=buffer_seconds)).total_seconds()
        # If the task is due in the past, even with the buffer, we consider it due.
        if next_due_buffered_seconds < 0:
            return True
        else:
            return False
