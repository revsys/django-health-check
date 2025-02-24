from unittest import mock

from health_check.contrib.mail.backends import MailHealthCheck


class TestMailHealthCheck:
    """Test mail health check."""

    @mock.patch("health_check.contrib.mail.backends.get_connection")
    def test_mail_conn_ok(self, mocked_backend):
        """Test everything is OK."""

        # instantiates the class
        mail_health_checker = MailHealthCheck()

        # invokes the method check_status()
        mail_health_checker.check_status()
        assert len(mail_health_checker.errors) == 0, mail_health_checker.errors

        # mock assertions
        assert mocked_backend.return_value.timeout == 15
        mocked_backend.return_value.open.assert_called_once()
        mocked_backend.return_value.close.assert_called_once()

    @mock.patch("health_check.contrib.mail.backends.get_connection")
    def test_mail_conn_refused(self, mocked_backend):
        """Test case then connection refused."""

        mocked_backend.return_value.open.side_effect = ConnectionRefusedError(
            "Refused connection"
        )
        # instantiates the class
        mail_health_checker = MailHealthCheck()

        # invokes the method check_status()
        mail_health_checker.check_status()
        assert len(mail_health_checker.errors) == 1, mail_health_checker.errors
        assert (
            mail_health_checker.errors[0].message
            == mocked_backend.return_value.open.side_effect
        )

        # mock assertions
        mocked_backend.return_value.open.assert_called_once()
