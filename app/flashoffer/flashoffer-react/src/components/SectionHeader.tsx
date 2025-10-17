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
  /** Supporting copy rendered beneath the section title. */
  subtitle?: ReactNode;
  /** Horizontal alignment for the text stack. Defaults to "center". */
  align?: "left" | "center";
}

const DEFAULT_EYEBROW = "FLASHOFFER";
const DEFAULT_TITLE = "Launch faster with reusable content blocks.";
const DEFAULT_SUBTITLE = "";

/**
 * Section heading with optional eyebrow, subtitle, and configurable alignment.
 *
 * Defaults render the "FLASHOFFER" eyebrow and the "Launch faster with
 * reusable content blocks." title. Text is centered unless `align="left"` is
 * provided. Eyebrow, title, or subtitle content can be omitted by passing
 * `null`.
 */
export function SectionHeader({
  eyebrow = DEFAULT_EYEBROW,
  title = DEFAULT_TITLE,
  subtitle = DEFAULT_SUBTITLE,
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
      {subtitle ? (
        <Typography variant="body1" color="text.secondary">
          {subtitle}
        </Typography>
      ) : null}
    </Stack>
  );
}
