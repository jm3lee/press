import Button from "@mui/material/Button";
import type { ButtonProps } from "@mui/material/Button";
import type { AnchorHTMLAttributes, ReactNode } from "react";

export interface OutlineCtaButtonProps
  extends ButtonProps,
    Pick<AnchorHTMLAttributes<HTMLAnchorElement>, "target" | "rel"> {
  /**
   * Textual label rendered when no custom children are provided.
   */
  label?: ReactNode;
}

/**
 * Secondary call-to-action button that defaults to an outlined style.
 */
export function OutlineCtaButton({
  label = "Contact support",
  children,
  ...props
}: OutlineCtaButtonProps) {
  return (
    <Button color="primary" variant="outlined" size="large" {...props}>
      {children ?? label}
    </Button>
  );
}
