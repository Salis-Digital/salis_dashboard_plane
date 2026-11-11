/**
 * Copyright (c) 2023-present Plane Software, Inc. and contributors
 * SPDX-License-Identifier: AGPL-3.0-only
 * See the LICENSE file for details.
 */

import type { TPaginationInfo } from "../common";

export type TInstanceUserWorkspace = {
  id: string;
  name: string;
  slug: string;
};

export type TInstanceUser = {
  id: string;
  email: string;
  display_name: string;
  first_name: string;
  last_name: string;
  avatar_url: string | null;
  last_login_medium: string;
  date_joined: string;
  workspaces: TInstanceUserWorkspace[];
};

export type TInstanceUserPaginationInfo = TPaginationInfo & {
  results: TInstanceUser[];
};

export type TInstanceAddWorkspaceMembersPayload = {
  user_ids: string[];
  role?: 5 | 15 | 20;
};

export type TInstanceAddWorkspaceMembersResult = {
  added: number;
  reactivated: number;
  skipped: number;
  errors: { user_id: string; error: string }[];
};
