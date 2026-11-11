/**
 * Copyright (c) 2023-present Plane Software, Inc. and contributors
 * SPDX-License-Identifier: AGPL-3.0-only
 * See the LICENSE file for details.
 */

import { useEffect, useMemo, useState } from "react";
import { observer } from "mobx-react";
import useSWR from "swr";
import { Loader as LoaderIcon, Search } from "lucide-react";
// plane imports
import { Button } from "@plane/propel/button";
import type { TInstanceUser } from "@plane/types";
import { Avatar, Loader } from "@plane/ui";
import { cn, getFileURL, renderFormattedDate } from "@plane/utils";
// components
import { PageWrapper } from "@/components/common/page-wrapper";
import { AddToWorkspaceModal } from "@/components/users/add-to-workspace-modal";
// hooks
import { useInstanceUser, useWorkspace } from "@/hooks/store";
// types
import type { Route } from "./+types/page";

type TUserGroup = {
  key: string;
  title: string;
  users: TInstanceUser[];
  isUnregistered?: boolean;
};

const isRegistered = (user: TInstanceUser) => (user.workspaces?.length ?? 0) > 0;

export default observer(function UsersManagementPage(_props: Route.ComponentProps) {
  // store
  const {
    userIds,
    loader,
    paginationInfo,
    searchQuery,
    workspaceFilter,
    unregisteredOnly,
    fetchUsers,
    fetchNextUsers,
    getUserById,
    setSearchQuery,
    setWorkspaceFilter,
    setUnregisteredOnly,
  } = useInstanceUser();
  const { workspaceIds, fetchWorkspaces, getWorkspaceById } = useWorkspace();
  // local state
  const [localSearch, setLocalSearch] = useState("");
  const [selectedIds, setSelectedIds] = useState<string[]>([]);
  const [modalUsers, setModalUsers] = useState<TInstanceUser[]>([]);
  const [isModalOpen, setIsModalOpen] = useState(false);

  useSWR("INSTANCE_USERS", () => fetchUsers());
  useSWR("INSTANCE_WORKSPACES_FOR_USERS_FILTER", () => fetchWorkspaces());

  useEffect(() => {
    const timeout = window.setTimeout(() => {
      if (localSearch === searchQuery) return;
      void fetchUsers({ search: localSearch });
    }, 300);
    return () => window.clearTimeout(timeout);
  }, [localSearch, searchQuery, fetchUsers]);

  const users = useMemo(
    () => userIds.map((id) => getUserById(id)).filter((user): user is TInstanceUser => Boolean(user)),
    [userIds, getUserById]
  );

  const groups = useMemo(() => {
    const workspaceMap = new Map<string, TUserGroup>();
    const unregistered: TInstanceUser[] = [];

    users.forEach((user) => {
      const memberships = user.workspaces ?? [];
      if (memberships.length === 0) {
        unregistered.push(user);
        return;
      }
      memberships.forEach((workspace) => {
        const existing = workspaceMap.get(workspace.id);
        if (existing) {
          if (!existing.users.some((u) => u.id === user.id)) existing.users.push(user);
        } else {
          workspaceMap.set(workspace.id, {
            key: workspace.id,
            title: workspace.name,
            users: [user],
          });
        }
      });
    });

    const workspaceGroups = Array.from(workspaceMap.values()).toSorted((a, b) => a.title.localeCompare(b.title));
    if (unregistered.length > 0) {
      workspaceGroups.push({
        key: "unregistered",
        title: "Unregistered users",
        users: unregistered,
        isUnregistered: true,
      });
    }
    return workspaceGroups;
  }, [users]);

  const selectableUsers = useMemo(() => users.filter((user) => !isRegistered(user)), [users]);
  const hasNextPage = paginationInfo?.next_page_results && paginationInfo?.next_cursor !== undefined;
  const allSelectableSelected =
    selectableUsers.length > 0 && selectableUsers.every((user) => selectedIds.includes(user.id));

  const toggleSelectAll = () => {
    if (allSelectableSelected) {
      setSelectedIds((prev) => prev.filter((id) => !selectableUsers.some((user) => user.id === id)));
      return;
    }
    setSelectedIds((prev) => Array.from(new Set([...prev, ...selectableUsers.map((user) => user.id)])));
  };

  const toggleSelect = (user: TInstanceUser) => {
    if (isRegistered(user)) return;
    setSelectedIds((prev) => (prev.includes(user.id) ? prev.filter((id) => id !== user.id) : [...prev, user.id]));
  };

  const openModalForUsers = (targetUsers: TInstanceUser[]) => {
    const eligible = targetUsers.filter((user) => !isRegistered(user));
    if (eligible.length === 0) return;
    setModalUsers(eligible);
    setIsModalOpen(true);
  };

  const selectedUsers = selectableUsers.filter((user) => selectedIds.includes(user.id));

  const handleFilterChange = (value: string) => {
    setSelectedIds([]);
    if (value === "unregistered") {
      setUnregisteredOnly(true);
      void fetchUsers({ search: localSearch, unregistered: true, workspace: "" });
      return;
    }
    setWorkspaceFilter(value);
    setUnregisteredOnly(false);
    void fetchUsers({ search: localSearch, workspace: value || undefined, unregistered: false });
  };

  const filterValue = unregisteredOnly ? "unregistered" : workspaceFilter;

  return (
    <>
      <AddToWorkspaceModal
        isOpen={isModalOpen}
        onClose={() => {
          setIsModalOpen(false);
          setModalUsers([]);
          setSelectedIds([]);
        }}
        users={modalUsers}
      />
      <PageWrapper
        header={{
          title: "Users on this instance",
          description: "People who have signed in (including via Salis IAM). Add unregistered users to a workspace.",
          actions:
            selectedUsers.length > 0 ? (
              <Button variant="primary" size="base" onClick={() => openModalForUsers(selectedUsers)}>
                Add {selectedUsers.length} to workspace
              </Button>
            ) : undefined,
        }}
      >
        <div className="space-y-4">
          <div className="flex flex-col gap-2 sm:flex-row">
            <div className="flex min-w-0 flex-1 items-center gap-2 rounded-md border border-subtle bg-surface-1 px-3 py-2">
              <Search className="size-4 shrink-0 text-placeholder" />
              <input
                type="search"
                value={localSearch}
                onChange={(e) => {
                  setLocalSearch(e.target.value);
                  setSearchQuery(e.target.value);
                }}
                placeholder="Search by name or email"
                className="w-full bg-transparent text-13 text-primary outline-none placeholder:text-placeholder"
              />
            </div>
            <select
              value={filterValue}
              onChange={(e) => handleFilterChange(e.target.value)}
              className="rounded-md border border-subtle bg-surface-1 px-3 py-2 text-13 text-primary outline-none focus:border-strong sm:min-w-56"
              aria-label="Filter users"
            >
              <option value="">All users</option>
              <option value="unregistered">Unregistered only</option>
              {workspaceIds.map((id) => {
                const workspace = getWorkspaceById(id);
                if (!workspace) return null;
                return (
                  <option key={id} value={workspace.slug}>
                    {workspace.name}
                  </option>
                );
              })}
            </select>
          </div>

          {loader === "init-loader" ? (
            <Loader className="space-y-3">
              <Loader.Item height="64px" width="100%" />
              <Loader.Item height="64px" width="100%" />
              <Loader.Item height="64px" width="100%" />
            </Loader>
          ) : (
            <>
              <div className="flex items-center justify-between gap-2">
                <label className="flex items-center gap-2 text-13 text-secondary">
                  <input
                    type="checkbox"
                    checked={allSelectableSelected}
                    onChange={toggleSelectAll}
                    disabled={selectableUsers.length === 0}
                    className="size-4 rounded border-subtle disabled:opacity-40"
                  />
                  Select all unregistered on this page
                </label>
                <span className="text-11 text-tertiary">{paginationInfo?.total_results ?? users.length} users</span>
              </div>

              {users.length === 0 ? (
                <div className="rounded-lg border border-dashed border-subtle px-4 py-10 text-center text-13 text-secondary">
                  No users found.
                </div>
              ) : (
                <div className="space-y-6">
                  {groups.map((group) => (
                    <section key={group.key} className="space-y-2">
                      <div className="flex items-center justify-between gap-2 border-b border-subtle pb-1.5">
                        <h3 className="text-13 font-semibold text-primary">{group.title}</h3>
                        <span className="text-11 text-tertiary">{group.users.length}</span>
                      </div>
                      <div className="space-y-2">
                        {group.users.map((user) => {
                          const registered = isRegistered(user);
                          return (
                            <div
                              key={`${group.key}-${user.id}`}
                              className={cn(
                                "flex items-center justify-between gap-3 rounded-lg border border-subtle bg-layer-1 p-3",
                                registered && "opacity-70"
                              )}
                            >
                              <div className="flex min-w-0 items-center gap-3">
                                <input
                                  type="checkbox"
                                  checked={selectedIds.includes(user.id)}
                                  onChange={() => toggleSelect(user)}
                                  disabled={registered}
                                  className="size-4 shrink-0 rounded border-subtle disabled:cursor-not-allowed disabled:opacity-40"
                                  aria-label={`Select ${user.display_name || user.email}`}
                                />
                                <Avatar
                                  name={user.display_name || user.email}
                                  src={user.avatar_url ? getFileURL(user.avatar_url) : undefined}
                                  size={32}
                                  shape="circle"
                                />
                                <div className="min-w-0">
                                  <div className="truncate text-14 font-medium text-primary">
                                    {user.display_name ||
                                      `${user.first_name} ${user.last_name}`.trim() ||
                                      user.email}
                                  </div>
                                  <div className="truncate text-12 text-tertiary">{user.email}</div>
                                  <div className="mt-0.5 flex flex-wrap items-center gap-x-2 text-11 text-placeholder">
                                    <span>via {user.last_login_medium || "unknown"}</span>
                                    {user.date_joined && (
                                      <>
                                        <span>•</span>
                                        <span>Joined {renderFormattedDate(user.date_joined)}</span>
                                      </>
                                    )}
                                    {registered && !group.isUnregistered && (
                                      <>
                                        <span>•</span>
                                        <span>Already in workspace</span>
                                      </>
                                    )}
                                  </div>
                                </div>
                              </div>
                              <Button
                                variant="secondary"
                                size="sm"
                                onClick={() => openModalForUsers([user])}
                                disabled={registered}
                                className={cn(registered && "cursor-not-allowed opacity-50")}
                              >
                                Add to workspace
                              </Button>
                            </div>
                          );
                        })}
                      </div>
                    </section>
                  ))}
                </div>
              )}

              {hasNextPage && (
                <div className="flex justify-center pt-2">
                  <button
                    type="button"
                    onClick={() => void fetchNextUsers()}
                    disabled={loader === "pagination"}
                    className={cn(
                      "flex items-center gap-2 rounded-md px-3 py-2 text-13 font-medium text-secondary hover:bg-layer-1-hover",
                      loader === "pagination" && "opacity-70"
                    )}
                  >
                    {loader === "pagination" && <LoaderIcon className="size-4 animate-spin" />}
                    Load more
                  </button>
                </div>
              )}
            </>
          )}
        </div>
      </PageWrapper>
    </>
  );
});
