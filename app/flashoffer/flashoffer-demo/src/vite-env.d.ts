/*
 * Copyright (c) Flashoffer Developers
 * Released under the MIT license.
 */

/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_FLASHOFFER_ANALYTICS_ENDPOINT?: string;
  readonly VITE_FLASHOFFER_ANALYTICS_RECENT_URL?: string;
  readonly VITE_FLASHOFFER_CAMPAIGN_API_BASE?: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
