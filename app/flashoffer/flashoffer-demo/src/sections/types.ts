/*
 * Copyright (c) Flashoffer Developers
 * Released under the MIT license.
 */

export type ThemePreset =
  | "ocean"
  | "sunset"
  | "midnight"
  | "sunriseGlow"
  | "midnightPulse"
  | "oceanBreeze"
  | "forestCanopy"
  | "monochromeFocus"
  | "spaciousLight"
  | "spaciousDark";
export type HeroAlignment = "left" | "center";

export const THEME_PRESET_ORDER: readonly ThemePreset[] = [
  "ocean",
  "sunset",
  "midnight",
  "sunriseGlow",
  "midnightPulse",
  "oceanBreeze",
  "forestCanopy",
  "monochromeFocus",
  "spaciousLight",
  "spaciousDark"
];

export const THEME_PRESET_LABELS: Record<ThemePreset, string> = {
  ocean: "Ocean (default)",
  sunset: "Sunset",
  midnight: "Midnight",
  sunriseGlow: "Sunrise glow",
  midnightPulse: "Midnight pulse",
  oceanBreeze: "Ocean breeze",
  forestCanopy: "Forest canopy",
  monochromeFocus: "Monochrome focus",
  spaciousLight: "Spacious typography (light)",
  spaciousDark: "Spacious typography (dark)"
};
