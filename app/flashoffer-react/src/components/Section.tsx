import Box from "@mui/material/Box";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";
import { useTheme } from "@mui/material/styles";
import type { ReactNode } from "react";
import { SectionHeader } from "./SectionHeader";
import type { SectionHeaderProps } from "./SectionHeader";

export interface SectionProps extends SectionHeaderProps {
  /**
   * Body copy rendered under the section header. Each entry is wrapped in a
   * paragraph-level Typography component.
   */
  paragraphs?: ReactNode[];
  /** Optional custom id applied to the underlying section element. */
  id?: string;
}

const DEFAULT_PARAGRAPHS: ReactNode[] = [
  "Flashoffer sections pair concise headlines with digestible copy blocks so " +
    "marketing teams can narrate launches without bespoke layouts.",
  "Swap the content as needed while retaining consistent spacing, typography, " +
    "and accessible markup across campaigns."
];

/**
 * High-level section wrapper that combines SectionHeader with supporting copy.
 */
export function Section({
  paragraphs = DEFAULT_PARAGRAPHS,
  align = "center",
  id,
  ...headerProps
}: SectionProps) {
  const theme = useTheme();
  const hasParagraphs = paragraphs && paragraphs.length > 0;
  const textAlign = align;
  const alignItems = align === "center" ? "center" : "flex-start";
  const paragraphColor = theme.palette.text.secondary;
  const sectionTextColor = theme.palette.text.primary;
  const paragraphMarginTop = theme.spacing(3);

  return (
    <Box component="section" id={id} sx={{ color: sectionTextColor }}>
      <SectionHeader align={align} {...headerProps} />
      {hasParagraphs ? (
        <Stack
          spacing={2}
          sx={{
            mt: paragraphMarginTop,
            maxWidth: "65ch",
            mx: align === "center" ? "auto" : undefined
          }}
          alignItems={alignItems}
          textAlign={textAlign}
        >
          {paragraphs.map((paragraph, index) => (
            <Typography
              key={index}
              component="p"
              variant="body1"
              sx={{ color: paragraphColor }}
            >
              {paragraph}
            </Typography>
          ))}
        </Stack>
      ) : null}
    </Box>
  );
}
