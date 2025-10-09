/*
 * Copyright (c) Flashoffer Developers
 * Released under the MIT license.
 */

import Alert from "@mui/material/Alert";
import Container from "@mui/material/Container";
import CssBaseline from "@mui/material/CssBaseline";
import Snackbar from "@mui/material/Snackbar";
import Stack from "@mui/material/Stack";
import { useCallback, useEffect, useMemo, useState } from "react";
import { FlashofferThemeProvider } from "flashoffer-react";

import { createCampaign, listCampaigns, login, updateCampaign } from "./api";
import { CampaignDashboard } from "./components/CampaignDashboard";
import { LoginView } from "./components/LoginView";
import type { CampaignPayload, CampaignSummary, Credentials, LoginResult } from "./types";

interface AuthState {
  token: string;
  expiresAt: string;
}

const STORAGE_KEY = "flashoffer.campaignManager.auth";

function loadStoredAuth(): AuthState | null {
  try {
    const raw = window.localStorage.getItem(STORAGE_KEY);
    if (!raw) {
      return null;
    }
    const parsed = JSON.parse(raw) as AuthState;
    if (!parsed.token || !parsed.expiresAt) {
      return null;
    }
    const expiry = Date.parse(parsed.expiresAt);
    if (Number.isNaN(expiry) || expiry <= Date.now()) {
      return null;
    }
    return parsed;
  } catch (error) {
    console.warn("Failed to parse stored auth state", error);
    return null;
  }
}

function persistAuth(state: AuthState | null): void {
  if (!state) {
    window.localStorage.removeItem(STORAGE_KEY);
    return;
  }
  window.localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
}

const App = (): JSX.Element => {
  const [auth, setAuth] = useState<AuthState | null>(() => loadStoredAuth());
  const [campaigns, setCampaigns] = useState<CampaignSummary[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const token = auth?.token ?? null;
  const expiresAt = useMemo(() => auth?.expiresAt ?? null, [auth]);

  const refreshCampaigns = useCallback(async () => {
    if (!token) {
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const data = await listCampaigns(token);
      setCampaigns(data);
    } catch (refreshError) {
      const message = refreshError instanceof Error ? refreshError.message : String(refreshError);
      setError(message);
    } finally {
      setLoading(false);
    }
  }, [token]);

  useEffect(() => {
    if (!token) {
      setCampaigns([]);
      return;
    }
    void refreshCampaigns();
  }, [token, refreshCampaigns]);

  const handleLogin = useCallback(
    async (credentials: Credentials): Promise<void> => {
      setLoading(true);
      setError(null);
      try {
        const result: LoginResult = await login(credentials);
        const state: AuthState = {
          token: result.token,
          expiresAt: result.expiresAt,
        };
        setAuth(state);
        persistAuth(state);
        setSuccess("Signed in successfully.");
      } catch (loginError) {
        const message = loginError instanceof Error ? loginError.message : String(loginError);
        setError(message);
        throw loginError;
      } finally {
        setLoading(false);
      }
    },
    [],
  );

  const handleLogout = useCallback(() => {
    setAuth(null);
    persistAuth(null);
    setCampaigns([]);
    setSuccess("Signed out.");
  }, []);

  const handleCreate = useCallback(
    async (campaignId: string, payload: CampaignPayload): Promise<void> => {
      if (!token) {
        throw new Error("Authentication required");
      }
      setLoading(true);
      setError(null);
      try {
        const created = await createCampaign(token, campaignId, payload);
        setCampaigns((current) => {
          const next = current.filter((item) => item.campaignId !== created.campaignId);
          return [...next, created].sort((a, b) => a.campaignId.localeCompare(b.campaignId));
        });
        setSuccess(`Campaign "${created.campaignId}" saved.`);
      } catch (createError) {
        const message = createError instanceof Error ? createError.message : String(createError);
        setError(message);
        throw createError;
      } finally {
        setLoading(false);
      }
    },
    [token],
  );

  const handleUpdate = useCallback(
    async (campaignId: string, payload: CampaignPayload): Promise<void> => {
      if (!token) {
        throw new Error("Authentication required");
      }
      setLoading(true);
      setError(null);
      try {
        const updated = await updateCampaign(token, campaignId, payload);
        setCampaigns((current) =>
          current
            .map((item) => (item.campaignId === updated.campaignId ? updated : item))
            .sort((a, b) => a.campaignId.localeCompare(b.campaignId)),
        );
        setSuccess(`Campaign "${updated.campaignId}" updated.`);
      } catch (updateError) {
        const message = updateError instanceof Error ? updateError.message : String(updateError);
        setError(message);
        throw updateError;
      } finally {
        setLoading(false);
      }
    },
    [token],
  );

  const clearError = useCallback(() => setError(null), []);
  const clearSuccess = useCallback(() => setSuccess(null), []);

  return (
    <FlashofferThemeProvider>
      <CssBaseline />
      <Container maxWidth="lg" sx={{ py: 6 }}>
        <Stack spacing={4}>
          {token ? (
            <CampaignDashboard
              campaigns={campaigns}
              loading={loading}
              onCreate={handleCreate}
              onRefresh={refreshCampaigns}
              onUpdate={handleUpdate}
              onLogout={handleLogout}
              expiresAt={expiresAt}
            />
          ) : (
            <LoginView loading={loading} onSubmit={handleLogin} />
          )}
        </Stack>
      </Container>
      <Snackbar open={Boolean(error)} autoHideDuration={6000} onClose={clearError}>
        <Alert severity="error" onClose={clearError} sx={{ width: "100%" }}>
          {error}
        </Alert>
      </Snackbar>
      <Snackbar open={Boolean(success)} autoHideDuration={4000} onClose={clearSuccess}>
        <Alert severity="success" onClose={clearSuccess} sx={{ width: "100%" }}>
          {success}
        </Alert>
      </Snackbar>
    </FlashofferThemeProvider>
  );
};

export default App;
