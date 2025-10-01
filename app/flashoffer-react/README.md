# Flashoffer React

Reusable React components, built on Material UI, that mirror the design tokens
used by Flashoffer experiences. The library ships with a theme provider,
strongly typed component APIs, and accessibility-focused defaults so marketing
teams can drop the primitives into landing pages without extra scaffolding.

## Maintenance guidelines

- Whenever you modify a `flashoffer-react` component, open a companion pull
  request on `flashoffer-demo` so the marketing showcase mirrors the latest API
  and visual treatment. The demo must ship the same defaults and examples as
  the component library to guarantee parity.
- Components should always render a sensible layout when instantiated with no
  props. Verify that each primitive exposes defaults that marketing teams can
  compose into a functional experiment page without first wiring bespoke data.
- Every component must accept child React nodes in the obvious content slots.
  Where Material UI slots exist (e.g., `CardActions`, `CardContent`), ensure we
  forward them so integrators can replace copy, media, and CTAs without
  forking the component.

## Installation

```bash
npm install flashoffer-react
```

The package exposes both ESM and CommonJS bundles alongside TypeScript
definitions. Consumers can tree-shake individual exports from `flashoffer-react`
or import the entire surface area from the entry point.

## Usage

Wrap your application (or a single subtree) in the `FlashofferThemeProvider` to
activate the CSS-token palette. Every token ships with a sensible default and
may be overridden with custom CSS variables or explicit theme options.

```tsx
import {
  FlashofferThemeProvider,
  HeroBanner,
  PreviewCard,
  SectionHeader
} from "flashoffer-react";

export function LandingPage() {
  return (
    <FlashofferThemeProvider
      themeOptions={{ palette: { primary: { main: "#8b5cf6" } } }}
    >
      <HeroBanner
        primaryCta={{ label: "Start trial", href: "https://flashoffer.dev" }}
        secondaryCta={{ label: "Contact sales" }}
      />
      <SectionHeader />
      <PreviewCard />
    </FlashofferThemeProvider>
  );
}
```

### Theme customization

`FlashofferThemeProvider` merges any supplied Material UI `ThemeOptions` with the
baseline palette. For more granular control, call `createFlashofferTheme` and
pass the resulting theme to your own `ThemeProvider` instance. The component
primitives respect CSS tokens such as `--flashoffer-color-primary` and
`--flashoffer-font-family`, enabling runtime theming through global styles.

```tsx
import { ThemeProvider } from "@mui/material/styles";
import { createFlashofferTheme } from "flashoffer-react";

const theme = createFlashofferTheme({
  palette: {
    primary: { main: "var(--brand-primary, #0ea5e9)" }
  }
});

export function App({ children }: { children: React.ReactNode }) {
  return <ThemeProvider theme={theme}>{children}</ThemeProvider>;
}
```

### Component overview

The library includes call-to-action buttons, hero banners, section headers,
preview cards, and a footer with neutral defaults. Each component exposes typed
props so product teams can swap copy, inject custom media, or override CTA
behavior while retaining baseline accessibility attributes.

## Development

- `npm test`: run Jest and React Testing Library suites.
- `npm run build`: compile the component library via Vite, producing ESM/CJS
  bundles and type declarations in `dist/`.

See `dep.mk` for details on how the top-level build copies the generated
artifacts into the monorepo distribution directories.
