import unittest

from health_check.contrib.db_heartbeat.backends import DatabaseHeartBeatCheck
from health_check.exceptions import ServiceUnavailable


class TestDatabaseHeartBeatCheck(unittest.TestCase):
    def test_check_status_success(self):
        health_check = DatabaseHeartBeatCheck()
        try:
            health_check.check_status()  # Should pass without exceptions
        except Exception as e:
            self.fail(f"check_status() raised an exception unexpectedly: {e}")

    def test_check_status_unexpected_result(self):
        health_check = DatabaseHeartBeatCheck()
        with self.assertRaises(ServiceUnavailable):
            health_check.check_status()
