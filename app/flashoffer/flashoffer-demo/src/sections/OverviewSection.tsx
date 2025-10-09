/*
 * Copyright (c) Flashoffer Developers
 * Released under the MIT license.
 */

import Box from "@mui/material/Box";
import Typography from "@mui/material/Typography";
import { Section } from "flashoffer-react";

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
      </Section>
    </Box>
  );
}
