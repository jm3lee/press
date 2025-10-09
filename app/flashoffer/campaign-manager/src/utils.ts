/*
 * Copyright (c) Flashoffer Developers
 * Released under the MIT license.
 */

/**
 * Converts a UTC ISO timestamp into the value expected by datetime-local inputs.
 *
 * @param iso - Timestamp expressed in ISO 8601 format or `null`/`undefined`.
 * @returns Local datetime string truncated to minute precision or an empty
 * string when the input cannot be parsed.
 */
export function toLocalDateTimeInputValue(iso: string | null | undefined): string {
  if (!iso) {
    return "";
  }
  const parsed = new Date(iso);
  if (Number.isNaN(parsed.getTime())) {
    return "";
  }
  const tzOffsetMinutes = parsed.getTimezoneOffset();
  const adjusted = new Date(parsed.getTime() - tzOffsetMinutes * 60_000);
  return adjusted.toISOString().slice(0, 16);
}

/**
 * Normalizes a browser datetime-local value to a UTC ISO timestamp.
 *
 * @param input - Local datetime string captured from a user input.
 * @returns ISO 8601 timestamp in UTC or `null` when parsing fails.
 */
export function fromLocalInputToUtc(input: string): string | null {
  if (!input) {
    return null;
  }
  const parsed = new Date(input);
  if (Number.isNaN(parsed.getTime())) {
    return null;
  }
  return new Date(
    Date.UTC(
      parsed.getFullYear(),
      parsed.getMonth(),
      parsed.getDate(),
      parsed.getHours(),
      parsed.getMinutes(),
      parsed.getSeconds(),
      parsed.getMilliseconds(),
    ),
  ).toISOString();
}

/**
 * Converts an ISO timestamp into a localized display string.
 *
 * @param iso - Timestamp expressed in ISO 8601 format.
 * @returns Localized date/time string or `-` when parsing fails.
 */
export function formatTimestampForDisplay(iso: string): string {
  const parsed = new Date(iso);
  if (Number.isNaN(parsed.getTime())) {
    return "-";
  }
  return parsed.toLocaleString();
}
