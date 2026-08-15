# Copyright (c) 2023-present Plane Software, Inc. and contributors
# SPDX-License-Identifier: AGPL-3.0-only
# See the LICENSE file for details.

import pytest
from django.test import override_settings

from plane.utils.email import email_branding_context, get_email_logo_url, get_email_site_url


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
def test_get_email_logo_url_is_absolute_and_points_at_static_logo():
    url = get_email_logo_url()
    assert url.startswith("https://plane.salis.app/")
    assert "salis-logo" in url


@pytest.mark.unit
@override_settings(WEB_URL="https://plane.salis.app")
def test_email_branding_context_includes_logo_url():
    ctx = email_branding_context()
    assert ctx["current_site"] == "https://plane.salis.app"
    assert "salis-logo" in ctx["logo_url"]
