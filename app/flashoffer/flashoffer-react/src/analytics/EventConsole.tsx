/*
 * Copyright (c) Flashoffer Developers
 * Released under the MIT license.
 */

import { useMemo } from "react";

import "./EventConsole.css";

import {
  type CapturedEvent,
  type ConsoleStatus,
  useEventStream,
} from "./hooks/useEventStream";

/**
 * Properties for configuring the `EventConsole` component.
 *
 * @property eventsUrl - Endpoint that serves recent campaign events.
 * @property pollInterval - Milliseconds between successive fetches.
 * @property limit - Maximum number of events to request per poll.
 * @property authToken - Optional bearer token for authenticated requests.
 */
export interface EventConsoleProps {
  eventsUrl?: string;
  pollInterval?: number;
  limit?: number;
  authToken?: string;
}

/**
 * Format a timestamp for display within the event console.
 *
 * @param value - ISO timestamp or compatible string.
 */
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

/**
 * Calculate a human-readable latency between two timestamps.
 *
 * @param occurredAt - ISO timestamp indicating when the event occurred.
 * @param receivedAt - ISO timestamp indicating when the event was captured.
 */
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

/**
 * Render a live-updating console of campaign events fetched from the backend.
 */
export function EventConsole({
  eventsUrl,
  pollInterval = 3000,
  limit = 25,
  authToken,
}: EventConsoleProps) {
  const { events, status, error, lastUpdated } = useEventStream({
    eventsUrl,
    pollInterval,
    limit,
    authToken,
  });

  const summary = useMemo(() => buildSummary(events), [events]);
  const statusLabel = useMemo(() => getStatusLabel(status), [status]);

  return (
    <section className="event-console" aria-live="polite">
      <EventConsoleStatusHeader
        summary={summary}
        status={status}
        statusLabel={statusLabel}
      />

      {error ? (
        <p className="event-console__error">
          Failed to load events: {error.message || String(error)}
        </p>
      ) : null}

      <EventConsoleEventList events={events} />

      <EventConsoleFooter lastUpdated={lastUpdated} />
    </section>
  );
}

/**
 * Render the header summarizing the event stream status.
 *
 * @param summary - Narrative description of the current event selection.
 * @param status - Connectivity status for the stream.
 * @param statusLabel - Human-readable label describing {@link status}.
 */
function EventConsoleStatusHeader({
  summary,
  status,
  statusLabel,
}: {
  summary: string;
  status: ConsoleStatus;
  statusLabel: string;
}) {
  return (
    <header className="event-console__header">
      <div>
        <h2>Captured events</h2>
        <p className="event-console__summary">{summary}</p>
      </div>
      <div className={`event-console__badge event-console__badge--${status}`}>
        {statusLabel}
      </div>
    </header>
  );
}

/**
 * List captured events using the canonical console styling.
 *
 * @param events - Event payloads to display.
 */
function EventConsoleEventList({ events }: { events: CapturedEvent[] }) {
  return (
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
  );
}

/**
 * Present the timestamp of the most recent event update.
 *
 * @param lastUpdated - ISO timestamp representing the latest poll completion.
 */
function EventConsoleFooter({ lastUpdated }: { lastUpdated: string | null }) {
  return (
    <footer className="event-console__footer">
      <span>Last update {lastUpdated ? formatTime(lastUpdated) : "—"}</span>
    </footer>
  );
}

/**
 * Build a human-readable summary of the captured event stream.
 *
 * @param events - Events currently displayed in the console.
 */
function buildSummary(events: CapturedEvent[]): string {
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
}

/**
 * Compute the label describing the current event stream status.
 *
 * @param status - Machine-readable connection status indicator.
 */
function getStatusLabel(status: ConsoleStatus): string {
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
}

export default EventConsole;
