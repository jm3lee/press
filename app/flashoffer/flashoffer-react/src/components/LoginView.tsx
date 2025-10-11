/*
 * Copyright (c) Flashoffer Developers
 * Released under the MIT license.
 */

import Alert from "@mui/material/Alert";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Stack from "@mui/material/Stack";
import TextField from "@mui/material/TextField";
import type { FormEvent, ReactNode } from "react";
import { useCallback, useState } from "react";

import { Section } from "./Section";

export interface LoginCredentials {
  username: string;
  password: string;
}

export interface LoginViewProps {
  /**
   * Handler invoked when the sign-in form is submitted successfully.
   */
  onSubmit: (credentials: LoginCredentials) => Promise<void>;
  /**
   * Optional eyebrow label rendered above the section title.
   * Defaults to "Account access".
   */
  eyebrow?: string;
  /**
   * Section title displayed above the form.
   * Defaults to "Sign in to continue".
   */
  title?: string;
  /**
   * Supporting subtitle copy displayed under the title.
   * Defaults to "Enter your credentials to unlock this dashboard."
   */
  subtitle?: string;
  /**
   * Optional helper content rendered under the submit button.
   */
  helperText?: ReactNode;
  /**
   * Pre-filled username value shown when the form loads.
   */
  defaultUsername?: string;
  /**
   * Label used for the username text field.
   * Defaults to "Username".
   */
  usernameLabel?: string;
  /**
   * Label used for the password text field.
   * Defaults to "Password".
   */
  passwordLabel?: string;
  /**
   * Label displayed on the submit button when the form is idle.
   * Defaults to "Sign in".
   */
  submitLabel?: string;
  /**
   * Label displayed on the submit button while the form is submitting.
   * Defaults to "Signing in".
   */
  submittingLabel?: string;
  /**
   * When true the inputs and button are disabled to reflect an upstream loading state.
   */
  loading?: boolean;
  /**
   * Section alignment; aligns headers and helper copy consistently with other Flashoffer components.
   */
  align?: "center" | "left";
}

const DEFAULT_EYEBROW = "Account access";
const DEFAULT_TITLE = "Sign in to continue";
const DEFAULT_SUBTITLE = "Enter your credentials to unlock this dashboard.";
const DEFAULT_USERNAME_LABEL = "Username";
const DEFAULT_PASSWORD_LABEL = "Password";
const DEFAULT_SUBMIT_LABEL = "Sign in";
const DEFAULT_SUBMITTING_LABEL = "Signing in";

/**
 * Opinionated authentication form styled to match Flashoffer marketing sections.
 * Provides a sensible default layout while allowing downstream apps to customise copy
 * and helper content without re-implementing validation or loading states.
 */
export function LoginView({
  onSubmit,
  helperText,
  eyebrow = DEFAULT_EYEBROW,
  title = DEFAULT_TITLE,
  subtitle = DEFAULT_SUBTITLE,
  defaultUsername = "",
  usernameLabel = DEFAULT_USERNAME_LABEL,
  passwordLabel = DEFAULT_PASSWORD_LABEL,
  submitLabel = DEFAULT_SUBMIT_LABEL,
  submittingLabel = DEFAULT_SUBMITTING_LABEL,
  loading = false,
  align = "left",
}: LoginViewProps): JSX.Element {
  const [username, setUsername] = useState(defaultUsername);
  const [password, setPassword] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [localError, setLocalError] = useState<string | null>(null);

  const handleSubmit = useCallback(
    async (event: FormEvent<HTMLFormElement>) => {
      event.preventDefault();
      setLocalError(null);
      setSubmitting(true);
      try {
        await onSubmit({ username: username.trim(), password });
      } catch (error) {
        const message = error instanceof Error ? error.message : String(error);
        setLocalError(message);
      } finally {
        setSubmitting(false);
      }
    },
    [onSubmit, password, username],
  );

  const disabled = loading || submitting;
  const buttonLabel = disabled ? submittingLabel : submitLabel;

  return (
    <Section align={align} eyebrow={eyebrow} title={title} subtitle={subtitle}>
      <Box component="form" onSubmit={handleSubmit} noValidate sx={{ width: "100%", maxWidth: 420 }}>
        <Stack spacing={3}>
          <TextField
            label={usernameLabel}
            value={username}
            onChange={(event) => setUsername(event.target.value)}
            autoComplete="username"
            required
            fullWidth
          />
          <TextField
            label={passwordLabel}
            type="password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            autoComplete="current-password"
            required
            fullWidth
          />
          {localError && <Alert severity="error">{localError}</Alert>}
          <Button type="submit" variant="contained" disabled={disabled} size="large">
            {buttonLabel}
          </Button>
          {helperText && (
            <Box
              sx={{
                color: "text.secondary",
                fontSize: (theme) => theme.typography.body2.fontSize,
                lineHeight: (theme) => theme.typography.body2.lineHeight,
                "& a": { color: "inherit", fontWeight: 500 },
              }}
            >
              {helperText}
            </Box>
          )}
        </Stack>
      </Box>
    </Section>
  );
}
