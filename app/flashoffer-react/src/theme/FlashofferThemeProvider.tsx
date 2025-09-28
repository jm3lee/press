import CssBaseline from "@mui/material/CssBaseline";
import GlobalStyles from "@mui/material/GlobalStyles";
import { StyledEngineProvider } from "@mui/material/styles";
import { ThemeProvider, createTheme } from "@mui/material/styles";
import type { Theme, ThemeOptions } from "@mui/material/styles";
import { deepmerge } from "@mui/utils";
import type { PropsWithChildren } from "react";
import { useMemo } from "react";

const baseThemeOptions: ThemeOptions = {
  palette: {
    primary: {
      main: "#2563eb",
      contrastText: "#ffffff"
    },
    secondary: {
      main: "#f97316",
      contrastText: "#1f2937"
    },
    background: {
      default: "#f8fafc",
      paper: "#ffffff"
    },
    text: {
      primary: "#0f172a",
      secondary: "#475569"
    }
  },
  typography: {
    fontFamily: '"Inter", "Helvetica", "Arial", sans-serif',
    h3: {
      fontWeight: 600,
      letterSpacing: "-0.01em"
    },
    h4: {
      fontWeight: 600,
      letterSpacing: "-0.01em"
    },
    button: {
      textTransform: "none",
      fontWeight: 600
    }
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: "var(--flashoffer-radius-button, 999px)",
          paddingInline: "1.75rem",
          paddingBlock: "0.75rem"
        }
      }
    }
  }
};

/**
 * Create a Flashoffer design system theme with optional overrides.
 */
export function createFlashofferTheme(overrides?: ThemeOptions): Theme {
  if (!overrides) {
    return createTheme(baseThemeOptions);
  }
  return createTheme(deepmerge(baseThemeOptions, overrides));
}

const cssVariableStyles = (theme: Theme) => ({
  ":root": {
    "--flashoffer-color-primary": theme.palette.primary.main,
    "--flashoffer-color-on-primary": theme.palette.primary.contrastText,
    "--flashoffer-color-secondary": theme.palette.secondary.main,
    "--flashoffer-color-on-secondary": theme.palette.secondary.contrastText,
    "--flashoffer-color-background": theme.palette.background.default,
    "--flashoffer-color-surface": theme.palette.background.paper,
    "--flashoffer-color-text-primary": theme.palette.text.primary,
    "--flashoffer-color-text-secondary": theme.palette.text.secondary,
    "--flashoffer-font-family": theme.typography.fontFamily ||
      '"Inter", "Helvetica", "Arial", sans-serif'
  }
});

export interface FlashofferThemeProviderProps extends PropsWithChildren {
  /** Optional theme overrides merged with the default Flashoffer palette. */
  themeOptions?: ThemeOptions;
  /** Whether to include MUI's CssBaseline. */
  applyCssBaseline?: boolean;
}

/**
 * Theme provider exposing CSS-token aware defaults for Flashoffer surfaces.
 */
export function FlashofferThemeProvider({
  children,
  themeOptions,
  applyCssBaseline = true
}: FlashofferThemeProviderProps) {
  const theme = useMemo(
    () => createFlashofferTheme(themeOptions),
    [themeOptions]
  );

  return (
    <StyledEngineProvider injectFirst>
      <ThemeProvider theme={theme}>
        {applyCssBaseline ? <CssBaseline /> : null}
        <GlobalStyles styles={cssVariableStyles(theme)} />
        {children}
      </ThemeProvider>
    </StyledEngineProvider>
  );
}
