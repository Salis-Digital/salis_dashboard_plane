/**
 * Copyright (c) 2023-present Plane Software, Inc. and contributors
 * SPDX-License-Identifier: AGPL-3.0-only
 * See the LICENSE file for details.
 */

// assets
import packageJson from "package.json";

export function PlaneVersionNumber() {
  return <div className="flex w-full gap-1 text-14 text-secondary">Version: v{packageJson.version}</div>;
}
