import Box from "@mui/material/Box";
import Typography from "@mui/material/Typography";
import { Section } from "flashoffer-react";
import { OVERVIEW_PARAGRAPHS } from "./content";

export interface OverviewSectionProps {
  overviewMeta: string;
}

export function OverviewSection({ overviewMeta }: OverviewSectionProps) {
  return (
    <Box
      data-track-id="overview-section"
      data-track-label="Section overview"
      data-track-meta={overviewMeta}
    >
      <Section
        align="center"
        eyebrow="OVERVIEW"
        title="Narrate launches with reusable sections"
      >
        <Typography color="text.secondary">
          Combine headlines and supporting copy while staying independent from
          opaque review cycles.
        </Typography>
        {OVERVIEW_PARAGRAPHS.map((paragraph) => (
          <Typography key={paragraph} color="text.secondary">
            {paragraph}
          </Typography>
        ))}
      </Section>
    </Box>
  );
}

export { OVERVIEW_PARAGRAPHS };
