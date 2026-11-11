/**
 * Copyright (c) 2023-present Plane Software, Inc. and contributors
 * SPDX-License-Identifier: AGPL-3.0-only
 * See the LICENSE file for details.
 */

import { useState, useRef } from "react";
import { useNavigate } from "react-router";
import { LogOut, MoreHorizontal, Settings, Share2, ArchiveIcon } from "lucide-react";
// plane imports
import { IS_PROJECT_PUBLISH_ENABLED, MEMBER_TRACKER_ELEMENTS } from "@plane/constants";
import { useTranslation } from "@plane/i18n";
import { LinkIcon } from "@plane/propel/icons";
import { CustomMenu } from "@plane/ui";

type Props = {
  workspaceSlug: string;
  project: {
    id: string;
  };
  isAdmin: boolean;
  isAuthorized: boolean;
  onCopyText: () => void;
  onLeaveProject: () => void;
  onPublishModal: () => void;
};

export function ProjectActionsMenu({
  workspaceSlug,
  project,
  isAdmin,
  isAuthorized,
  onCopyText,
  onLeaveProject,
  onPublishModal,
}: Props) {
  // states
  const [isMenuActive, setIsMenuActive] = useState(false);
  // translation
  const { t } = useTranslation();
  // refs
  const actionSectionRef = useRef<HTMLButtonElement | null>(null);
  // router
  const navigate = useNavigate();

  // #region agent log
  fetch("http://127.0.0.1:7609/ingest/a3234f4c-2272-4198-9e54-87cbc33df2f3", {
    method: "POST",
    headers: { "Content-Type": "application/json", "X-Debug-Session-Id": "03c010" },
    body: JSON.stringify({
      sessionId: "03c010",
      runId: "publish-disable",
      hypothesisId: "A",
      location: "project-actions-menu.tsx:render",
      message: "ProjectActionsMenu render publish gate",
      data: { isAdmin, publishEnabled: IS_PROJECT_PUBLISH_ENABLED, showPublish: IS_PROJECT_PUBLISH_ENABLED && isAdmin },
      timestamp: Date.now(),
    }),
  }).catch(() => {});
  // #endregion

  return (
    <CustomMenu
      customButton={
        <button
          type="button"
          ref={actionSectionRef}
          className="grid place-items-center rounded-sm p-0.5 text-placeholder hover:bg-layer-1"
          onClick={() => setIsMenuActive(!isMenuActive)}
        >
          <MoreHorizontal className="size-4" />
        </button>
      }
      className="flex-shrink-0"
      customButtonClassName="grid place-items-center"
      placement="bottom-start"
      ariaLabel={t("aria_labels.projects_sidebar.toggle_quick_actions_menu")}
      useCaptureForOutsideClick
      closeOnSelect
      onMenuClose={() => setIsMenuActive(false)}
    >
      {/* Publish project settings — disabled for Salis fork (IS_PROJECT_PUBLISH_ENABLED) */}
      {IS_PROJECT_PUBLISH_ENABLED && isAdmin && (
        <CustomMenu.MenuItem onClick={onPublishModal}>
          <div className="relative flex flex-shrink-0 items-center justify-start gap-2">
            <div className="flex h-4 w-4 cursor-pointer items-center justify-center rounded-sm text-secondary transition-all duration-300 hover:bg-layer-1">
              <Share2 className="h-3.5 w-3.5 stroke-[1.5]" />
            </div>
            <div>{t("publish_project")}</div>
          </div>
        </CustomMenu.MenuItem>
      )}
      <CustomMenu.MenuItem onClick={onCopyText}>
        <span className="flex items-center justify-start gap-2">
          <LinkIcon className="h-3.5 w-3.5 stroke-[1.5]" />
          <span>{t("copy_link")}</span>
        </span>
      </CustomMenu.MenuItem>
      {isAuthorized && (
        <CustomMenu.MenuItem
          onClick={() => {
            navigate(`/${workspaceSlug}/projects/${project?.id}/archives/issues`);
          }}
        >
          <div className="flex cursor-pointer items-center justify-start gap-2">
            <ArchiveIcon className="h-3.5 w-3.5 stroke-[1.5]" />
            <span>{t("archives")}</span>
          </div>
        </CustomMenu.MenuItem>
      )}
      <CustomMenu.MenuItem
        onClick={() => {
          navigate(`/${workspaceSlug}/settings/projects/${project?.id}`);
        }}
      >
        <div className="flex cursor-pointer items-center justify-start gap-2">
          <Settings className="h-3.5 w-3.5 stroke-[1.5]" />
          <span>{t("settings")}</span>
        </div>
      </CustomMenu.MenuItem>
      {/* Leave project */}
      <CustomMenu.MenuItem
        onClick={onLeaveProject}
        data-ph-element={MEMBER_TRACKER_ELEMENTS.SIDEBAR_PROJECT_QUICK_ACTIONS}
      >
        <div className="flex items-center justify-start gap-2">
          <LogOut className="h-3.5 w-3.5 stroke-[1.5]" />
          <span>{t("leave_project")}</span>
        </div>
      </CustomMenu.MenuItem>
    </CustomMenu>
  );
}
