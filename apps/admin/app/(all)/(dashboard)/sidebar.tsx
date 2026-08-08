/**
 * Copyright (c) 2023-present Plane Software, Inc. and contributors
 * SPDX-License-Identifier: AGPL-3.0-only
 * See the LICENSE file for details.
 */

import { useEffect, useRef, useState } from "react";
import { observer } from "mobx-react";
// plane helpers
import { useOutsideClickDetector } from "@plane/hooks";
import { cn } from "@plane/utils";
// hooks
import { useTheme } from "@/hooks/store";
// components
import { AdminSidebarDropdown } from "./sidebar-dropdown";
import { AdminSidebarHelpSection } from "./sidebar-help-section";
import { AdminSidebarMenu } from "./sidebar-menu";

export const AdminSidebar = observer(function AdminSidebar() {
  // store
  const { isSidebarCollapsed, toggleSidebar } = useTheme();
  // viewport — overlay below md so the drawer fills the screen instead of squishing content
  const [isOverlayViewport, setIsOverlayViewport] = useState(() =>
    typeof window !== "undefined" ? window.innerWidth < 768 : false
  );
  const prevWidthRef = useRef(typeof window !== "undefined" ? window.innerWidth : 1024);
  const ref = useRef<HTMLDivElement>(null);

  useOutsideClickDetector(ref, () => {
    if (isSidebarCollapsed === false && isOverlayViewport) {
      toggleSidebar(true);
    }
  });

  useEffect(() => {
    const handleResize = () => {
      const width = window.innerWidth;
      const crossedIntoMobile = prevWidthRef.current >= 768 && width < 768;
      setIsOverlayViewport(width < 768);
      // Only auto-collapse when crossing into mobile, not on every height/chrome resize
      if (crossedIntoMobile) toggleSidebar(true);
      prevWidthRef.current = width;
    };
    handleResize();
    window.addEventListener("resize", handleResize);
    return () => {
      window.removeEventListener("resize", handleResize);
    };
  }, [toggleSidebar]);

  const isMobileOpen = isOverlayViewport && !isSidebarCollapsed;

  return (
    <>
      {/* Mobile backdrop — drawer floats over content */}
      {isMobileOpen && (
        <button
          type="button"
          aria-label="Close sidebar"
          className="fixed inset-0 z-[19] bg-backdrop md:hidden"
          onClick={() => toggleSidebar(true)}
        />
      )}
      <div
        className={cn(
          "z-20 flex h-full flex-shrink-0 flex-col border-r border-subtle bg-surface-1 transition-all duration-300 ease-in-out",
          // Desktop: in-flow rail (expanded or icon-only)
          "md:relative md:translate-x-0 md:opacity-100",
          isSidebarCollapsed ? "md:w-[70px]" : "md:w-[290px]",
          // Mobile: full-screen overlay drawer
          "fixed inset-y-0 left-0 w-full max-w-full md:max-w-none",
          {
            "pointer-events-none -translate-x-full opacity-0 md:pointer-events-auto":
              isOverlayViewport && isSidebarCollapsed,
            "translate-x-0 opacity-100 shadow-raised-200": isMobileOpen,
          }
        )}
        data-prevent-outside-click={isOverlayViewport || undefined}
      >
        <div ref={ref} className="flex h-full w-full flex-1 flex-col">
          <AdminSidebarDropdown />
          <AdminSidebarMenu />
          <AdminSidebarHelpSection />
        </div>
      </div>
    </>
  );
});
