/*
 * Copyright (c) Flashoffer Developers
 * Released under the MIT license.
 */

import { render, screen } from "@testing-library/react";
import type { MockedFunction } from "jest-mock";

import type { CapturedEvent } from "../hooks/useEventStream";
import EventConsole from "../EventConsole";
import { useEventStream } from "../hooks/useEventStream";

jest.mock("../hooks/useEventStream");

const useEventStreamMock = useEventStream as MockedFunction<
  typeof useEventStream
>;

/**
 * Provide a deterministic captured event for component rendering tests.
 */
function sampleEvent(): CapturedEvent {
  return {
    id: "evt-99",
    event_type: "cta_click",
    target: "hero",
    occurred_at: "2024-02-01T10:00:00.000Z",
    received_at: "2024-02-01T10:00:01.500Z",
    site: "flashoffer.example",
    session_id: "session-99",
    meta: { campaign: "winter" },
  };
}

describe("EventConsole", () => {
  afterEach(() => {
    jest.clearAllMocks();
  });

  it("renders the captured events and status header", () => {
    useEventStreamMock.mockReturnValue({
      events: [sampleEvent()],
      status: "connecting",
      error: null,
      lastUpdated: "2024-02-01T10:00:02.000Z",
    });

    render(
      <EventConsole
        eventsUrl="/events"
        pollInterval={1_000}
        limit={5}
        authToken="token"
      />
    );

    expect(screen.getByRole("heading", { name: "Captured events" })).toBeInTheDocument();
    expect(
      screen.getByText(
        "Showing 1 recent events (1 cta_click)",
        { exact: false }
      )
    ).toBeInTheDocument();
    expect(screen.getByText("Connecting…")).toBeInTheDocument();
    expect(screen.getByText("cta_click")).toBeInTheDocument();
    expect(screen.getByText("hero")).toBeInTheDocument();
    expect(screen.getByText("session-99")).toBeInTheDocument();
    const footer = screen.getByText(/Last update/);
    expect(footer).toBeInTheDocument();
    expect(footer.textContent).toContain("10:00:02");
  });

  it("displays an error message when the stream reports a failure", () => {
    useEventStreamMock.mockReturnValue({
      events: [],
      status: "error",
      error: new Error("unavailable"),
      lastUpdated: null,
    });

    render(
      <EventConsole eventsUrl="/events" pollInterval={1_000} limit={5} />
    );

    expect(
      screen.getByText("Failed to load events: unavailable")
    ).toBeInTheDocument();
  });
});
