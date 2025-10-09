/*
 * Copyright (c) Flashoffer Developers
 * Released under the MIT license.
 */

import type { CampaignPayload, CampaignSummary, Credentials, LoginResult } from "./types";

type ApiCampaign = {
  campaign_id: string;
  name: string | null;
  end_time: string;
  updated_at: string;
};

type ApiLoginResponse = {
  token: string;
  expires_at: string;
};

const RAW_BASE = import.meta.env.VITE_FLASHOFFER_CAMPAIGN_MANAGER_API_BASE?.trim();
const API_BASE = RAW_BASE ? RAW_BASE.replace(/\/$/, "") : "";

type FetchOptions = {
  token?: string;
  method?: string;
  body?: Record<string, unknown>;
};

/**
 * Issues a JSON request against the campaign manager backend.
 *
 * @param path - API path starting with `/api`.
 * @param options - Optional HTTP overrides including method, body, and token.
 * @returns Parsed JSON payload typed to `T`.
 * @throws Error when the response indicates failure.
 */
async function request<T>(path: string, options: FetchOptions = {}): Promise<T> {
  const url = `${API_BASE}${path}`;
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
  };

  if (options.token) {
    headers.Authorization = `Bearer ${options.token}`;
  }

  const response = await fetch(url, {
    method: options.method ?? "GET",
    headers,
    body: options.body ? JSON.stringify(options.body) : undefined,
  });

  if (!response.ok) {
    const message = await extractError(response);
    throw new Error(message);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  const data = (await response.json()) as T;
  return data;
}

/**
 * Attempts to extract a human-readable error message from a failed response.
 *
 * @param response - Fetch API response to parse.
 * @returns Message suitable for display to the operator.
 */
async function extractError(response: Response): Promise<string> {
  try {
    const payload = (await response.json()) as { detail?: string; error?: string };
    return payload.detail ?? payload.error ?? response.statusText;
  } catch (error) {
    return response.statusText;
  }
}

/**
 * Submits administrator credentials and returns an authentication token.
 *
 * @param credentials - Username and password provided by the operator.
 * @returns Token payload including the expiry timestamp.
 */
export async function login(credentials: Credentials): Promise<LoginResult> {
  const payload = await request<ApiLoginResponse>("/api/auth/login", {
    method: "POST",
    body: credentials,
  });
  return { token: payload.token, expiresAt: payload.expires_at };
}

/**
 * Retrieves the list of campaigns stored in the backend repository.
 *
 * @param token - Bearer token issued by the authentication endpoint.
 * @returns Campaign summaries suitable for display in the dashboard.
 */
export async function listCampaigns(token: string): Promise<CampaignSummary[]> {
  const payload = await request<{ campaigns: ApiCampaign[] }>("/api/campaigns", {
    token,
  });
  return payload.campaigns.map(mapCampaign);
}

/**
 * Creates a new campaign record in the backend.
 *
 * @param token - Bearer token issued by the authentication endpoint.
 * @param campaignId - Unique identifier for the campaign.
 * @param payload - Campaign metadata such as name and end time.
 * @returns Summary of the persisted campaign.
 */
export async function createCampaign(
  token: string,
  campaignId: string,
  payload: CampaignPayload,
): Promise<CampaignSummary> {
  const response = await request<ApiCampaign>("/api/campaigns", {
    token,
    method: "POST",
    body: { campaign_id: campaignId, ...payload },
  });
  return mapCampaign(response);
}

/**
 * Updates an existing campaign with new metadata.
 *
 * @param token - Bearer token issued by the authentication endpoint.
 * @param campaignId - Identifier of the campaign to mutate.
 * @param payload - Mutated metadata to persist in the backend.
 * @returns Summary of the updated campaign.
 */
export async function updateCampaign(
  token: string,
  campaignId: string,
  payload: CampaignPayload,
): Promise<CampaignSummary> {
  const response = await request<ApiCampaign>(`/api/campaigns/${encodeURIComponent(campaignId)}`, {
    token,
    method: "PUT",
    body: payload,
  });
  return mapCampaign(response);
}

/**
 * Builds the events endpoint URL for a campaign using the configured API base.
 *
 * @param campaignId - Unique identifier for the campaign to inspect.
 * @returns URL that can be requested to retrieve recent campaign events.
 */
export function buildCampaignEventsUrl(campaignId: string): string {
  const encodedId = encodeURIComponent(campaignId);
  return `${API_BASE}/api/campaigns/${encodedId}/events`;
}

/**
 * Normalizes the backend campaign payload to the dashboard shape.
 *
 * @param payload - Campaign object returned by the FastAPI backend.
 * @returns Dashboard-friendly campaign summary.
 */
function mapCampaign(payload: ApiCampaign): CampaignSummary {
  return {
    campaignId: payload.campaign_id,
    name: payload.name,
    endTime: payload.end_time,
    updatedAt: payload.updated_at,
  };
}
