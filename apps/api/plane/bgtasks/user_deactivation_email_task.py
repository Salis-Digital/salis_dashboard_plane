# Copyright (c) 2023-present Plane Software, Inc. and contributors
# SPDX-License-Identifier: AGPL-3.0-only
# See the LICENSE file for details.

# Python imports
import logging

# Django imports
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

# Third party imports
from celery import shared_task

# Module imports
from plane.db.models import User
from plane.license.utils.instance_value import get_email_configuration
from plane.utils.email import email_branding_context, generate_plain_text_from_html
from plane.utils.exception_logger import log_exception
from plane.utils.smtp import send_smtp_message


@shared_task
def user_deactivation_email(current_site, user_id):
    try:
        # Send email to user when account is deactivated
        user = User.objects.get(id=user_id)
        subject = f"{user.first_name or user.display_name or user.email} has been deactivated on Salis Plane"

        context = {
            **email_branding_context(current_site),
            "email": str(user.email),
            "login_url": current_site + "/login",
        }

        # Send email to user
        html_content = render_to_string("emails/user/user_deactivation.html", context)

        text_content = generate_plain_text_from_html(html_content)
        # Configure email connection from the database
        EMAIL_FROM = get_email_configuration()[-1]

        # Send email
        msg = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=EMAIL_FROM,
            to=[user.email],
        )

        # Attach HTML content
        msg.attach_alternative(html_content, "text/html")
        send_smtp_message(msg)
        logging.getLogger("plane.worker").info("Email sent successfully.")
        return
    except Exception as e:
        log_exception(e)
        return
