import React from "react";
import ReactDOM from "react-dom/client";
import { AutoTrack, EngagementProvider } from "flashoffer-react";
import App from "./App";
import { MultipleChoiceDemoPage } from "./pages/MultipleChoiceDemoPage";
import "./index.css";

const normalizePath = (pathname: string, baseUrl: string) => {
  const trimmedBase = baseUrl === "/" ? "" : baseUrl.replace(/\/$/, "");
  let routePath = pathname;

  if (trimmedBase && routePath.startsWith(trimmedBase)) {
    routePath = routePath.slice(trimmedBase.length);
  }

  if (routePath === "") {
    routePath = "/";
  }

  if (!routePath.startsWith("/")) {
    routePath = `/${routePath}`;
  }

  if (routePath.length > 1 && routePath.endsWith("/")) {
    routePath = routePath.slice(0, -1);
  }

  return routePath;
};

const analyticsEndpoint =
  typeof import.meta.env.VITE_FLASHOFFER_ANALYTICS_ENDPOINT === "string" &&
  import.meta.env.VITE_FLASHOFFER_ANALYTICS_ENDPOINT.trim() !== ""
    ? import.meta.env.VITE_FLASHOFFER_ANALYTICS_ENDPOINT
    : undefined;

const rootElement = document.getElementById("root");

if (!rootElement) {
  throw new Error("Missing root element");
}

const routePath = normalizePath(window.location.pathname, import.meta.env.BASE_URL);
const isMultipleChoiceRoute = routePath === "/multiple-choice";

ReactDOM.createRoot(rootElement).render(
  <React.StrictMode>
    <EngagementProvider site="flashoffer-demo" endpoint={analyticsEndpoint}>
      {isMultipleChoiceRoute ? <MultipleChoiceDemoPage /> : <App />}
      <AutoTrack />
    </EngagementProvider>
  </React.StrictMode>
);
