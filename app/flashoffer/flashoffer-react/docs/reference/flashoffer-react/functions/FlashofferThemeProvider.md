[**flashoffer-react**](../README.md)

***

# Function: FlashofferThemeProvider()

> **FlashofferThemeProvider**(`__namedParameters`): `Element`

Defined in: src/theme/FlashofferThemeProvider.tsx:92

Theme provider exposing CSS-token aware defaults for Flashoffer surfaces.

Wrap this component around your React subtree to inject the Flashoffer theme.
It constructs an MUI `Theme` from the selected preset, merges any supplied
`themeOptions`, and exposes the result through `ThemeProvider`. The provider
also emits a collection of CSS custom properties so non-MUI components can
consume the same palette tokens.

## Usage example

Mount the provider close to your app shell so all descendants share the same
design tokens. Extend the preset theme with `themeOptions` when you need to
override typography or component styles.

```tsx
import { FlashofferThemeProvider } from "flashoffer-react";
import { CssBaseline, Typography } from "@mui/material";

export function App() {
  return (
    <FlashofferThemeProvider
      applyCssBaseline
      preset="spaciousTypography"
      themeOptions={{
        typography: {
          h1: {
            fontSize: "3rem",
          },
        },
      }}
    >
      <CssBaseline />
      <Typography variant="h1">Deals of the Day</Typography>
    </FlashofferThemeProvider>
  );
}
```

## Parameters

### \_\_namedParameters

[`FlashofferThemeProviderProps`](../interfaces/FlashofferThemeProviderProps.md)

- `themeOptions`: Additional `ThemeOptions` merged with the preset defaults.
- `applyCssBaseline`: Controls whether MUI's `CssBaseline` is rendered.
- `preset`: Choose between the `default` palette and `spaciousTypography`.
- `colorMode`: Palette mode forwarded to presets that support light or dark
  variants.

## Returns

`Element`
