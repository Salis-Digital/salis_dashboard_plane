/**
 * Copyright (c) 2023-present Plane Software, Inc. and contributors
 * SPDX-License-Identifier: AGPL-3.0-only
 * See the LICENSE file for details.
 */

/**
 * Feature gates for the Salis fork.
 * Flip these to re-enable without restoring deleted code paths.
 */

/** When false: hide Publish project UI and treat spaces as unavailable in the web client. */
export const IS_PROJECT_PUBLISH_ENABLED = false;

/** When false: space app should not be started by local turbo/dev workflows. */
export const IS_SPACE_APP_ENABLED = false;
