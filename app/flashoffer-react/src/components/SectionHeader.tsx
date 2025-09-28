import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";
import type { ReactNode } from "react";

export interface SectionHeaderProps {
  /** Optional label rendered above the title. */
  eyebrow?: ReactNode;
  /** Main heading text. */
  title?: ReactNode;
  /** Supporting description under the title. */
  description?: ReactNode;
  /** Horizontal alignment for the text stack. */
  align?: "left" | "center";
}

const DEFAULT_EYEBROW = "FLASHOFFER";
const DEFAULT_TITLE = "Launch faster with reusable content blocks.";
const DEFAULT_DESCRIPTION =
  "Compose hero banners, feature highlights, and testimonials using the same " +
  "accessible primitives found in production Flashoffer experiences.";

/**
 * Section heading with optional eyebrow and description.
 */
export function SectionHeader({
  eyebrow = DEFAULT_EYEBROW,
  title = DEFAULT_TITLE,
  description = DEFAULT_DESCRIPTION,
  align = "center"
}: SectionHeaderProps) {
  return (
    <Stack
      component="header"
      spacing={1}
      alignItems={align === "center" ? "center" : "flex-start"}
      textAlign={align}
    >
      {eyebrow ? (
        <Typography variant="overline" color="text.secondary">
          {eyebrow}
        </Typography>
      ) : null}
      <Typography component="h2" variant="h4">
        {title}
      </Typography>
      {description ? (
        <Typography variant="body1" color="text.secondary">
          {description}
        </Typography>
      ) : null}
    </Stack>
  );
}
