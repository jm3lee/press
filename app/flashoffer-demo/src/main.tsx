import React from "react";
import ReactDOM from "react-dom/client";
import { AutoTrack, EngagementProvider } from "flashoffer-react";
import App from "./App";
import "./index.css";

const rootElement = document.getElementById("root");

if (!rootElement) {
  throw new Error("Missing root element");
}

ReactDOM.createRoot(rootElement).render(
  <React.StrictMode>
    <EngagementProvider site="flashoffer-demo">
      <App />
      <AutoTrack />
    </EngagementProvider>
  </React.StrictMode>
);
