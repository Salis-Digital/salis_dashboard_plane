# Copyright (c) 2023-present Plane Software, Inc. and contributors
# SPDX-License-Identifier: AGPL-3.0-only
# See the LICENSE file for details.

"""Outbound SMTP helpers.

Always use Django's SMTP backend (never console/locmem) and never block the
request/worker on SMTP QUIT / TLS shutdown. Migadu and similar servers accept
DATA immediately, then hang on quit(); that previously 504'd God Mode.
"""

from django.core.mail import get_connection

from plane.license.utils.instance_value import get_email_configuration
from plane.utils.email import attach_email_branding

SMTP_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
SMTP_TIMEOUT = 20


class SMTPNotConfiguredError(ValueError):
    """Raised when instance SMTP host or port is missing."""


def get_smtp_connection(*, timeout: int = SMTP_TIMEOUT):
    """Build an SMTP connection from instance config.

    Returns (connection, from_email).
    """
    (
        email_host,
        email_host_user,
        email_host_password,
        email_port,
        email_use_tls,
        email_use_ssl,
        email_from,
    ) = get_email_configuration()

    if not email_host or email_port in (None, ""):
        raise SMTPNotConfiguredError("SMTP is not configured")

    connection = get_connection(
        backend=SMTP_BACKEND,
        host=email_host,
        port=int(email_port),
        username=email_host_user,
        password=email_host_password,
        use_tls=email_use_tls == "1",
        use_ssl=email_use_ssl == "1",
        timeout=timeout,
    )
    return connection, email_from


def close_smtp_connection(connection) -> None:
    """Drop the SMTP socket without waiting for QUIT or TLS shutdown."""
    smtp = getattr(connection, "connection", None)
    try:
        connection.connection = None
    except Exception:
        pass
    if smtp is None:
        return
    try:
        smtp.close()
    except Exception:
        pass


def send_smtp_message(msg, *, timeout: int = SMTP_TIMEOUT):
    """Send `msg` and return as soon as DATA is accepted.

    Opens the connection first so Django will not close it inside send()
    (that path calls quit() and can hang). Close is a raw socket drop.
    """
    connection, from_email = get_smtp_connection(timeout=timeout)
    if not msg.from_email:
        msg.from_email = from_email
    msg.connection = connection
    attach_email_branding(msg)
    try:
        connection.open()
        return msg.send(fail_silently=False)
    finally:
        close_smtp_connection(connection)
