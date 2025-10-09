/*
 * Copyright (c) Flashoffer Developers
 * Released under the MIT license.
 */

import { useCallback, useEffect, useMemo, useState } from "react";

import "./EventConsole.css";

export interface EventConsoleProps {
  eventsUrl?: string;
  pollInterval?: number;
  limit?: number;
}

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

type ConsoleStatus = "idle" | "connecting" | "updating" | "live" | "error";

function formatTime(value: string | null | undefined): string {
  if (!value) {
    return "—";
  }
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return value;
  }
  return date.toLocaleTimeString([], {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  });
}

function describeLatency(occurredAt: string, receivedAt: string): string | null {
  const occurred = new Date(occurredAt);
  const received = new Date(receivedAt);
  if (Number.isNaN(occurred.getTime()) || Number.isNaN(received.getTime())) {
    return null;
  }
  const delta = Math.max(0, received.getTime() - occurred.getTime());
  if (delta < 1000) {
    return `${delta} ms`;
  }
  if (delta < 60000) {
    return `${(delta / 1000).toFixed(1)} s`;
  }
  return `${Math.round(delta / 60000)} min`;
}

function isAbortError(error: unknown): boolean {
  return (
    !!error &&
    typeof error === "object" &&
    "name" in error &&
    (error as { name?: string }).name === "AbortError"
  );
}

function extractEvents(
  data: { events?: CapturedEvent[] } | undefined
): CapturedEvent[] {
  if (!data || !Array.isArray(data.events)) {
    return [];
  }
  return data.events as CapturedEvent[];
}

export function EventConsole({
  eventsUrl,
  pollInterval = 3000,
  limit = 25,
}: EventConsoleProps) {
  const [events, setEvents] = useState<CapturedEvent[]>([]);
  const [status, setStatus] = useState<ConsoleStatus>("idle");
  const [error, setError] = useState<Error | null>(null);
  const [lastUpdated, setLastUpdated] = useState<string | null>(null);

  const applyLimitParam = useCallback(
    (url: URL) => {
      if (limit && !url.searchParams.has("limit")) {
        url.searchParams.set("limit", String(limit));
      }
    },
    [limit]
  );

  const handleLoadSuccess = useCallback((payload: CapturedEvent[]) => {
    setEvents(payload);
    setLastUpdated(new Date().toISOString());
    setStatus("live");
    setError(null);
  }, []);

  const handleLoadFailure = useCallback((cause: unknown) => {
    setStatus("error");
    setError(cause instanceof Error ? cause : new Error(String(cause)));
  }, []);

  useEffect(() => {
    if (!eventsUrl) {
      return () => undefined;
    }

    let cancelled = false;
    let controller = new AbortController();

    const load = async () => {
      controller.abort();
      controller = new AbortController();
      try {
        setStatus((current) => (current === "idle" ? "connecting" : "updating"));
        const url = new URL(eventsUrl, window.location.href);
        applyLimitParam(url);
        const response = await fetch(url, {
          credentials: "include",
          signal: controller.signal,
        });
        if (!response.ok) {
          throw new Error(`Request failed with status ${response.status}`);
        }
        const data = (await response.json()) as { events?: CapturedEvent[] };
        if (cancelled) {
          return;
        }
        handleLoadSuccess(extractEvents(data));
      } catch (err) {
        if (cancelled || isAbortError(err)) {
          return;
        }
        handleLoadFailure(err);
      }
    };

    void load();
    const interval = window.setInterval(() => {
      void load();
    }, pollInterval);

    return () => {
      cancelled = true;
      controller.abort();
      window.clearInterval(interval);
    };
  }, [
    applyLimitParam,
    eventsUrl,
    handleLoadFailure,
    handleLoadSuccess,
    pollInterval,
  ]);

  const summary = useMemo(() => {
    if (events.length === 0) {
      return "Waiting for events… Scroll the page or click a call to action.";
    }
    const types = new Map<string, number>();
    events.forEach((event) => {
      const next = (types.get(event.event_type) || 0) + 1;
      types.set(event.event_type, next);
    });
    const parts = Array.from(types.entries()).map(([type, count]) => `${count} ${type}`);
    return `Showing ${events.length} recent events (${parts.join(", ")})`;
  }, [events]);

  const statusLabel = useMemo(() => {
    switch (status) {
      case "live":
        return "Live";
      case "updating":
        return "Updating…";
      case "connecting":
        return "Connecting…";
      case "error":
        return "Error";
      default:
        return "Idle";
    }
  }, [status]);

  return (
    <section className="event-console" aria-live="polite">
      <header className="event-console__header">
        <div>
          <h2>Captured events</h2>
          <p className="event-console__summary">{summary}</p>
        </div>
        <div className={`event-console__badge event-console__badge--${status}`}>
          {statusLabel}
        </div>
      </header>

      {error ? (
        <p className="event-console__error">
          Failed to load events: {error.message || String(error)}
        </p>
      ) : null}

      <ul className="event-console__list">
        {events.map((event) => {
          const latency = describeLatency(event.occurred_at, event.received_at);
          return (
            <li key={event.id} className={`event-card event-card--${event.event_type}`}>
              <div className="event-card__meta">
                <span className="event-card__type">{event.event_type}</span>
                <span className="event-card__target">{event.target}</span>
                <span className="event-card__time" title={event.occurred_at}>
                  {formatTime(event.occurred_at)}
                </span>
                {latency ? <span className="event-card__latency">+{latency}</span> : null}
              </div>
              <dl className="event-card__details">
                <div>
                  <dt>Site</dt>
                  <dd>{event.site}</dd>
                </div>
                <div>
                  <dt>Session</dt>
                  <dd>{event.session_id}</dd>
                </div>
                <div>
                  <dt>Received</dt>
                  <dd title={event.received_at}>{formatTime(event.received_at)}</dd>
                </div>
              </dl>
              <pre className="event-card__payload">
                {JSON.stringify(event.meta ?? {}, null, 2)}
              </pre>
            </li>
          );
        })}
      </ul>

      <footer className="event-console__footer">
        <span>
          Last update {lastUpdated ? formatTime(lastUpdated) : "—"}
        </span>
      </footer>
    </section>
  );
}

export default EventConsole;
