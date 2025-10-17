/*
 * Copyright (c) Flashoffer Developers
 * Released under the MIT license.
 */

import Box from "@mui/material/Box";
import Chip from "@mui/material/Chip";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";
import { alpha, darken, lighten } from "@mui/material/styles";
import { useEffect, useMemo, useState } from "react";
import type { ReactNode } from "react";

const SEGMENT_DEFINITIONS = [
  { key: "days", label: "Days" },
  { key: "hours", label: "Hours" },
  { key: "minutes", label: "Minutes" },
  { key: "seconds", label: "Seconds" }
] as const;

interface CountdownSegments {
  days: number;
  hours: number;
  minutes: number;
  seconds: number;
  totalMs: number;
}

type CountdownDataMode =
  | { kind: "campaign"; campaignId: string }
  | { kind: "time-remaining"; remainingMs: number }
  | { kind: "end-time"; targetTimestamp: number };

/**
 * Normalizes end time inputs into a Unix timestamp in milliseconds.
 *
 * @param endTime - End time candidate to convert into milliseconds.
 * @returns Millisecond precision timestamp representing the countdown end.
 */
function normalizeEndTime(endTime: Date | string | number): number {
  const candidate =
    endTime instanceof Date ? endTime.getTime() : new Date(endTime).getTime();

  if (!Number.isFinite(candidate)) {
    throw new Error("CountdownTimer received an invalid endTime value.");
  }

  return candidate;
}

/**
 * Derives the remaining time segments from a millisecond timestamp.
 *
 * @param targetTimestamp - Future timestamp that represents when the offer
 *   expires.
 * @returns Structured segment breakdown describing the time left.
 */
function deriveSegments(targetTimestamp: number): CountdownSegments {
  const now = Date.now();
  const difference = Math.max(targetTimestamp - now, 0);

  const totalSeconds = Math.floor(difference / 1000);
  const days = Math.floor(totalSeconds / 86400);
  const hours = Math.floor((totalSeconds % 86400) / 3600);
  const minutes = Math.floor((totalSeconds % 3600) / 60);
  const seconds = totalSeconds % 60;

  return {
    days,
    hours,
    minutes,
    seconds,
    totalMs: difference
  };
}

/**
 * Creates a spoken announcement summarizing the remaining time segments.
 *
 * @param segments - Countdown breakdown that informs the assistive summary.
 * @returns Readable and accessible message for screen readers.
 */
function createAriaAnnouncement(segments: CountdownSegments): string {
  const parts: string[] = [];

  SEGMENT_DEFINITIONS.forEach(({ key, label }) => {
    const value = segments[key];
    const base = label.toLowerCase();
    const singular = base.endsWith("s") ? base.slice(0, -1) : base;

    if (value > 0 || (key === "seconds" && segments.totalMs === 0)) {
      const noun = value === 1 ? singular : base;
      parts.push(`${value} ${noun}`);
    }
  });

  if (parts.length === 0) {
    return "Offer window has concluded.";
  }

  return `Offer ends in ${parts.join(", ")}.`;
}

/**
 * Formats numbers using at least two digits for compact presentation.
 *
 * @param value - Segment number to render.
 * @returns Segment value padded to at least two characters.
 */
function formatSegmentValue(value: number): string {
  return value.toString().padStart(2, "0");
}

export interface CountdownTimerProps {
  /** Campaign identifier whose end time is loaded from the backend. */
  campaignId?: string;
  /**
   * Target time indicating when the promotion ends. Supply this when the
   * backend is unavailable and the deadline is known upfront.
   */
  endTime?: Date | string | number;
  /**
   * Direct countdown duration in milliseconds when an end time is unavailable.
   * Cannot be combined with `campaignId`.
   */
  timeRemainingMs?: number;
  /** Optional number of items remaining for the promotion. */
  quantityRemaining?: number;
  /** Headline emphasizing the urgency of the promotion. */
  headline?: ReactNode;
  /** Label describing the timer group. */
  timerLabel?: ReactNode;
  /** Custom label rendered alongside the remaining quantity. */
  quantityLabel?: ReactNode;
  /** Interval, in milliseconds, at which the timer updates. */
  intervalMs?: number;
}

const DEFAULT_HEADLINE = "Hurry! This drop is moving fast.";
const DEFAULT_TIMER_LABEL = "Offer ends in";
const DEFAULT_QUANTITY_LABEL = "units remaining";

/**
 * High-contrast countdown module pairing urgency copy with remaining
 * quantity.
 *
 * Provide `campaignId` to source the deadline from the Flashoffer campaign
 * backend. When no campaign identifier is supplied, specify either
 * `endTime` or `timeRemainingMs` to render a static countdown.
 *
 * @param props - Component configuration describing end time sourcing and
 *   messaging.
 * @returns A visually urgent countdown surface.
 */
export function CountdownTimer({
  campaignId,
  endTime,
  timeRemainingMs,
  quantityRemaining,
  headline = DEFAULT_HEADLINE,
  timerLabel = DEFAULT_TIMER_LABEL,
  quantityLabel = DEFAULT_QUANTITY_LABEL,
  intervalMs = 1000
}: CountdownTimerProps) {
  const countdownMode = useMemo<CountdownDataMode>(() => {
    const trimmedCampaignId = campaignId?.trim() ?? "";
    const hasCampaign = trimmedCampaignId.length > 0;
    const hasRemaining = typeof timeRemainingMs === "number";
    const hasEndTime = typeof endTime !== "undefined";

    if (hasCampaign) {
      if (hasRemaining || hasEndTime) {
        throw new Error(
          "CountdownTimer cannot mix campaignId with explicit time values."
        );
      }

      return { kind: "campaign", campaignId: trimmedCampaignId };
    }

    if (hasRemaining) {
      const parsedRemaining = Number(timeRemainingMs);
      if (!Number.isFinite(parsedRemaining)) {
        throw new Error(
          "CountdownTimer received an invalid timeRemainingMs value."
        );
      }

      return {
        kind: "time-remaining",
        remainingMs: Math.max(0, parsedRemaining)
      };
    }

    if (hasEndTime) {
      return {
        kind: "end-time",
        targetTimestamp: normalizeEndTime(endTime as Date | string | number)
      };
    }

    throw new Error(
      "CountdownTimer requires either a campaignId or a timeRemainingMs/endTime value."
    );
  }, [campaignId, endTime, timeRemainingMs]);

  const [targetTimestamp, setTargetTimestamp] = useState<number>(() => {
    if (countdownMode.kind === "end-time") {
      return countdownMode.targetTimestamp;
    }

    if (countdownMode.kind === "time-remaining") {
      return Date.now() + countdownMode.remainingMs;
    }

    return Date.now();
  });

  const [segments, setSegments] = useState<CountdownSegments>(() =>
    deriveSegments(targetTimestamp)
  );

  useEffect(() => {
    if (countdownMode.kind === "campaign") {
      if (typeof globalThis.fetch !== "function") {
        setTargetTimestamp(Date.now());
        return;
      }

      let cancelled = false;
      const AbortCtor = globalThis.AbortController;
      const controller = typeof AbortCtor === "function" ? new AbortCtor() : null;

      const resolveTarget = (data: Record<string, unknown>): number | null => {
        const remainingCandidates = [
          data["remainingMs"],
          data["remaining_ms"],
          data["remainingMilliseconds"]
        ];

        for (const candidate of remainingCandidates) {
          if (typeof candidate === "number" && Number.isFinite(candidate)) {
            return Date.now() + Math.max(0, candidate);
          }
        }

        const endTimeCandidate =
          data["endTime"] ?? data["end_time"] ?? data["deadline"];
        if (typeof endTimeCandidate === "string" || endTimeCandidate instanceof Date) {
          try {
            return normalizeEndTime(endTimeCandidate);
          } catch (error) {
            console.warn("Failed to parse campaign end time", error);
          }
        } else if (typeof endTimeCandidate === "number") {
          return normalizeEndTime(endTimeCandidate);
        }

        return null;
      };

      const fetchEndTime = async () => {
        try {
          const response = await globalThis.fetch(
            `/api/campaign/${encodeURIComponent(countdownMode.campaignId)}/end_time`,
            {
              signal: controller?.signal,
              headers: { Accept: "application/json" }
            }
          );

          if (!response.ok) {
            throw new Error(`Unexpected response: ${response.status}`);
          }

          const payload = (await response.json()) as Record<string, unknown>;
          const nextTarget = resolveTarget(payload);

          if (cancelled) {
            return;
          }

          setTargetTimestamp(nextTarget ?? Date.now());
        } catch (error) {
          if (cancelled) {
            return;
          }
          console.warn("Failed to load campaign end time", error);
          setTargetTimestamp(Date.now());
        }
      };

      void fetchEndTime();

      return () => {
        cancelled = true;
        controller?.abort();
      };
    }

    if (countdownMode.kind === "time-remaining") {
      setTargetTimestamp(Date.now() + countdownMode.remainingMs);
      return;
    }

    setTargetTimestamp(countdownMode.targetTimestamp);
  }, [countdownMode]);

  useEffect(() => {
    setSegments(deriveSegments(targetTimestamp));

    if (typeof window === "undefined") {
      return;
    }

    const id = window.setInterval(() => {
      setSegments(deriveSegments(targetTimestamp));
    }, intervalMs);

    return () => {
      window.clearInterval(id);
    };
  }, [targetTimestamp, intervalMs]);

  const ariaAnnouncement = useMemo(
    () => createAriaAnnouncement(segments),
    [segments]
  );

  const formattedQuantity = useMemo(() => {
    if (typeof quantityRemaining !== "number") {
      return null;
    }

    const formatter = new Intl.NumberFormat();
    return formatter.format(Math.max(quantityRemaining, 0));
  }, [quantityRemaining]);

  return (
    <Box
      component="section"
      role="timer"
      aria-live="polite"
      aria-atomic="true"
      aria-label={ariaAnnouncement}
      sx={(theme) => {
        const primaryMain = theme.palette.primary.main;
        const primaryLight =
          theme.palette.primary.light ?? lighten(primaryMain, 0.22);
        const primaryDark =
          theme.palette.primary.dark ?? darken(primaryMain, 0.18);
        const surface = theme.palette.background.paper;

        return {
          background: `linear-gradient(135deg, ${alpha(
            primaryLight,
            0.95
          )} 0%, ${alpha(primaryMain, 0.95)} 45%, ${alpha(
            surface,
            0.95
          )} 100%)`,
          borderRadius: 6,
          border: "1px solid",
          borderColor: alpha(primaryMain, 0.4),
          boxShadow: `0 24px 40px ${alpha(primaryDark, 0.35)}`,
          color: theme.palette.text.primary,
          overflow: "visible",
          p: { xs: 3, md: 4 },
          position: "relative"
        };
      }}
    >
      <Stack spacing={3} alignItems={{ xs: "stretch", md: "center" }}>
        <Stack
          direction={{ xs: "column", md: "row" }}
          spacing={2}
          alignItems={{ xs: "flex-start", md: "center" }}
          justifyContent="space-between"
        >
          <Stack spacing={1}>
            <Typography
              component="p"
              variant="overline"
              sx={(theme) => ({
                color:
                  theme.palette.primary.dark ??
                  darken(theme.palette.primary.main, 0.25),
                fontWeight: 700,
                letterSpacing: 2,
                textTransform: "uppercase"
              })}
            >
              {timerLabel}
            </Typography>
            <Typography
              component="h2"
              variant="h4"
              sx={{
                fontWeight: 800,
                letterSpacing: -0.5,
                lineHeight: 1.1,
                maxWidth: 520
              }}
            >
              {headline}
            </Typography>
          </Stack>
          {formattedQuantity ? (
            <Chip
              color="primary"
              label={
                <Stack spacing={0.5} alignItems="center">
                  <Typography
                    component="span"
                    variant="caption"
                    sx={{ textTransform: "uppercase", fontWeight: 700 }}
                  >
                    {quantityLabel}
                  </Typography>
                  <Typography
                    component="span"
                    variant="h6"
                    sx={{ fontWeight: 800, lineHeight: 1 }}
                  >
                    {formattedQuantity}
                  </Typography>
                </Stack>
              }
              sx={(theme) => {
                const main = theme.palette.primary.main;
                const light =
                  theme.palette.primary.light ?? lighten(main, 0.18);
                const dark =
                  theme.palette.primary.dark ?? darken(main, 0.18);
                return {
                  background: `linear-gradient(135deg, ${dark} 0%, ${main} 50%, ${light} 100%)`,
                  alignItems: "center",
                  display: "flex",
                  justifyContent: "center",
                  minHeight: 88,
                  minWidth: 200,
                  px: 2.5,
                  py: 2.5,
                  borderRadius: 4,
                  "& .MuiChip-label": {
                    px: 0,
                    py: 0,
                    color: theme.palette.getContrastText(main),
                    display: "block",
                    width: "100%"
                  }
                };
              }}
            />
          ) : null}
        </Stack>

        <Box
          sx={{
            display: "grid",
            gap: 2,
            gridAutoRows: "minmax(152px, auto)",
            gridTemplateColumns: {
              xs: "repeat(auto-fit, minmax(168px, 1fr))",
              lg: "repeat(auto-fit, minmax(184px, 1fr))"
            }
          }}
        >
          {SEGMENT_DEFINITIONS.map(({ key, label }) => {
            const value = segments[key];
            return (
              <Box
                key={key}
                sx={(theme) => {
                  const main = theme.palette.primary.main;
                  const light =
                    theme.palette.primary.light ?? lighten(main, 0.24);
                  const dark =
                    theme.palette.primary.dark ?? darken(main, 0.22);
                  const surface = theme.palette.background.paper;
                  const text =
                    theme.palette.mode === "dark"
                      ? theme.palette.getContrastText(dark)
                      : theme.palette.text.secondary;
                  const borderColor =
                    theme.palette.mode === "dark"
                      ? alpha(theme.palette.common.black, 0.4)
                      : alpha(theme.palette.common.white, 0.7);
                  return {
                    alignItems: "center",
                    background: `linear-gradient(160deg, ${alpha(
                      surface,
                      0.9
                    )} 0%, ${alpha(light, 0.6)} 60%, ${alpha(main, 0.6)} 100%)`,
                    borderRadius: 4,
                    border: `1px solid ${borderColor}`,
                    boxShadow: `0 20px 40px ${alpha(dark, 0.35)}`,
                    display: "flex",
                    flexDirection: "column",
                    gap: 1,
                    justifyContent: "center",
                    minHeight: 152,
                    minWidth: 168,
                    px: 3.5,
                    py: 3,
                    textAlign: "center",
                    "& .CountdownTimer-segmentLabel": {
                      color: text
                    }
                  };
                }}
              >
                <Typography
                  component="span"
                  variant="h3"
                  aria-label={`${value} ${label.toLowerCase()} remaining`}
                  sx={{
                    display: "block",
                    fontFeatureSettings: '"tnum" on, "ss01" on',
                    fontWeight: 800,
                    letterSpacing: -1,
                    lineHeight: 1,
                    wordBreak: "break-word"
                  }}
                >
                  {formatSegmentValue(value)}
                </Typography>
                <Typography
                  component="span"
                  variant="subtitle2"
                  className="CountdownTimer-segmentLabel"
                  sx={{
                    fontWeight: 700,
                    letterSpacing: 1.5,
                    textTransform: "uppercase"
                  }}
                >
                  {label}
                </Typography>
              </Box>
            );
          })}
        </Box>
      </Stack>
    </Box>
  );
}
