/*
 * Copyright (c) Flashoffer Developers
 * Released under the MIT license.
 */

import React from "react";
import ReactDOM from "react-dom/client";
import { AutoTrack, EngagementProvider } from "flashoffer-react";
import App from "./App";
import "./index.css";

const analyticsEndpoint =
  typeof import.meta.env.VITE_FLASHOFFER_ANALYTICS_ENDPOINT === "string" &&
  import.meta.env.VITE_FLASHOFFER_ANALYTICS_ENDPOINT.trim() !== ""
    ? import.meta.env.VITE_FLASHOFFER_ANALYTICS_ENDPOINT
    : undefined;

const rootElement = document.getElementById("root");

if (!rootElement) {
  throw new Error("Missing root element");
}

ReactDOM.createRoot(rootElement).render(
  <React.StrictMode>
    <EngagementProvider
      site="flashoffer-demo"
      campaignId="flashoffer-demo"
      endpoint={analyticsEndpoint}
    >
      <App />
      <AutoTrack />
    </EngagementProvider>
  </React.StrictMode>
);
