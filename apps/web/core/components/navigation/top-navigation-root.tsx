/**
 * Copyright (c) 2023-present Plane Software, Inc. and contributors
 * SPDX-License-Identifier: AGPL-3.0-only
 * See the LICENSE file for details.
 */

// components
import { observer } from "mobx-react";
import { useParams, usePathname } from "next/navigation";
import { cn } from "@plane/utils";
import { TopNavPowerK } from "@/components/navigation";
import { HelpMenuRoot } from "@/components/workspace/sidebar/help-section/root";
import { UserMenuRoot } from "@/components/workspace/sidebar/user-menu-root";
import { WorkspaceMenuRoot } from "@/components/workspace/sidebar/workspace-menu-root";
import { useAppRailPreferences } from "@/hooks/use-navigation-preferences";
import { Tooltip } from "@plane/propel/tooltip";
import { AppSidebarItem } from "@/components/sidebar/sidebar-item";
import useSWR from "swr";
import { useWorkspaceNotifications } from "@/hooks/store/notifications";
// local imports
import { InboxIcon } from "@plane/propel/icons";

export const TopNavigationRoot = observer(function TopNavigationRoot() {
  // router
  const { workspaceSlug } = useParams();
  const pathname = usePathname();

  // store hooks
  const { unreadNotificationsCount, getUnreadNotificationsCount } = useWorkspaceNotifications();
  const { preferences } = useAppRailPreferences();

  const showLabel = preferences.displayMode === "icon_with_label";

  // Fetch notification count
  useSWR(
    workspaceSlug ? "WORKSPACE_UNREAD_NOTIFICATION_COUNT" : null,
    workspaceSlug ? () => getUnreadNotificationsCount(workspaceSlug.toString()) : null
  );

  // Calculate notification count
  const isMentionsEnabled = unreadNotificationsCount.mention_unread_notifications_count > 0;
  const totalNotifications = isMentionsEnabled
    ? unreadNotificationsCount.mention_unread_notifications_count
    : unreadNotificationsCount.total_unread_notifications_count;

  return (
    <div
      className={cn(
        "z-[27] flex min-h-10 w-full items-center gap-2 bg-canvas px-2 transition-all duration-300 sm:gap-3 sm:px-3.5",
        {
          "sm:px-2": !showLabel,
        }
      )}
    >
      {/* Workspace Menu — shrink-0 so logo+chevron never collapse to 0 on mobile */}
      <div className="max-w-[42%] min-w-0 shrink-0 sm:max-w-[40%] md:max-w-none md:flex-auto md:basis-0">
        <WorkspaceMenuRoot variant="top-navigation" />
      </div>
      {/* Power K Search — takes remaining space without forcing w-full over workspace */}
      <div className="flex min-w-0 flex-1 justify-center">
        <TopNavPowerK />
      </div>
      {/* Additional Actions */}
      <div className="flex shrink-0 items-center justify-end gap-0.5 sm:gap-2 md:gap-3">
        <Tooltip tooltipContent="Inbox" position="bottom">
          <AppSidebarItem
            variant="link"
            item={{
              href: `/${workspaceSlug?.toString()}/notifications/`,
              icon: (
                <div className="relative">
                  <InboxIcon className="size-5" />
                  {totalNotifications > 0 && (
                    <span className="absolute top-0 right-0 size-2 rounded-full bg-danger-primary" />
                  )}
                </div>
              ),
              isActive: pathname?.includes("/notifications/"),
            }}
          />
        </Tooltip>
        {/* Keyboard shortcuts are desktop-oriented; hide on mobile to free tap space */}
        <div className="hidden sm:block">
          <Tooltip tooltipContent="Keyboard Shortcuts" position="bottom">
            <HelpMenuRoot />
          </Tooltip>
        </div>
        <div className="flex size-8 items-center justify-center rounded-md hover:bg-layer-1-hover">
          <UserMenuRoot />
        </div>
      </div>
    </div>
  );
});
