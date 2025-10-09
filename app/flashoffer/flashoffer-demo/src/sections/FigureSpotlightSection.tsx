/*
 * Copyright (c) Flashoffer Developers
 * Released under the MIT license.
 */

import Box from "@mui/material/Box";
import Typography from "@mui/material/Typography";
import { Figure, Section } from "flashoffer-react";

const FIGURE_META = JSON.stringify({ orientation: "landscape" });

const FIGURE_IMAGE_SRC = `data:image/svg+xml;utf8,${encodeURIComponent(
  `<svg viewBox="0 0 960 640" xmlns="http://www.w3.org/2000/svg" role="img" aria-hidden="true">
    <defs>
      <linearGradient id="figureGradient" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" stop-color="#1d4ed8" stop-opacity="0.18" />
        <stop offset="100%" stop-color="#a855f7" stop-opacity="0.28" />
      </linearGradient>
    </defs>
    <rect x="0" y="0" width="960" height="640" rx="48" fill="#0f172a" />
    <rect x="48" y="60" width="864" height="520" rx="40" fill="url(#figureGradient)" />
    <g transform="translate(120 140)" fill="#0f172a" fill-opacity="0.9">
      <rect x="0" y="0" width="720" height="80" rx="20" />
      <rect x="60" y="24" width="200" height="16" rx="8" fill="#cbd5f5" />
      <rect x="60" y="52" width="320" height="12" rx="6" fill="#94a3b8" />
      <circle cx="36" cy="40" r="14" fill="#38bdf8" />
    </g>
    <g transform="translate(174 260)">
      <rect x="0" y="0" width="612" height="300" rx="32" fill="#0f172a" fill-opacity="0.92" />
      <polyline points="72,220 168,168 264,196 360,140 456,176 528,104" fill="none" stroke="#facc15" stroke-width="16" stroke-linecap="round" stroke-linejoin="round" stroke-opacity="0.9" />
      <rect x="90" y="72" width="48" height="168" rx="16" fill="#38bdf8" />
      <rect x="198" y="116" width="48" height="124" rx="16" fill="#6366f1" />
      <rect x="306" y="96" width="48" height="144" rx="16" fill="#a855f7" />
      <rect x="414" y="52" width="48" height="188" rx="16" fill="#22d3ee" />
      <rect x="522" y="132" width="48" height="108" rx="16" fill="#38bdf8" />
      <rect x="120" y="244" width="168" height="18" rx="9" fill="#38bdf8" fill-opacity="0.85" />
      <rect x="318" y="244" width="168" height="18" rx="9" fill="#6366f1" fill-opacity="0.75" />
    </g>
  </svg>`
)}
`;

export function FigureSpotlightSection() {
  return (
    <Box
      component="section"
      data-track-id="figure-section"
      data-track-label="Figure component"
      data-track-meta={FIGURE_META}
    >
      <Section
        eyebrow="MEDIA"
        title="Pair imagery with supporting context"
      >
        <Typography color="text.secondary">
          Use Figure to keep visuals responsive across breakpoints while pairing
          them with captions or attributions.
        </Typography>
        <Box
          sx={{
            display: "flex",
            justifyContent: "center",
            width: "100%"
          }}
        >
          <Figure
            src={FIGURE_IMAGE_SRC}
            alt="Product marketer reviewing launch campaign timelines"
            caption="Launch dashboards stay legible on any device thanks to responsive scaling."
            sx={{
              maxWidth: 560
            }}
          />
        </Box>
      </Section>
    </Box>
  );
}

export { FIGURE_META };
