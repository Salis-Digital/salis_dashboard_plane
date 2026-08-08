/**
 * Copyright (c) 2023-present Plane Software, Inc. and contributors
 * SPDX-License-Identifier: AGPL-3.0-only
 * See the LICENSE file for details.
 */

import { set } from "lodash-es";
import { action, observable, runInAction, makeObservable, computed } from "mobx";
// plane imports
import { InstanceUserService } from "@plane/services";
import type {
  TInstanceAddWorkspaceMembersPayload,
  TInstanceAddWorkspaceMembersResult,
  TInstanceUser,
  TLoader,
  TPaginationInfo,
} from "@plane/types";
// root store
import type { RootStore } from "@/store/root.store";

export type TInstanceUserFilter = {
  search?: string;
  workspace?: string;
  unregistered?: boolean;
};

export interface IInstanceUserStore {
  loader: TLoader;
  users: Record<string, TInstanceUser>;
  paginationInfo: TPaginationInfo | undefined;
  searchQuery: string;
  workspaceFilter: string;
  unregisteredOnly: boolean;
  userIds: string[];
  hydrate: (data: Record<string, TInstanceUser>) => void;
  getUserById: (userId: string) => TInstanceUser | undefined;
  setSearchQuery: (query: string) => void;
  setWorkspaceFilter: (workspaceSlug: string) => void;
  setUnregisteredOnly: (value: boolean) => void;
  fetchUsers: (filter?: TInstanceUserFilter) => Promise<TInstanceUser[]>;
  fetchNextUsers: () => Promise<TInstanceUser[]>;
  addWorkspaceMembers: (
    workspaceSlug: string,
    data: TInstanceAddWorkspaceMembersPayload
  ) => Promise<TInstanceAddWorkspaceMembersResult>;
}

export class InstanceUserStore implements IInstanceUserStore {
  loader: TLoader = "init-loader";
  users: Record<string, TInstanceUser> = {};
  paginationInfo: TPaginationInfo | undefined = undefined;
  searchQuery: string = "";
  workspaceFilter: string = "";
  unregisteredOnly: boolean = false;
  instanceUserService;

  constructor(private store: RootStore) {
    makeObservable(this, {
      loader: observable,
      users: observable,
      paginationInfo: observable,
      searchQuery: observable,
      workspaceFilter: observable,
      unregisteredOnly: observable,
      userIds: computed,
      hydrate: action,
      getUserById: action,
      setSearchQuery: action,
      setWorkspaceFilter: action,
      setUnregisteredOnly: action,
      fetchUsers: action,
      fetchNextUsers: action,
      addWorkspaceMembers: action,
    });
    this.instanceUserService = new InstanceUserService();
  }

  get userIds() {
    return Object.keys(this.users);
  }

  hydrate = (data: Record<string, TInstanceUser>) => {
    if (data) this.users = data;
  };

  getUserById = (userId: string) => this.users[userId];

  setSearchQuery = (query: string) => {
    this.searchQuery = query;
  };

  setWorkspaceFilter = (workspaceSlug: string) => {
    this.workspaceFilter = workspaceSlug;
    this.unregisteredOnly = false;
  };

  setUnregisteredOnly = (value: boolean) => {
    this.unregisteredOnly = value;
    if (value) this.workspaceFilter = "";
  };

  fetchUsers = async (filter?: TInstanceUserFilter): Promise<TInstanceUser[]> => {
    try {
      const search = filter?.search ?? this.searchQuery;
      const workspace = filter?.workspace ?? this.workspaceFilter;
      const unregistered = filter?.unregistered ?? this.unregisteredOnly;
      if (this.userIds.length > 0) {
        this.loader = "mutation";
      } else {
        this.loader = "init-loader";
      }
      const paginatedUserData = await this.instanceUserService.list({
        search: search || undefined,
        workspace: workspace || undefined,
        unregistered: unregistered || undefined,
      });
      runInAction(() => {
        this.users = {};
        const { results, ...paginationInfo } = paginatedUserData;
        results.forEach((user: TInstanceUser) => {
          set(this.users, [user.id], { ...user, workspaces: user.workspaces ?? [] });
        });
        set(this, "paginationInfo", paginationInfo);
        this.searchQuery = search;
        this.workspaceFilter = workspace;
        this.unregisteredOnly = unregistered;
      });
      return paginatedUserData.results;
    } catch (error) {
      console.error("Error fetching instance users", error);
      throw error;
    } finally {
      this.loader = "loaded";
    }
  };

  fetchNextUsers = async (): Promise<TInstanceUser[]> => {
    if (!this.paginationInfo || this.paginationInfo.next_page_results === false) return [];
    try {
      this.loader = "pagination";
      const paginatedUserData = await this.instanceUserService.list({
        search: this.searchQuery || undefined,
        workspace: this.workspaceFilter || undefined,
        unregistered: this.unregisteredOnly || undefined,
        cursor: this.paginationInfo.next_cursor,
      });
      runInAction(() => {
        const { results, ...paginationInfo } = paginatedUserData;
        results.forEach((user: TInstanceUser) => {
          set(this.users, [user.id], { ...user, workspaces: user.workspaces ?? [] });
        });
        set(this, "paginationInfo", paginationInfo);
      });
      return paginatedUserData.results;
    } catch (error) {
      console.error("Error fetching next instance users", error);
      throw error;
    } finally {
      this.loader = "loaded";
    }
  };

  addWorkspaceMembers = async (
    workspaceSlug: string,
    data: TInstanceAddWorkspaceMembersPayload
  ): Promise<TInstanceAddWorkspaceMembersResult> => {
    try {
      this.loader = "mutation";
      const result = await this.instanceUserService.addWorkspaceMembers(workspaceSlug, data);
      // Refresh list so grouping/membership badges stay accurate
      await this.fetchUsers();
      return result;
    } catch (error) {
      console.error("Error adding workspace members", error);
      throw error;
    } finally {
      this.loader = "loaded";
    }
  };
}
