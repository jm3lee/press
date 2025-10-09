/*
 * Copyright (c) Flashoffer Developers
 * Released under the MIT license.
 */

import { renderHook, waitFor } from "@testing-library/react";

import { useEventStream, type CapturedEvent } from "../hooks/useEventStream";

/**
 * Create a representative captured event for testing.
 *
 * @param override - Optional event field overrides.
 */
function createEvent(
  override: Partial<CapturedEvent> = {}
): CapturedEvent {
  return {
    id: "evt-1",
    event_type: "cta_click",
    target: "checkout",
    occurred_at: "2024-01-01T00:00:00.000Z",
    received_at: "2024-01-01T00:00:01.000Z",
    site: "flashoffer.test",
    session_id: "session-1",
    meta: { foo: "bar" },
    ...override,
  };
}

describe("useEventStream", () => {
  const globalScope = globalThis as typeof globalThis & {
    fetch?: typeof fetch;
  };
  const originalFetch = globalScope.fetch;

  afterEach(() => {
    globalScope.fetch = originalFetch;
    jest.clearAllMocks();
  });

  it("polls the backend endpoint and updates the hook state", async () => {
    const events = [createEvent({ id: "evt-42" })];
    const fetchMock = jest.fn(async () => ({
      ok: true,
      json: async () => ({ events }),
    })) as jest.MockedFunction<typeof fetch>;
    globalScope.fetch = fetchMock;

    const { result, unmount } = renderHook(() =>
      useEventStream({
        eventsUrl: "/analytics/events",
        pollInterval: 12_000,
        limit: 50,
        authToken: "secret-token",
      })
    );

    await waitFor(() => {
      expect(result.current.status).toBe("live");
    });

    expect(fetchMock).toHaveBeenCalledTimes(1);
    const [requestUrl, options] = fetchMock.mock.calls[0] ?? [];
    expect(String(requestUrl)).toBe(
      "http://localhost/analytics/events?limit=50"
    );
    expect(options?.headers).toEqual({
      Authorization: "Bearer secret-token",
    });
    expect(result.current.events).toEqual(events);
    expect(result.current.error).toBeNull();
    expect(result.current.lastUpdated).not.toBeNull();

    unmount();
  });

  it("resets to an idle state when the events URL is cleared", async () => {
    const fetchMock = jest.fn(async () => ({
      ok: true,
      json: async () => ({ events: [createEvent()] }),
    })) as jest.MockedFunction<typeof fetch>;
    globalScope.fetch = fetchMock;

    const { result, rerender, unmount } = renderHook(
      (props: {
        eventsUrl?: string;
      }) =>
        useEventStream({
          eventsUrl: props.eventsUrl,
          pollInterval: 3_000,
        }),
      {
        initialProps: { eventsUrl: "/events" },
      }
    );

    await waitFor(() => {
      expect(result.current.status).toBe("live");
    });

    rerender({ eventsUrl: undefined });

    await waitFor(() => {
      expect(result.current.status).toBe("idle");
    });

    expect(result.current.events).toHaveLength(0);
    expect(result.current.error).toBeNull();
    expect(result.current.lastUpdated).toBeNull();

    unmount();
  });
});
