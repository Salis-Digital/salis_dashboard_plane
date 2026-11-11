/**
 * Copyright (c) 2023-present Plane Software, Inc. and contributors
 * SPDX-License-Identifier: AGPL-3.0-only
 * See the LICENSE file for details.
 */

// assets
import { useTranslation } from "@plane/i18n";
import packageJson from "package.json";

export function PlaneVersionNumber() {
  const { t } = useTranslation();
  return (
    <div className="flex w-full gap-1 py-2 text-12 text-secondary">
      {t("version")}: v{packageJson.version}
    </div>
  );
}
