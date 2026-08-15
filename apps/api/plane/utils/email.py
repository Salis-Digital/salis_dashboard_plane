# SPDX-FileCopyrightText: 2023-present Plane Software, Inc.
# SPDX-License-Identifier: LicenseRef-Plane-Commercial
#
# Licensed under the Plane Commercial License (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# https://plane.so/legals/eula
#
# DO NOT remove or modify this notice.
# NOTICE: Proprietary and confidential. Unauthorized use or distribution is prohibited.

# Python imports
import re

# Django imports
from django.conf import settings
from django.contrib.staticfiles.storage import staticfiles_storage
from django.utils.html import strip_tags

EMAIL_LOGO_STATIC_PATH = "logos/salis-logo.png"


def get_email_site_url(current_site=None):
    """
    Absolute origin for email asset URLs (e.g. logo). Prefer an explicit
    current_site from the caller; otherwise fall back to configured web URL.
    """
    site = current_site or settings.WEB_URL or settings.APP_BASE_URL or ""
    return str(site).rstrip("/")


def get_email_logo_url(current_site=None):
    """
    Absolute logo URL for HTML emails.

    Uses the staticfiles storage URL so Manifest/WhiteNoise hashed filenames
    resolve correctly after collectstatic.
    """
    site = get_email_site_url(current_site)
    try:
        logo_path = staticfiles_storage.url(EMAIL_LOGO_STATIC_PATH)
    except Exception:
        logo_path = f"/static/{EMAIL_LOGO_STATIC_PATH}"
    if logo_path.startswith("http://") or logo_path.startswith("https://"):
        return logo_path
    if not site:
        return logo_path
    if not logo_path.startswith("/"):
        logo_path = f"/{logo_path}"
    return f"{site}{logo_path}"


def email_branding_context(current_site=None):
    """Common template context for Salis-branded emails."""
    site = get_email_site_url(current_site)
    return {
        "current_site": site,
        "logo_url": get_email_logo_url(site),
    }


def generate_plain_text_from_html(html_content):
    """
    Generate clean plain text from HTML email template.
    Removes all HTML tags, CSS styles, and excessive whitespace.

    Args:
        html_content (str): The HTML content to convert to plain text

    Returns:
        str: Clean plain text without HTML tags, styles, or excessive whitespace
    """
    # Remove style tags and their content
    html_content = re.sub(r"<style[^>]*>.*?</style>", "", html_content, flags=re.DOTALL | re.IGNORECASE)

    # Strip HTML tags
    text_content = strip_tags(html_content)

    # Remove excessive empty lines
    text_content = re.sub(r"\n\s*\n\s*\n+", "\n\n", text_content)

    # Ensure there's a leading and trailing whitespace
    text_content = "\n\n" + text_content.lstrip().rstrip() + "\n\n"

    return text_content
