import Box from "@mui/material/Box";
import { Section } from "flashoffer-react";

const OVERVIEW_PARAGRAPHS = [
  "Use the Section component to pair launch announcements, feature guides, or changelog summaries with consistent typography.",
  "Each paragraph is wrapped in semantic markup and inherits spacing from the Flashoffer design tokens, so marketing teams can focus on messaging."
];

export function OverviewSection() {
  const overviewMeta = JSON.stringify({ paragraphs: OVERVIEW_PARAGRAPHS.length });

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
