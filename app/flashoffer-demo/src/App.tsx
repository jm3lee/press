import Box from "@mui/material/Box";
import Container from "@mui/material/Container";
import Stack from "@mui/material/Stack";
import type { ThemeOptions } from "@mui/material/styles";
import { Suspense, lazy, startTransition, useMemo, useState } from "react";
import { FlashofferThemeProvider } from "flashoffer-react";
import type { HeroAlignment, ThemePreset } from "./sections/types";
import { OVERVIEW_PARAGRAPHS, PREVIEW_CARDS } from "./sections/content";

const CustomizationControlsSection = lazy(async () => ({
  default: (await import("./sections/CustomizationControlsSection")).CustomizationControlsSection
}));

const HeroShowcaseSection = lazy(async () => ({
  default: (await import("./sections/HeroShowcaseSection")).HeroShowcaseSection
}));

const OverviewSection = lazy(async () => ({
  default: (await import("./sections/OverviewSection")).OverviewSection
}));

const CtaShowcaseSection = lazy(async () => ({
  default: (await import("./sections/CtaShowcaseSection")).CtaShowcaseSection
}));

const PreviewShowcaseSection = lazy(async () => ({
  default: (await import("./sections/PreviewShowcaseSection")).PreviewShowcaseSection
}));

const FigureSpotlightSection = lazy(async () => ({
  default: (await import("./sections/FigureSpotlightSection")).FigureSpotlightSection
}));

const FooterSection = lazy(async () => ({
  default: (await import("./sections/FooterSection")).FooterSection
}));

const themePresets: Record<ThemePreset, ThemeOptions | undefined> = {
  ocean: undefined,
  sunset: {
    palette: {
      primary: { main: "#f97316", contrastText: "#1f2937" },
      secondary: { main: "#facc15", contrastText: "#0f172a" }
    }
  },
  midnight: {
    palette: {
      primary: { main: "#6366f1", contrastText: "#f8fafc" },
      secondary: { main: "#38bdf8", contrastText: "#0f172a" },
      background: { default: "#0f172a", paper: "#111827" },
      text: { primary: "#f8fafc", secondary: "#cbd5f5" }
    },
    components: {
      MuiCard: {
        styleOverrides: {
          root: {
            backgroundColor: "rgba(15, 23, 42, 0.75)",
            border: "1px solid rgba(148, 163, 184, 0.2)"
          }
        }
      }
    }
  }
};

const heroMedia = (
  <img
    src="https://images.unsplash.com/photo-1553877522-43269d4ea984?auto=format&fit=crop&w=720&q=80"
    alt="Marketing dashboard showing campaign metrics"
    style={{ width: "100%", borderRadius: "24px", boxShadow: "0 24px 60px rgba(15, 23, 42, 0.12)" }}
  />
);

export default function App() {
  const [palettePreset, setPalettePreset] = useState<ThemePreset>("ocean");
  const [heroAlignment, setHeroAlignment] = useState<HeroAlignment>("center");

  const themeOptions = useMemo(
    () => themePresets[palettePreset],
    [palettePreset]
  );

  const controlsMeta = useMemo(
    () => JSON.stringify({ palette: palettePreset, heroAlignment }),
    [heroAlignment, palettePreset]
  );

  const heroMeta = useMemo(
    () => JSON.stringify({ alignment: heroAlignment, palette: palettePreset }),
    [heroAlignment, palettePreset]
  );

  const previewMeta = useMemo(
    () => JSON.stringify({ cards: PREVIEW_CARDS.length }),
    []
  );

  const overviewMeta = useMemo(
    () => JSON.stringify({ paragraphs: OVERVIEW_PARAGRAPHS.length }),
    []
  );

  const pageMeta = useMemo(
    () => JSON.stringify({ palette: palettePreset }),
    [palettePreset]
  );

  return (
    <FlashofferThemeProvider themeOptions={themeOptions}>
      <Box
        sx={{
          backgroundColor: "var(--flashoffer-color-background)",
          color: "var(--flashoffer-color-text-primary)",
          minHeight: "100vh"
        }}
        data-track-id="flashoffer-demo-surface"
        data-track-label="Flashoffer demo surface"
        data-track-meta={pageMeta}
      >
        <Container maxWidth="lg" sx={{ py: { xs: 6, md: 10 } }}>
          <Stack spacing={10}>
            <Suspense fallback={null}>
              <CustomizationControlsSection
                palettePreset={palettePreset}
                onPalettePresetChange={(nextPreset) => {
                  startTransition(() => {
                    setPalettePreset(nextPreset);
                  });
                }}
                heroAlignment={heroAlignment}
                onHeroAlignmentChange={(nextAlignment) => {
                  startTransition(() => {
                    setHeroAlignment(nextAlignment);
                  });
                }}
                controlsMeta={controlsMeta}
              />
            </Suspense>
            <Suspense fallback={null}>
              <HeroShowcaseSection
                heroAlignment={heroAlignment}
                heroMeta={heroMeta}
                heroMedia={heroMedia}
                palettePreset={palettePreset}
              />
            </Suspense>
            <Suspense fallback={null}>
              <OverviewSection overviewMeta={overviewMeta} />
            </Suspense>
            <Suspense fallback={null}>
              <CtaShowcaseSection />
            </Suspense>
            <Suspense fallback={null}>
              <PreviewShowcaseSection previewMeta={previewMeta} />
            </Suspense>
            <Suspense fallback={null}>
              <FigureSpotlightSection />
            </Suspense>
            <Suspense fallback={null}>
              <FooterSection />
            </Suspense>
          </Stack>
        </Container>
      </Box>
    </FlashofferThemeProvider>
  );
}
