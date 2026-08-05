# Copyright (c) 2023-present Plane Software, Inc. and contributors
# SPDX-License-Identifier: AGPL-3.0-only
# See the LICENSE file for details.

# Python imports
import base64
import json
import os
from datetime import datetime
from urllib.parse import urlencode

import pytz
import requests
from django.db import DatabaseError, IntegrityError
from django.utils import timezone

# Module imports
from plane.authentication.adapter.base import Adapter
from plane.authentication.adapter.error import (
    AUTHENTICATION_ERROR_CODES,
    AuthenticationException,
)
from plane.db.models import Account
from plane.license.utils.instance_value import get_configuration_value
from plane.utils.exception_logger import log_exception


def _b64url_decode(segment: str) -> bytes:
    padding = "=" * (-len(segment) % 4)
    return base64.urlsafe_b64decode(segment + padding)


def decode_jwt_payload(token: str) -> dict:
    """Decode JWT payload without verifying signature (claims inspection only)."""
    try:
        parts = token.split(".")
        if len(parts) < 2:
            return {}
        return json.loads(_b64url_decode(parts[1]).decode("utf-8"))
    except (ValueError, json.JSONDecodeError, UnicodeDecodeError):
        return {}


class SalisOAuthProvider(Adapter):
    """
    Salis IAM client using the implicit token flow used by other Salis apps
    (e.g. Carmey/Odoo): redirect to iam.salis.app/oauth2/auth with
    response_type=token, then complete login from the returned access_token.

    Identity is taken from the JWT claims (email + name/username) after the
    token is validated against the Salis security API.
    """

    provider = "salis"
    scope = "token"

    def __init__(self, request, access_token=None, state=None, callback=None):
        (
            SALIS_CLIENT_ID,
            SALIS_IAM_HOST,
            SALIS_API_BASE,
            SALIS_TENANT_ID,
            SALIS_REDIRECT_URI,
        ) = get_configuration_value(
            [
                {
                    "key": "SALIS_CLIENT_ID",
                    "default": os.environ.get("SALIS_CLIENT_ID", "salisplane"),
                },
                {
                    "key": "SALIS_IAM_HOST",
                    "default": os.environ.get("SALIS_IAM_HOST", "https://iam.salis.app"),
                },
                {
                    "key": "SALIS_API_BASE",
                    "default": os.environ.get("SALIS_API_BASE", "https://api2.saalees.com"),
                },
                {
                    "key": "SALIS_TENANT_ID",
                    "default": os.environ.get("SALIS_TENANT_ID", "91"),
                },
                {
                    "key": "SALIS_REDIRECT_URI",
                    "default": os.environ.get("SALIS_REDIRECT_URI", ""),
                },
            ]
        )

        if not SALIS_CLIENT_ID:
            raise AuthenticationException(
                error_code=AUTHENTICATION_ERROR_CODES["SALIS_NOT_CONFIGURED"],
                error_message="SALIS_NOT_CONFIGURED",
            )

        self.client_id = SALIS_CLIENT_ID
        self.iam_host = (SALIS_IAM_HOST or "https://iam.salis.app").rstrip("/")
        self.api_base = (SALIS_API_BASE or "https://api2.saalees.com").rstrip("/")
        self.tenant_id = str(SALIS_TENANT_ID or "91")
        self.access_token = access_token
        self.state = state

        if SALIS_REDIRECT_URI:
            self.redirect_uri = SALIS_REDIRECT_URI
        else:
            scheme = "https" if request.is_secure() else "http"
            self.redirect_uri = f"{scheme}://{request.get_host()}/auth/salis/callback/"

        url_params = {
            "response_type": "token",
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "scope": self.scope,
            "state": state or "",
        }
        self.auth_url = f"{self.iam_host}/oauth2/auth?{urlencode(url_params)}"

        super().__init__(request=request, provider=self.provider, callback=callback)

    def get_auth_url(self):
        return self.auth_url

    def authentication_error_code(self):
        return "SALIS_OAUTH_PROVIDER_ERROR"

    def _request_headers(self):
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
            "tenant-id": self.tenant_id,
        }

    def _verify_token_via_api(self) -> dict:
        """Validate the access token with Salis security API and return profile data."""
        headers = self._request_headers()

        # Prefer get_user (GET) — same identity shape used by IAM getuserinfo.
        try:
            response = requests.get(
                f"{self.api_base}/security/v1/get_user",
                headers=headers,
                timeout=15,
            )
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, dict):
                    return data
        except requests.RequestException:
            self.logger.warning("Salis get_user request failed", exc_info=True)

        # Fallback: verify_token (POST + tenant_id query)
        try:
            response = requests.post(
                f"{self.api_base}/security/v1/verify_token",
                headers=headers,
                params={"tenant_id": self.tenant_id},
                timeout=15,
            )
            response.raise_for_status()
            data = response.json()
            if isinstance(data, dict):
                return data
        except requests.RequestException:
            self.logger.warning("Salis verify_token request failed", exc_info=True)

        code = self.authentication_error_code()
        raise AuthenticationException(
            error_code=AUTHENTICATION_ERROR_CODES[code],
            error_message=str(code),
        )

    def set_token_data(self):
        payload = decode_jwt_payload(self.access_token or "")
        expires_at = None
        if payload.get("exp"):
            try:
                expires_at = datetime.fromtimestamp(int(payload["exp"]), tz=pytz.utc)
            except (TypeError, ValueError, OSError):
                expires_at = None

        self.token_data = {
            "access_token": self.access_token,
            "refresh_token": None,
            "access_token_expired_at": expires_at,
            "refresh_token_expired_at": None,
            "id_token": self.access_token or "",
        }

    def set_user_data(self):
        if not self.access_token:
            code = self.authentication_error_code()
            raise AuthenticationException(
                error_code=AUTHENTICATION_ERROR_CODES[code],
                error_message=str(code),
            )

        # Always validate with Salis — never trust an unverified JWT alone.
        api_profile = self._verify_token_via_api()
        jwt_claims = decode_jwt_payload(self.access_token)

        email = (
            api_profile.get("email")
            or jwt_claims.get("email")
            or api_profile.get("mail")
            or jwt_claims.get("mail")
        )
        display_name = (
            api_profile.get("username")
            or api_profile.get("name")
            or jwt_claims.get("name")
            or jwt_claims.get("username")
            or jwt_claims.get("preferred_username")
            or ""
        )
        provider_id = str(
            api_profile.get("poinum")
            or api_profile.get("sub")
            or api_profile.get("id")
            or jwt_claims.get("sub")
            or jwt_claims.get("poinum")
            or email
            or ""
        )

        if not email:
            raise AuthenticationException(
                error_code=AUTHENTICATION_ERROR_CODES["INVALID_EMAIL"],
                error_message="INVALID_EMAIL",
            )

        # Split display name into first/last for Plane's user model.
        name_parts = str(display_name).strip().split(None, 1)
        first_name = name_parts[0] if name_parts else ""
        last_name = name_parts[1] if len(name_parts) > 1 else ""

        self.user_data = {
            "email": email,
            "user": {
                "provider_id": provider_id,
                "email": email,
                "avatar": api_profile.get("avatar") or jwt_claims.get("picture") or "",
                "first_name": first_name,
                "last_name": last_name,
                "display_name": display_name or None,
                "is_password_autoset": True,
            },
        }

    def create_update_account(self, user):
        try:
            account = Account.objects.filter(
                user=user,
                provider=self.provider,
                provider_account_id=self.user_data.get("user", {}).get("provider_id"),
            ).first()
            if account:
                account.access_token = self.token_data.get("access_token")
                account.refresh_token = self.token_data.get("refresh_token", None)
                account.access_token_expired_at = self.token_data.get("access_token_expired_at")
                account.refresh_token_expired_at = self.token_data.get("refresh_token_expired_at")
                account.last_connected_at = timezone.now()
                account.id_token = self.token_data.get("id_token", "")
                account.save()
            else:
                Account.objects.create(
                    user=user,
                    provider=self.provider,
                    provider_account_id=self.user_data.get("user", {}).get("provider_id"),
                    access_token=self.token_data.get("access_token"),
                    refresh_token=self.token_data.get("refresh_token", None),
                    access_token_expired_at=self.token_data.get("access_token_expired_at"),
                    refresh_token_expired_at=self.token_data.get("refresh_token_expired_at"),
                    last_connected_at=timezone.now(),
                    id_token=self.token_data.get("id_token", ""),
                )
        except (DatabaseError, IntegrityError) as e:
            log_exception(e)

    def authenticate(self):
        self.set_token_data()
        self.set_user_data()
        return self.complete_login_or_signup()
