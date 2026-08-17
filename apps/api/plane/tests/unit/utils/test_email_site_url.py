# Copyright (c) 2023-present Plane Software, Inc. and contributors
# SPDX-License-Identifier: AGPL-3.0-only
# See the LICENSE file for details.

from email.mime.image import MIMEImage

import pytest
from django.core.mail import EmailMultiAlternatives
from django.test import override_settings

from plane.utils.email import (
    EMAIL_LOGO_CID,
    attach_email_branding,
    email_branding_context,
    get_email_logo_filepath,
    get_email_logo_url,
    get_email_site_url,
)


@pytest.mark.unit
def test_get_email_site_url_prefers_explicit_current_site():
    assert get_email_site_url("https://plane.salis.app/") == "https://plane.salis.app"


@pytest.mark.unit
@override_settings(WEB_URL="https://web.example/", APP_BASE_URL="https://app.example/")
def test_get_email_site_url_falls_back_to_web_url():
    assert get_email_site_url() == "https://web.example"


@pytest.mark.unit
@override_settings(WEB_URL=None, APP_BASE_URL="https://app.example/")
def test_get_email_site_url_falls_back_to_app_base_url():
    assert get_email_site_url() == "https://app.example"


@pytest.mark.unit
@override_settings(WEB_URL="https://plane.salis.app")
def test_get_email_logo_url_uses_cid_not_public_static():
    url = get_email_logo_url()
    assert url == f"cid:{EMAIL_LOGO_CID}"


@pytest.mark.unit
@override_settings(WEB_URL="https://plane.salis.app")
def test_email_branding_context_includes_logo_url():
    ctx = email_branding_context()
    assert ctx["current_site"] == "https://plane.salis.app"
    assert ctx["logo_url"] == f"cid:{EMAIL_LOGO_CID}"


@pytest.mark.unit
def test_email_logo_png_exists_on_disk():
    path = get_email_logo_filepath()
    assert path
    assert path.endswith("salis-logo.png")


@pytest.mark.unit
def test_attach_email_branding_inlines_png():
    msg = EmailMultiAlternatives(subject="t", body="b", to=["devnull@example.com"])
    assert attach_email_branding(msg) is True
    images = [part for part in msg.attachments if isinstance(part, MIMEImage)]
    assert len(images) == 1
    assert images[0].get("Content-ID") == f"<{EMAIL_LOGO_CID}>"
