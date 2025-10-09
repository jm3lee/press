/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_FLASHOFFER_ANALYTICS_ENDPOINT?: string;
  readonly VITE_FLASHOFFER_ANALYTICS_RECENT_URL?: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
