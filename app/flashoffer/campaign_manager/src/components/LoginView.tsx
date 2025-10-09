/*
 * Copyright (c) Flashoffer Developers
 * Released under the MIT license.
 */

import Alert from "@mui/material/Alert";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Stack from "@mui/material/Stack";
import TextField from "@mui/material/TextField";
import Typography from "@mui/material/Typography";
import { FormEvent, useCallback, useState } from "react";
import { Section, SectionHeader } from "flashoffer-react";

import type { Credentials } from "../types";

interface LoginViewProps {
  loading: boolean;
  onSubmit: (credentials: Credentials) => Promise<void>;
}

export const LoginView = ({ loading, onSubmit }: LoginViewProps): JSX.Element => {
  const [username, setUsername] = useState("admin");
  const [password, setPassword] = useState("");
  const [localError, setLocalError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = useCallback(
    async (event: FormEvent<HTMLFormElement>) => {
      event.preventDefault();
      setLocalError(null);
      setSubmitting(true);
      try {
        await onSubmit({ username: username.trim(), password });
      } catch (submitError) {
        const message = submitError instanceof Error ? submitError.message : String(submitError);
        setLocalError(message);
      } finally {
        setSubmitting(false);
      }
    },
    [onSubmit, password, username],
  );

  const disabled = loading || submitting;

  return (
    <Section>
      <SectionHeader
        eyebrow="Admin access"
        title="Sign in to manage campaigns"
        subtitle="Authenticate with the credentials generated during the Docker build."
      />
      <Box component="form" onSubmit={handleSubmit} noValidate sx={{ maxWidth: 420 }}>
        <Stack spacing={3}>
          <TextField
            label="Username"
            value={username}
            onChange={(event) => setUsername(event.target.value)}
            autoComplete="username"
            required
            fullWidth
          />
          <TextField
            label="Password"
            type="password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            autoComplete="current-password"
            required
            fullWidth
          />
          {localError && <Alert severity="error">{localError}</Alert>}
          <Button type="submit" variant="contained" disabled={disabled} size="large">
            {disabled ? "Signing in" : "Sign in"}
          </Button>
          <Typography variant="body2" color="text.secondary">
            The admin password is written to
            {" "}
            <code>/workspace/app/flashoffer/campaign_manager/admin_password</code>
            {" "}
            each time the container image is built.
          </Typography>
        </Stack>
      </Box>
    </Section>
  );
};
