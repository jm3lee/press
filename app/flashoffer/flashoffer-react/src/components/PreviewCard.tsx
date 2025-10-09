import Box from "@mui/material/Box";
import Card from "@mui/material/Card";
import CardActions from "@mui/material/CardActions";
import CardContent from "@mui/material/CardContent";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";
import type { ReactNode } from "react";
import { OutlineCtaButton } from "./OutlineCtaButton";
import type { OutlineCtaButtonProps } from "./OutlineCtaButton";
import { PrimaryCtaButton } from "./PrimaryCtaButton";
import type { PrimaryCtaButtonProps } from "./PrimaryCtaButton";

export interface PreviewCardProps {
  /** Optional illustration or icon rendered above the title. */
  media?: ReactNode;
  /** Heading text shown in the card. */
  title?: ReactNode;
  /** Supporting description for the card. */
  description?: ReactNode;
  /** Primary CTA rendered in the card footer. */
  primaryCta?: PrimaryCtaButtonProps;
  /** Secondary CTA rendered next to the primary CTA. */
  secondaryCta?: OutlineCtaButtonProps;
}

const DEFAULT_TITLE = "Preview a Flashoffer landing page.";
const DEFAULT_DESCRIPTION =
  "Drop this card into marketing sites to tease Flashoffer experiences. All " +
  "content can be replaced or removed without losing the baseline layout.";

/**
 * Compact preview card with optional media and CTA controls.
 */
export function PreviewCard({
  media,
  title = DEFAULT_TITLE,
  description = DEFAULT_DESCRIPTION,
  primaryCta,
  secondaryCta
}: PreviewCardProps) {
  return (
    <Card component="article" elevation={2} sx={{ height: "100%" }}>
      <CardContent>
        <Stack spacing={2}>
          {media ? <Box aria-hidden>{media}</Box> : null}
          <Typography component="h3" variant="h6">
            {title}
          </Typography>
          {description ? (
            <Typography variant="body2" color="text.secondary">
              {description}
            </Typography>
          ) : null}
        </Stack>
      </CardContent>
      {(primaryCta || secondaryCta) && (
        <CardActions sx={{ gap: 1, alignItems: "center", px: 3, pb: 3 }}>
          {primaryCta ? (
            <PrimaryCtaButton size="medium" {...primaryCta} />
          ) : null}
          {secondaryCta ? (
            <OutlineCtaButton size="medium" {...secondaryCta} />
          ) : null}
        </CardActions>
      )}
    </Card>
  );
}
