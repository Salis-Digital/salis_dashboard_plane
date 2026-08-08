# Copyright (c) 2023-present Plane Software, Inc. and contributors
# SPDX-License-Identifier: AGPL-3.0-only
# See the LICENSE file for details.

"""Unit tests for instance user directory and workspace member add endpoints."""

from uuid import uuid4

import pytest
from django.utils import timezone
from rest_framework import status

from plane.db.models import User, WorkspaceMember
from plane.license.models import Instance, InstanceAdmin
from plane.tests.factories import WorkspaceFactory, WorkspaceMemberFactory


def create_user(*, email: str, **kwargs) -> User:
    local = email.split("@")[0]
    return User.objects.create(
        email=email,
        username=f"{local}-{uuid4().hex[:8]}",
        first_name=kwargs.pop("first_name", local),
        last_name=kwargs.pop("last_name", "User"),
        display_name=kwargs.pop("display_name", local),
        **kwargs,
    )


@pytest.fixture
def instance(db):
    return Instance.objects.create(
        instance_name="Test Instance",
        instance_id=str(uuid4()),
        current_version="1.0.0",
        last_checked_at=timezone.now(),
        is_setup_done=True,
    )


@pytest.fixture
def instance_admin_user(db):
    return create_user(email="admin@plane.so")


@pytest.fixture
def instance_admin(db, instance, instance_admin_user):
    return InstanceAdmin.objects.create(
        user=instance_admin_user,
        instance=instance,
        role=20,
        is_verified=True,
    )


@pytest.fixture
def admin_client(api_client, instance_admin_user, instance_admin):
    api_client.force_authenticate(user=instance_admin_user)
    return api_client


@pytest.mark.unit
@pytest.mark.django_db
class TestInstanceUserEndpoint:
    def test_lists_active_non_bot_users(self, admin_client, instance_admin_user):
        human = create_user(email="human@plane.so", display_name="Human User")
        create_user(email="bot@plane.so", is_bot=True)
        inactive = create_user(email="inactive@plane.so", is_active=False)

        response = admin_client.get("/api/instances/users/")

        assert response.status_code == status.HTTP_200_OK
        emails = {user["email"] for user in response.data["results"]}
        assert human.email in emails
        assert instance_admin_user.email in emails
        assert "bot@plane.so" not in emails
        assert inactive.email not in emails

    def test_search_filters_users(self, admin_client):
        create_user(email="alice@plane.so", display_name="Alice", first_name="Alice")
        create_user(email="bob@plane.so", display_name="Bob", first_name="Bob")

        response = admin_client.get("/api/instances/users/", {"search": "alice"})

        assert response.status_code == status.HTTP_200_OK
        emails = [user["email"] for user in response.data["results"]]
        assert emails == ["alice@plane.so"]

    def test_includes_workspace_memberships(self, admin_client, instance_admin_user):
        workspace = WorkspaceFactory(owner=instance_admin_user, slug="acme", name="Acme")
        member = create_user(email="member@plane.so", display_name="Member")
        unregistered = create_user(email="lone@plane.so", display_name="Lone")
        WorkspaceMemberFactory(workspace=workspace, member=member, role=15)

        response = admin_client.get("/api/instances/users/")

        assert response.status_code == status.HTTP_200_OK
        by_email = {user["email"]: user for user in response.data["results"]}
        assert by_email[member.email]["workspaces"] == [
            {"id": str(workspace.id), "name": "Acme", "slug": "acme"}
        ]
        assert by_email[unregistered.email]["workspaces"] == []

    def test_filters_by_workspace_and_unregistered(self, admin_client, instance_admin_user):
        workspace_a = WorkspaceFactory(owner=instance_admin_user, slug="alpha")
        workspace_b = WorkspaceFactory(owner=instance_admin_user, slug="beta")
        in_a = create_user(email="in-a@plane.so")
        in_b = create_user(email="in-b@plane.so")
        unregistered = create_user(email="unregistered@plane.so")
        WorkspaceMemberFactory(workspace=workspace_a, member=in_a, role=15)
        WorkspaceMemberFactory(workspace=workspace_b, member=in_b, role=15)

        by_workspace = admin_client.get("/api/instances/users/", {"workspace": "alpha"})
        assert by_workspace.status_code == status.HTTP_200_OK
        assert {user["email"] for user in by_workspace.data["results"]} == {in_a.email}

        unregistered_only = admin_client.get("/api/instances/users/", {"unregistered": "true"})
        assert unregistered_only.status_code == status.HTTP_200_OK
        emails = {user["email"] for user in unregistered_only.data["results"]}
        assert unregistered.email in emails
        assert in_a.email not in emails
        assert in_b.email not in emails

    def test_requires_instance_admin(self, api_client, db):
        user = create_user(email="member@plane.so")
        api_client.force_authenticate(user=user)

        response = api_client.get("/api/instances/users/")

        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.unit
@pytest.mark.django_db
class TestInstanceWorkspaceMemberEndpoint:
    def test_adds_new_members(self, admin_client, instance_admin_user):
        workspace = WorkspaceFactory(owner=instance_admin_user, slug="team-alpha")
        WorkspaceMemberFactory(workspace=workspace, member=instance_admin_user, role=20)
        user_a = create_user(email="a@plane.so")
        user_b = create_user(email="b@plane.so")

        response = admin_client.post(
            f"/api/instances/workspaces/{workspace.slug}/members/",
            {"user_ids": [str(user_a.id), str(user_b.id)], "role": 15},
            format="json",
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data["added"] == 2
        assert response.data["reactivated"] == 0
        assert response.data["skipped"] == 0
        assert WorkspaceMember.objects.filter(workspace=workspace, member=user_a, is_active=True, role=15).exists()
        assert WorkspaceMember.objects.filter(workspace=workspace, member=user_b, is_active=True, role=15).exists()

    def test_skips_existing_active_members_and_reactivates_inactive(self, admin_client, instance_admin_user):
        workspace = WorkspaceFactory(owner=instance_admin_user, slug="team-beta")
        WorkspaceMemberFactory(workspace=workspace, member=instance_admin_user, role=20)
        active_user = create_user(email="active@plane.so")
        inactive_user = create_user(email="inactive-member@plane.so")
        WorkspaceMemberFactory(workspace=workspace, member=active_user, role=15, is_active=True)
        WorkspaceMemberFactory(workspace=workspace, member=inactive_user, role=5, is_active=False)

        response = admin_client.post(
            f"/api/instances/workspaces/{workspace.slug}/members/",
            {"user_ids": [str(active_user.id), str(inactive_user.id)], "role": 15},
            format="json",
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data["added"] == 0
        assert response.data["reactivated"] == 1
        assert response.data["skipped"] == 1
        membership = WorkspaceMember.objects.get(workspace=workspace, member=inactive_user)
        assert membership.is_active is True
        assert membership.role == 15

    def test_rejects_invalid_role_and_missing_workspace(self, admin_client, instance_admin_user):
        workspace = WorkspaceFactory(owner=instance_admin_user, slug="team-gamma")
        user = create_user(email="c@plane.so")

        invalid_role = admin_client.post(
            f"/api/instances/workspaces/{workspace.slug}/members/",
            {"user_ids": [str(user.id)], "role": 99},
            format="json",
        )
        assert invalid_role.status_code == status.HTTP_400_BAD_REQUEST

        missing_workspace = admin_client.post(
            "/api/instances/workspaces/does-not-exist/members/",
            {"user_ids": [str(user.id)], "role": 15},
            format="json",
        )
        assert missing_workspace.status_code == status.HTTP_404_NOT_FOUND
