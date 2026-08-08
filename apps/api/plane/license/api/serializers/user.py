# Copyright (c) 2023-present Plane Software, Inc. and contributors
# SPDX-License-Identifier: AGPL-3.0-only
# See the LICENSE file for details.

from rest_framework import serializers

from .base import BaseSerializer
from plane.db.models import User


class UserLiteSerializer(BaseSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "first_name", "last_name"]


class InstanceUserWorkspaceSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    name = serializers.CharField()
    slug = serializers.CharField()


class InstanceUserSerializer(BaseSerializer):
    avatar_url = serializers.CharField(read_only=True)
    workspaces = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "display_name",
            "first_name",
            "last_name",
            "avatar_url",
            "last_login_medium",
            "date_joined",
            "workspaces",
        ]
        read_only_fields = fields

    def get_workspaces(self, obj):
        memberships_by_user = self.context.get("memberships_by_user") or {}
        workspaces = memberships_by_user.get(str(obj.id), [])
        return InstanceUserWorkspaceSerializer(workspaces, many=True).data
