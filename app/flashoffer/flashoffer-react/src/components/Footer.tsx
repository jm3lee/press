/*
 * Copyright (c) Flashoffer Developers
 * Released under the MIT license.
 */

import Box from "@mui/material/Box";
import Link from "@mui/material/Link";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";
import type { BoxProps } from "@mui/material/Box";
import type { SxProps, Theme } from "@mui/material/styles";
import type { ReactNode } from "react";

export interface FooterLink {
  label: ReactNode;
  href: string;
  target?: string;
  rel?: string;
}

export interface FooterProps extends Omit<BoxProps, "children"> {
  /** Optional set of navigational links rendered in the footer. */
  links?: FooterLink[];
  /** Copyright or attribution text shown below the links. */
  copyrightText?: ReactNode;
}

const DEFAULT_LINKS: FooterLink[] = [
  { label: "Docs", href: "https://example.com/docs" },
  { label: "Status", href: "https://status.example.com" },
  { label: "Support", href: "mailto:support@example.com" }
];

const DEFAULT_COPYRIGHT = "© Flashoffer. All rights reserved.";

/**
 * Footer component that renders navigation links and attribution text.
 */
export function Footer({
  links = DEFAULT_LINKS,
  copyrightText = DEFAULT_COPYRIGHT,
  sx,
  component = "footer",
  role = "contentinfo",
  ...boxProps
}: FooterProps) {
  const baseSx = { padding: 4, pb: 6 };
  let mergedSx: SxProps<Theme>;
  if (Array.isArray(sx)) {
    mergedSx = [baseSx, ...sx];
  } else if (sx) {
    mergedSx = [baseSx, sx];
  } else {
    mergedSx = baseSx;
  }

  return (
    <Box
      component={component}
      role={role}
      sx={mergedSx}
      {...boxProps}
    >
      <Stack spacing={2} alignItems="center" textAlign="center">
        {links?.length ? (
          <Stack direction="row" spacing={3} useFlexGap flexWrap="wrap" justifyContent="center">
            {links.map((link) => (
              <Link
                key={String(link.href)}
                href={link.href}
                target={link.target}
                rel={link.rel}
                underline="hover"
                color="text.secondary"
              >
                {link.label}
              </Link>
            ))}
          </Stack>
        ) : null}
        {copyrightText ? (
          <Typography variant="body2" color="text.disabled">
            {copyrightText}
          </Typography>
        ) : null}
      </Stack>
    </Box>
  );
}
