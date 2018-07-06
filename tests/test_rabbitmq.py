"""
Module with unit tests for the RabbitMQ healthchecker.

"""

import unittest
from unittest import mock

from pika.exceptions import ConnectionClosed
from pika.exceptions import ProbableAuthenticationError

from health_check.contrib.rabbitmq.backends import RabbitMQHealthCheck


class TestRabbitMQHealthCheck(unittest.TestCase):
    """
    Unit tests for RabbitMQ healthchecker.

    """

    @mock.patch("health_check.contrib.rabbitmq.backends.ServiceUnavailable")
    @mock.patch("health_check.contrib.rabbitmq.backends.RabbitMQHealthCheck.add_error")
    @mock.patch("health_check.contrib.rabbitmq.backends.pika")
    @mock.patch("health_check.contrib.rabbitmq.backends.RabbitMQHealthCheck._RabbitMQHealthCheck__get_broker_url")
    def test_broker_connection_exception(
        self, mocked_get_broker_url, mocked_pika, mocked_add_error, mocked_service_unavailable
    ):
        """
        Unit: Test case when the connection to RabbitMQ is refused.

        """
        conn_exception = ConnectionClosed("Closed connection")  # used to assert rabbit conn exception was raised

        # mock returns
        mocked_get_broker_url.return_value = "rabbit_url"
        mocked_pika.BlockingConnection.side_effect = conn_exception  # raises an exception
        mocked_pika.URLParameters.return_value = "rabbit_conn"
        mocked_service_unavailable.return_value = "ServinceUnavailable Instance"

        # instantiates the class
        rabbitmq_healthchecker = RabbitMQHealthCheck()

        # invokes the method check_status()
        rabbitmq_healthchecker.check_status()
        self.assertEqual(len(rabbitmq_healthchecker.errors), 1)

        # mock assertions
        mocked_pika.URLParameters.assert_called_once_with("rabbit_url")
        mocked_pika.BlockingConnection.assert_called_once_with("rabbit_conn")
        mocked_add_error.assert_called_once_with("ServinceUnavailable Instance", conn_exception)

    @mock.patch("health_check.contrib.rabbitmq.backends.ServiceUnavailable")
    @mock.patch("health_check.contrib.rabbitmq.backends.RabbitMQHealthCheck.add_error")
    @mock.patch("health_check.contrib.rabbitmq.backends.pika")
    @mock.patch("health_check.contrib.rabbitmq.backends.RabbitMQHealthCheck._RabbitMQHealthCheck__get_broker_url")
    def test_broker_auth_exception(
        self, mocked_get_broker_url, mocked_pika, mocked_add_error, mocked_service_unavailable
    ):
        """
        Unit: Test case when there's an authentication error to connecto RabbitMQ.

        """
        auth_exception = ProbableAuthenticationError("Auth error")  # used to assert rabbit conn exception was raised

        # mock returns
        mocked_get_broker_url.return_value = "rabbit_url"
        mocked_pika.BlockingConnection.side_effect = auth_exception  # raises an exception
        mocked_pika.URLParameters.return_value = "rabbit_conn"
        mocked_service_unavailable.return_value = "ServinceUnavailable Instance"

        # instantiates the class
        rabbitmq_healthchecker = RabbitMQHealthCheck()

        # invokes the method check_status()
        rabbitmq_healthchecker.check_status()
        self.assertEqual(len(rabbitmq_healthchecker.errors), 1)

        # mock assertions
        mocked_pika.URLParameters.assert_called_once_with("rabbit_url")
        mocked_pika.BlockingConnection.assert_called_once_with("rabbit_conn")
        mocked_add_error.assert_called_once_with("ServinceUnavailable Instance", auth_exception)


if __name__ == "__main__":
    unittest.main()
