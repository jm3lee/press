/*
 * Copyright (c) Flashoffer Developers
 * Released under the MIT license.
 */

import type { QuizConfettiPreset } from "flashoffer-react";

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

export type QuizCelebrationSelection = "off" | QuizConfettiPreset;

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

export const QUIZ_CELEBRATION_OPTIONS: readonly QuizCelebrationSelection[] = [
  "off",
  "classic",
  "streamers",
  "burst"
];

export const QUIZ_CELEBRATION_LABELS: Record<
  QuizCelebrationSelection,
  string
> = {
  off: "None",
  classic: "Classic confetti",
  streamers: "Streamer launch",
  burst: "Grand finale"
};
