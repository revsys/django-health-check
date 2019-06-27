import mock

from health_check.contrib.redis.backends import RedisHealthCheck


class TestRabbitMQHealthCheck:
    """Test Redis health check."""

    @mock.patch("health_check.contrib.redis.backends.getattr")
    @mock.patch("health_check.contrib.redis.backends.Connection")
    def test_broker_refused_connection(self, mocked_connection, mocked_getattr):
        """Test when the connection to Redis is refused."""
        mocked_getattr.return_value = "celery_broker_url"

        conn_exception = ConnectionRefusedError("Refused connection")

        # mock returns
        mocked_conn = mock.MagicMock()
        mocked_connection.return_value.__enter__.return_value = mocked_conn
        mocked_conn.connect.side_effect = conn_exception

        # instantiates the class
        redis_healthchecker = RedisHealthCheck()

        # invokes the method check_status()
        redis_healthchecker.check_status()
        assert len(redis_healthchecker.errors), 1

        # mock assertions
        mocked_connection.assert_called_once_with("celery_broker_url")
