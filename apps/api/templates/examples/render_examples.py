#!/usr/bin/env python3
"""Render apps/api/templates into static HTML previews under examples/.

Usage (from repo root, with Django installed):

    python3 apps/api/templates/examples/render_examples.py
"""

from __future__ import annotations

import re
import shutil
import sys
from pathlib import Path

try:
    from django.conf import settings
    from django.template import Context, Engine
except ImportError:
    print("Django is required: pip install 'Django>=4.2,<6'", file=sys.stderr)
    sys.exit(1)

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(__file__).resolve().parent
ASSETS = OUT / "assets"
LOGO_REL = "assets/salis-logo.png"
SITE = "https://plane.salis.app"

FILES = [
    ("emails/auth/magic_signin.html", "email-magic-signin.html"),
    ("emails/auth/forgot_password.html", "email-forgot-password.html"),
    ("emails/invitations/workspace_invitation.html", "email-workspace-invitation.html"),
    ("emails/invitations/project_invitation.html", "email-project-invitation.html"),
    ("emails/notifications/project_addition.html", "email-project-addition.html"),
    ("emails/notifications/issue-updates.html", "email-issue-updates.html"),
    ("emails/notifications/webhook-deactivate.html", "email-webhook-deactivate.html"),
    ("emails/user/user_activation.html", "email-user-activation.html"),
    ("emails/user/user_deactivation.html", "email-user-deactivation.html"),
    ("emails/user/email_updated.html", "email-email-updated.html"),
    ("emails/exports/analytics.html", "email-analytics-export.html"),
    ("emails/test_email.html", "email-test.html"),
    ("authentication/salis_callback.html", "auth-salis-callback.html"),
    ("csrf_failure.html", "csrf-failure.html"),
    ("base.html", "base.html"),
]


def sample_context() -> dict:
    return {
        "current_site": SITE,
        "code": "847291",
        "email": "alex@example.com",
        "first_name": "Alex",
        "forgot_password_url": f"{SITE}/accounts/reset-password/?uidb64=demo&token=demo",
        "workspace_name": "Salis Digital",
        "project_name": "Platform Launch",
        "abs_url": f"{SITE}/workspace-invitations/?invitation_id=demo&slug=salis&token=demo",
        "invitation_url": f"{SITE}/project-invitations/?invitation_id=demo",
        "inviter_first_name": "Sam",
        "project_url": f"{SITE}/salis/projects/demo/issues",
        "profile_url": f"{SITE}/profile",
        "login_url": f"{SITE}/login",
        "webhook_url": f"{SITE}/salis/settings/webhooks/demo",
        "message": "Webhook https://hooks.example.com/salis has been deactivated due to failed requests.",
        "root_url": SITE,
        "complete_url": f"{SITE}/auth/salis/complete/",
        "mirror": "#",
        "unsubscribe": "#",
        "entity_type": "issue",
        "actors_involved": 1,
        "summary": "Updates were made to the issue by",
        "workspace": "salis",
        "project": "Platform Launch",
        "issue_url": f"{SITE}/salis/projects/demo/issues/demo-issue",
        "user_preference": f"{SITE}/salis/settings/account/notifications/",
        "issue": {
            "issue_identifier": "PLN-42",
            "name": "Polish email templates for Salis brand",
            "issue_url": f"{SITE}/salis/projects/demo/issues/demo-issue",
        },
        "receiver": {"email": "alex@example.com"},
        "data": [
            {
                "actor_detail": {"avatar_url": "", "first_name": "Sam", "last_name": "Lee"},
                "activity_time": "2 hours ago",
                "changes": {
                    "state": {"old_value": ["Todo"], "new_value": ["In Progress"]},
                    "priority": {"old_value": ["medium"], "new_value": ["high"]},
                    "assignees": {"old_value": [], "new_value": ["Alex Example"]},
                },
            }
        ],
        "comments": [
            {
                "actor_detail": {"avatar_url": "", "first_name": "Sam", "last_name": "Lee"},
                "activity_time": "1 hour ago",
                "comment": "Looks good — shipping after brand pass.",
                "is_mention": False,
            }
        ],
    }


def main() -> None:
    if not settings.configured:
        settings.configure(DEBUG=True, SECRET_KEY="demo-examples")

    ASSETS.mkdir(parents=True, exist_ok=True)
    shutil.copy(ROOT.parent / "plane/static/logos/salis-logo.png", ASSETS / "salis-logo.png")

    engine = Engine(dirs=[str(ROOT)], autoescape=True)
    ctx = sample_context()
    index_items: list[tuple[str, str]] = []

    for rel, out_name in FILES:
        raw = (ROOT / rel).read_text()
        raw = re.sub(r"\{%\s*load\s+[^%]+%\}", "", raw)
        raw = re.sub(
            r"\{%\s*csrf_token\s*%\}",
            '<input type="hidden" name="csrfmiddlewaretoken" value="demo" />',
            raw,
        )
        html = engine.from_string(raw).render(Context(ctx, autoescape=True))
        html = html.replace(f"{SITE}/static/logos/salis-logo.png", LOGO_REL)
        html = html.replace("/static/logos/salis-logo.png", LOGO_REL)
        (OUT / out_name).write_text(html)
        index_items.append((out_name, rel))
        print("wrote", out_name)

    (OUT / "admin-base-site.html").write_text(
        """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <title>Salis Django Admin (preview)</title>
  <style>
    body { margin: 0; font-family: system-ui, sans-serif; background: #f5f5f5; }
    #header { background: #0F0F0F; color: #fff; padding: 16px 24px; }
    #site-name { margin: 0; font-size: 1.25rem; color: #fff; }
    .button { background: #DD4A48; color: #fff; border: 0; padding: 8px 14px; border-radius: 4px; }
    .button:hover { background: #C94040; }
    a { color: #DD4A48; }
    main { padding: 24px; }
  </style>
</head>
<body>
  <div id="header"><h1 id="site-name">Salis Django Admin</h1></div>
  <main>
    <p>Standalone preview of <code>admin/base_site.html</code> branding.</p>
    <button class="button" type="button">Sample action</button>
  </main>
</body>
</html>
"""
    )
    index_items.append(("admin-base-site.html", "admin/base_site.html"))

    cards = "\n".join(
        f'      <li><a href="{name}">{name}</a> <span class="src">← {src}</span></li>'
        for name, src in index_items
    )
    (OUT / "index.html").write_text(
        f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Salis template examples</title>
  <style>
    body {{ margin: 0; font-family: system-ui, sans-serif; background: #0F0F0F; color: #e8eaed; padding: 40px 24px; }}
    h1 {{ color: #fff; margin: 0 0 8px; }}
    .accent {{ color: #DD4A48; }}
    p {{ color: #a1a1aa; max-width: 40rem; }}
    ul {{ list-style: none; padding: 0; margin: 32px 0 0; }}
    li {{ margin: 0 0 10px; padding: 12px 16px; background: #171717; border-radius: 8px; border: 1px solid #262626; }}
    a {{ color: #DD4A48; text-decoration: none; font-weight: 600; }}
    a:hover {{ text-decoration: underline; }}
    .src {{ color: #71717a; font-size: 0.85rem; margin-left: 8px; font-weight: 400; }}
    img.logo {{ width: 56px; height: 56px; border-radius: 10px; margin-bottom: 16px; }}
  </style>
</head>
<body>
  <img class="logo" src="assets/salis-logo.png" alt="Salis" />
  <h1>Salis <span class="accent">template</span> examples</h1>
  <p>Static previews of API email and HTML templates with sample data.</p>
  <ul>
{cards}
  </ul>
</body>
</html>
"""
    )
    print("index.html ready →", OUT / "index.html")


if __name__ == "__main__":
    main()
