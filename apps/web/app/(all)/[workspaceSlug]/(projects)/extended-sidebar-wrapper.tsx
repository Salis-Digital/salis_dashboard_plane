/**
 * Copyright (c) 2023-present Plane Software, Inc. and contributors
 * SPDX-License-Identifier: AGPL-3.0-only
 * See the LICENSE file for details.
 */

import React, { useEffect } from "react";
import { observer } from "mobx-react";
import { ArrowLeft } from "lucide-react";
// plane imports
import { EXTENDED_SIDEBAR_WIDTH, SIDEBAR_WIDTH } from "@plane/constants";
import { useLocalStorage } from "@plane/hooks";
import { cn } from "@plane/utils";
// hooks
import { useAppTheme } from "@/hooks/store/use-app-theme";
import useExtendedSidebarOutsideClickDetector from "@/hooks/use-extended-sidebar-overview-outside-click";
import useSize from "@/hooks/use-window-size";

type Props = {
  className?: string;
  children: React.ReactNode;
  extendedSidebarRef: React.RefObject<HTMLDivElement>;
  isExtendedSidebarOpened: boolean;
  handleClose: () => void;
  excludedElementId: string;
};

export const ExtendedSidebarWrapper = observer(function ExtendedSidebarWrapper(props: Props) {
  const { className, children, extendedSidebarRef, isExtendedSidebarOpened, handleClose, excludedElementId } = props;
  // store hooks
  const { sidebarCollapsed } = useAppTheme();
  // local storage
  const { storedValue } = useLocalStorage("sidebarWidth", SIDEBAR_WIDTH);
  // viewport — on mobile the extended list replaces the main drawer instead of sitting muted beside it
  const windowSize = useSize();
  const isOverlayViewport = windowSize[0] > 0 && windowSize[0] < 768;

  useExtendedSidebarOutsideClickDetector(extendedSidebarRef, handleClose, excludedElementId);

  useEffect(() => {
    if (sidebarCollapsed) {
      handleClose();
    }
  }, [sidebarCollapsed, handleClose]);

  return (
    <div
      id={excludedElementId}
      ref={extendedSidebarRef}
      data-prevent-outside-click={isOverlayViewport || undefined}
      className={cn(
        "absolute flex h-full transform flex-col border-r border-subtle bg-surface-1 transition-all duration-300 ease-in-out",
        {
          "opacity-100": isExtendedSidebarOpened,
          "pointer-events-none hidden opacity-0": !isExtendedSidebarOpened,
          // Desktop: sit beside the main sidebar
          "shadow-sm z-[21] p-4 py-2": !isOverlayViewport,
          // Mobile: replace the main drawer content above backdrop
          "inset-y-0 left-0 z-[32] w-full p-3 pt-2 shadow-raised-200": isOverlayViewport,
        },
        className
      )}
      style={
        isOverlayViewport
          ? undefined
          : {
              left: `${storedValue ?? SIDEBAR_WIDTH}px`,
              width: `${EXTENDED_SIDEBAR_WIDTH}px`,
            }
      }
    >
      {isOverlayViewport && (
        <div className="mb-2 flex shrink-0 items-center border-b border-subtle pb-2">
          <button
            type="button"
            onClick={(e) => {
              e.stopPropagation();
              handleClose();
            }}
            onMouseDown={(e) => e.stopPropagation()}
            className="flex items-center gap-1.5 rounded-md px-2 py-1.5 text-13 font-medium text-secondary hover:bg-layer-1-hover"
            aria-label="Back"
          >
            <ArrowLeft className="size-4 shrink-0" />
            <span>Back</span>
          </button>
        </div>
      )}
      <div className={cn("flex min-h-0 flex-1 flex-col overflow-y-auto", isOverlayViewport && "gap-0.5")}>
        {children}
      </div>
    </div>
  );
});
