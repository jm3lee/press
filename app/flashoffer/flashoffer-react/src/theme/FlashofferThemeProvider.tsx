/*
 * Copyright (c) Flashoffer Developers
 * Released under the MIT license.
 */

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

/**
 * Create a spacious typography-first preset with mode-specific palettes and
 * optional overrides for fine-grained adjustments.
 */
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

/**
 * Create a preset theme by merging base, palette, and override options.
 */
function createPresetTheme(
  baseOptions: ThemeOptions,
  paletteByMode: Record<PaletteMode, ThemeOptions>,
  mode: PaletteMode,
  overrides?: ThemeOptions
): Theme {
  const mergedBase = deepmerge(baseOptions, paletteByMode[mode]);
  if (!overrides) {
    return createTheme(mergedBase);
  }
  return createTheme(deepmerge(mergedBase, overrides));
}

const sunriseGlowBaseOptions: ThemeOptions = {
  typography: {
    fontFamily: '"Poppins", "Inter", "Helvetica", "Arial", sans-serif',
    h1: {
      fontWeight: 700,
      letterSpacing: "-0.02em"
    },
    h2: {
      fontWeight: 600,
      letterSpacing: "-0.018em"
    },
    button: {
      borderRadius: "999px",
      fontWeight: 700,
      letterSpacing: "0.02em"
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
    },
    MuiChip: {
      styleOverrides: {
        root: {
          borderRadius: "999px",
          fontWeight: 600
        }
      }
    }
  }
};

const sunriseGlowPalette: Record<PaletteMode, ThemeOptions> = {
  light: {
    palette: {
      mode: "light",
      primary: {
        main: "#f97316",
        contrastText: "#ffffff"
      },
      secondary: {
        main: "#facc15",
        contrastText: "#1f2937"
      },
      background: {
        default: "#fff7ed",
        paper: "#fffbeb"
      },
      text: {
        primary: "#7c2d12",
        secondary: "#b45309"
      }
    }
  },
  dark: {
    palette: {
      mode: "dark",
      primary: {
        main: "#fb923c",
        contrastText: "#1f2937"
      },
      secondary: {
        main: "#fbbf24",
        contrastText: "#0f172a"
      },
      background: {
        default: "#1c1917",
        paper: "#292524"
      },
      text: {
        primary: "#fed7aa",
        secondary: "#fde68a"
      }
    }
  }
};

const midnightPulseBaseOptions: ThemeOptions = {
  typography: {
    fontFamily: '"Space Grotesk", "Inter", "Helvetica", "Arial", sans-serif',
    h1: {
      fontWeight: 700,
      letterSpacing: "-0.015em"
    },
    button: {
      textTransform: "uppercase",
      letterSpacing: "0.08em"
    }
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: "18px",
          paddingInline: "1.5rem"
        }
      }
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          borderRadius: "28px"
        }
      }
    }
  }
};

const midnightPulsePalette: Record<PaletteMode, ThemeOptions> = {
  light: {
    palette: {
      mode: "light",
      primary: {
        main: "#4f46e5",
        contrastText: "#ffffff"
      },
      secondary: {
        main: "#0ea5e9",
        contrastText: "#0f172a"
      },
      background: {
        default: "#eef2ff",
        paper: "#e0e7ff"
      },
      text: {
        primary: "#111827",
        secondary: "#4338ca"
      }
    }
  },
  dark: {
    palette: {
      mode: "dark",
      primary: {
        main: "#6366f1",
        contrastText: "#0f172a"
      },
      secondary: {
        main: "#22d3ee",
        contrastText: "#0f172a"
      },
      background: {
        default: "#020617",
        paper: "#0f172a"
      },
      text: {
        primary: "#e0e7ff",
        secondary: "#bae6fd"
      }
    }
  }
};

const oceanBreezeBaseOptions: ThemeOptions = {
  typography: {
    fontFamily: '"Rubik", "Inter", "Helvetica", "Arial", sans-serif',
    h2: {
      fontWeight: 700,
      letterSpacing: "-0.012em"
    },
    subtitle1: {
      letterSpacing: "0.015em"
    }
  },
  components: {
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: "26px",
          padding: "1.5rem"
        }
      }
    },
    MuiContainer: {
      styleOverrides: {
        root: {
          paddingInline: "clamp(1rem, 4vw, 3rem)"
        }
      }
    }
  }
};

const oceanBreezePalette: Record<PaletteMode, ThemeOptions> = {
  light: {
    palette: {
      mode: "light",
      primary: {
        main: "#0284c7",
        contrastText: "#f8fafc"
      },
      secondary: {
        main: "#14b8a6",
        contrastText: "#022c22"
      },
      background: {
        default: "#f1f5f9",
        paper: "#e0f2fe"
      },
      text: {
        primary: "#0f172a",
        secondary: "#0f766e"
      }
    }
  },
  dark: {
    palette: {
      mode: "dark",
      primary: {
        main: "#38bdf8",
        contrastText: "#082f49"
      },
      secondary: {
        main: "#2dd4bf",
        contrastText: "#042f2e"
      },
      background: {
        default: "#0f172a",
        paper: "#11263a"
      },
      text: {
        primary: "#e0f2fe",
        secondary: "#99f6e4"
      }
    }
  }
};

const forestCanopyBaseOptions: ThemeOptions = {
  typography: {
    fontFamily: '"Inter", "Helvetica", "Arial", sans-serif',
    h3: {
      fontWeight: 700,
      letterSpacing: "-0.01em"
    },
    body1: {
      lineHeight: 1.7
    }
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: "14px",
          paddingInline: "1.5rem"
        }
      }
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          borderRadius: "24px"
        }
      }
    }
  }
};

const forestCanopyPalette: Record<PaletteMode, ThemeOptions> = {
  light: {
    palette: {
      mode: "light",
      primary: {
        main: "#15803d",
        contrastText: "#f0fdf4"
      },
      secondary: {
        main: "#65a30d",
        contrastText: "#1a2e05"
      },
      background: {
        default: "#f7fee7",
        paper: "#ecfccb"
      },
      text: {
        primary: "#1f2937",
        secondary: "#365314"
      }
    }
  },
  dark: {
    palette: {
      mode: "dark",
      primary: {
        main: "#34d399",
        contrastText: "#052e16"
      },
      secondary: {
        main: "#bef264",
        contrastText: "#1a2e05"
      },
      background: {
        default: "#052e16",
        paper: "#0f3f23"
      },
      text: {
        primary: "#dcfce7",
        secondary: "#bbf7d0"
      }
    }
  }
};

const monochromeFocusBaseOptions: ThemeOptions = {
  typography: {
    fontFamily: '"Inter", "Helvetica", "Arial", sans-serif',
    h1: {
      fontWeight: 700,
      letterSpacing: "-0.02em"
    },
    caption: {
      letterSpacing: "0.1em"
    }
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: "0.75rem",
          paddingInline: "1.5rem"
        }
      }
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          borderRadius: "20px",
          borderWidth: 1,
          borderStyle: "solid",
          borderColor: "rgba(15, 23, 42, 0.12)"
        }
      }
    }
  }
};

const monochromeFocusPalette: Record<PaletteMode, ThemeOptions> = {
  light: {
    palette: {
      mode: "light",
      primary: {
        main: "#111827",
        contrastText: "#f8fafc"
      },
      secondary: {
        main: "#475569",
        contrastText: "#f8fafc"
      },
      background: {
        default: "#f8fafc",
        paper: "#ffffff"
      },
      text: {
        primary: "#0f172a",
        secondary: "#475569"
      }
    }
  },
  dark: {
    palette: {
      mode: "dark",
      primary: {
        main: "#e2e8f0",
        contrastText: "#0f172a"
      },
      secondary: {
        main: "#94a3b8",
        contrastText: "#020617"
      },
      background: {
        default: "#0f172a",
        paper: "#111827"
      },
      text: {
        primary: "#f8fafc",
        secondary: "#cbd5f5"
      }
    }
  }
};

/**
 * Create a sunrise-inspired palette with bold warm gradients.
 */
export function createSunriseGlowTheme(
  mode: PaletteMode = "light",
  overrides?: ThemeOptions
): Theme {
  return createPresetTheme(
    sunriseGlowBaseOptions,
    sunriseGlowPalette,
    mode,
    overrides
  );
}

/**
 * Create a neon-accented palette optimized for dark hero sections.
 */
export function createMidnightPulseTheme(
  mode: PaletteMode = "light",
  overrides?: ThemeOptions
): Theme {
  return createPresetTheme(
    midnightPulseBaseOptions,
    midnightPulsePalette,
    mode,
    overrides
  );
}

/**
 * Create a calm oceanic palette focused on teal gradients.
 */
export function createOceanBreezeTheme(
  mode: PaletteMode = "light",
  overrides?: ThemeOptions
): Theme {
  return createPresetTheme(
    oceanBreezeBaseOptions,
    oceanBreezePalette,
    mode,
    overrides
  );
}

/**
 * Create a green-forward palette suited for sustainability campaigns.
 */
export function createForestCanopyTheme(
  mode: PaletteMode = "light",
  overrides?: ThemeOptions
): Theme {
  return createPresetTheme(
    forestCanopyBaseOptions,
    forestCanopyPalette,
    mode,
    overrides
  );
}

/**
 * Create a high-contrast monochrome palette for editorial layouts.
 */
export function createMonochromeFocusTheme(
  mode: PaletteMode = "light",
  overrides?: ThemeOptions
): Theme {
  return createPresetTheme(
    monochromeFocusBaseOptions,
    monochromeFocusPalette,
    mode,
    overrides
  );
}

export type FlashofferThemePreset =
  | "default"
  | "spaciousTypography"
  | "sunriseGlow"
  | "midnightPulse"
  | "oceanBreeze"
  | "forestCanopy"
  | "monochromeFocus";

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
  const themeFactories: Record<FlashofferThemePreset, (mode: PaletteMode) => Theme> =
    useMemo(
      () => ({
        default: () => createFlashofferTheme(themeOptions),
        spaciousTypography: (mode) =>
          createSpaciousTypographyTheme(mode, themeOptions),
        sunriseGlow: (mode) => createSunriseGlowTheme(mode, themeOptions),
        midnightPulse: (mode) => createMidnightPulseTheme(mode, themeOptions),
        oceanBreeze: (mode) => createOceanBreezeTheme(mode, themeOptions),
        forestCanopy: (mode) => createForestCanopyTheme(mode, themeOptions),
        monochromeFocus: (mode) =>
          createMonochromeFocusTheme(mode, themeOptions)
      }),
      [themeOptions]
    );

  const theme = useMemo(
    () => themeFactories[preset](colorMode),
    [colorMode, preset, themeFactories]
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
