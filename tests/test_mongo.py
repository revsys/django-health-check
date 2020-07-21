import mock
from pymongo import errors

from health_check.contrib.mongo.backends import MongoHealthCheck


class TestMongoHealthCheck:
    """Test Mongo health check."""

    @mock.patch("health_check.contrib.mongo.backends.getattr")
    @mock.patch("health_check.contrib.mongo.backends.MongoClient")
    def test_mongo_refused_connection(self, mocked_client, mocked_getattr):
        """Test when the connection to Mongo is refused."""
        mocked_getattr.return_value = "mongo_host"

        # mock returns
        mocked_client.return_value.server_info.side_effect = errors.PyMongoError("Refused connection")

        # instantiates the class
        mongo_healthchecker = MongoHealthCheck()

        # invokes the method check_status()
        mongo_healthchecker.check_status()
        assert len(mongo_healthchecker.errors) == 1

        # mock assertions
        mocked_client.return_value.server_info.assert_called_once()

    @mock.patch("health_check.contrib.mongo.backends.getattr")
    @mock.patch("health_check.contrib.mongo.backends.MongoClient")
    def test_mongo_conn_ok(self, mocked_client, mocked_getattr):
        """Test everything is OK."""
        mocked_getattr.return_value = "mongo_host"

        # instantiates the class
        mongo_healthchecker = MongoHealthCheck()

        # invokes the method check_status()
        mongo_healthchecker.check_status()
        assert len(mongo_healthchecker.errors) == 0

        # mock assertions
        mocked_client.return_value.server_info.assert_called_once()
