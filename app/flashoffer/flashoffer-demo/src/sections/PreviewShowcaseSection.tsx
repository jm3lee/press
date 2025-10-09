import Box from "@mui/material/Box";
import Grid from "@mui/material/Grid";
import Typography from "@mui/material/Typography";
import { PreviewCard, Section } from "flashoffer-react";

function previewMedia(
  gradientId: string,
  accentColor: string,
  secondaryAccent: string
) {
  return (
    <svg
      viewBox="0 0 320 240"
      role="img"
      aria-hidden="true"
      style={{ width: "100%", borderRadius: "16px" }}
    >
      <defs>
        <linearGradient
          id={`${gradientId}-background`}
          x1="0%"
          y1="0%"
          x2="100%"
          y2="100%"
        >
          <stop offset="0%" stopColor={accentColor} stopOpacity="0.12" />
          <stop offset="100%" stopColor={secondaryAccent} stopOpacity="0.24" />
        </linearGradient>
      </defs>
      <rect
        x="0"
        y="0"
        width="320"
        height="240"
        rx="18"
        fill={`url(#${gradientId}-background)`}
      />
      <g transform="translate(36 42)" fill="#0f172a" opacity="0.85">
        <rect x="0" y="0" width="248" height="30" rx="8" />
        <rect x="0" y="48" width="208" height="18" rx="9" opacity="0.9" />
        <rect x="0" y="78" width="168" height="18" rx="9" opacity="0.8" />
        <rect x="0" y="108" width="192" height="18" rx="9" opacity="0.7" />
      </g>
      <g transform="translate(36 150)">
        <rect x="0" y="0" width="36" height="60" rx="12" fill={accentColor} />
        <rect
          x="60"
          y="12"
          width="36"
          height="48"
          rx="12"
          fill={secondaryAccent}
          opacity="0.85"
        />
        <rect
          x="120"
          y="6"
          width="36"
          height="54"
          rx="12"
          fill={accentColor}
          opacity="0.8"
        />
        <rect
          x="180"
          y="18"
          width="36"
          height="42"
          rx="12"
          fill={secondaryAccent}
          opacity="0.75"
        />
      </g>
      <circle cx="252" cy="72" r="18" fill={accentColor} opacity="0.9" />
      <circle cx="280" cy="96" r="12" fill={secondaryAccent} opacity="0.8" />
      <circle cx="258" cy="116" r="8" fill="#0f172a" opacity="0.75" />
    </svg>
  );
}

const PREVIEW_CARDS = [
  {
    title: "Personalized launch offers",
    description:
      "Highlight tailored bundles that can be activated in a few clicks. " +
      "Swap copy and imagery to match your latest campaign without rebuilding " +
      "layouts.",
    media: previewMedia("preview-offers", "#22d3ee", "#6366f1")
  },
  {
    title: "Lifecycle automation",
    description:
      "Pair Flashoffer pages with your automation stack to trigger discounts " +
      "or add-ons in response to usage signals.",
    media: previewMedia("preview-automation", "#f97316", "#facc15"),
    secondaryCta: {
      label: "View playbook",
      href: "https://example.com/playbook"
    }
  },
  {
    title: "Localized experiences",
    description:
      "Clone the same structure across regions while tuning content, pricing, " +
      "and compliance disclosures in minutes.",
    media: previewMedia("preview-localized", "#34d399", "#60a5fa"),
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

