/**
 * Copyright (c) 2023-present Plane Software, Inc. and contributors
 * SPDX-License-Identifier: AGPL-3.0-only
 * See the LICENSE file for details.
 */

import { observer } from "mobx-react";
import { useParams } from "next/navigation";
import { Controller, useForm } from "react-hook-form";
import { AlertTriangleIcon } from "lucide-react";
// Plane imports
import { Button } from "@plane/propel/button";
import { TOAST_TYPE, setToast } from "@plane/propel/toast";
import type { IProject } from "@plane/types";
import { Input, EModalPosition, EModalWidth, ModalCore } from "@plane/ui";
// hooks
import { useUserPermissions } from "@/hooks/store/user";
import { useAppRouter } from "@/hooks/use-app-router";

type FormData = {
  projectName: string;
  confirmLeave: string;
};

const CONFIRM_LEAVE_TEXT = "Leave Project";

const defaultValues: FormData = {
  projectName: "",
  confirmLeave: "",
};

export interface ILeaveProjectModal {
  project: IProject;
  isOpen: boolean;
  onClose: () => void;
}

export const LeaveProjectModal = observer(function LeaveProjectModal(props: ILeaveProjectModal) {
  const { project, isOpen, onClose } = props;
  // router
  const router = useAppRouter();
  const { workspaceSlug } = useParams();
  // store hooks
  const { leaveProject } = useUserPermissions();

  const {
    control,
    formState: { errors, isSubmitting },
    handleSubmit,
    reset,
    watch,
  } = useForm({ defaultValues });

  const canLeave = watch("projectName") === project?.name && watch("confirmLeave") === CONFIRM_LEAVE_TEXT;

  const handleClose = () => {
    reset({ ...defaultValues });
    onClose();
  };

  const onSubmit = async () => {
    if (!workspaceSlug || !canLeave) return;

    try {
      await leaveProject(workspaceSlug.toString(), project.id);
      handleClose();
      router.push(`/${workspaceSlug}/projects`);
    } catch (_err) {
      setToast({
        type: TOAST_TYPE.ERROR,
        title: "You can't leave this project yet.",
        message:
          (typeof _err === "object" && (_err as { error?: string })?.error) ||
          "Something went wrong. Please try again.",
      });
    }
  };

  return (
    <ModalCore isOpen={isOpen} handleClose={handleClose} position={EModalPosition.CENTER} width={EModalWidth.XXL}>
      <form onSubmit={handleSubmit(onSubmit)} className="flex flex-col gap-6 p-6">
        <div className="flex w-full items-center justify-start gap-6">
          <span className="place-items-center rounded-full bg-danger-subtle p-4">
            <AlertTriangleIcon className="h-6 w-6 text-danger-primary" aria-hidden="true" />
          </span>
          <span className="flex items-center justify-start">
            <h3 className="text-18 font-medium 2xl:text-20">Leave Project</h3>
          </span>
        </div>

        <span>
          <p className="text-13 leading-7 text-secondary">
            Are you sure you want to leave the project -
            <span className="font-medium text-primary">{` "${project?.name}" `}</span>? All of the work items associated
            with you will become inaccessible.
          </p>
        </span>

        <div className="text-secondary">
          <p className="text-13 break-words">
            Enter the project name <span className="font-medium text-primary">{project?.name}</span> to continue:
          </p>
          <Controller
            control={control}
            name="projectName"
            rules={{
              required: "Project name is required",
            }}
            render={({ field: { value, onChange, ref } }) => (
              <Input
                id="projectName"
                name="projectName"
                type="text"
                value={value}
                onChange={onChange}
                ref={ref}
                hasError={Boolean(errors.projectName)}
                placeholder="Enter project name"
                className="mt-2 w-full"
                autoComplete="off"
              />
            )}
          />
        </div>

        <div className="text-secondary">
          <p className="text-13">
            To confirm, type <span className="font-medium text-primary">{CONFIRM_LEAVE_TEXT}</span> below:
          </p>
          <Controller
            control={control}
            name="confirmLeave"
            render={({ field: { value, onChange, ref } }) => (
              <Input
                id="confirmLeave"
                name="confirmLeave"
                type="text"
                value={value}
                onChange={onChange}
                ref={ref}
                hasError={Boolean(errors.confirmLeave)}
                placeholder={`Enter '${CONFIRM_LEAVE_TEXT}'`}
                className="mt-2 w-full"
                autoComplete="off"
              />
            )}
          />
        </div>
        <div className="flex justify-end gap-2">
          <Button variant="secondary" size="lg" onClick={handleClose}>
            Cancel
          </Button>
          <Button variant="error-fill" size="lg" type="submit" disabled={!canLeave} loading={isSubmitting}>
            {isSubmitting ? "Leaving..." : "Leave Project"}
          </Button>
        </div>
      </form>
    </ModalCore>
  );
});
