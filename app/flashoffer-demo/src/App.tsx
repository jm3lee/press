import Box from "@mui/material/Box";
import Container from "@mui/material/Container";
import Stack from "@mui/material/Stack";
import type { PaletteMode, ThemeOptions } from "@mui/material/styles";
import { Suspense, lazy, startTransition, useMemo, useState } from "react";
import { FlashofferThemeProvider } from "flashoffer-react";
import type { FlashofferThemePreset } from "flashoffer-react";
import type { HeroAlignment, ThemePreset } from "./sections/types";
import { THEME_PRESET_LABELS } from "./sections/types";

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

const QuizShowcaseSection = lazy(async () => ({
  default: (await import("./sections/QuizShowcaseSection")).QuizShowcaseSection
}));

const FooterSection = lazy(async () => ({
  default: (await import("./sections/FooterSection")).FooterSection
}));

interface ThemePresetConfig {
  preset?: FlashofferThemePreset;
  colorMode?: PaletteMode;
  themeOptions?: ThemeOptions;
}

const themePresets: Record<ThemePreset, ThemePresetConfig> = {
  ocean: {},
  sunset: {
    themeOptions: {
      palette: {
        primary: { main: "#f97316", contrastText: "#1f2937" },
        secondary: { main: "#facc15", contrastText: "#0f172a" }
      }
    }
  },
  midnight: {
    themeOptions: {
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
  },
  spaciousLight: {
    preset: "spaciousTypography",
    colorMode: "light"
  },
  spaciousDark: {
    preset: "spaciousTypography",
    colorMode: "dark"
  }
};

const PREVIEW_CARD_COUNT = 3;
const OVERVIEW_SUPPORTING_PARAGRAPHS = 3;

const heroMedia = (
  <svg
    viewBox="0 0 720 480"
    role="img"
    aria-labelledby="hero-illustration-title hero-illustration-desc"
    style={{
      width: "100%",
      borderRadius: "24px",
      boxShadow: "0 24px 60px rgba(15, 23, 42, 0.12)"
    }}
  >
    <title id="hero-illustration-title">
      Marketing dashboard illustration
    </title>
    <desc id="hero-illustration-desc">
      A stylized dashboard with charts representing campaign performance.
    </desc>
    <defs>
      <linearGradient id="heroGradient" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" stopColor="#1d4ed8" stopOpacity="0.16" />
        <stop offset="100%" stopColor="#60a5fa" stopOpacity="0.32" />
      </linearGradient>
      <linearGradient id="heroBar" x1="0%" y1="100%" x2="0%" y2="0%">
        <stop offset="0%" stopColor="#2563eb" />
        <stop offset="100%" stopColor="#a855f7" />
      </linearGradient>
    </defs>
    <rect fill="#f8fafc" x="0" y="0" width="720" height="480" rx="32" />
    <rect
      x="36"
      y="48"
      width="648"
      height="384"
      rx="24"
      fill="url(#heroGradient)"
    />
    <g transform="translate(96 120)">
      <rect
        x="0"
        y="0"
        width="528"
        height="72"
        rx="12"
        fill="#0f172a"
        opacity="0.92"
      />
      <circle cx="48" cy="36" r="18" fill="#38bdf8" opacity="0.85" />
      <rect x="90" y="24" width="96" height="12" rx="6" fill="#cbd5f5" />
      <rect x="90" y="48" width="168" height="8" rx="4" fill="#a5b4fc" />
      <rect x="282" y="24" width="72" height="12" rx="6" fill="#cbd5f5" />
      <rect x="282" y="48" width="102" height="8" rx="4" fill="#a5b4fc" />
      <rect x="402" y="24" width="66" height="12" rx="6" fill="#cbd5f5" />
      <rect x="402" y="48" width="84" height="8" rx="4" fill="#a5b4fc" />
    </g>
    <g transform="translate(126 228)">
      <rect
        x="0"
        y="0"
        width="468"
        height="180"
        rx="20"
        fill="#0f172a"
        opacity="0.88"
      />
      <polyline
        points="48,132 126,72 204,108 282,60 360,96 420,24"
        fill="none"
        stroke="#facc15"
        strokeWidth="8"
        strokeLinecap="round"
        strokeLinejoin="round"
        opacity="0.9"
      />
      <rect x="60" y="36" width="48" height="84" rx="8" fill="url(#heroBar)" />
      <rect x="144" y="60" width="48" height="60" rx="8" fill="url(#heroBar)" />
      <rect x="228" y="36" width="48" height="84" rx="8" fill="url(#heroBar)" />
      <rect x="312" y="24" width="48" height="96" rx="8" fill="url(#heroBar)" />
      <rect x="396" y="48" width="48" height="72" rx="8" fill="url(#heroBar)" />
      <rect x="36" y="144" width="96" height="12" rx="6" fill="#38bdf8" />
      <rect x="150" y="144" width="96" height="12" rx="6" fill="#38bdf8" />
      <rect x="264" y="144" width="96" height="12" rx="6" fill="#38bdf8" />
    </g>
    <rect
      x="96"
      y="348"
      width="528"
      height="66"
      rx="18"
      fill="#0f172a"
      opacity="0.92"
    />
    <rect x="132" y="372" width="162" height="18" rx="9" fill="#38bdf8" />
    <rect x="318" y="372" width="108" height="18" rx="9" fill="#6366f1" />
    <rect x="450" y="372" width="102" height="18" rx="9" fill="#a855f7" />
  </svg>
);

export default function App() {
  const [palettePreset, setPalettePreset] = useState<ThemePreset>("ocean");
  const [heroAlignment, setHeroAlignment] = useState<HeroAlignment>("center");

  const themeConfig = useMemo(
    () => themePresets[palettePreset],
    [palettePreset]
  );

  const controlsMeta = useMemo(
    () =>
      JSON.stringify({
        palette: palettePreset,
        presetLabel: THEME_PRESET_LABELS[palettePreset],
        heroAlignment
      }),
    [heroAlignment, palettePreset]
  );

  const heroMeta = useMemo(
    () =>
      JSON.stringify({
        alignment: heroAlignment,
        palette: palettePreset,
        presetLabel: THEME_PRESET_LABELS[palettePreset]
      }),
    [heroAlignment, palettePreset]
  );

  const previewMeta = useMemo(
    () => JSON.stringify({ cards: PREVIEW_CARD_COUNT }),
    []
  );

  const overviewMeta = useMemo(
    () => JSON.stringify({ paragraphs: OVERVIEW_SUPPORTING_PARAGRAPHS }),
    []
  );

  const pageMeta = useMemo(
    () =>
      JSON.stringify({
        palette: palettePreset,
        presetLabel: THEME_PRESET_LABELS[palettePreset]
      }),
    [palettePreset]
  );

  return (
    <FlashofferThemeProvider
      themeOptions={themeConfig.themeOptions}
      preset={themeConfig.preset}
      colorMode={themeConfig.colorMode}
    >
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
              <QuizShowcaseSection />
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
