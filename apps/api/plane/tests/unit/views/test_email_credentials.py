# Copyright (c) 2023-present Plane Software, Inc. and contributors
# SPDX-License-Identifier: AGPL-3.0-only
# See the LICENSE file for details.

from unittest.mock import patch
from uuid import uuid4

import pytest
from django.utils import timezone
from rest_framework import status
from smtplib import SMTPAuthenticationError

from plane.db.models import User
from plane.license.models import Instance, InstanceAdmin
from plane.utils.smtp import SMTPNotConfiguredError


def create_user(*, email: str, **kwargs) -> User:
    local = email.split("@")[0]
    return User.objects.create(
        email=email,
        username=f"{local}-{uuid4().hex[:8]}",
        first_name=kwargs.pop("first_name", local),
        last_name=kwargs.pop("last_name", "User"),
        display_name=kwargs.pop("display_name", local),
        **kwargs,
    )


@pytest.fixture
def instance(db):
    return Instance.objects.create(
        instance_name="Test Instance",
        instance_id=str(uuid4()),
        current_version="1.0.0",
        last_checked_at=timezone.now(),
        is_setup_done=True,
    )


@pytest.fixture
def instance_admin_user(db):
    return create_user(email="admin@plane.so")


@pytest.fixture
def instance_admin(db, instance, instance_admin_user):
    return InstanceAdmin.objects.create(
        user=instance_admin_user,
        instance=instance,
        role=20,
        is_verified=True,
    )


@pytest.fixture
def admin_client(api_client, instance_admin_user, instance_admin):
    api_client.force_authenticate(user=instance_admin_user)
    return api_client


@pytest.mark.unit
@pytest.mark.django_db
class TestEmailCredentialCheckEndpoint:
    def test_requires_receiver_email(self, admin_client):
        response = admin_client.post("/api/instances/email-credentials-check/", {})
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @patch("plane.license.api.views.configuration.send_smtp_message")
    @patch(
        "plane.license.api.views.configuration.get_email_configuration",
        return_value=("smtp.example.com", "user", "pass", "587", "1", "0", "from@example.com"),
    )
    def test_returns_200_when_send_succeeds(self, _mock_config, mock_send, admin_client):
        mock_send.return_value = 1

        response = admin_client.post(
            "/api/instances/email-credentials-check/",
            {"receiver_email": "to@example.com"},
        )

        assert response.status_code == status.HTTP_200_OK
        mock_send.assert_called_once()
        msg = mock_send.call_args[0][0]
        assert msg.alternatives
        html = msg.alternatives[0][0]
        assert 'src="cid:salis-logo"' in html
        assert 'alt="Salis"' in html

    @patch("plane.license.api.views.configuration.send_smtp_message")
    @patch(
        "plane.license.api.views.configuration.get_email_configuration",
        return_value=("", "", "", "", "1", "0", ""),
    )
    def test_returns_400_when_smtp_not_configured(self, _mock_config, mock_send, admin_client):
        mock_send.side_effect = SMTPNotConfiguredError("SMTP is not configured")

        response = admin_client.post(
            "/api/instances/email-credentials-check/",
            {"receiver_email": "to@example.com"},
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "SMTP is not configured" in response.data["error"]

    @patch("plane.license.api.views.configuration.send_smtp_message")
    @patch(
        "plane.license.api.views.configuration.get_email_configuration",
        return_value=("smtp.example.com", "user", "pass", "587", "1", "0", "from@example.com"),
    )
    def test_returns_400_for_invalid_credentials(self, _mock_config, mock_send, admin_client):
        mock_send.side_effect = SMTPAuthenticationError(454, b"4.7.0 invalid credentials")

        response = admin_client.post(
            "/api/instances/email-credentials-check/",
            {"receiver_email": "to@example.com"},
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["error"] == "Invalid credentials provided"
