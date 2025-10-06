import Box from "@mui/material/Box";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";
import { PrimaryCtaButton, Section } from "flashoffer-react";

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
        <Typography color="text.secondary">
          Flashoffer-react emerged after repeated takedowns of fine art on
          mainstream networks. We respect law and order, yet opaque filters
          squeeze the livelihoods of artists.
        </Typography>
        <Typography color="text.secondary">
          We understand the tension between shielding minors from explicit
          material and giving artists room to breathe. The framework offers
          reusable, policy-free layouts so you can advertise art on your own
          terms.
        </Typography>
        <Typography color="text.secondary">
          Compose campaigns and deploy them to any Docker-ready cloud in
          minutes. While any tool can be misused, we trust creators to stand by
          one another more often than not.
        </Typography>
        <Stack
          direction={{ xs: "column", sm: "row" }}
          justifyContent="center"
          alignItems="center"
          spacing={2}
          sx={{ pt: { xs: 3, md: 4 } }}
        >
          <PrimaryCtaButton
            component="a"
            href="/multiple-choice"
            label="Try the multiple choice demo"
            data-track-id="overview-multiple-choice-link"
            data-track-label="Multiple choice demo link"
            data-track-meta={overviewMeta}
          />
        </Stack>
      </Section>
    </Box>
  );
}
