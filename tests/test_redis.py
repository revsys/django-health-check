import mock
from kombu.exceptions import ConnectionLimitExceeded, TimeoutError

from health_check.contrib.redis.backends import RedisHealthCheck


class TestRedisHealthCheck:
    """Test Redis health check."""

    @mock.patch("health_check.contrib.redis.backends.getattr")
    @mock.patch("health_check.contrib.redis.backends.Connection")
    def test_redis_refused_connection(self, mocked_connection, mocked_getattr):
        """Test when the connection to Redis is refused."""
        mocked_getattr.return_value = "redis_url"

        # mock returns
        mocked_conn = mock.MagicMock()
        mocked_connection.return_value.__enter__.return_value = mocked_conn
        mocked_conn.connect.side_effect = ConnectionRefusedError("Refused connection")

        # instantiates the class
        redis_healthchecker = RedisHealthCheck()

        # invokes the method check_status()
        redis_healthchecker.check_status()
        assert len(redis_healthchecker.errors), 1

        # mock assertions
        mocked_connection.assert_called_once_with("redis_url")

    @mock.patch("health_check.contrib.redis.backends.getattr")
    @mock.patch("health_check.contrib.redis.backends.Connection")
    def test_redis_timeout_error(self, mocked_connection, mocked_getattr):
        """Test Redis TimeoutError."""
        mocked_getattr.return_value = "redis_url"

        # mock returns
        mocked_conn = mock.MagicMock()
        mocked_connection.return_value.__enter__.return_value = mocked_conn
        mocked_conn.connect.side_effect = TimeoutError("Timeout Error")

        # instantiates the class
        redis_healthchecker = RedisHealthCheck()

        # invokes the method check_status()
        redis_healthchecker.check_status()
        assert len(redis_healthchecker.errors), 1

        # mock assertions
        mocked_connection.assert_called_once_with("redis_url")

    @mock.patch("health_check.contrib.redis.backends.getattr")
    @mock.patch("health_check.contrib.redis.backends.Connection")
    def test_redis_con_limit_exceeded(self, mocked_connection, mocked_getattr):
        """Test Connection Limit Exceeded error."""
        mocked_getattr.return_value = "redis_url"

        # mock returns
        mocked_conn = mock.MagicMock()
        mocked_connection.return_value.__enter__.return_value = mocked_conn
        mocked_conn.connect.side_effect = ConnectionLimitExceeded("Connection limit exceeded")

        # instantiates the class
        redis_healthchecker = RedisHealthCheck()

        # invokes the method check_status()
        redis_healthchecker.check_status()
        assert len(redis_healthchecker.errors), 1

        # mock assertions
        mocked_connection.assert_called_once_with("redis_url")
