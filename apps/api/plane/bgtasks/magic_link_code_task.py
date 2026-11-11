# Copyright (c) 2023-present Plane Software, Inc. and contributors
# SPDX-License-Identifier: AGPL-3.0-only
# See the LICENSE file for details.

# Python imports
import logging

# Third party imports
from celery import shared_task

# Django imports
# Third party imports
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

# Module imports
from plane.license.utils.instance_value import get_email_configuration
from plane.utils.email import email_branding_context, generate_plain_text_from_html
from plane.utils.exception_logger import log_exception
from plane.utils.smtp import send_smtp_message


@shared_task
def magic_link(email, key, token):
    try:
        EMAIL_FROM = get_email_configuration()[-1]

        # Send the mail
        subject = f"Your unique Salis login code is {token}"
        context = {**email_branding_context(), "code": token, "email": email}

        html_content = render_to_string("emails/auth/magic_signin.html", context)
        text_content = generate_plain_text_from_html(html_content)

        msg = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=EMAIL_FROM,
            to=[email],
        )
        msg.attach_alternative(html_content, "text/html")
        send_smtp_message(msg)
        logging.getLogger("plane.worker").info("Email sent successfully.")
        return
    except Exception as e:
        log_exception(e)
        return
