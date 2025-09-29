import { useEffect } from "react";
import { useEngagement } from "./EngagementProvider";

const DEFAULT_SELECTOR = "[data-track-id]";

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

export function AutoTrack({ selector = DEFAULT_SELECTOR }: AutoTrackProps) {
  const { attachElement, detachElement } = useEngagement();

  useEffect(() => {
    if (typeof document === "undefined") {
      return () => undefined;
    }

    const tracked = new Map<HTMLElement, () => void>();

    const connect = (element: Element | null) => {
      if (!(element instanceof HTMLElement)) {
        return;
      }
      const trackId = element.getAttribute("data-track-id");
      if (!trackId || tracked.has(element)) {
        return;
      }
      const cleanup = attachElement(trackId, element, parseMeta(element));
      tracked.set(element, cleanup);
    };

    const disconnect = (element: Element | null) => {
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

    document.querySelectorAll(selector).forEach((node) => {
      connect(node);
    });

    const observer = new MutationObserver((mutations) => {
      mutations.forEach((mutation) => {
        mutation.addedNodes.forEach((node) => {
          if (node instanceof HTMLElement) {
            if (node.matches(selector)) {
              connect(node);
            }
            node.querySelectorAll(selector).forEach((child) => connect(child));
          }
        });
        mutation.removedNodes.forEach((node) => {
          if (node instanceof HTMLElement) {
            if (node.matches(selector)) {
              disconnect(node);
            }
            node.querySelectorAll(selector).forEach((child) => disconnect(child));
          }
        });
        if (
          mutation.type === "attributes" &&
          mutation.target instanceof HTMLElement &&
          mutation.target.matches(selector)
        ) {
          disconnect(mutation.target);
          connect(mutation.target);
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
      observer.disconnect();
      tracked.forEach((cleanup) => cleanup());
      tracked.clear();
    };
  }, [attachElement, detachElement, selector]);

  return null;
}

export default AutoTrack;
