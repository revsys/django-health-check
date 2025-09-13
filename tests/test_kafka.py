from unittest import mock

from kafka.errors import KafkaError

from health_check.contrib.kafka.backends import KafkaHealthCheck


class TestKafkaHealthCheck:
    """Test Kafka health check."""

    @mock.patch("health_check.contrib.kafka.backends.getattr")
    @mock.patch("health_check.contrib.kafka.backends.Connection")
    def test_broker_refused_connection(self, mocked_connection, mocked_getattr):
        """Test when the connection to Kafka is refused."""
        mocked_getattr.return_value = "KAFKA_URL"

        conn_exception = ConnectionRefusedError("Refused connection")

        # mock returns
        mocked_conn = mock.MagicMock()
        mocked_connection.return_value.__enter__.return_value = mocked_conn
        mocked_conn.connect.side_effect = conn_exception

        # instantiates the class
        kafka_healthchecker = KafkaHealthCheck()

        # invokes the method check_status()
        kafka_healthchecker.check_status()
        assert len(kafka_healthchecker.errors), 1

        # mock assertions
        mocked_connection.assert_called_once_with("KAFKA_URL")

    @mock.patch("health_check.contrib.kafka.backends.getattr")
    @mock.patch("health_check.contrib.kafka.backends.Connection")
    def test_broker_auth_error(self, mocked_connection, mocked_getattr):
        """Test that the connection to Kafka has an authentication error."""
        mocked_getattr.return_value = "KAFKA_URL"

        conn_exception = KafkaError("Refused connection")

        # mock returns
        mocked_conn = mock.MagicMock()
        mocked_connection.return_value.__enter__.return_value = mocked_conn
        mocked_conn.connect.side_effect = conn_exception

        # instantiates the class
        rabbitmq_healthchecker = KafkaHealthCheck()

        # invokes the method check_status()
        rabbitmq_healthchecker.check_status()
        assert len(rabbitmq_healthchecker.errors), 1

        # mock assertions
        mocked_connection.assert_called_once_with("KAFKA_URL")

