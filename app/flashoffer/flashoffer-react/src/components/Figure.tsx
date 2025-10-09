/*
 * Copyright (c) Flashoffer Developers
 * Released under the MIT license.
 */

import Box from "@mui/material/Box";
import Typography from "@mui/material/Typography";
import type { SxProps, Theme } from "@mui/material/styles";
import type { ImgHTMLAttributes, ReactNode } from "react";

export interface FigureProps {
  /** Image source rendered inside the figure. */
  src: string;
  /** Descriptive alt text for the image. Defaults to decorative. */
  alt?: string;
  /** Optional caption content rendered below the image. */
  caption?: ReactNode;
  /** Custom styles merged into the root figure element. */
  sx?: SxProps<Theme>;
  /** Additional props forwarded to the underlying <img> element. */
  imgProps?: Omit<ImgHTMLAttributes<HTMLImageElement>, "src" | "alt">;
}

/**
 * Responsive image container with optional caption support.
 */
export function Figure({
  src,
  alt = "",
  caption,
  sx,
  imgProps
}: FigureProps) {
  return (
    <Box
      component="figure"
      sx={{
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        gap: 1,
        my: 0,
        ...sx
      }}
    >
      <Box
        component="img"
        alt={alt}
        src={src}
        sx={{
          display: "block",
          maxWidth: "100%",
          width: "100%",
          height: "auto",
          objectFit: "contain"
        }}
        {...imgProps}
      />
      <Typography component="figcaption" variant="caption" color="text.secondary">
        {caption ?? null}
      </Typography>
    </Box>
  );
}
