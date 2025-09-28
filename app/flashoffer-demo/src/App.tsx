import Box from "@mui/material/Box";
import Container from "@mui/material/Container";
import Divider from "@mui/material/Divider";
import Grid from "@mui/material/Grid";
import Paper from "@mui/material/Paper";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";
import type { ThemeOptions } from "@mui/material/styles";
import { useMemo, useState } from "react";
import {
  FlashofferThemeProvider,
  Footer,
  HeroBanner,
  OutlineCtaButton,
  PreviewCard,
  PrimaryCtaButton,
  SectionHeader
} from "flashoffer-react";

type ThemePreset = "ocean" | "sunset" | "midnight";

type HeroAlignment = "left" | "center";

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

const previewCards = [
  {
    title: "Personalized launch offers",
    description:
      "Highlight tailored bundles that can be activated in a few clicks. Swap copy and imagery to match your latest campaign without rebuilding layouts.",
    media: (
      <img
        src="https://images.unsplash.com/photo-1522202176988-66273c2fd55f?auto=format&fit=crop&w=480&q=80"
        alt="Two teammates collaborating over a laptop"
        style={{ width: "100%", borderRadius: "16px" }}
      />
    )
  },
  {
    title: "Lifecycle automation",
    description:
      "Pair Flashoffer pages with your automation stack to trigger discounts or add-ons in response to usage signals.",
    media: (
      <img
        src="https://images.unsplash.com/photo-1527430253228-e93688616381?auto=format&fit=crop&w=480&q=80"
        alt="Abstract dashboard charts"
        style={{ width: "100%", borderRadius: "16px" }}
      />
    ),
    secondaryCta: {
      label: "View playbook",
      href: "https://example.com/playbook"
    }
  },
  {
    title: "Localized experiences",
    description:
      "Clone the same structure across regions while tuning content, pricing, and compliance disclosures in minutes.",
    media: (
      <img
        src="https://images.unsplash.com/photo-1521292270410-a8c6788e40cc?auto=format&fit=crop&w=480&q=80"
        alt="Color swatches and typography samples"
        style={{ width: "100%", borderRadius: "16px" }}
      />
    ),
    primaryCta: {
      label: "See localization tips",
      href: "https://example.com/localization"
    }
  }
];

const footerLinks = [
  { label: "Docs", href: "https://example.com/docs" },
  { label: "Status", href: "https://status.example.com" },
  { label: "Support", href: "mailto:support@example.com" }
];

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

  return (
    <FlashofferThemeProvider themeOptions={themeOptions}>
      <Box
        sx={{
          backgroundColor: "var(--flashoffer-color-background)",
          color: "var(--flashoffer-color-text-primary)",
          minHeight: "100vh"
        }}
      >
        <Container maxWidth="lg" sx={{ py: { xs: 6, md: 10 } }}>
          <Stack spacing={10}>
            <Paper component="section" elevation={0} sx={{ p: { xs: 3, md: 4 } }}>
              <Stack spacing={3}>
                <Typography variant="h6" component="h2">
                  Customize the showcase
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Switch palettes or tweak hero alignment to preview how Flashoffer primitives adapt.
                </Typography>
                <Divider flexItem sx={{ borderColor: "divider" }} />
                <Stack
                  direction={{ xs: "column", sm: "row" }}
                  spacing={3}
                  divider={<Divider orientation="vertical" flexItem sx={{ display: { xs: "none", sm: "block" } }} />}
                  useFlexGap
                >
                  <Box>
                    <Typography variant="overline" color="text.secondary">
                      Palette
                    </Typography>
                    <select
                      value={palettePreset}
                      onChange={(event) =>
                        setPalettePreset(event.target.value as ThemePreset)
                      }
                      aria-label="Select theme palette"
                      style={{
                        marginTop: "0.5rem",
                        padding: "0.5rem 0.75rem",
                        borderRadius: "0.75rem",
                        border: "1px solid rgba(148, 163, 184, 0.4)",
                        backgroundColor: "var(--flashoffer-color-surface)",
                        color: "var(--flashoffer-color-text-primary)",
                        fontSize: "0.95rem"
                      }}
                    >
                      <option value="ocean">Ocean (default)</option>
                      <option value="sunset">Sunset</option>
                      <option value="midnight">Midnight</option>
                    </select>
                  </Box>
                  <Box>
                    <Typography variant="overline" color="text.secondary">
                      Hero alignment
                    </Typography>
                    <select
                      value={heroAlignment}
                      onChange={(event) =>
                        setHeroAlignment(event.target.value as HeroAlignment)
                      }
                      aria-label="Select hero alignment"
                      style={{
                        marginTop: "0.5rem",
                        padding: "0.5rem 0.75rem",
                        borderRadius: "0.75rem",
                        border: "1px solid rgba(148, 163, 184, 0.4)",
                        backgroundColor: "var(--flashoffer-color-surface)",
                        color: "var(--flashoffer-color-text-primary)",
                        fontSize: "0.95rem"
                      }}
                    >
                      <option value="center">Centered</option>
                      <option value="left">Left aligned</option>
                    </select>
                  </Box>
                </Stack>
              </Stack>
            </Paper>

            <HeroBanner
              align={heroAlignment}
              title="Launch coordinated offers in minutes."
              subtitle="Flashoffer ships reusable hero, CTA, and preview components so teams can publish landing experiments without bespoke design cycles."
              primaryCta={{
                label: "Explore Flashoffer components",
                href: "https://example.com/flashoffer",
                target: "_blank",
                rel: "noreferrer"
              }}
              secondaryCta={{
                label: "Contact support",
                href: "mailto:support@example.com"
              }}
              media={heroMedia}
            />

            <Box component="section">
              <SectionHeader
                eyebrow="CALL TO ACTION"
                title="Pre-built CTA variations"
                description="Mix and match primary and secondary button styles to suit product launches, onboarding nudges, or seasonal promotions."
              />
              <Stack
                direction={{ xs: "column", sm: "row" }}
                spacing={2}
                sx={{ mt: 3 }}
                alignItems="center"
                justifyContent="center"
              >
                <PrimaryCtaButton href="https://example.com/flashoffer">
                  Explore Flashoffer components
                </PrimaryCtaButton>
                <OutlineCtaButton href="mailto:support@example.com">
                  Contact support
                </OutlineCtaButton>
              </Stack>
            </Box>

            <Box component="section">
              <SectionHeader
                eyebrow="SHOWCASE"
                title="Modular previews for any campaign"
                description="Drop PreviewCard components into grid layouts to tease content, share regional updates, or pair with testimonials."
                align="left"
              />
              <Grid container spacing={3} sx={{ mt: 3 }}>
                {previewCards.map((card) => (
                  <Grid key={card.title} size={{ xs: 12, md: 4 }}>
                    <PreviewCard {...card} />
                  </Grid>
                ))}
              </Grid>
            </Box>

            <Footer
              links={footerLinks}
              copyrightText="© 2025 Flashoffer. All rights reserved."
            />
          </Stack>
        </Container>
      </Box>
    </FlashofferThemeProvider>
  );
}
