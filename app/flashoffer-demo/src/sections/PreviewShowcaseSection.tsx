import Grid from "@mui/material/Grid";
import Box from "@mui/material/Box";
import { PreviewCard, Section } from "flashoffer-react";

const PREVIEW_CARDS = [
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

function toTrackId(value: string): string {
  return value
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "")
    .replace(/-{2,}/g, "-");
}

export function PreviewShowcaseSection() {
  const previewMeta = JSON.stringify({ cards: PREVIEW_CARDS.length });

  return (
    <Box
      component="section"
      data-track-id="preview-section"
      data-track-label="Preview cards"
      data-track-meta={previewMeta}
    >
      <Section
        eyebrow="SHOWCASE"
        title="Modular previews for any campaign"
        description="Drop PreviewCard components into grid layouts to tease content, share regional updates, or pair with testimonials."
        align="left"
        paragraphs={[]}
      />
      <Grid container spacing={3} sx={{ mt: 3 }}>
        {PREVIEW_CARDS.map((card, index) => {
          const label = String(card.title);
          const cardTrackId = `preview-card-${toTrackId(label) || index + 1}`;
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
  );
}

export { PREVIEW_CARDS };
