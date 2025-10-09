/*
 * Copyright (c) Flashoffer Developers
 * Released under the MIT license.
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

export function formatTimestampForDisplay(iso: string): string {
  const parsed = new Date(iso);
  if (Number.isNaN(parsed.getTime())) {
    return "-";
  }
  return parsed.toLocaleString();
}
