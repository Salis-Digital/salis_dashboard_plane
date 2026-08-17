/**
 * Copyright (c) 2023-present Plane Software, Inc. and contributors
 * SPDX-License-Identifier: AGPL-3.0-only
 * See the LICENSE file for details.
 */

import { useState } from "react";
import { isEmpty } from "lodash-es";
import Link from "next/link";
import { useForm } from "react-hook-form";
import { Monitor } from "lucide-react";
// plane internal packages
import { API_BASE_URL } from "@plane/constants";
import { Button, getButtonStyling } from "@plane/propel/button";
import { TOAST_TYPE, setToast } from "@plane/propel/toast";
import type { IFormattedInstanceConfiguration, TInstanceSalisAuthenticationConfigurationKeys } from "@plane/types";
// components
import { CodeBlock } from "@/components/common/code-block";
import { ConfirmDiscardModal } from "@/components/common/confirm-discard-modal";
import type { TControllerInputFormField } from "@/components/common/controller-input";
import { ControllerInput } from "@/components/common/controller-input";
import type { TCopyField } from "@/components/common/copy-field";
import { CopyField } from "@/components/common/copy-field";
// hooks
import { useInstance } from "@/hooks/store";

type Props = {
  config: IFormattedInstanceConfiguration;
};

type SalisConfigFormValues = Record<TInstanceSalisAuthenticationConfigurationKeys, string>;

export function InstanceSalisConfigForm(props: Props) {
  const { config } = props;
  const [isDiscardChangesModalOpen, setIsDiscardChangesModalOpen] = useState(false);
  const { updateInstanceConfigurations } = useInstance();
  const {
    handleSubmit,
    control,
    reset,
    formState: { errors, isDirty, isSubmitting },
  } = useForm<SalisConfigFormValues>({
    defaultValues: {
      SALIS_CLIENT_ID: config["SALIS_CLIENT_ID"] || "salisplane",
      SALIS_IAM_HOST: config["SALIS_IAM_HOST"] || "https://iam.salis.app",
      SALIS_API_BASE: config["SALIS_API_BASE"] || "https://api2.saalees.com",
      SALIS_TENANT_ID: config["SALIS_TENANT_ID"] || "91",
      SALIS_REDIRECT_URI: config["SALIS_REDIRECT_URI"] || "",
      SALIS_AUTH_QUERY_PARAMS: config["SALIS_AUTH_QUERY_PARAMS"] || "",
    },
  });

  const originURL = !isEmpty(API_BASE_URL) ? API_BASE_URL : typeof window !== "undefined" ? window.location.origin : "";
  const defaultCallback = `${originURL}/auth/salis/callback/`;

  const SALIS_FORM_FIELDS: TControllerInputFormField[] = [
    {
      key: "SALIS_CLIENT_ID",
      type: "text",
      label: "Client ID",
      description: (
        <>
          OAuth client id registered with Salis IAM (same pattern as <CodeBlock darkerShade>salisodoo</CodeBlock> for
          Carmey).
        </>
      ),
      placeholder: "salisplane",
      error: Boolean(errors.SALIS_CLIENT_ID),
      required: true,
    },
    {
      key: "SALIS_IAM_HOST",
      type: "text",
      label: "IAM host",
      description: <>Base URL for the Salis login app (authorize endpoint lives at /oauth2/auth).</>,
      placeholder: "https://iam.salis.app",
      error: Boolean(errors.SALIS_IAM_HOST),
      required: true,
    },
    {
      key: "SALIS_API_BASE",
      type: "text",
      label: "Security API base",
      description: <>Used to validate the access token and read email/name claims (get_user / verify_token).</>,
      placeholder: "https://api2.saalees.com",
      error: Boolean(errors.SALIS_API_BASE),
      required: true,
    },
    {
      key: "SALIS_TENANT_ID",
      type: "text",
      label: "Tenant ID",
      description: <>Sent as tenant-id / tenant_id when calling the Salis security API.</>,
      placeholder: "91",
      error: Boolean(errors.SALIS_TENANT_ID),
      required: true,
    },
    {
      key: "SALIS_REDIRECT_URI",
      type: "text",
      label: "Redirect URI (optional override)",
      description: (
        <>
          Must be a hostname allowed by IAM (<CodeBlock darkerShade>*.salis.app</CodeBlock>,{" "}
          <CodeBlock darkerShade>*.salis.pro</CodeBlock>, etc.). Leave blank to use the API callback below.
        </>
      ),
      placeholder: defaultCallback,
      error: Boolean(errors.SALIS_REDIRECT_URI),
      required: false,
    },
    {
      key: "SALIS_AUTH_QUERY_PARAMS",
      type: "text",
      label: "Login query parameters",
      description: (
        <>
          Extra query string appended to the IAM authorize URL (for example{" "}
          <CodeBlock darkerShade>kc_idp_hint=google&amp;prompt=login</CodeBlock>). Do not include{" "}
          <CodeBlock darkerShade>client_id</CodeBlock>, <CodeBlock darkerShade>redirect_uri</CodeBlock>,{" "}
          <CodeBlock darkerShade>scope</CodeBlock>, or <CodeBlock darkerShade>state</CodeBlock> — those are set
          automatically.
        </>
      ),
      placeholder: "kc_idp_hint=google",
      error: Boolean(errors.SALIS_AUTH_QUERY_PARAMS),
      required: false,
    },
  ];

  const SALIS_SERVICE_DETAILS: TCopyField[] = [
    {
      key: "Callback_URI",
      label: "Callback URI",
      url: config["SALIS_REDIRECT_URI"] || defaultCallback,
      description: (
        <p>
          IAM redirects here with <CodeBlock darkerShade>#access_token=…</CodeBlock>. Register this exact URL with Salis
          IAM allowlisting (hostname must be permitted).
        </p>
      ),
    },
  ];

  const onSubmit = async (formData: SalisConfigFormValues) => {
    try {
      const response = await updateInstanceConfigurations(formData);
      setToast({
        type: TOAST_TYPE.SUCCESS,
        title: "Done!",
        message: "Salis IAM authentication is configured. Enable it from the authentication list, then test sign-in.",
      });
      reset({
        SALIS_CLIENT_ID: response.find((item) => item.key === "SALIS_CLIENT_ID")?.value,
        SALIS_IAM_HOST: response.find((item) => item.key === "SALIS_IAM_HOST")?.value,
        SALIS_API_BASE: response.find((item) => item.key === "SALIS_API_BASE")?.value,
        SALIS_TENANT_ID: response.find((item) => item.key === "SALIS_TENANT_ID")?.value,
        SALIS_REDIRECT_URI: response.find((item) => item.key === "SALIS_REDIRECT_URI")?.value,
        SALIS_AUTH_QUERY_PARAMS: response.find((item) => item.key === "SALIS_AUTH_QUERY_PARAMS")?.value,
      });
    } catch (err) {
      console.error(err);
    }
  };

  const handleGoBack = (e: React.MouseEvent<HTMLAnchorElement, MouseEvent>) => {
    if (isDirty) {
      e.preventDefault();
      setIsDiscardChangesModalOpen(true);
    }
  };

  return (
    <>
      <ConfirmDiscardModal
        isOpen={isDiscardChangesModalOpen}
        onDiscardHref="/authentication"
        handleClose={() => setIsDiscardChangesModalOpen(false)}
      />
      <div className="flex flex-col gap-8">
        <div className="grid w-full grid-cols-2 gap-x-12 gap-y-8">
          <div className="col-span-2 flex flex-col gap-y-4 pt-1 md:col-span-1">
            <div className="pt-2.5 text-18 font-medium">Salis IAM details for Plane</div>
            {SALIS_FORM_FIELDS.map((field) => (
              <ControllerInput
                key={field.key}
                control={control}
                type={field.type}
                name={field.key}
                label={field.label}
                description={field.description}
                placeholder={field.placeholder}
                error={field.error}
                required={field.required}
              />
            ))}
            <div className="flex flex-col gap-1 pt-4">
              <div className="flex items-center gap-4">
                <Button
                  variant="primary"
                  size="lg"
                  onClick={(e) => void handleSubmit(onSubmit)(e)}
                  loading={isSubmitting}
                  disabled={!isDirty}
                >
                  {isSubmitting ? "Saving" : "Save changes"}
                </Button>
                <Link href="/authentication" className={getButtonStyling("secondary", "lg")} onClick={handleGoBack}>
                  Go back
                </Link>
              </div>
            </div>
          </div>
          <div className="col-span-2 flex flex-col gap-y-6 md:col-span-1">
            <div className="pt-2 text-18 font-medium">Plane callback for Salis IAM</div>
            <div className="flex flex-col overflow-hidden rounded-lg">
              <div className="flex items-center gap-x-3 bg-layer-3 px-6 py-3 text-11 font-medium text-secondary uppercase">
                <Monitor className="h-3 w-3" />
                Web
              </div>
              <div className="flex flex-col gap-y-4 bg-layer-1 px-6 py-4">
                {SALIS_SERVICE_DETAILS.map((field) => (
                  <CopyField key={field.key} label={field.label} url={field.url} description={field.description} />
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
