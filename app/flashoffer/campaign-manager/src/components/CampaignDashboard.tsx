/*
 * Copyright (c) Flashoffer Developers
 * Released under the MIT license.
 */

import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import CircularProgress from "@mui/material/CircularProgress";
import Paper from "@mui/material/Paper";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";
import { useCallback, useEffect, useMemo, useState } from "react";
import { EventConsole, PrimaryCtaButton, Section, SectionHeader } from "flashoffer-react";

import { buildCampaignEventsUrl } from "../api";
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
  token: string;
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
  token,
}: CampaignDashboardProps): JSX.Element => {
  const [dialog, setDialog] = useState<DialogState | null>(null);
  const [formError, setFormError] = useState<string | null>(null);
  const [formSaving, setFormSaving] = useState(false);
  const [selectedCampaignId, setSelectedCampaignId] = useState<string | null>(null);

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

  useEffect(() => {
    if (!selectedCampaignId) {
      return;
    }
    const exists = campaigns.some((campaign) => campaign.campaignId === selectedCampaignId);
    if (!exists) {
      setSelectedCampaignId(null);
    }
  }, [campaigns, selectedCampaignId]);

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

  const handleSelectCampaign = useCallback((campaign: CampaignSummary | null) => {
    setSelectedCampaignId(campaign ? campaign.campaignId : null);
  }, []);

  const currentExpiry = useMemo(() => {
    if (!expiresAt) {
      return null;
    }
    return formatTimestampForDisplay(expiresAt);
  }, [expiresAt]);

  const selectedCampaign = useMemo(() => {
    if (!selectedCampaignId) {
      return null;
    }
    return campaigns.find((campaign) => campaign.campaignId === selectedCampaignId) ?? null;
  }, [campaigns, selectedCampaignId]);

  const eventsUrl = useMemo(() => {
    if (!selectedCampaign) {
      return null;
    }
    return buildCampaignEventsUrl(selectedCampaign.campaignId);
  }, [selectedCampaign]);

  let eventPaneContent: JSX.Element;
  if (loading && campaigns.length === 0) {
    eventPaneContent = (
      <Stack spacing={2} alignItems="center" justifyContent="center" sx={{ py: 6 }}>
        <CircularProgress size={28} />
        <Typography variant="body2" color="text.secondary" align="center">
          Loading campaigns…
        </Typography>
      </Stack>
    );
  } else if (campaigns.length === 0) {
    eventPaneContent = (
      <Stack spacing={1.5} alignItems="center" justifyContent="center" sx={{ py: 6 }}>
        <Typography variant="h6" align="center">
          No campaigns available
        </Typography>
        <Typography variant="body2" color="text.secondary" align="center">
          Create a campaign to start monitoring incoming event activity in real time.
        </Typography>
      </Stack>
    );
  } else if (!selectedCampaign || !eventsUrl) {
    eventPaneContent = (
      <Stack spacing={1.5} alignItems="center" justifyContent="center" sx={{ py: 6 }}>
        <Typography variant="h6" align="center">
          Select a campaign to monitor events
        </Typography>
        <Typography variant="body2" color="text.secondary" align="center">
          Choose a row above to review the most recent activity captured for that campaign.
        </Typography>
      </Stack>
    );
  } else {
    eventPaneContent = (
      <Box sx={{ width: "100%" }}>
        <EventConsole eventsUrl={eventsUrl} limit={10} authToken={token} />
      </Box>
    );
  }

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
      <Stack spacing={4} sx={{ mt: 4 }}>
        <CampaignTable
          campaigns={campaigns}
          loading={loading}
          onEdit={openEdit}
          onSelect={handleSelectCampaign}
          selectedCampaignId={selectedCampaignId}
        />
        <Paper
          variant="outlined"
          elevation={0}
          sx={{
            borderRadius: 3,
            borderColor: "divider",
            backgroundColor: "background.paper",
            px: { xs: 2, sm: 3 },
            py: { xs: 3, sm: 4 },
          }}
        >
          {eventPaneContent}
        </Paper>
      </Stack>
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
