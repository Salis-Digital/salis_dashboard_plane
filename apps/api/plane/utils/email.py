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
import os
import re
from email.mime.image import MIMEImage

# Django imports
from django.conf import settings
from django.contrib.staticfiles import finders
from django.contrib.staticfiles.storage import staticfiles_storage
from django.utils.html import strip_tags

EMAIL_LOGO_STATIC_PATH = "logos/salis-logo.png"
EMAIL_LOGO_CID = "salis-logo"


def get_email_site_url(current_site=None):
    """
    Absolute origin for email asset URLs (e.g. logo). Prefer an explicit
    current_site from the caller; otherwise fall back to configured web URL.
    """
    site = current_site or settings.WEB_URL or settings.APP_BASE_URL or ""
    return str(site).rstrip("/")


def get_email_logo_filepath():
    """Filesystem path of the PNG logo shipped with the API."""
    source_path = os.path.join(settings.BASE_DIR, "static", EMAIL_LOGO_STATIC_PATH)
    if os.path.isfile(source_path):
        return source_path
    try:
        stored = staticfiles_storage.path(EMAIL_LOGO_STATIC_PATH)
        if stored and os.path.isfile(stored):
            return stored
    except Exception:
        pass
    found = finders.find(EMAIL_LOGO_STATIC_PATH)
    if isinstance(found, (list, tuple)):
        found = found[0] if found else None
    if found and os.path.isfile(found):
        return found
    return None


def get_email_logo_url(current_site=None):
    """
    Logo src for HTML emails.

    Production `WEB_URL/static/...` is served as the web app HTML shell, and
    hashed God Mode SVGs are not reliable in mail clients. Embed via CID.
    """
    return f"cid:{EMAIL_LOGO_CID}"


def attach_email_branding(msg):
    """Inline-attach the Salis logo so templates can use cid:salis-logo."""
    path = get_email_logo_filepath()
    if not path:
        return False
    with open(path, "rb") as logo_file:
        image = MIMEImage(logo_file.read(), _subtype="png")
    image.add_header("Content-ID", f"<{EMAIL_LOGO_CID}>")
    image.add_header("Content-Disposition", "inline", filename="salis-logo.png")
    msg.attach(image)
    return True


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
