# Copyright (c) 2023-present Plane Software, Inc. and contributors
# SPDX-License-Identifier: AGPL-3.0-only
# See the LICENSE file for details.

"""Unit tests for issue attachment MIME allowlist and filename fallback."""

import pytest
from django.conf import settings

from plane.app.views.issue.attachment import resolve_attachment_mime_type


@pytest.mark.unit
def test_attachment_mime_types_include_markdown_and_csv_variants():
    assert "text/markdown" in settings.ATTACHMENT_MIME_TYPES
    assert "text/x-markdown" in settings.ATTACHMENT_MIME_TYPES
    assert "text/csv" in settings.ATTACHMENT_MIME_TYPES
    assert "application/csv" in settings.ATTACHMENT_MIME_TYPES


@pytest.mark.unit
@pytest.mark.parametrize(
    ("file_type", "name", "expected"),
    [
        # Empty type + markdown filename → guessed allowlisted type or text fallback
        (False, "notes.md", "text/markdown"),
        ("", "notes.md", "text/markdown"),
        ("application/x-unknown", "notes.md", "text/markdown"),
        # Empty type + csv filename → text/csv (stdlib guess) which is allowlisted
        (False, "export.csv", "text/csv"),
        ("", "export.csv", "text/csv"),
        # Explicit allowlisted type is preserved
        ("image/png", "photo.png", "image/png"),
        # Unknown extension with invalid type → octet-stream
        ("application/x-unknown", "blob.unknownext", "application/octet-stream"),
    ],
)
def test_resolve_attachment_mime_type_fallback(file_type, name, expected, monkeypatch):
    # Ensure .md maps to text/markdown regardless of host mimetypes DB.
    if name.endswith(".md"):
        monkeypatch.setattr(
            "plane.app.views.issue.attachment.mimetypes.guess_type",
            lambda _name, strict=False: ("text/markdown", None),
        )
    if name.endswith(".csv"):
        monkeypatch.setattr(
            "plane.app.views.issue.attachment.mimetypes.guess_type",
            lambda _name, strict=False: ("text/csv", None),
        )
    if name.endswith(".unknownext"):
        monkeypatch.setattr(
            "plane.app.views.issue.attachment.mimetypes.guess_type",
            lambda _name, strict=False: (None, None),
        )

    assert resolve_attachment_mime_type(file_type, name) == expected


@pytest.mark.unit
def test_resolve_attachment_mime_type_maps_unlisted_text_guess_to_plain(monkeypatch):
    monkeypatch.setattr(
        "plane.app.views.issue.attachment.mimetypes.guess_type",
        lambda _name, strict=False: ("text/x-custom-unlisted", None),
    )
    assert resolve_attachment_mime_type(False, "file.custom") == "text/plain"
