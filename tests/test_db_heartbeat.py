import unittest
from unittest.mock import MagicMock, patch

from health_check.contrib.db_heartbeat.backends import DatabaseHeartBeatCheck
from health_check.exceptions import ServiceUnavailable


class TestDatabaseHeartBeatCheck(unittest.TestCase):
    @patch("health_check.contrib.db_heartbeat.backends.connection")
    def test_check_status_success(self, mock_connection):
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = (1,)
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor

        health_check = DatabaseHeartBeatCheck()
        try:
            health_check.check_status()
        except Exception as e:
            self.fail(f"check_status() raised an exception unexpectedly: {e}")

    @patch("health_check.contrib.db_heartbeat.backends.connection")
    def test_check_status_service_unavailable(self, mock_connection):
        mock_connection.cursor.side_effect = Exception("Database error")

        health_check = DatabaseHeartBeatCheck()
        with self.assertRaises(ServiceUnavailable):
            health_check.check_status()
