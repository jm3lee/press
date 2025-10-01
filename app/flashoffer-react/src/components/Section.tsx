import Box from "@mui/material/Box";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";
import { useTheme } from "@mui/material/styles";
import type { ReactNode } from "react";
import { SectionHeader } from "./SectionHeader";
import type { SectionHeaderProps } from "./SectionHeader";

export interface SectionProps {
  /**
   * Body copy rendered under the section header. Each entry is wrapped in a
   * paragraph-level Typography component.
   */
  children?: ReactNode[];
  /** Optional custom id applied to the underlying section element. */
  id?: string;
}

/**
 * High-level section wrapper that combines SectionHeader with supporting copy.
 */
export function Section({
  align = "center",
  id,
  children,
  ...headerProps
}: SectionProps) {
  const theme = useTheme();
  const textAlign = align;
  const alignItems = align === "center" ? "center" : "flex-start";
  const paragraphColor = theme.palette.text.secondary;
  const sectionTextColor = theme.palette.text.primary;
  const paragraphMarginTop = theme.spacing(3);

  return (
    <Stack component="section" id={id} sx={{ color: sectionTextColor }} spacing={3}>
      <SectionHeader align={align} {...headerProps} />
      {children}
    </Stack>
  );
}
