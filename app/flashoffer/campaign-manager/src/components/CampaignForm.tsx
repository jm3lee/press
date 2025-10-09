/*
 * Copyright (c) Flashoffer Developers
 * Released under the MIT license.
 */

import Button from "@mui/material/Button";
import Dialog from "@mui/material/Dialog";
import DialogActions from "@mui/material/DialogActions";
import DialogContent from "@mui/material/DialogContent";
import DialogTitle from "@mui/material/DialogTitle";
import Stack from "@mui/material/Stack";
import TextField from "@mui/material/TextField";
import Typography from "@mui/material/Typography";
import { FormEvent, useEffect, useMemo, useState } from "react";

import type { CampaignPayload, CampaignSummary } from "../types";
import { fromLocalInputToUtc, toLocalDateTimeInputValue } from "../utils";

interface CampaignFormProps {
  mode: "create" | "edit";
  initial: CampaignSummary | null;
  open: boolean;
  onCancel: () => void;
  onSubmit: (campaignId: string, payload: CampaignPayload) => Promise<void>;
  saving: boolean;
  error: string | null;
}

export const CampaignForm = ({
  mode,
  initial,
  open,
  onCancel,
  onSubmit,
  saving,
  error,
}: CampaignFormProps): JSX.Element => {
  const [campaignId, setCampaignId] = useState(initial?.campaignId ?? "");
  const [name, setName] = useState(initial?.name ?? "");
  const [endTimeLocal, setEndTimeLocal] = useState(toLocalDateTimeInputValue(initial?.endTime));
  const [validationError, setValidationError] = useState<string | null>(null);

  useEffect(() => {
    setCampaignId(initial?.campaignId ?? "");
    setName(initial?.name ?? "");
    setEndTimeLocal(toLocalDateTimeInputValue(initial?.endTime));
    setValidationError(null);
  }, [initial, mode, open]);

  const title = useMemo(() => (mode === "create" ? "Create campaign" : "Edit campaign"), [mode]);

  const submitLabel = useMemo(
    () => (mode === "create" ? "Create campaign" : "Save changes"),
    [mode],
  );

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setValidationError(null);

    const normalizedId = campaignId.trim();
    if (!normalizedId) {
      setValidationError("Campaign identifier is required.");
      return;
    }

    const iso = fromLocalInputToUtc(endTimeLocal);
    if (!iso) {
      setValidationError("Provide a valid end time in your local timezone.");
      return;
    }

    const normalizedName = name.trim();

    await onSubmit(normalizedId, {
      name: normalizedName ? normalizedName : null,
      end_time: iso,
    });
  };

  return (
    <Dialog open={open} onClose={onCancel} fullWidth maxWidth="sm">
      <DialogTitle>{title}</DialogTitle>
      <DialogContent>
        <Stack component="form" spacing={3} sx={{ mt: 1 }} onSubmit={handleSubmit}>
          <TextField
            label="Campaign ID"
            value={campaignId}
            onChange={(event) => setCampaignId(event.target.value)}
            disabled={mode === "edit"}
            required
            fullWidth
          />
          <TextField
            label="Display name"
            value={name}
            onChange={(event) => setName(event.target.value)}
            fullWidth
            placeholder="Optional description"
          />
          <TextField
            label="End time"
            type="datetime-local"
            value={endTimeLocal}
            onChange={(event) => setEndTimeLocal(event.target.value)}
            required
            fullWidth
            helperText="Times are stored in UTC and shown here in your local timezone."
          />
          {validationError && <Typography color="error">{validationError}</Typography>}
          {error && <Typography color="error">{error}</Typography>}
          <DialogActions sx={{ px: 0 }}>
            <Button onClick={onCancel} disabled={saving}>
              Cancel
            </Button>
            <Button type="submit" variant="contained" disabled={saving}>
              {saving ? "Saving" : submitLabel}
            </Button>
          </DialogActions>
        </Stack>
      </DialogContent>
    </Dialog>
  );
};
