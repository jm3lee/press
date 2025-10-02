import Box from "@mui/material/Box";
import { HeroBanner, Section } from "flashoffer-react";
import type { ReactNode } from "react";
import type { HeroAlignment, ThemePreset } from "./types";

type HeroGradientVariable =
  | "--flashoffer-hero-gradient-start"
  | "--flashoffer-hero-gradient-stop";

const HERO_GRADIENT_OVERRIDES: Record<
  ThemePreset,
  Partial<Record<HeroGradientVariable, string>>
> = {
  ocean: {
    "--flashoffer-hero-gradient-start": "rgba(37, 99, 235, 0.08)",
    "--flashoffer-hero-gradient-stop": "rgba(59, 130, 246, 0.16)"
  },
  sunset: {
    "--flashoffer-hero-gradient-start": "rgba(249, 115, 22, 0.18)",
    "--flashoffer-hero-gradient-stop": "rgba(234, 88, 12, 0.26)"
  },
  midnight: {
    "--flashoffer-hero-gradient-start": "#1e293b",
    "--flashoffer-hero-gradient-stop": "#0f172a"
  },
  spaciousLight: {
    "--flashoffer-hero-gradient-start": "rgba(29, 78, 216, 0.14)",
    "--flashoffer-hero-gradient-stop": "rgba(219, 39, 119, 0.18)"
  },
  spaciousDark: {
    "--flashoffer-hero-gradient-start": "rgba(96, 165, 250, 0.28)",
    "--flashoffer-hero-gradient-stop": "rgba(15, 23, 42, 0.85)"
  }
};

export interface HeroShowcaseSectionProps {
  heroAlignment: HeroAlignment;
  heroMeta: string;
  heroMedia: ReactNode;
  palettePreset: ThemePreset;
}

export function HeroShowcaseSection({
  heroAlignment,
  heroMeta,
  heroMedia,
  palettePreset
}: HeroShowcaseSectionProps) {
  const heroGradientOverrides = HERO_GRADIENT_OVERRIDES[palettePreset];

  return (
    <Box
      data-track-id="hero-banner"
      data-track-label="Hero banner"
      data-track-meta={heroMeta}
      data-testid="hero-banner-wrapper"
      sx={heroGradientOverrides}
    >
      <HeroBanner
        align={heroAlignment}
        title="Launch coordinated offers in minutes."
        subtitle="Flashoffer ships reusable hero, CTA, and preview components so teams can publish landing experiments without bespoke design cycles."
        primaryCta={{
          label: "Explore Flashoffer components",
          href: "https://example.com/flashoffer",
          target: "_blank",
          rel: "noreferrer",
          "data-track-id": "hero-primary-cta",
          "data-track-label": "Hero primary CTA",
          "data-track-meta": heroMeta
        }}
        secondaryCta={{
          label: "Contact support",
          href: "mailto:support@example.com",
          "data-track-id": "hero-secondary-cta",
          "data-track-label": "Hero secondary CTA",
          "data-track-meta": heroMeta
        }}
        media={heroMedia}
      />
    </Box>
  );
}
