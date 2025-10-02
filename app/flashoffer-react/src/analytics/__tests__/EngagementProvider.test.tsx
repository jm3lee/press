import { act, render } from "@testing-library/react";
import type { MutableRefObject } from "react";
import {
  EngagementProvider,
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
