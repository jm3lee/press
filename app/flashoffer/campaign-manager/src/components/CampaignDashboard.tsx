/*
 * Copyright (c) Flashoffer Developers
 * Released under the MIT license.
 */

import Button from "@mui/material/Button";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";
import { useCallback, useMemo, useState } from "react";
import { PrimaryCtaButton, Section, SectionHeader } from "flashoffer-react";

import type { CampaignPayload, CampaignSummary } from "../types";
import { formatTimestampForDisplay } from "../utils";
import { CampaignForm } from "./CampaignForm";
import { CampaignTable } from "./CampaignTable";

interface CampaignDashboardProps {
  campaigns: CampaignSummary[];
  loading: boolean;
  onCreate: (campaignId: string, payload: CampaignPayload) => Promise<void>;
  onUpdate: (campaignId: string, payload: CampaignPayload) => Promise<void>;
  onRefresh: () => Promise<void> | void;
  onLogout: () => void;
  expiresAt: string | null;
}

type DialogState =
  | { mode: "create" }
  | { mode: "edit"; campaign: CampaignSummary };

export const CampaignDashboard = ({
  campaigns,
  loading,
  onCreate,
  onUpdate,
  onRefresh,
  onLogout,
  expiresAt,
}: CampaignDashboardProps): JSX.Element => {
  const [dialog, setDialog] = useState<DialogState | null>(null);
  const [formError, setFormError] = useState<string | null>(null);
  const [formSaving, setFormSaving] = useState(false);

  const openCreate = useCallback(() => {
    setFormError(null);
    setDialog({ mode: "create" });
  }, []);

  const openEdit = useCallback((campaign: CampaignSummary) => {
    setFormError(null);
    setDialog({ mode: "edit", campaign });
  }, []);

  const closeDialog = useCallback(() => {
    if (formSaving) {
      return;
    }
    setDialog(null);
  }, [formSaving]);

  const handleSubmit = useCallback(
    async (campaignId: string, payload: CampaignPayload) => {
      if (!dialog) {
        return;
      }
      setFormSaving(true);
      setFormError(null);
      try {
        if (dialog.mode === "create") {
          await onCreate(campaignId, payload);
        } else {
          await onUpdate(campaignId, payload);
        }
        setDialog(null);
      } catch (submitError) {
        const message = submitError instanceof Error ? submitError.message : String(submitError);
        setFormError(message);
      } finally {
        setFormSaving(false);
      }
    },
    [dialog, onCreate, onUpdate],
  );

  const currentExpiry = useMemo(() => {
    if (!expiresAt) {
      return null;
    }
    return formatTimestampForDisplay(expiresAt);
  }, [expiresAt]);

  return (
    <Section>
      <SectionHeader
        eyebrow="Campaigns"
        title="Manage Flashoffer campaign metadata"
        subtitle="Create new campaigns or adjust deadlines in UTC while reviewing details in your local timezone."
      />
      <Stack direction={{ xs: "column", sm: "row" }} spacing={2} justifyContent="space-between">
        <Stack direction={{ xs: "column", sm: "row" }} spacing={2} alignItems="center">
          <PrimaryCtaButton onClick={openCreate}>New campaign</PrimaryCtaButton>
          <Button variant="outlined" onClick={() => void onRefresh()} disabled={loading}>
            Refresh
          </Button>
        </Stack>
        <Stack direction={{ xs: "column", sm: "row" }} spacing={1} alignItems={{ xs: "flex-start", sm: "center" }}>
          {currentExpiry && (
            <Typography variant="body2" color="text.secondary">
              Session expires at {currentExpiry}
            </Typography>
          )}
          <Button color="inherit" onClick={onLogout}>
            Sign out
          </Button>
        </Stack>
      </Stack>
      <CampaignTable campaigns={campaigns} loading={loading} onEdit={openEdit} />
      {dialog && (
        <CampaignForm
          open
          mode={dialog.mode}
          initial={dialog.mode === "edit" ? dialog.campaign : null}
          onCancel={closeDialog}
          onSubmit={handleSubmit}
          error={formError}
          saving={formSaving}
        />
      )}
    </Section>
  );
};
