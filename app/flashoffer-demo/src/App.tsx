import Box from "@mui/material/Box";
import Container from "@mui/material/Container";
import Stack from "@mui/material/Stack";
import type { ThemeOptions } from "@mui/material/styles";
import { FlashofferThemeProvider } from "flashoffer-react";
import type { ComponentType } from "react";
import {
  Suspense,
  lazy,
  startTransition,
  useMemo,
  useState
} from "react";
import type { CustomizationControlsSectionProps } from "./sections/CustomizationControlsSection";
import type { HeroAlignment, ThemePreset } from "./sections/types";

const CustomizationControlsSection = lazy(
  () =>
    import("./sections/CustomizationControlsSection").then((module) => ({
      default: module.CustomizationControlsSection
    })) as Promise<{
      default: ComponentType<CustomizationControlsSectionProps>;
    }>
);

const HeroShowcaseSection = lazy(() =>
  import("./sections/HeroShowcaseSection").then((module) => ({
    default: module.HeroShowcaseSection
  }))
);

const OverviewSection = lazy(() =>
  import("./sections/OverviewSection").then((module) => ({
    default: module.OverviewSection
  }))
);

const CtaShowcaseSection = lazy(() =>
  import("./sections/CtaShowcaseSection").then((module) => ({
    default: module.CtaShowcaseSection
  }))
);

const PreviewShowcaseSection = lazy(() =>
  import("./sections/PreviewShowcaseSection").then((module) => ({
    default: module.PreviewShowcaseSection
  }))
);

const FigureSpotlightSection = lazy(() =>
  import("./sections/FigureSpotlightSection").then((module) => ({
    default: module.FigureSpotlightSection
  }))
);

const FooterSection = lazy(() =>
  import("./sections/FooterSection").then((module) => ({
    default: module.FooterSection
  }))
);

function SectionPlaceholder({ label }: { label: string }) {
  return (
    <Box
      component="section"
      role="status"
      aria-live="polite"
      sx={{
        borderRadius: 3,
        border: "1px solid",
        borderColor: "divider",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        minHeight: 200,
        color: "text.secondary",
        typography: "body2"
      }}
    >
      Loading {label}…
    </Box>
  );
}

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
            <Suspense fallback={<SectionPlaceholder label="Customization controls" />}>
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
              />
            </Suspense>
            <Suspense fallback={<SectionPlaceholder label="Hero" />}>
              <HeroShowcaseSection
                heroAlignment={heroAlignment}
                heroMedia={heroMedia}
                palettePreset={palettePreset}
              />
            </Suspense>
            <Suspense fallback={<SectionPlaceholder label="Overview" />}>
              <OverviewSection />
            </Suspense>
            <Suspense fallback={<SectionPlaceholder label="CTA showcase" />}>
              <CtaShowcaseSection />
            </Suspense>
            <Suspense fallback={<SectionPlaceholder label="Preview cards" />}>
              <PreviewShowcaseSection />
            </Suspense>
            <Suspense fallback={<SectionPlaceholder label="Figure spotlight" />}>
              <FigureSpotlightSection />
            </Suspense>
            <Suspense fallback={<SectionPlaceholder label="Footer" />}>
              <FooterSection />
            </Suspense>
          </Stack>
        </Container>
      </Box>
    </FlashofferThemeProvider>
  );
}
