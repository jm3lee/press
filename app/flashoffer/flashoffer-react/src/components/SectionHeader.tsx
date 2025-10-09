/*
 * Copyright (c) Flashoffer Developers
 * Released under the MIT license.
 */

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
 *
 * Defaults render the "FLASHOFFER" eyebrow and the "Launch faster with
 * reusable content blocks." title. Text is centered unless `align="left"` is
 * provided, and either content slot can be omitted by passing `null`.
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
      <Typography variant="h2">
        {title}
      </Typography>
    </Stack>
  );
}
