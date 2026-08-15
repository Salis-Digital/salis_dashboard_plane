# Copyright (c) 2023-present Plane Software, Inc. and contributors
# SPDX-License-Identifier: AGPL-3.0-only
# See the LICENSE file for details.

# Python imports
import logging

# Third party imports
from celery import shared_task

# Django imports
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

# Module imports
from plane.license.utils.instance_value import get_email_configuration
from plane.utils.email import email_branding_context, generate_plain_text_from_html
from plane.utils.exception_logger import log_exception
from plane.utils.smtp import send_smtp_message


@shared_task
def send_email_update_magic_code(email, token):
    try:
        EMAIL_FROM = get_email_configuration()[-1]

        # Send the mail
        subject = "Verify your new email address"
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


@shared_task
def send_email_update_confirmation(email):
    """
    Send a confirmation email to the user after their email address has been successfully updated.

    Args:
        email: The new email address that was successfully updated
    """
    try:
        EMAIL_FROM = get_email_configuration()[-1]

        # Send the confirmation email
        subject = "Salis email address successfully updated"
        context = {**email_branding_context(), "email": email}

        html_content = render_to_string("emails/user/email_updated.html", context)
        text_content = generate_plain_text_from_html(html_content)

        msg = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=EMAIL_FROM,
            to=[email],
        )
        msg.attach_alternative(html_content, "text/html")
        send_smtp_message(msg)
        logging.getLogger("plane.worker").info(f"Email update confirmation sent successfully to {email}.")
        return
    except Exception as e:
        log_exception(e)
        return
