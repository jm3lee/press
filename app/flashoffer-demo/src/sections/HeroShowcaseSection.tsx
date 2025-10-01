import Box from "@mui/material/Box";
import { HeroBanner, Section } from "flashoffer-react";
import { useMemo } from "react";
import type { ReactNode } from "react";
import type { HeroAlignment, ThemePreset } from "./types";

export interface HeroShowcaseSectionProps {
  heroAlignment: HeroAlignment;
  heroMedia: ReactNode;
  palettePreset: ThemePreset;
}

export function HeroShowcaseSection({
  heroAlignment,
  heroMedia,
  palettePreset
}: HeroShowcaseSectionProps) {
  const heroMeta = useMemo(
    () => JSON.stringify({ alignment: heroAlignment, palette: palettePreset }),
    [heroAlignment, palettePreset]
  );

  return (
    <Box
      data-track-id="hero-banner"
      data-track-label="Hero banner"
      data-track-meta={heroMeta}
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
