import Box from "@mui/material/Box";
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
        description="Combine headlines and supporting copy without rebuilding layouts from scratch."
        paragraphs={OVERVIEW_PARAGRAPHS}
      />
    </Box>
  );
}

export { OVERVIEW_PARAGRAPHS };
