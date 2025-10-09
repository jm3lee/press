/*
 * Copyright (c) Flashoffer Developers
 * Released under the MIT license.
 */

import Box from "@mui/material/Box";
import Chip from "@mui/material/Chip";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";
import { alpha, lighten } from "@mui/material/styles";
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
  /** Target time indicating when the promotion ends. */
  endTime: Date | string | number;
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
 * @param props - Component configuration describing end time and messaging.
 * @returns A visually urgent countdown surface.
 */
export function CountdownTimer({
  endTime,
  quantityRemaining,
  headline = DEFAULT_HEADLINE,
  timerLabel = DEFAULT_TIMER_LABEL,
  quantityLabel = DEFAULT_QUANTITY_LABEL,
  intervalMs = 1000
}: CountdownTimerProps) {
  const targetTimestamp = useMemo(() => normalizeEndTime(endTime), [endTime]);
  const [segments, setSegments] = useState<CountdownSegments>(() =>
    deriveSegments(targetTimestamp)
  );

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
        const errorLight = theme.palette.error.light;
        const errorMain = theme.palette.error.main;
        const surface = theme.palette.background.paper;

        return {
          background: `linear-gradient(135deg, ${alpha(errorLight, 0.95)} 0%, ${alpha(
            errorMain,
            0.95
          )} 45%, ${alpha(surface, 0.95)} 100%)`,
          borderRadius: 6,
          border: "1px solid",
          borderColor: errorLight,
          boxShadow: `0 24px 40px ${alpha(errorMain, 0.35)}`,
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
              sx={{
                color: "error.dark",
                fontWeight: 700,
                letterSpacing: 2,
                textTransform: "uppercase"
              }}
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
              color="error"
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
                const main = theme.palette.error.main;
                const light = theme.palette.error.light;
                return {
                  background: `linear-gradient(135deg, ${main} 0%, ${lighten(
                    main,
                    0.2
                  )} 50%, ${lighten(light, 0.1)} 100%)`,
                  px: 2.5,
                  py: 2.5,
                  borderRadius: 4,
                  "& .MuiChip-label": {
                    px: 0,
                    py: 0
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
            gridTemplateColumns: {
              xs: "repeat(1, minmax(0, 1fr))",
              sm: "repeat(2, minmax(0, 1fr))",
              lg: "repeat(4, minmax(0, 1fr))"
            }
          }}
        >
          {SEGMENT_DEFINITIONS.map(({ key, label }) => {
            const value = segments[key];
            return (
              <Box
                key={key}
                sx={(theme) => {
                  const main = theme.palette.error.main;
                  const light = theme.palette.error.light;
                  const surface = theme.palette.background.paper;
                  const text =
                    theme.palette.error[
                      theme.palette.mode === "dark" ? "light" : "dark"
                    ] ?? main;
                  return {
                    background: `linear-gradient(160deg, ${alpha(
                      surface,
                      0.9
                    )} 0%, ${alpha(light, 0.6)} 60%, ${alpha(main, 0.6)} 100%)`,
                    borderRadius: 4,
                    border: `1px solid ${alpha(theme.palette.common.white, 0.7)}`,
                    boxShadow: `0 20px 40px ${alpha(main, 0.35)}`,
                    px: 3,
                    py: 2,
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
                    mb: 1
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
