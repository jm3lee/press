import CssBaseline from "@mui/material/CssBaseline";
import GlobalStyles from "@mui/material/GlobalStyles";
import { StyledEngineProvider } from "@mui/material/styles";
import { ThemeProvider, createTheme } from "@mui/material/styles";
import type { PaletteMode, Theme, ThemeOptions } from "@mui/material/styles";
import { deepmerge } from "@mui/utils";
import type { PropsWithChildren } from "react";
import { useMemo } from "react";

const baseThemeOptions: ThemeOptions = {
  palette: {
    mode: "light",
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

const spaciousTypographyBaseOptions: ThemeOptions = {
  typography: {
    fontFamily:
      '"Source Sans 3", "Inter", "Helvetica", "Arial", sans-serif',
    fontSize: 16,
    h1: {
      fontWeight: 600,
      fontSize: "clamp(2.75rem, 6vw, 3.5rem)",
      lineHeight: 1.2,
      letterSpacing: "-0.015em"
    },
    h2: {
      fontWeight: 600,
      fontSize: "clamp(2.25rem, 5vw, 3rem)",
      lineHeight: 1.25,
      letterSpacing: "-0.012em"
    },
    h3: {
      fontWeight: 600,
      fontSize: "clamp(1.75rem, 3.5vw, 2.25rem)",
      lineHeight: 1.3,
      letterSpacing: "-0.01em"
    },
    h4: {
      fontWeight: 600,
      fontSize: "clamp(1.5rem, 3vw, 1.875rem)",
      lineHeight: 1.35,
      letterSpacing: "-0.008em"
    },
    body1: {
      fontSize: "1.125rem",
      lineHeight: 1.75
    },
    body2: {
      fontSize: "1.05rem",
      lineHeight: 1.7
    },
    subtitle1: {
      fontSize: "1rem",
      lineHeight: 1.65
    },
    subtitle2: {
      fontSize: "0.95rem",
      lineHeight: 1.6
    },
    caption: {
      letterSpacing: "0.08em",
      textTransform: "uppercase"
    },
    button: {
      textTransform: "none",
      fontWeight: 600,
      letterSpacing: "0.02em"
    }
  },
  spacing: 10,
  components: {
    MuiCssBaseline: {
      styleOverrides: {
        body: {
          fontFeatureSettings: '"liga" 1, "kern" 1'
        }
      }
    },
    MuiContainer: {
      styleOverrides: {
        root: {
          paddingInline: "clamp(1.25rem, 4vw, 2.5rem)"
        }
      }
    },
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: "var(--flashoffer-radius-button, 999px)",
          paddingInline: "clamp(2rem, 5vw, 2.75rem)",
          paddingBlock: "0.875rem"
        }
      }
    }
  }
};

const spaciousTypographyPalette: Record<PaletteMode, ThemeOptions> = {
  light: {
    palette: {
      mode: "light",
      primary: {
        main: "#1d4ed8",
        contrastText: "#ffffff"
      },
      secondary: {
        main: "#db2777",
        contrastText: "#ffffff"
      },
      background: {
        default: "#f1f5f9",
        paper: "#ffffff"
      },
      text: {
        primary: "#0f172a",
        secondary: "#334155"
      }
    }
  },
  dark: {
    palette: {
      mode: "dark",
      primary: {
        main: "#60a5fa",
        contrastText: "#0b1120"
      },
      secondary: {
        main: "#f9a8d4",
        contrastText: "#111827"
      },
      background: {
        default: "#0b1120",
        paper: "#111827"
      },
      text: {
        primary: "#e2e8f0",
        secondary: "#cbd5f5"
      }
    }
  }
};

function buildSpaciousTypographyThemeOptions(mode: PaletteMode): ThemeOptions {
  return deepmerge(
    spaciousTypographyBaseOptions,
    spaciousTypographyPalette[mode]
  );
}

/**
 * Create a Flashoffer design system theme with optional overrides.
 */
export function createFlashofferTheme(overrides?: ThemeOptions): Theme {
  if (!overrides) {
    return createTheme(baseThemeOptions);
  }
  return createTheme(deepmerge(baseThemeOptions, overrides));
}

export function createSpaciousTypographyTheme(
  mode: PaletteMode = "light",
  overrides?: ThemeOptions
): Theme {
  const baseOptions = buildSpaciousTypographyThemeOptions(mode);
  if (!overrides) {
    return createTheme(baseOptions);
  }
  return createTheme(deepmerge(baseOptions, overrides));
}

export type FlashofferThemePreset = "default" | "spaciousTypography";

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
  /**
   * Select a preset to use as the base Flashoffer theme before applying
   * overrides.
   */
  preset?: FlashofferThemePreset;
  /** Controls the palette mode for presets that support it. */
  colorMode?: PaletteMode;
}

/**
 * Theme provider exposing CSS-token aware defaults for Flashoffer surfaces.
 */
export function FlashofferThemeProvider({
  children,
  themeOptions,
  applyCssBaseline = true,
  preset = "default",
  colorMode = "light"
}: FlashofferThemeProviderProps) {
  const theme = useMemo(
    () => {
      if (preset === "spaciousTypography") {
        return createSpaciousTypographyTheme(colorMode, themeOptions);
      }
      return createFlashofferTheme(themeOptions);
    },
    [colorMode, preset, themeOptions]
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
