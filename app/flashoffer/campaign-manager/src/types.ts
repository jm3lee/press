/*
 * Copyright (c) Flashoffer Developers
 * Released under the MIT license.
 */

export interface CampaignSummary {
  campaignId: string;
  name: string | null;
  endTime: string;
  updatedAt: string;
}

export interface CampaignPayload {
  name: string | null;
  endTime: string;
}

export interface LoginResult {
  token: string;
  expiresAt: string;
}

export interface Credentials {
  username: string;
  password: string;
}
