# Copyright (c) 2023-present Plane Software, Inc. and contributors
# SPDX-License-Identifier: AGPL-3.0-only
# See the LICENSE file for details.

"""plane URL Configuration"""

from django.apps import apps
from django.conf import settings
from django.urls import include, path, re_path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

handler404 = "plane.app.views.error_404.custom_404_view"

urlpatterns = [
    path("api/", include("plane.app.urls")),
    path("api/instances/", include("plane.license.urls")),
    path("api/v1/", include("plane.api.urls")),
    path("auth/", include("plane.authentication.urls")),
    path("", include("plane.web.urls")),
]

# Public spaces API — disabled while ENABLE_SPACE=0 (files kept under plane.space)
if settings.ENABLE_SPACE:
    urlpatterns.insert(1, path("api/public/", include("plane.space.urls")))

# region agent log
try:
    import json
    import time

    with open("/Users/salisdigital/salis_dashboard_plane/.cursor/debug-03c010.log", "a") as _dbg:
        _dbg.write(
            json.dumps(
                {
                    "sessionId": "03c010",
                    "runId": "publish-disable",
                    "hypothesisId": "B",
                    "location": "plane/urls.py",
                    "message": "API space route gate",
                    "data": {
                        "enable_space": bool(settings.ENABLE_SPACE),
                        "public_mounted": any(
                            getattr(p, "pattern", None) and "public" in str(p.pattern) for p in urlpatterns
                        ),
                    },
                    "timestamp": int(time.time() * 1000),
                }
            )
            + "\n"
        )
except Exception:
    pass
# endregion

if settings.ENABLE_DRF_SPECTACULAR:
    urlpatterns += [
        path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
        path(
            "api/schema/swagger-ui/",
            SpectacularSwaggerView.as_view(url_name="schema"),
            name="swagger-ui",
        ),
        path(
            "api/schema/redoc/",
            SpectacularRedocView.as_view(url_name="schema"),
            name="redoc",
        ),
    ]

if settings.DEBUG and apps.is_installed("debug_toolbar"):
    try:
        import debug_toolbar

        urlpatterns = [re_path(r"^__debug__/", include(debug_toolbar.urls))] + urlpatterns
    except ImportError:
        pass
