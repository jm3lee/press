import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";
import type { ReactNode } from "react";

export interface SectionHeaderProps {
  /** Optional label rendered above the title. Defaults to "FLASHOFFER". */
  eyebrow?: ReactNode;
  /** Main heading text. Defaults to Flashoffer marketing copy. */
  title?: ReactNode;
  /** Horizontal alignment for the text stack. Defaults to "center". */
  align?: "left" | "center";
}

const DEFAULT_EYEBROW = "FLASHOFFER";
const DEFAULT_TITLE = "Launch faster with reusable content blocks.";

/**
 * Section heading with optional eyebrow and configurable alignment.
 */
export function SectionHeader({
  eyebrow = DEFAULT_EYEBROW,
  title = DEFAULT_TITLE,
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
    </Stack>
  );
}
