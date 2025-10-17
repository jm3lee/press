/*
 * Copyright (c) Flashoffer Developers
 * Released under the MIT license.
 */

import { useEffect } from "react";
import { useEngagement } from "./EngagementProvider";

const DEFAULT_SELECTOR = "[data-track-id]";

const scheduleMicrotask =
  typeof queueMicrotask === "function"
    ? queueMicrotask
    : (callback: () => void) => {
        void Promise.resolve().then(callback);
      };

function parseMeta(element: HTMLElement): Record<string, unknown> {
  const meta: Record<string, unknown> = {};
  const label = element.getAttribute("data-track-label");
  if (label) {
    meta.label = label;
  }
  const raw = element.getAttribute("data-track-meta");
  if (raw) {
    try {
      const parsed = JSON.parse(raw) as unknown;
      if (parsed && typeof parsed === "object") {
        Object.assign(meta, parsed as Record<string, unknown>);
      }
    } catch (error) {
      meta.meta = raw;
      // eslint-disable-next-line no-console
      console.warn("Failed to parse data-track-meta", raw, error);
    }
  }
  return meta;
}

export interface AutoTrackProps {
  selector?: string;
}

/**
 * Watches the document for nodes that expose tracking metadata and wires them
 * up to the engagement provider. Elements matching the `selector` (defaults to
 * `[data-track-id]`) are connected when they appear and automatically
 * disconnected when they are removed.
 *
 * @param selector - CSS selector that identifies trackable elements.
 */
export function AutoTrack({ selector = DEFAULT_SELECTOR }: AutoTrackProps) {
  const { attachElement, detachElement } = useEngagement();

  useEffect(() => {
    if (typeof document === "undefined") {
      return () => undefined;
    }

    const tracked = new Map<HTMLElement, () => void>();
    const pendingConnects = new Set<HTMLElement>();
    const pendingDisconnects = new Set<HTMLElement>();
    let flushScheduled = false;
    let disposed = false;

    const connectNow = (element: Element | null) => {
      if (!(element instanceof HTMLElement) || disposed) {
        return;
      }
      const trackId = element.getAttribute("data-track-id");
      if (!trackId || tracked.has(element)) {
        return;
      }
      const cleanup = attachElement(trackId, element, parseMeta(element));
      tracked.set(element, cleanup);
    };

    const disconnectNow = (element: Element | null) => {
      if (!(element instanceof HTMLElement)) {
        return;
      }
      const cleanup = tracked.get(element);
      if (cleanup) {
        cleanup();
        tracked.delete(element);
      } else {
        detachElement(element);
      }
    };

    const flushPending = () => {
      if (disposed) {
        pendingConnects.clear();
        pendingDisconnects.clear();
        return;
      }
      pendingDisconnects.forEach((element) => {
        disconnectNow(element);
      });
      pendingDisconnects.clear();
      pendingConnects.forEach((element) => {
        connectNow(element);
      });
      pendingConnects.clear();
    };

    const scheduleFlush = () => {
      if (flushScheduled || disposed) {
        return;
      }
      flushScheduled = true;
      scheduleMicrotask(() => {
        flushScheduled = false;
        flushPending();
      });
    };

    const queueDisconnect = (
      element: Element | null,
      { preserve }: { preserve?: boolean } = {}
    ) => {
      if (!(element instanceof HTMLElement) || disposed) {
        return;
      }
      if (!preserve) {
        pendingConnects.delete(element);
      }
      pendingDisconnects.add(element);
      scheduleFlush();
    };

    const queueConnect = (
      element: Element | null,
      { preserve }: { preserve?: boolean } = {}
    ) => {
      if (!(element instanceof HTMLElement) || disposed) {
        return;
      }
      if (!preserve) {
        pendingDisconnects.delete(element);
      }
      pendingConnects.add(element);
      scheduleFlush();
    };

    const visitMatches = (
      node: HTMLElement,
      visitor: (element: HTMLElement) => void
    ) => {
      if (node.matches(selector)) {
        visitor(node);
      }
      node.querySelectorAll(selector).forEach((child) => {
        if (child instanceof HTMLElement) {
          visitor(child);
        }
      });
    };

    document.querySelectorAll(selector).forEach((node) => {
      connectNow(node);
    });

    const observer = new MutationObserver((mutations) => {
      mutations.forEach((mutation) => {
        mutation.addedNodes.forEach((node) => {
          if (node instanceof HTMLElement) {
            visitMatches(node, (element) => queueConnect(element));
          }
        });
        mutation.removedNodes.forEach((node) => {
          if (node instanceof HTMLElement) {
            visitMatches(node, (element) => queueDisconnect(element));
          }
        });
        if (
          mutation.type === "attributes" &&
          mutation.target instanceof HTMLElement &&
          mutation.target.matches(selector)
        ) {
          queueDisconnect(mutation.target, { preserve: true });
          queueConnect(mutation.target, { preserve: true });
        } else if (
          mutation.type === "attributes" &&
          mutation.target instanceof HTMLElement &&
          !mutation.target.matches(selector)
        ) {
          queueDisconnect(mutation.target);
        }
      });
    });

    observer.observe(document.body, {
      childList: true,
      subtree: true,
      attributes: true,
      attributeFilter: ["data-track-id", "data-track-label", "data-track-meta"],
    });

    return () => {
      disposed = true;
      flushScheduled = false;
      pendingConnects.clear();
      pendingDisconnects.clear();
      observer.disconnect();
      tracked.forEach((cleanup) => cleanup());
      tracked.clear();
    };
  }, [attachElement, detachElement, selector]);

  return null;
}

export default AutoTrack;
