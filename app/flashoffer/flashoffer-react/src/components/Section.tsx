/*
 * Copyright (c) Flashoffer Developers
 * Released under the MIT license.
 */

import Stack from "@mui/material/Stack";
import type { ReactNode } from "react";
import { SectionHeader } from "./SectionHeader";
import type { SectionHeaderProps } from "./SectionHeader";

export interface SectionProps extends SectionHeaderProps {
  /** Supporting content rendered under the section header. */
  children?: ReactNode;
  /** Optional custom id applied to the underlying section element. */
  id?: string;
}

/**
 * High-level section wrapper that combines SectionHeader with supporting copy.
 *
 * Mirrors SectionHeader defaults (Flashoffer eyebrow, marketing title,
 * centered alignment) while exposing extra space for arbitrary `children` and
 * an optional section `id`. Pass supporting markup as regular React nodes
 * rather than assembling arrays; the surrounding Stack handles spacing.
 */
export function Section({
  align = "center",
  id,
  children,
  ...headerProps
}: SectionProps) {
  const alignItems = align === "center" ? "center" : "flex-start";

  return (
    <Stack
      component="section"
      id={id}
      spacing={3}
      alignItems={alignItems}
      textAlign={align}
    >
      <SectionHeader align={align} {...headerProps} />
      {children}
    </Stack>
  );
}
