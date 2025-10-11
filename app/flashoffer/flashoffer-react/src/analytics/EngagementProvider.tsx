/*
 * Copyright (c) Flashoffer Developers
 * Released under the MIT license.
 */

import {
  createContext,
  createElement,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useRef,
} from "react";
import type { ElementType, ReactNode } from "react";

const MAX_CONSECUTIVE_FAILURES = 10;
const MAX_COLLECTION_DURATION_MS = 60_000;

export interface EngagementEvent {
  type: string;
  target: string;
  meta: Record<string, unknown>;
  at: string;
}

interface ActiveViewState {
  startedAt: number;
  maxRatio: number;
  meta: Record<string, unknown>;
}

export interface EngagementProviderProps {
  endpoint?: string;
  site: string;
  campaignId?: string;
  children: ReactNode;
  flushInterval?: number | null;
  heartbeatInterval?: number;
  idleTimeout?: number;
  scrollThresholds?: number[];
  viewThresholds?: number[];
  maxBatch?: number;
}

export interface EngagementContextValue {
  register: (
    trackId: string,
    element: Element | null,
    meta?: Record<string, unknown>
  ) => () => void;
  attachElement: (
    trackId: string,
    element: Element | null,
    meta?: Record<string, unknown>
  ) => () => void;
  detachElement: (element: Element | null) => void;
  recordInteraction: (target: string, meta?: Record<string, unknown>) => void;
  getActiveTargets: () => string[];
}

const EngagementContext = createContext<EngagementContextValue | null>(null);

function nowIso(): string {
  return new Date().toISOString();
}

function fallbackUuid(): string {
  if (typeof crypto !== "undefined" && typeof crypto.randomUUID === "function") {
    return crypto.randomUUID();
  }
  return `${Date.now().toString(16)}-${Math.random().toString(16).slice(2)}`;
}

function clampRatio(value: number): number {
  return Number(Math.max(0, Math.min(1, value)).toFixed(3));
}

function canUseBeacon(sync: boolean): boolean {
  return (
    sync &&
    typeof navigator !== "undefined" &&
    "sendBeacon" in navigator
  );
}

function getScrollOffset(win: Window): number {
  if (typeof win.scrollY === "number") {
    return win.scrollY;
  }
  if (typeof win.pageYOffset === "number") {
    return win.pageYOffset;
  }
  return 0;
}

function getViewportHeight(win: Window): number {
  return typeof win.innerHeight === "number" ? win.innerHeight : 0;
}

function getDocumentHeight(doc: Document): number {
  const root = doc.documentElement;
  return root && typeof root.scrollHeight === "number" ? root.scrollHeight : 0;
}

function calculateScrollRatio(): { ratio: number; pixels: number } {
  if (typeof window === "undefined") {
    return { ratio: 0, pixels: 0 };
  }
  const scrollY = getScrollOffset(window);
  const viewport = getViewportHeight(window);
  const fullHeight = getDocumentHeight(document);
  const denominator = fullHeight <= 0 ? 1 : fullHeight;
  const ratio = (scrollY + viewport) / denominator;
  return { ratio: Math.min(1, ratio), pixels: Math.round(scrollY) };
}

function measurePageLoadDuration(): number | null {
  if (typeof performance === "undefined") {
    return null;
  }
  if (typeof performance.getEntriesByType === "function") {
    const [entry] = performance.getEntriesByType("navigation");
    if (entry) {
      const timing = entry as PerformanceNavigationTiming;
      const duration = Math.round(timing.loadEventEnd - timing.startTime);
      if (Number.isFinite(duration) && duration >= 0) {
        return duration;
      }
    }
  }
  const navigationTiming = (performance as Performance & {
    timing?: PerformanceTiming;
  }).timing;
  if (!navigationTiming) {
    return null;
  }
  const duration = Math.round(
    navigationTiming.loadEventEnd - navigationTiming.navigationStart
  );
  if (Number.isFinite(duration) && duration >= 0) {
    return duration;
  }
  return null;
}

export function EngagementProvider({
  endpoint,
  site,
  campaignId,
  children,
  flushInterval = 5000,
  heartbeatInterval = 15000,
  idleTimeout = 30000,
  scrollThresholds = [0.25, 0.5, 0.75, 1],
  viewThresholds = [0.25, 0.5, 0.75, 1],
  maxBatch = 25,
}: EngagementProviderProps) {
  const normalizedCampaignId = useMemo(() => {
    const trimmed = campaignId?.trim();
    return trimmed ? trimmed : undefined;
  }, [campaignId]);
  const queueRef = useRef<EngagementEvent[]>([]);
  const sessionIdRef = useRef<string>(fallbackUuid());
  const trackedElementsRef = useRef(
    new Map<Element, { trackId: string; meta: Record<string, unknown> }>()
  );
  const activeViewsRef = useRef(new Map<string, ActiveViewState>());
  const activeTargetsRef = useRef(new Set<string>());
  const observerRef = useRef<IntersectionObserver | null>(null);
  const thresholdsRef = useRef<number[]>(viewThresholds);
  const flushRef = useRef<
    ((reason?: string, options?: { sync?: boolean }) => Promise<void> | void) | null
  >(null);
  const maxBatchRef = useRef<number>(maxBatch);
  const scrollStateRef = useRef<{ ratio: number; pixels: number }>(
    calculateScrollRatio()
  );
  const intersectionHandlerRef = useRef<
    (entries: IntersectionObserverEntry[]) => void
  >(() => undefined);
  const failureCountRef = useRef(0);
  const disabledRef = useRef(false);

  const disableTracking = useCallback(() => {
    if (disabledRef.current) {
      return;
    }
    disabledRef.current = true;
    queueRef.current = [];
    trackedElementsRef.current.clear();
    activeTargetsRef.current.clear();
    activeViewsRef.current.clear();
    failureCountRef.current = 0;
    if (observerRef.current) {
      observerRef.current.disconnect();
      observerRef.current = null;
    }
  }, []);

  const registerFailure = useCallback(() => {
    failureCountRef.current += 1;
    if (failureCountRef.current >= MAX_CONSECUTIVE_FAILURES) {
      disableTracking();
    }
  }, [disableTracking]);

  const resetFailure = useCallback(() => {
    failureCountRef.current = 0;
  }, []);

  useEffect(() => {
    maxBatchRef.current = maxBatch;
  }, [maxBatch]);

  const requeueEvents = useCallback((events: EngagementEvent[]) => {
    if (!disabledRef.current) {
      queueRef.current.unshift(...events);
    }
  }, []);

  const evaluateFlushEndpoint = useCallback((): string | null => {
    if (disabledRef.current) {
      queueRef.current = [];
      return null;
    }
    if (failureCountRef.current >= MAX_CONSECUTIVE_FAILURES) {
      disableTracking();
      return null;
    }
    if (!endpoint || queueRef.current.length === 0) {
      return null;
    }
    return endpoint;
  }, [disableTracking, endpoint]);

  const deliverWithBeacon = useCallback(
    (currentEndpoint: string, events: EngagementEvent[], body: string) => {
      const delivered = navigator.sendBeacon(currentEndpoint, body);
      if (!delivered) {
        registerFailure();
        requeueEvents(events);
        return;
      }
      resetFailure();
    },
    [registerFailure, requeueEvents, resetFailure]
  );

  const deliverWithFetch = useCallback(
    async (
      currentEndpoint: string,
      events: EngagementEvent[],
      body: string,
      syncDelivery: boolean
    ) => {
      try {
        const response = await fetch(currentEndpoint, {
          method: "POST",
          credentials: "include",
          headers: { "Content-Type": "application/json" },
          body,
          keepalive: syncDelivery,
        });
        if (!response.ok) {
          throw new Error(`Unexpected status ${response.status}`);
        }
        resetFailure();
      } catch (error) {
        // eslint-disable-next-line no-console
        console.warn("Failed to flush engagement events", error);
        registerFailure();
        requeueEvents(events);
      }
    },
    [registerFailure, requeueEvents, resetFailure]
  );

  const enqueue = useCallback(
    (
      event: EngagementEvent,
      options: {
        flushReason?: string;
        flushOptions?: { sync?: boolean };
      } = {}
    ) => {
      if (disabledRef.current) {
        return;
      }
      queueRef.current.push(event);
      if (options.flushReason) {
        flushRef.current?.(options.flushReason, options.flushOptions);
        return;
      }
      if (queueRef.current.length >= maxBatchRef.current) {
        flushRef.current?.("capacity");
      }
    },
    []
  );

  const flush = useCallback(
    async (reason = "interval", { sync = false }: { sync?: boolean } = {}) => {
      const currentEndpoint = evaluateFlushEndpoint();
      if (!currentEndpoint) {
        return;
      }
      const events = queueRef.current.splice(0, queueRef.current.length);
      const payload = {
        site,
        session_id: sessionIdRef.current,
        events,
        reason,
        ...(normalizedCampaignId
          ? { campaign_id: normalizedCampaignId }
          : {}),
      };
      const body = JSON.stringify(payload);
      if (canUseBeacon(sync)) {
        deliverWithBeacon(currentEndpoint, events, body);
        return;
      }
      await deliverWithFetch(currentEndpoint, events, body, sync);
    },
    [
      deliverWithBeacon,
      deliverWithFetch,
      evaluateFlushEndpoint,
      normalizedCampaignId,
      site,
    ]
  );

  useEffect(() => {
    flushRef.current = flush;
  }, [flush]);

  useEffect(() => {
    if (typeof window === "undefined") {
      return undefined;
    }
    let hasFired = false;

    const emitPageLoad = () => {
      if (hasFired || disabledRef.current) {
        return;
      }
      hasFired = true;
      const meta: Record<string, unknown> = {};
      const loadDuration = measurePageLoadDuration();
      if (loadDuration !== null) {
        meta.load_duration_ms = loadDuration;
      }
      enqueue(
        {
          type: "page-load",
          target: "page",
          meta,
          at: nowIso(),
        },
        { flushReason: "page-load" }
      );
    };

    if (document.readyState === "complete") {
      emitPageLoad();
      return () => {
        hasFired = true;
      };
    }

    window.addEventListener("load", emitPageLoad, { once: true });

    return () => {
      hasFired = true;
      window.removeEventListener("load", emitPageLoad);
    };
  }, [enqueue]);

  useEffect(() => {
    if (typeof window === "undefined") {
      return undefined;
    }
    const timeout = window.setTimeout(() => {
      void flushRef.current?.("lifetime");
      disableTracking();
    }, MAX_COLLECTION_DURATION_MS);
    return () => {
      window.clearTimeout(timeout);
    };
  }, [disableTracking]);

  useEffect(() => {
    thresholdsRef.current = viewThresholds;
    if (!observerRef.current) {
      return;
    }
    const elements = Array.from(trackedElementsRef.current.keys());
    observerRef.current.disconnect();
    observerRef.current = new IntersectionObserver(
      (entries) => {
        intersectionHandlerRef.current(entries);
      },
      { threshold: thresholdsRef.current }
    );
    elements.forEach((element) => observerRef.current?.observe(element));
  }, [viewThresholds]);

  const detachElement = useCallback((element: Element | null) => {
    if (!element || !trackedElementsRef.current.has(element)) {
      return;
    }
    const info = trackedElementsRef.current.get(element);
    trackedElementsRef.current.delete(element);
    if (observerRef.current) {
      observerRef.current.unobserve(element);
    }
    if (info) {
      activeTargetsRef.current.delete(info.trackId);
      activeViewsRef.current.delete(info.trackId);
    }
  }, []);

  const ensureObserver = useCallback(() => {
    if (disabledRef.current) {
      return null;
    }
    if (observerRef.current) {
      return observerRef.current;
    }
    if (typeof window === "undefined" || typeof IntersectionObserver === "undefined") {
      return null;
    }
    observerRef.current = new IntersectionObserver(
      (entries) => {
        intersectionHandlerRef.current(entries);
      },
      { threshold: thresholdsRef.current }
    );
    return observerRef.current;
  }, []);

  const handleIntersectionEntry = useCallback(
    (
      trackId: string,
      meta: Record<string, unknown>,
      entry: IntersectionObserverEntry,
      timestamp: number
    ) => {
      activeTargetsRef.current.add(trackId);
      const ratio = clampRatio(entry.intersectionRatio || 0);
      const state = activeViewsRef.current.get(trackId);
      if (state) {
        state.maxRatio = Math.max(state.maxRatio, ratio);
        return;
      }
      activeViewsRef.current.set(trackId, {
        startedAt: timestamp,
        maxRatio: ratio,
        meta,
      });
      // Fires when an element first becomes visible; ratio captures the clamped entry intersection.
      enqueue({ type: "view", target: trackId, meta: { ...meta, ratio }, at: nowIso() });
    },
    [enqueue]
  );

  const handleIntersectionExit = useCallback(
    (trackId: string, timestamp: number) => {
      activeTargetsRef.current.delete(trackId);
      const state = activeViewsRef.current.get(trackId);
      if (!state) {
        return;
      }
      activeViewsRef.current.delete(trackId);
      const duration = Math.round(timestamp - state.startedAt);
      // Fires when visibility ends; duration_ms covers time since entry and ratio records the peak visibility.
      enqueue({
        type: "view-end",
        target: trackId,
        meta: { ...state.meta, duration_ms: duration, ratio: state.maxRatio },
        at: nowIso(),
      });
    },
    [enqueue]
  );

  intersectionHandlerRef.current = (entries: IntersectionObserverEntry[]) => {
    if (disabledRef.current) {
      return;
    }
    const timestamp = typeof performance !== "undefined" ? performance.now() : 0;
    entries.forEach((entry) => {
      const info = trackedElementsRef.current.get(entry.target);
      if (!info) {
        return;
      }
      const { trackId, meta } = info;
      if (entry.isIntersecting) {
        handleIntersectionEntry(trackId, meta, entry, timestamp);
      } else {
        handleIntersectionExit(trackId, timestamp);
      }
    });
  };

  const attachElement = useCallback(
    (trackId: string, element: Element | null, meta: Record<string, unknown> = {}) => {
      if (disabledRef.current) {
        return () => undefined;
      }
      if (!trackId || !element) {
        return () => undefined;
      }
      const observer = ensureObserver();
      if (!observer) {
        return () => undefined;
      }
      if (trackedElementsRef.current.has(element)) {
        detachElement(element);
      }
      trackedElementsRef.current.set(element, { trackId, meta });
      if (element instanceof HTMLElement) {
        const currentTrackId = element.getAttribute("data-track-id");
        if (currentTrackId !== trackId) {
          element.setAttribute("data-track-id", trackId);
        }
      }
      observer.observe(element as Element);
      return () => detachElement(element);
    },
    [detachElement, ensureObserver]
  );

  const register = useCallback(
    (trackId: string, element: Element | null, meta: Record<string, unknown> = {}) =>
      attachElement(trackId, element, meta),
    [attachElement]
  );

  const recordInteraction = useCallback(
    (target: string, data: Record<string, unknown> = {}) => {
      if (disabledRef.current) {
        return;
      }
      if (!target) {
        return;
      }
      const scroll = scrollStateRef.current;
      const meta: Record<string, unknown> = {
        ...data,
        scroll: {
          ratio: clampRatio(scroll.ratio || 0),
          pixels: scroll.pixels || 0,
        },
      };
      if (activeTargetsRef.current.size > 0) {
        meta.active = Array.from(activeTargetsRef.current.values());
      }
      enqueue({ type: "interaction", target, meta, at: nowIso() });
    },
    [enqueue]
  );

  useEffect(() => {
    if (typeof window === "undefined") {
      return undefined;
    }
    let scheduled = false;
    const thresholds = Array.from(new Set(scrollThresholds)).sort((a, b) => a - b);
    const crossed = new Set<number>();

    const updateState = () => {
      scheduled = false;
      const next = calculateScrollRatio();
      scrollStateRef.current = next;
      thresholds.forEach((threshold) => {
        if (!crossed.has(threshold) && next.ratio >= threshold) {
          crossed.add(threshold);
          enqueue({
            type: "scroll-depth",
            target: "page",
            meta: { depth: threshold, pixels: next.pixels },
            at: nowIso(),
          });
        }
      });
    };

    const onScroll = () => {
      if (!scheduled) {
        scheduled = true;
        requestAnimationFrame(updateState);
      }
    };

    window.addEventListener("scroll", onScroll, { passive: true });
    updateState();
    return () => {
      window.removeEventListener("scroll", onScroll);
    };
  }, [enqueue, scrollThresholds]);

  useEffect(() => {
    if (typeof window === "undefined") {
      return undefined;
    }
    let lastActive = Date.now();

    const markActive = () => {
      lastActive = Date.now();
    };

    const activityEvents: Array<keyof WindowEventMap> = [
      "mousemove",
      "keydown",
      "scroll",
      "touchstart",
      "focus",
    ];
    activityEvents.forEach((event) => {
      window.addEventListener(event, markActive, { passive: true });
    });

    const visibilityListener = () => {
      if (document.visibilityState === "visible") {
        markActive();
      }
    };
    document.addEventListener("visibilitychange", visibilityListener);

    const heartbeat = window.setInterval(() => {
      if (document.visibilityState !== "visible") {
        return;
      }
      if (Date.now() - lastActive > idleTimeout) {
        return;
      }
      enqueue({
        type: "dwell",
        target: "page",
        meta: { interval_ms: heartbeatInterval },
        at: nowIso(),
      });
    }, heartbeatInterval);

    return () => {
      window.clearInterval(heartbeat);
      document.removeEventListener("visibilitychange", visibilityListener);
      activityEvents.forEach((event) => {
        window.removeEventListener(event, markActive);
      });
    };
  }, [enqueue, heartbeatInterval, idleTimeout]);

  useEffect(() => {
    if (!flushInterval) {
      return undefined;
    }
    const id = window.setInterval(() => {
      void flush("interval");
    }, flushInterval);
    return () => {
      window.clearInterval(id);
    };
  }, [flush, flushInterval]);

  useEffect(() => {
    if (typeof window === "undefined") {
      return undefined;
    }
    const handleVisibility = () => {
      if (document.visibilityState === "hidden") {
        flushRef.current?.("visibility", { sync: true });
      }
    };
    const handleUnload = () => {
      flushRef.current?.("unload", { sync: true });
    };
    document.addEventListener("visibilitychange", handleVisibility);
    window.addEventListener("pagehide", handleUnload);
    window.addEventListener("beforeunload", handleUnload);
    return () => {
      document.removeEventListener("visibilitychange", handleVisibility);
      window.removeEventListener("pagehide", handleUnload);
      window.removeEventListener("beforeunload", handleUnload);
    };
  }, []);

  const value = useMemo<EngagementContextValue>(
    () => ({
      register,
      attachElement,
      detachElement,
      recordInteraction,
      getActiveTargets: () => Array.from(activeTargetsRef.current.values()),
    }),
    [attachElement, detachElement, recordInteraction, register]
  );

  return (
    <EngagementContext.Provider value={value}>{children}</EngagementContext.Provider>
  );
}

export function useEngagement(): EngagementContextValue {
  const context = useContext(EngagementContext);
  if (!context) {
    throw new Error("useEngagement must be used within an EngagementProvider");
  }
  return context;
}

export function useViewTracker(
  trackId: string,
  meta: Record<string, unknown> = {}
) {
  const { register } = useEngagement();
  const cleanupRef = useRef<(() => void) | null>(null);
  const metaRef = useRef<Record<string, unknown>>(meta);

  useEffect(() => {
    metaRef.current = meta;
  }, [meta]);

  return useCallback(
    (node: Element | null) => {
      if (cleanupRef.current) {
        cleanupRef.current();
        cleanupRef.current = null;
      }
      if (node) {
        cleanupRef.current = register(trackId, node, metaRef.current);
      }
    },
    [register, trackId]
  );
}

export interface ViewTrackerProps {
  trackId: string;
  meta?: Record<string, unknown>;
  as?: ElementType;
  children?: ReactNode;
  [key: string]: unknown;
}

export function ViewTracker({
  trackId,
  meta = {},
  as: Component = "div",
  children,
  ...props
}: ViewTrackerProps) {
  const ref = useViewTracker(trackId, meta);
  return createElement(
    Component,
    { ref, ...props, "data-track-id": trackId },
    children
  );
}

export function useRecordInteraction(
  defaultTarget?: string,
  defaultMeta: Record<string, unknown> = {}
) {
  const { recordInteraction } = useEngagement();
  return useCallback(
    (target: string = defaultTarget ?? "", meta: Record<string, unknown> = defaultMeta) => {
      recordInteraction(target, meta);
    },
    [defaultMeta, defaultTarget, recordInteraction]
  );
}
