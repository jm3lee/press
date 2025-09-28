import Button from "@mui/material/Button";
import type { ButtonProps } from "@mui/material/Button";
import type { AnchorHTMLAttributes, ReactNode } from "react";

export interface PrimaryCtaButtonProps
  extends ButtonProps,
    Pick<AnchorHTMLAttributes<HTMLAnchorElement>, "target" | "rel"> {
  /**
   * Textual label rendered when no custom children are provided.
   */
  label?: ReactNode;
}

/**
 * Primary call-to-action button styled with the Flashoffer theme.
 */
export function PrimaryCtaButton({
  label = "Explore Flashoffer components",
  children,
  ...props
}: PrimaryCtaButtonProps) {
  return (
    <Button color="primary" variant="contained" size="large" {...props}>
      {children ?? label}
    </Button>
  );
}
