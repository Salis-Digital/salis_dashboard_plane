# Copyright (c) 2023-present Plane Software, Inc. and contributors
# SPDX-License-Identifier: AGPL-3.0-only
# See the LICENSE file for details.

from django.core.mail import EmailMultiAlternatives
from django.core.management import BaseCommand, CommandError
from django.template.loader import render_to_string
from django.utils.html import strip_tags

# Module imports
from plane.license.utils.instance_value import get_email_configuration
from plane.utils.smtp import send_smtp_message


class Command(BaseCommand):
    """Django command to pause execution until db is available"""

    def add_arguments(self, parser):
        # Positional argument
        parser.add_argument("to_email", type=str, help="receiver's email")

    def handle(self, *args, **options):
        receiver_email = options.get("to_email")

        if not receiver_email:
            raise CommandError("Receiver email is required")

        EMAIL_FROM = get_email_configuration()[-1]
        subject = "Test email from Salis"

        html_content = render_to_string("emails/test_email.html")
        text_content = strip_tags(html_content)

        self.stdout.write(self.style.SUCCESS("Trying to send test email..."))

        try:
            msg = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=EMAIL_FROM,
                to=[receiver_email],
            )
            msg.attach_alternative(html_content, "text/html")
            send_smtp_message(msg)
            self.stdout.write(self.style.SUCCESS("Email successfully sent"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error: Email could not be delivered due to {e}"))
