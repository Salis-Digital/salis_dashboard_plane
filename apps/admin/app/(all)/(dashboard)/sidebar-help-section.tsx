/**
 * Copyright (c) 2023-present Plane Software, Inc. and contributors
 * SPDX-License-Identifier: AGPL-3.0-only
 * See the LICENSE file for details.
 */

import { observer } from "mobx-react";
import { WEB_BASE_URL } from "@plane/constants";
// plane internal packages
import { NewTabIcon } from "@plane/propel/icons";
import { Tooltip } from "@plane/propel/tooltip";
import { cn } from "@plane/utils";
// hooks
import { useTheme } from "@/hooks/store";
import { PlaneVersionNumber } from "@/components/common/version-number";

export const AdminSidebarHelpSection = observer(function AdminSidebarHelpSection() {
  const { isSidebarCollapsed } = useTheme();

  const redirectionLink = encodeURI(WEB_BASE_URL + "/");

  return (
    <div
      className={cn(
        "flex h-14 w-full flex-shrink-0 items-center justify-between gap-5 self-baseline border-t border-subtle bg-surface-1 px-4",
        {
          "h-auto flex-col py-1.5": isSidebarCollapsed,
        }
      )}
    >
      <PlaneVersionNumber />
      <div className={`flex items-center gap-1 ${isSidebarCollapsed ? "flex-col justify-center" : "w-full"}`}>
        <Tooltip tooltipContent="Redirect to Plane" position="right" className="ml-4" disabled={!isSidebarCollapsed}>
          <a
            href={redirectionLink}
            className={`relative flex items-center gap-1 rounded-sm bg-layer-1 px-2 py-1 text-body-xs-medium whitespace-nowrap text-secondary`}
          >
            <NewTabIcon width={14} height={14} />
            {!isSidebarCollapsed && "Redirect to Plane"}
          </a>
        </Tooltip>
      </div>
    </div>
  );
});
