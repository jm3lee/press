/*
 * Copyright (c) Flashoffer Developers
 * Released under the MIT license.
 */

import { act, render } from "@testing-library/react";
import type { MutableRefObject } from "react";
import {
  EngagementProvider,
  ViewTracker,
  useRecordInteraction,
} from "../EngagementProvider";

type RecordFn = (target?: string, meta?: Record<string, unknown>) => void;

function Recorder({
  recordRef,
}: {
  recordRef: MutableRefObject<RecordFn>;
}) {
  recordRef.current = useRecordInteraction();
  return null;
}

type GlobalWithOptionalFetch = typeof globalThis & { fetch?: typeof fetch };

describe("EngagementProvider connection failure handling", () => {
  const globalScope = globalThis as GlobalWithOptionalFetch;
  const originalFetch = globalScope.fetch;
  let fetchMock: jest.MockedFunction<typeof fetch>;
  beforeEach(() => {
    fetchMock = jest
      .fn(async () => {
        throw new Error("network failure");
      })
      .mockName("fetch") as jest.MockedFunction<typeof fetch>;
    globalScope.fetch = fetchMock;
  });

  afterEach(() => {
    globalScope.fetch = originalFetch;
    jest.clearAllMocks();
  });

  it("stops sending events after 10 consecutive connection failures", async () => {
    const recordRef = {
      current: (() => undefined) as RecordFn,
    } as MutableRefObject<RecordFn>;

    const view = render(
      <EngagementProvider
        endpoint="/engagement"
        site="test"
        maxBatch={1}
        flushInterval={null}
        heartbeatInterval={60_000}
        idleTimeout={60_000}
        scrollThresholds={[]}
        viewThresholds={[]}
      >
        <Recorder recordRef={recordRef} />
      </EngagementProvider>
    );

    const expectFetchIncrease = async (run: () => void) => {
      const before = fetchMock.mock.calls.length;
      await act(async () => {
        run();
        await Promise.resolve();
      });
      expect(fetchMock.mock.calls.length).toBeGreaterThan(before);
    };

    const expectNoFetchIncrease = async (run: () => void) => {
      const before = fetchMock.mock.calls.length;
      await act(async () => {
        run();
        await Promise.resolve();
      });
      expect(fetchMock.mock.calls.length).toBe(before);
    };

    for (let i = 0; i < 10; i += 1) {
      await expectFetchIncrease(() => {
        recordRef.current(`event-${i}`);
      });
    }

    fetchMock.mockClear();

    await expectNoFetchIncrease(() => {
      recordRef.current("post-failure");
    });

    await expectNoFetchIncrease(() => {
      recordRef.current("post-failure-2");
    });

    view.unmount();
  });
});

describe("EngagementProvider payload metadata", () => {
  const globalScope = globalThis as GlobalWithOptionalFetch;
  const originalFetch = globalScope.fetch;
  let fetchMock: jest.MockedFunction<typeof fetch>;

  beforeEach(() => {
    fetchMock = jest
      .fn(async () => ({ ok: true } as Response))
      .mockName("fetch") as jest.MockedFunction<typeof fetch>;
    globalScope.fetch = fetchMock;
  });

  afterEach(() => {
    globalScope.fetch = originalFetch;
    jest.clearAllMocks();
  });

  it("includes a sanitised campaign identifier when provided", async () => {
    const recordRef = {
      current: (() => undefined) as RecordFn,
    } as MutableRefObject<RecordFn>;

    const view = render(
      <EngagementProvider
        endpoint="/engagement"
        site="test-site"
        campaignId="  spring-promo  "
        maxBatch={1}
        flushInterval={null}
        heartbeatInterval={60_000}
        idleTimeout={60_000}
        scrollThresholds={[]}
        viewThresholds={[]}
      >
        <Recorder recordRef={recordRef} />
      </EngagementProvider>
    );

    await act(async () => {
      recordRef.current("cta-click");
      await Promise.resolve();
    });

    expect(fetchMock).toHaveBeenCalledTimes(1);
    const payload = JSON.parse(fetchMock.mock.calls[0][1]?.body ?? "{}");
    expect(payload).toMatchObject({
      site: "test-site",
      campaign_id: "spring-promo",
    });

    view.unmount();
  });
});

describe("EngagementProvider lifetime", () => {
  const globalScope = globalThis as GlobalWithOptionalFetch;
  const originalFetch = globalScope.fetch;
  let fetchMock: jest.MockedFunction<typeof fetch>;

  beforeEach(() => {
    jest.useFakeTimers();
    fetchMock = jest
      .fn(async () => ({ ok: true } as Response))
      .mockName("fetch") as jest.MockedFunction<typeof fetch>;
    globalScope.fetch = fetchMock;
  });

  afterEach(() => {
    jest.useRealTimers();
    globalScope.fetch = originalFetch;
    jest.clearAllMocks();
  });

  it("halts event recording after one minute", async () => {
    const recordRef = {
      current: (() => undefined) as RecordFn,
    } as MutableRefObject<RecordFn>;

    const view = render(
      <EngagementProvider
        endpoint="/engagement"
        site="test"
        maxBatch={1}
        flushInterval={null}
        heartbeatInterval={60_000}
        idleTimeout={-1}
        scrollThresholds={[]}
        viewThresholds={[]}
      >
        <Recorder recordRef={recordRef} />
      </EngagementProvider>
    );

    await act(async () => {
      recordRef.current("before-timeout");
      await Promise.resolve();
    });
    expect(fetchMock).toHaveBeenCalledTimes(1);

    await act(async () => {
      jest.advanceTimersByTime(59_000);
      await Promise.resolve();
    });

    await act(async () => {
      recordRef.current("still-active");
      await Promise.resolve();
    });
    expect(fetchMock).toHaveBeenCalledTimes(2);

    await act(async () => {
      jest.advanceTimersByTime(1_000);
      await Promise.resolve();
    });

    await act(async () => {
      recordRef.current("post-timeout");
      await Promise.resolve();
    });

    expect(fetchMock).toHaveBeenCalledTimes(2);

    view.unmount();
  });
});

describe("EngagementProvider view tracking", () => {
  const globalScope = globalThis as GlobalWithOptionalFetch & {
    IntersectionObserver?: typeof IntersectionObserver;
  };
  const originalFetch = globalScope.fetch;
  const originalObserver = globalScope.IntersectionObserver;
  let fetchMock: jest.MockedFunction<typeof fetch>;
  let nowSpy: jest.SpyInstance<number, []> | undefined;

  class MockIntersectionObserver {
    callback: (entries: IntersectionObserverEntry[]) => void;

    observed = new Set<Element>();

    constructor(callback: (entries: IntersectionObserverEntry[]) => void) {
      this.callback = callback;
      observers.push(this);
    }

    observe(element: Element) {
      this.observed.add(element);
    }

    unobserve(element: Element) {
      this.observed.delete(element);
    }

    disconnect() {
      this.observed.clear();
    }

    trigger(entries: IntersectionObserverEntry[]) {
      this.callback(entries);
    }
  }

  const observers: MockIntersectionObserver[] = [];

  beforeEach(() => {
    fetchMock = jest
      .fn(async () => ({ ok: true } as Response))
      .mockName("fetch") as jest.MockedFunction<typeof fetch>;
    globalScope.fetch = fetchMock;
    observers.length = 0;
    globalScope.IntersectionObserver = MockIntersectionObserver as unknown as typeof IntersectionObserver;
    nowSpy = jest.spyOn(performance, "now").mockImplementation(() => currentNow);
    currentNow = 0;
  });

  afterEach(() => {
    nowSpy?.mockRestore();
    globalScope.fetch = originalFetch;
    if (originalObserver) {
      globalScope.IntersectionObserver = originalObserver;
    } else {
      delete globalScope.IntersectionObserver;
    }
    jest.clearAllMocks();
  });

  let currentNow = 0;

  const setNow = (value: number) => {
    currentNow = value;
  };

  const trigger = (observer: MockIntersectionObserver, entry: Partial<IntersectionObserverEntry>) => {
    const observed = Array.from(observer.observed.values());
    const target = entry.target ?? observed[0];
    if (!target) {
      throw new Error("No observed target to trigger");
    }
    observer.trigger([
      {
        time: currentNow,
        target,
        isIntersecting: false,
        intersectionRatio: 0,
        ...entry,
      } as IntersectionObserverEntry,
    ]);
  };

  it("emits matching view and view-end events with timing metadata", async () => {
    const view = render(
      <EngagementProvider
        endpoint="/engagement"
        site="test"
        maxBatch={1}
        flushInterval={null}
        heartbeatInterval={60_000}
        idleTimeout={60_000}
        scrollThresholds={[]}
        viewThresholds={[]}
      >
        <ViewTracker trackId="hero" meta={{ section: "hero" }} />
      </EngagementProvider>
    );

    const observer =
      observers.find((candidate) => candidate.observed.size > 0) ??
      observers[observers.length - 1];
    expect(observer).toBeDefined();
    setNow(100);
    await act(async () => {
      trigger(observer, { isIntersecting: true, intersectionRatio: 0.66 });
      await Promise.resolve();
    });

    expect(fetchMock).toHaveBeenCalledTimes(1);
    const firstPayload = JSON.parse(fetchMock.mock.calls[0][1]?.body ?? "{}");
    expect(firstPayload.events).toHaveLength(1);
    expect(firstPayload.events[0]).toMatchObject({
      type: "view",
      target: "hero",
      meta: { section: "hero", ratio: 0.66 },
    });

    setNow(220);
    await act(async () => {
      trigger(observer, { isIntersecting: false });
      await Promise.resolve();
    });

    expect(fetchMock).toHaveBeenCalledTimes(2);
    const secondPayload = JSON.parse(fetchMock.mock.calls[1][1]?.body ?? "{}");
    expect(secondPayload.events).toHaveLength(1);
    expect(secondPayload.events[0]).toMatchObject({
      type: "view-end",
      target: "hero",
      meta: { section: "hero", duration_ms: 120, ratio: 0.66 },
    });

    view.unmount();
  });
});
