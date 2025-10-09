export type ThemePreset =
  | "ocean"
  | "sunset"
  | "midnight"
  | "spaciousLight"
  | "spaciousDark";
export type HeroAlignment = "left" | "center";

export const THEME_PRESET_ORDER: readonly ThemePreset[] = [
  "ocean",
  "sunset",
  "midnight",
  "spaciousLight",
  "spaciousDark"
];

export const THEME_PRESET_LABELS: Record<ThemePreset, string> = {
  ocean: "Ocean (default)",
  sunset: "Sunset",
  midnight: "Midnight",
  spaciousLight: "Spacious typography (light)",
  spaciousDark: "Spacious typography (dark)"
};
