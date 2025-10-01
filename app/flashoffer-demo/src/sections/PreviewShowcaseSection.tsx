import Grid from "@mui/material/Grid";
import Box from "@mui/material/Box";
import Typography from "@mui/material/Typography";
import { PreviewCard, Section } from "flashoffer-react";
import { PREVIEW_CARDS } from "./content";

function toTrackId(value: string): string {
  return value
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "")
    .replace(/-{2,}/g, "-");
}

export interface PreviewShowcaseSectionProps {
  previewMeta: string;
}

export function PreviewShowcaseSection({ previewMeta }: PreviewShowcaseSectionProps) {
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
        align="left"
      >
        <Typography color="text.secondary">
          Drop PreviewCard components into grid layouts to tease content, share
          regional updates, or pair with testimonials.
        </Typography>
        <Grid container spacing={3} sx={{ width: "100%" }}>
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
      </Section>
    </Box>
  );
}

export { PREVIEW_CARDS };
