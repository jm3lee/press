import Box from "@mui/material/Box";
import Container from "@mui/material/Container";
import Divider from "@mui/material/Divider";
import Grid from "@mui/material/Grid";
import Paper from "@mui/material/Paper";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";
import type { ThemeOptions } from "@mui/material/styles";
import { startTransition, useMemo, useState } from "react";
import {
  Figure,
  FlashofferThemeProvider,
  Footer,
  HeroBanner,
  OutlineCtaButton,
  PreviewCard,
  PrimaryCtaButton,
  Section,
  SectionHeader
} from "flashoffer-react";

type ThemePreset = "ocean" | "sunset" | "midnight";

type HeroAlignment = "left" | "center";

function toTrackId(value: string): string {
  return value
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "")
    .replace(/-{2,}/g, "-");
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

const overviewParagraphs = [
  "Use the Section component to pair launch announcements, feature guides, " +
    "or changelog summaries with consistent typography.",
  "Each paragraph is wrapped in semantic markup and inherits spacing from the " +
    "Flashoffer design tokens, so marketing teams can focus on messaging."
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

  const controlsMeta = useMemo(
    () => JSON.stringify({ palette: palettePreset, heroAlignment }),
    [heroAlignment, palettePreset]
  );

  const heroMeta = useMemo(
    () => JSON.stringify({ alignment: heroAlignment, palette: palettePreset }),
    [heroAlignment, palettePreset]
  );

  const previewMeta = useMemo(
    () => JSON.stringify({ cards: previewCards.length }),
    []
  );

  const figureMeta = useMemo(
    () => JSON.stringify({ orientation: "landscape" }),
    []
  );

  const overviewMeta = useMemo(
    () => JSON.stringify({ paragraphs: overviewParagraphs.length }),
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
            <Paper
              component="section"
              elevation={0}
              sx={{ p: { xs: 3, md: 4 } }}
              data-track-id="customization-panel"
              data-track-label="Customization controls"
              data-track-meta={controlsMeta}
            >
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
                      onChange={(event) => {
                        const nextPreset = event.target.value as ThemePreset;
                        startTransition(() => {
                          setPalettePreset(nextPreset);
                        });
                      }}
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
                      data-track-id="palette-selector"
                      data-track-label="Palette selector"
                      data-track-meta={JSON.stringify({ palette: palettePreset })}
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
                      onChange={(event) => {
                        const nextAlignment =
                          event.target.value as HeroAlignment;
                        startTransition(() => {
                          setHeroAlignment(nextAlignment);
                        });
                      }}
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
                      data-track-id="hero-alignment"
                      data-track-label="Hero alignment selector"
                      data-track-meta={JSON.stringify({ alignment: heroAlignment })}
                    >
                      <option value="center">Centered</option>
                      <option value="left">Left aligned</option>
                    </select>
                  </Box>
                </Stack>
              </Stack>
            </Paper>

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

            <Box
              data-track-id="overview-section"
              data-track-label="Section overview"
              data-track-meta={overviewMeta}
            >
              <Section
                align="center"
                eyebrow="OVERVIEW"
                title="Narrate launches with reusable sections"
                description="Combine headlines and supporting copy without rebuilding layouts from scratch."
                paragraphs={overviewParagraphs}
              />
            </Box>

            <Box
              component="section"
              data-track-id="cta-variations"
              data-track-label="CTA showcase"
              data-track-meta={JSON.stringify({ variants: 2 })}
            >
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
                <PrimaryCtaButton
                  href="https://example.com/flashoffer"
                  data-track-id="cta-primary"
                  data-track-label="Primary CTA"
                  data-track-meta={JSON.stringify({ location: "cta-showcase" })}
                >
                  Explore Flashoffer components
                </PrimaryCtaButton>
                <OutlineCtaButton
                  href="mailto:support@example.com"
                  data-track-id="cta-secondary"
                  data-track-label="Secondary CTA"
                  data-track-meta={JSON.stringify({ location: "cta-showcase" })}
                >
                  Contact support
                </OutlineCtaButton>
              </Stack>
            </Box>

            <Box
              component="section"
              data-track-id="preview-section"
              data-track-label="Preview cards"
              data-track-meta={previewMeta}
            >
              <SectionHeader
                eyebrow="SHOWCASE"
                title="Modular previews for any campaign"
                description="Drop PreviewCard components into grid layouts to tease content, share regional updates, or pair with testimonials."
                align="left"
              />
              <Grid container spacing={3} sx={{ mt: 3 }}>
                {previewCards.map((card, index) => {
                  const label = String(card.title);
                  const cardTrackId = `preview-card-${
                    toTrackId(label) || index + 1
                  }`;
                  return (
                    <Grid
                      key={card.title}
                      size={{ xs: 12, md: 4 }}
                      data-track-id={cardTrackId}
                      data-track-label={label}
                      data-track-meta={JSON.stringify({ index, title: label })}
                    >
                      <PreviewCard {...card} />
                    </Grid>
                  );
                })}
              </Grid>
            </Box>

            <Box
              component="section"
              data-track-id="figure-section"
              data-track-label="Figure component"
              data-track-meta={figureMeta}
            >
              <SectionHeader
                eyebrow="MEDIA"
                title="Pair imagery with supporting context"
                description="Use Figure to keep visuals responsive across breakpoints while pairing them with captions or attributions."
              />
              <Box
                sx={{
                  mt: 3,
                  display: "flex",
                  justifyContent: "center"
                }}
              >
                <Figure
                  src="https://images.unsplash.com/photo-1489515217757-5fd1be406fef?auto=format&fit=crop&w=960&q=80"
                  alt="Product marketer reviewing launch campaign timelines"
                  caption="Launch dashboards stay legible on any device thanks to responsive scaling."
                  sx={{
                    maxWidth: 560
                  }}
                />
              </Box>
            </Box>

            <Box
              data-track-id="footer"
              data-track-label="Footer"
              data-track-meta={JSON.stringify({ links: footerLinks.length })}
            >
              <Footer
                links={footerLinks}
                copyrightText="© 2025 Flashoffer. All rights reserved."
              />
            </Box>
          </Stack>
        </Container>
      </Box>
    </FlashofferThemeProvider>
  );
}
