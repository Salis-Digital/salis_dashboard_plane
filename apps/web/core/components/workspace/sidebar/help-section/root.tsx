/**
 * Copyright (c) 2023-present Plane Software, Inc. and contributors
 * SPDX-License-Identifier: AGPL-3.0-only
 * See the LICENSE file for details.
 */

import { observer } from "mobx-react";
import { Keyboard } from "lucide-react";
// components
import { AppSidebarItem } from "@/components/sidebar/sidebar-item";
// hooks
import { usePowerK } from "@/hooks/store/use-power-k";

export const HelpMenuRoot = observer(function HelpMenuRoot() {
  const { toggleShortcutsListModal } = usePowerK();

  return (
    <AppSidebarItem
      variant="button"
      item={{
        icon: <Keyboard className="size-5" />,
        onClick: () => toggleShortcutsListModal(true),
      }}
    />
  );
});
