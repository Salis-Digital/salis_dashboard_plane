# Copyright (c) 2023-present Plane Software, Inc. and contributors
# SPDX-License-Identifier: AGPL-3.0-only
# See the LICENSE file for details.

from unittest.mock import MagicMock, patch

import pytest

from plane.utils.smtp import (
    SMTP_BACKEND,
    SMTPNotConfiguredError,
    close_smtp_connection,
    get_smtp_connection,
    send_smtp_message,
)


@pytest.mark.unit
class TestCloseSmtpConnection:
    def test_skips_quit_and_closes_socket(self):
        smtp = MagicMock()
        connection = MagicMock()
        connection.connection = smtp

        close_smtp_connection(connection)

        smtp.quit.assert_not_called()
        smtp.close.assert_called_once()
        assert connection.connection is None

    def test_swallows_socket_close_errors(self):
        smtp = MagicMock()
        smtp.close.side_effect = TimeoutError("TLS shutdown hung")
        connection = MagicMock()
        connection.connection = smtp

        close_smtp_connection(connection)

        assert connection.connection is None

    def test_noop_when_already_closed(self):
        connection = MagicMock()
        connection.connection = None

        close_smtp_connection(connection)


@pytest.mark.unit
class TestGetSmtpConnection:
    @patch("plane.utils.smtp.get_email_configuration")
    def test_requires_host(self, mock_config):
        mock_config.return_value = ("", "user", "pass", "587", "1", "0", "from@example.com")

        with pytest.raises(SMTPNotConfiguredError):
            get_smtp_connection()

    @patch("plane.utils.smtp.get_email_configuration")
    def test_requires_port(self, mock_config):
        mock_config.return_value = ("smtp.example.com", "user", "pass", "", "1", "0", "from@example.com")

        with pytest.raises(SMTPNotConfiguredError):
            get_smtp_connection()

    @patch("plane.utils.smtp.get_connection")
    @patch("plane.utils.smtp.get_email_configuration")
    def test_uses_smtp_backend_timeout_and_starttls(self, mock_config, mock_get_connection):
        mock_config.return_value = (
            "smtp.migadu.com",
            "plane@example.com",
            "secret",
            "587",
            "1",
            "0",
            "plane@example.com",
        )
        mock_get_connection.return_value = MagicMock()

        connection, from_email = get_smtp_connection(timeout=20)

        assert from_email == "plane@example.com"
        assert connection is mock_get_connection.return_value
        kwargs = mock_get_connection.call_args.kwargs
        assert kwargs["backend"] == SMTP_BACKEND
        assert kwargs["host"] == "smtp.migadu.com"
        assert kwargs["port"] == 587
        assert kwargs["username"] == "plane@example.com"
        assert kwargs["password"] == "secret"
        assert kwargs["use_tls"] is True
        assert kwargs["use_ssl"] is False
        assert kwargs["timeout"] == 20


@pytest.mark.unit
class TestSendSmtpMessage:
    @patch("plane.utils.smtp.close_smtp_connection")
    @patch("plane.utils.smtp.get_smtp_connection")
    def test_opens_before_send_and_closes_after(self, mock_get, mock_close):
        connection = MagicMock()
        mock_get.return_value = (connection, "from@example.com")
        msg = MagicMock()
        msg.from_email = "from@example.com"
        msg.send.return_value = 1

        result = send_smtp_message(msg)

        connection.open.assert_called_once()
        msg.send.assert_called_once_with(fail_silently=False)
        mock_close.assert_called_once_with(connection)
        assert msg.connection is connection
        assert result == 1

    @patch("plane.utils.smtp.close_smtp_connection")
    @patch("plane.utils.smtp.get_smtp_connection")
    def test_closes_even_when_send_raises(self, mock_get, mock_close):
        connection = MagicMock()
        mock_get.return_value = (connection, "from@example.com")
        msg = MagicMock()
        msg.from_email = "from@example.com"
        msg.send.side_effect = TimeoutError("connect hung")

        with pytest.raises(TimeoutError):
            send_smtp_message(msg)

        mock_close.assert_called_once_with(connection)
