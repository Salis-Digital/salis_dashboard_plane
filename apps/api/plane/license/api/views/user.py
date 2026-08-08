# Copyright (c) 2023-present Plane Software, Inc. and contributors
# SPDX-License-Identifier: AGPL-3.0-only
# See the LICENSE file for details.

# Third party imports
from django.db.models import Q
from rest_framework import status
from rest_framework.response import Response

# Module imports
from plane.app.views.base import BaseAPIView
from plane.db.models import User, Workspace, WorkspaceMember
from plane.license.api.permissions import InstanceAdminPermission
from plane.license.api.serializers import InstanceUserSerializer

ALLOWED_ROLES = {5, 15, 20}


class InstanceUserEndpoint(BaseAPIView):
    permission_classes = [InstanceAdminPermission]

    def get(self, request):
        users = User.objects.filter(is_bot=False, is_active=True).order_by("-date_joined")

        search = request.query_params.get("search", None)
        if search:
            users = users.filter(
                Q(email__icontains=search)
                | Q(display_name__icontains=search)
                | Q(first_name__icontains=search)
                | Q(last_name__icontains=search)
            )

        workspace_filter = request.query_params.get("workspace", None)
        unregistered_only = request.query_params.get("unregistered", "").lower() in {"1", "true", "yes"}

        if unregistered_only:
            users = users.exclude(member_workspace__is_active=True, member_workspace__deleted_at__isnull=True)
        elif workspace_filter:
            users = users.filter(
                member_workspace__is_active=True,
                member_workspace__deleted_at__isnull=True,
                member_workspace__workspace__slug=workspace_filter,
            ).distinct()

        def serialize_page(results):
            user_ids = [user.id for user in results]
            memberships = (
                WorkspaceMember.objects.filter(member_id__in=user_ids, is_active=True, deleted_at__isnull=True)
                .select_related("workspace")
                .order_by("workspace__name")
            )
            memberships_by_user = {}
            for membership in memberships:
                key = str(membership.member_id)
                memberships_by_user.setdefault(key, []).append(membership.workspace)
            return InstanceUserSerializer(
                results,
                many=True,
                context={"memberships_by_user": memberships_by_user},
            ).data

        return self.paginate(
            request=request,
            queryset=users,
            on_results=serialize_page,
            max_per_page=50,
            default_per_page=50,
        )


class InstanceWorkspaceMemberEndpoint(BaseAPIView):
    permission_classes = [InstanceAdminPermission]

    def post(self, request, slug):
        workspace = Workspace.objects.filter(slug=slug).first()
        if not workspace:
            return Response({"error": "Workspace does not exist"}, status=status.HTTP_404_NOT_FOUND)

        user_ids = request.data.get("user_ids", [])
        if not user_ids or not isinstance(user_ids, list):
            return Response({"error": "user_ids is required"}, status=status.HTTP_400_BAD_REQUEST)

        role = request.data.get("role", 15)
        try:
            role = int(role)
        except (TypeError, ValueError):
            return Response({"error": "Invalid role"}, status=status.HTTP_400_BAD_REQUEST)

        if role not in ALLOWED_ROLES:
            return Response(
                {"error": "role must be one of 5 (Guest), 15 (Member), or 20 (Admin)"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        added = 0
        reactivated = 0
        skipped = 0
        errors = []

        users = User.objects.filter(id__in=user_ids)
        users_by_id = {str(user.id): user for user in users}

        for raw_id in user_ids:
            user_id = str(raw_id)
            user = users_by_id.get(user_id)
            if not user:
                skipped += 1
                errors.append({"user_id": user_id, "error": "User not found"})
                continue

            if user.is_bot or not user.is_active:
                skipped += 1
                errors.append({"user_id": user_id, "error": "User is inactive or a bot"})
                continue

            membership = WorkspaceMember.objects.filter(workspace=workspace, member=user).first()
            if membership and membership.is_active:
                skipped += 1
                continue

            if membership and not membership.is_active:
                membership.is_active = True
                membership.role = role
                membership.save(update_fields=["is_active", "role", "updated_at"])
                reactivated += 1
                continue

            WorkspaceMember.objects.create(workspace=workspace, member=user, role=role)
            added += 1

        return Response(
            {
                "added": added,
                "reactivated": reactivated,
                "skipped": skipped,
                "errors": errors,
            },
            status=status.HTTP_200_OK,
        )
