# Copyright (c) 2023-present Plane Software, Inc. and contributors
# SPDX-License-Identifier: AGPL-3.0-only
# See the LICENSE file for details.

"""Unit tests for Salis IAM JWT claim inspection helpers."""

import base64
import json

import pytest

from plane.authentication.provider.oauth.salis import decode_jwt_payload, parse_extra_auth_query_params


def _encode_segment(payload: dict) -> str:
    raw = json.dumps(payload, separators=(",", ":")).encode("utf-8")
    return base64.urlsafe_b64encode(raw).decode("utf-8").rstrip("=")


@pytest.mark.unit
class TestSalisJwtDecode:
    def test_decode_jwt_payload_reads_email_and_name(self):
        header = _encode_segment({"alg": "none", "typ": "JWT"})
        body = _encode_segment({"email": "user@salis.app", "name": "Ada Lovelace", "sub": "123"})
        token = f"{header}.{body}.sig"

        claims = decode_jwt_payload(token)

        assert claims["email"] == "user@salis.app"
        assert claims["name"] == "Ada Lovelace"
        assert claims["sub"] == "123"

    def test_decode_jwt_payload_returns_empty_for_invalid_token(self):
        assert decode_jwt_payload("not-a-jwt") == {}
        assert decode_jwt_payload("") == {}


@pytest.mark.unit
class TestSalisAuthQueryParams:
    def test_parse_extra_auth_query_params_reads_pairs(self):
        parsed = parse_extra_auth_query_params("?kc_idp_hint=google&prompt=login")
        assert parsed == {"kc_idp_hint": "google", "prompt": "login"}

    def test_parse_extra_auth_query_params_ignores_reserved_keys(self):
        parsed = parse_extra_auth_query_params(
            "client_id=attacker&redirect_uri=https://evil.example&kc_idp_hint=google"
        )
        assert parsed == {"kc_idp_hint": "google"}
        assert "client_id" not in parsed
        assert "redirect_uri" not in parsed

    def test_parse_extra_auth_query_params_empty(self):
        assert parse_extra_auth_query_params("") == {}
        assert parse_extra_auth_query_params(None) == {}
