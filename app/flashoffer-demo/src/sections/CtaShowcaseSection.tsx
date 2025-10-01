import Box from "@mui/material/Box";
import Stack from "@mui/material/Stack";
import { OutlineCtaButton, PrimaryCtaButton, Section } from "flashoffer-react";

export function CtaShowcaseSection() {
  const trackMeta = JSON.stringify({ variants: 2 });

  return (
    <Box
      component="section"
      data-track-id="cta-variations"
      data-track-label="CTA showcase"
      data-track-meta={trackMeta}
    >
      <Section
        align="center"
        eyebrow="CALL TO ACTION"
        title="Pre-built CTA variations"
        description="Mix and match primary and secondary button styles to suit product launches, onboarding nudges, or seasonal promotions."
        paragraphs={[]}
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
  );
}
