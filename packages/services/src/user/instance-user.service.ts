/**
 * Copyright (c) 2023-present Plane Software, Inc. and contributors
 * SPDX-License-Identifier: AGPL-3.0-only
 * See the LICENSE file for details.
 */

import { API_BASE_URL } from "@plane/constants";
import type {
  TInstanceAddWorkspaceMembersPayload,
  TInstanceAddWorkspaceMembersResult,
  TInstanceUserPaginationInfo,
} from "@plane/types";
import { APIService } from "../api.service";

export type TInstanceUserListParams = {
  search?: string;
  cursor?: string;
  workspace?: string;
  unregistered?: boolean;
};

/**
 * Service for instance-level platform user directory and workspace membership.
 */
export class InstanceUserService extends APIService {
  constructor(BASE_URL?: string) {
    super(BASE_URL || API_BASE_URL);
  }

  /**
   * List platform users (non-bot, active) with optional search and cursor pagination.
   */
  async list(params?: TInstanceUserListParams): Promise<TInstanceUserPaginationInfo> {
    return this.get(`/api/instances/users/`, {
      params: {
        search: params?.search || undefined,
        cursor: params?.cursor || undefined,
        workspace: params?.workspace || undefined,
        unregistered: params?.unregistered ? "true" : undefined,
      },
    })
      .then((response) => response?.data)
      .catch((error) => {
        throw error?.response?.data;
      });
  }

  /**
   * Add existing platform users as direct workspace members.
   */
  async addWorkspaceMembers(
    workspaceSlug: string,
    data: TInstanceAddWorkspaceMembersPayload
  ): Promise<TInstanceAddWorkspaceMembersResult> {
    return this.post(`/api/instances/workspaces/${workspaceSlug}/members/`, data)
      .then((response) => response?.data)
      .catch((error) => {
        throw error?.response?.data;
      });
  }
}
