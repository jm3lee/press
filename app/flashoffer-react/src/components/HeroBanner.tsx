import Box from "@mui/material/Box";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";
import { useId } from "react";
import type { ReactNode } from "react";
import { OutlineCtaButton } from "./OutlineCtaButton";
import type { OutlineCtaButtonProps } from "./OutlineCtaButton";
import { PrimaryCtaButton } from "./PrimaryCtaButton";
import type { PrimaryCtaButtonProps } from "./PrimaryCtaButton";

export interface HeroBannerProps {
  /** Main headline for the hero banner. */
  title?: ReactNode;
  /** Supporting copy shown under the title. */
  subtitle?: ReactNode;
  /** Optional media element rendered alongside the copy. */
  media?: ReactNode;
  /** Props passed to the primary CTA button. */
  primaryCta?: PrimaryCtaButtonProps;
  /** Props passed to the secondary CTA button. */
  secondaryCta?: OutlineCtaButtonProps | null;
  /** Aligns content horizontally. */
  align?: "left" | "center";
}

const DEFAULT_TITLE = "Launch coordinated offers in minutes.";
const DEFAULT_SUBTITLE =
  "Flashoffer ships reusable hero, CTA, and preview components so teams " +
  "can publish landing experiments without bespoke design cycles.";

/**
 * Promotional hero unit with sensible defaults for copy and layout.
 */
export function HeroBanner({
  title = DEFAULT_TITLE,
  subtitle = DEFAULT_SUBTITLE,
  media,
  primaryCta = {
    label: "Explore Flashoffer components",
    href: "https://example.com/flashoffer"
  },
  secondaryCta = {
    label: "Contact support",
    href: "mailto:support@example.com"
  },
  align = "center"
}: HeroBannerProps) {
  const headingId = useId();
  const subtitleId = useId();
  return (
    <Box
      component="section"
      role="banner"
      aria-labelledby={headingId}
      aria-describedby={subtitle ? subtitleId : undefined}
      sx={{
        background:
          "linear-gradient(135deg, var(--flashoffer-hero-gradient-start, #f5f7ff) 0%, var(--flashoffer-hero-gradient-stop, #eef2ff) 100%)",
        borderRadius: 4,
        p: { xs: 4, md: 8 },
        textAlign: align,
        display: "flex",
        flexDirection: { xs: "column", md: "row" },
        gap: 4,
        alignItems: "center",
        justifyContent: "space-between"
      }}
    >
      <Stack spacing={3} alignItems={align === "center" ? "center" : "flex-start"}>
        <Typography id={headingId} component="h1" variant="h3">
          {title}
        </Typography>
        {subtitle ? (
          <Typography id={subtitleId} variant="body1" color="text.secondary">
            {subtitle}
          </Typography>
        ) : null}
        <Stack
          direction={{ xs: "column", sm: "row" }}
          spacing={2}
          useFlexGap
          alignItems={align === "center" ? "center" : "flex-start"}
        >
          <PrimaryCtaButton {...(primaryCta ?? {})} />
          {secondaryCta ? <OutlineCtaButton {...secondaryCta} /> : null}
        </Stack>
      </Stack>
      {media ? (
        <Box aria-hidden sx={{ flexShrink: 0, maxWidth: 360, width: "100%" }}>
          {media}
        </Box>
      ) : null}
    </Box>
  );
}
