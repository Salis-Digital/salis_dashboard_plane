# Copyright (c) 2023-present Plane Software, Inc. and contributors
# SPDX-License-Identifier: AGPL-3.0-only
# See the LICENSE file for details.

"""Contract tests for ``ProjectBulkAssetEndpoint`` project cover linking."""

import pytest
from rest_framework import status

from plane.db.models import FileAsset, Project, ProjectMember


@pytest.fixture
def project(db, workspace, create_user):
    project = Project.objects.create(
        name="Bulk Cover Project",
        identifier="BCP",
        workspace=workspace,
        created_by=create_user,
    )
    ProjectMember.objects.create(
        project=project, member=create_user, workspace=workspace, role=20
    )
    return project


def bulk_url(workspace_slug: str, project_id: str) -> str:
    return f"/api/assets/v2/workspaces/{workspace_slug}/projects/{project_id}/{project_id}/bulk/"


@pytest.mark.contract
class TestProjectBulkAssetCover:
    @pytest.mark.django_db
    def test_links_workspace_scoped_project_cover(self, session_client, workspace, project, create_user):
        """Cover uploaded before project exists (project_id null) can be linked via bulk."""
        asset = FileAsset.objects.create(
            attributes={"name": "cover.jpg", "type": "image/jpeg", "size": 1024},
            asset=f"{workspace.id}/cover.jpg",
            size=1024,
            workspace=workspace,
            project_id=None,
            created_by=create_user,
            entity_type=FileAsset.EntityTypeContext.PROJECT_COVER,
            is_uploaded=True,
        )

        response = session_client.post(
            bulk_url(workspace.slug, str(project.id)),
            {"asset_ids": [str(asset.id)]},
            format="json",
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT
        project.refresh_from_db()
        asset.refresh_from_db()
        assert project.cover_image_asset_id == asset.id
        assert asset.project_id == project.id

    @pytest.mark.django_db
    def test_links_project_scoped_cover(self, session_client, workspace, project, create_user):
        asset = FileAsset.objects.create(
            attributes={"name": "cover.jpg", "type": "image/jpeg", "size": 1024},
            asset=f"{workspace.id}/scoped-cover.jpg",
            size=1024,
            workspace=workspace,
            project=project,
            created_by=create_user,
            entity_type=FileAsset.EntityTypeContext.PROJECT_COVER,
            is_uploaded=True,
        )

        response = session_client.post(
            bulk_url(workspace.slug, str(project.id)),
            {"asset_ids": [str(asset.id)]},
            format="json",
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT
        project.refresh_from_db()
        assert project.cover_image_asset_id == asset.id

    @pytest.mark.django_db
    def test_returns_not_found_for_missing_asset(self, session_client, workspace, project):
        response = session_client.post(
            bulk_url(workspace.slug, str(project.id)),
            {"asset_ids": ["00000000-0000-0000-0000-000000000001"]},
            format="json",
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.data["error"] == "The requested asset could not be found."

    @pytest.mark.django_db
    def test_does_not_link_issue_asset_from_other_project(
        self, session_client, workspace, project, create_user
    ):
        other_project = Project.objects.create(
            name="Other Project",
            identifier="OTH",
            workspace=workspace,
            created_by=create_user,
        )
        foreign_asset = FileAsset.objects.create(
            attributes={"name": "file.pdf", "type": "application/pdf", "size": 1024},
            asset=f"{workspace.id}/foreign.pdf",
            size=1024,
            workspace=workspace,
            project=other_project,
            created_by=create_user,
            entity_type=FileAsset.EntityTypeContext.ISSUE_ATTACHMENT,
            is_uploaded=True,
        )

        response = session_client.post(
            bulk_url(workspace.slug, str(project.id)),
            {"asset_ids": [str(foreign_asset.id)]},
            format="json",
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
