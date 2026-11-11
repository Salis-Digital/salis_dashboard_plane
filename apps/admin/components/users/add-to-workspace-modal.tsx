/**
 * Copyright (c) 2023-present Plane Software, Inc. and contributors
 * SPDX-License-Identifier: AGPL-3.0-only
 * See the LICENSE file for details.
 */

import React, { useEffect, useMemo, useState } from "react";
import { observer } from "mobx-react";
import { Dialog, Transition } from "@headlessui/react";
// plane imports
import { Button } from "@plane/propel/button";
import { setPromiseToast } from "@plane/propel/toast";
import type { TInstanceUser } from "@plane/types";
import { cn } from "@plane/utils";
// hooks
import { useInstanceUser, useWorkspace } from "@/hooks/store";

type Props = {
  isOpen: boolean;
  onClose: () => void;
  users: TInstanceUser[];
};

const ROLE_OPTIONS: { value: 5 | 15 | 20; label: string }[] = [
  { value: 20, label: "Admin" },
  { value: 15, label: "Member" },
  { value: 5, label: "Guest" },
];

export const AddToWorkspaceModal = observer(function AddToWorkspaceModal(props: Props) {
  const { isOpen, onClose, users } = props;
  // store hooks
  const { workspaceIds, fetchWorkspaces, getWorkspaceById } = useWorkspace();
  const { addWorkspaceMembers } = useInstanceUser();
  // state
  const [workspaceId, setWorkspaceId] = useState<string>("");
  const [role, setRole] = useState<5 | 15 | 20>(15);
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    if (isOpen) {
      void fetchWorkspaces();
    }
  }, [isOpen, fetchWorkspaces]);

  useEffect(() => {
    if (!isOpen) {
      setWorkspaceId("");
      setRole(15);
      setIsSubmitting(false);
    }
  }, [isOpen]);

  const selectedWorkspace = workspaceId ? getWorkspaceById(workspaceId) : undefined;
  const userLabel = useMemo(() => {
    if (users.length === 1) {
      return users[0].display_name || users[0].email;
    }
    return `${users.length} users`;
  }, [users]);

  const membershipSlugSet = useMemo(() => {
    const slugs = new Set<string>();
    users.forEach((user) => {
      (user.workspaces ?? []).forEach((workspace) => slugs.add(workspace.slug));
    });
    return slugs;
  }, [users]);

  const handleSubmit = async () => {
    if (!selectedWorkspace || users.length === 0) return;
    if (membershipSlugSet.has(selectedWorkspace.slug) && users.length === 1) return;
    setIsSubmitting(true);

    const promise = addWorkspaceMembers(selectedWorkspace.slug, {
      user_ids: users.map((user) => user.id),
      role,
    });

    setPromiseToast(promise, {
      loading: "Adding members…",
      success: {
        title: "Members updated",
        message: (data) => `Added ${data.added}, reactivated ${data.reactivated}, skipped ${data.skipped}.`,
      },
      error: {
        title: "Failed to add members",
        message: () => "Could not add the selected users to the workspace.",
      },
    });

    try {
      await promise;
      onClose();
    } catch {
      // toast handles error
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Transition.Root show={isOpen} as={React.Fragment}>
      <Dialog as="div" className="relative z-50" onClose={onClose}>
        <Transition.Child
          as={React.Fragment}
          enter="ease-out duration-300"
          enterFrom="opacity-0"
          enterTo="opacity-100"
          leave="ease-in duration-200"
          leaveFrom="opacity-100"
          leaveTo="opacity-0"
        >
          <div className="fixed inset-0 bg-backdrop transition-opacity" />
        </Transition.Child>
        <div className="fixed inset-0 z-10 overflow-y-auto">
          <div className="my-10 flex items-center justify-center p-4 text-center sm:p-0 md:my-24">
            <Transition.Child
              as={React.Fragment}
              enter="ease-out duration-300"
              enterFrom="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95"
              enterTo="opacity-100 translate-y-0 sm:scale-100"
              leave="ease-in duration-200"
              leaveFrom="opacity-100 translate-y-0 sm:scale-100"
              leaveTo="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95"
            >
              <Dialog.Panel className="relative w-full max-w-md transform overflow-hidden rounded-lg bg-surface-1 text-left shadow-raised-200 transition-all">
                <div className="space-y-4 px-4 pt-5 pb-4 sm:p-6">
                  <div>
                    <Dialog.Title as="h3" className="text-16 font-medium text-primary">
                      Add to workspace
                    </Dialog.Title>
                    <p className="mt-1 text-13 text-secondary">
                      Add <span className="font-medium text-primary">{userLabel}</span> as workspace members.
                    </p>
                  </div>

                  <div className="space-y-1.5">
                    <label htmlFor="workspace" className="text-13 font-medium text-secondary">
                      Workspace
                    </label>
                    <select
                      id="workspace"
                      value={workspaceId}
                      onChange={(e) => setWorkspaceId(e.target.value)}
                      className="w-full rounded-md border border-subtle bg-surface-1 px-3 py-2 text-13 text-primary outline-none focus:border-strong"
                    >
                      <option value="">Select a workspace</option>
                      {workspaceIds.map((id) => {
                        const workspace = getWorkspaceById(id);
                        if (!workspace) return null;
                        const alreadyMember = users.length === 1 && membershipSlugSet.has(workspace.slug);
                        return (
                          <option key={id} value={id} disabled={alreadyMember}>
                            {workspace.name} [{workspace.slug}]{alreadyMember ? " — already a member" : ""}
                          </option>
                        );
                      })}
                    </select>
                  </div>

                  <div className="space-y-1.5">
                    <label htmlFor="role" className="text-13 font-medium text-secondary">
                      Role
                    </label>
                    <select
                      id="role"
                      value={role}
                      onChange={(e) => setRole(Number(e.target.value) as 5 | 15 | 20)}
                      className="w-full rounded-md border border-subtle bg-surface-1 px-3 py-2 text-13 text-primary outline-none focus:border-strong"
                    >
                      {ROLE_OPTIONS.map((option) => (
                        <option key={option.value} value={option.value}>
                          {option.label}
                        </option>
                      ))}
                    </select>
                  </div>
                </div>
                <div className="flex items-center justify-end gap-2 border-t border-subtle p-4 sm:px-6">
                  <Button variant="secondary" size="lg" onClick={onClose} disabled={isSubmitting}>
                    Cancel
                  </Button>
                  <Button
                    variant="primary"
                    size="lg"
                    onClick={() => void handleSubmit()}
                    disabled={!workspaceId || users.length === 0 || isSubmitting}
                    className={cn(isSubmitting && "opacity-70")}
                  >
                    Add member{users.length > 1 ? "s" : ""}
                  </Button>
                </div>
              </Dialog.Panel>
            </Transition.Child>
          </div>
        </div>
      </Dialog>
    </Transition.Root>
  );
});
