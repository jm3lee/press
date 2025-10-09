/*
 * Copyright (c) Flashoffer Developers
 * Released under the MIT license.
 */

import { useEffect, useMemo, useRef, useState } from "react";

type ConsoleStatus = "idle" | "connecting" | "updating" | "live" | "error";

interface CapturedEvent {
  id: string;
  event_type: string;
  target: string;
  occurred_at: string;
  received_at: string;
  site: string;
  session_id: string;
  meta?: Record<string, unknown>;
}

interface EventStreamState {
  events: CapturedEvent[];
  status: ConsoleStatus;
  error: Error | null;
  lastUpdated: string | null;
}

interface EventStreamOptions {
  eventsUrl?: string;
  pollInterval?: number;
  limit?: number;
  authToken?: string;
}

/**
 * Determine whether an error resulted from aborting a fetch request.
 *
 * @param error - Error thrown by a fetch request.
 */
function isAbortError(error: unknown): boolean {
  return (
    !!error &&
    typeof error === "object" &&
    "name" in error &&
    (error as { name?: string }).name === "AbortError"
  );
}

/**
 * Extract captured events from the backend response payload.
 *
 * @param data - Raw JSON payload returned by the backend.
 */
function extractEvents(
  data: { events?: CapturedEvent[] } | undefined
): CapturedEvent[] {
  if (!data || !Array.isArray(data.events)) {
    return [];
  }
  return data.events as CapturedEvent[];
}

/**
 * Poll a backend endpoint for Flashoffer events while tracking request state.
 *
 * @param options - Configuration options for the event stream.
 */
export function useEventStream({
  eventsUrl,
  pollInterval = 3000,
  limit = 25,
  authToken,
}: EventStreamOptions): EventStreamState {
  const [events, setEvents] = useState<CapturedEvent[]>([]);
  const [status, setStatus] = useState<ConsoleStatus>("idle");
  const [error, setError] = useState<Error | null>(null);
  const [lastUpdated, setLastUpdated] = useState<string | null>(null);
  const controllerRef = useRef<AbortController | null>(null);

  useEffect(() => {
    if (!eventsUrl) {
      controllerRef.current?.abort();
      controllerRef.current = null;
      setEvents([]);
      setStatus("idle");
      setError(null);
      setLastUpdated(null);
      return () => undefined;
    }

    let cancelled = false;

    /**
     * Cancel any pending fetch request before issuing a new poll.
     */
    const abortOngoing = () => {
      controllerRef.current?.abort();
      controllerRef.current = new AbortController();
    };

    /**
     * Ensure the request URL includes the configured result limit.
     *
     * @param url - Request URL prior to dispatching fetch.
     */
    const applyLimitParam = (url: URL) => {
      if (limit && !url.searchParams.has("limit")) {
        url.searchParams.set("limit", String(limit));
      }
    };

    /**
     * Apply event results from a successful polling request.
     *
     * @param payload - Event payload returned by the backend.
     */
    const handleLoadSuccess = (payload: CapturedEvent[]) => {
      if (cancelled) {
        return;
      }
      setEvents(payload);
      setLastUpdated(new Date().toISOString());
      setStatus("live");
      setError(null);
    };

    /**
     * Transition to an error state when polling fails.
     *
     * @param cause - Error thrown while attempting to poll events.
     */
    const handleLoadFailure = (cause: unknown) => {
      if (cancelled || isAbortError(cause)) {
        return;
      }
      setStatus("error");
      setError(cause instanceof Error ? cause : new Error(String(cause)));
    };

    /**
     * Fetch the most recent events from the backend endpoint.
     */
    const load = async () => {
      abortOngoing();
      const controller = controllerRef.current;
      try {
        setStatus((current) => (current === "idle" ? "connecting" : "updating"));
        const url = new URL(eventsUrl, window.location.href);
        applyLimitParam(url);
        const response = await fetch(url, {
          credentials: "include",
          signal: controller?.signal,
          headers: authToken
            ? { Authorization: `Bearer ${authToken}` }
            : undefined,
        });
        if (!response.ok) {
          throw new Error(`Request failed with status ${response.status}`);
        }
        const data = (await response.json()) as { events?: CapturedEvent[] };
        handleLoadSuccess(extractEvents(data));
      } catch (err) {
        handleLoadFailure(err);
      }
    };

    void load();
    const interval = window.setInterval(() => {
      void load();
    }, pollInterval);

    return () => {
      cancelled = true;
      controllerRef.current?.abort();
      window.clearInterval(interval);
    };
  }, [authToken, eventsUrl, limit, pollInterval]);

  return useMemo(
    () => ({
      events,
      status,
      error,
      lastUpdated,
    }),
    [events, status, error, lastUpdated]
  );
}

export type { CapturedEvent, ConsoleStatus, EventStreamState };
