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

`FlashofferThemeProvider` merges any supplied Material UI `ThemeOptions` with
the baseline palette. Use the `preset` prop to activate opinionated design
systems that ship with the library. The `colorMode` prop toggles between light
and dark variants when a preset exposes them. For more granular control, call
`createFlashofferTheme` and pass the resulting theme to your own
`ThemeProvider` instance. The component primitives respect CSS tokens such as
`--flashoffer-color-primary` and `--flashoffer-font-family`, enabling runtime
theming through global styles.

When you need direct access to preset factories outside of the Flashoffer
provider, import helpers such as `createSunriseGlowTheme`,
`createMidnightPulseTheme`, `createOceanBreezeTheme`,
`createForestCanopyTheme`, or `createMonochromeFocusTheme`. Each factory
accepts an optional `ThemeOptions` object and palette mode so host
applications can extend the presets while keeping gradients and typography
consistent with Flashoffer landing pages.

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

To start from the spacious typography preset rather than the default palette,
pass the preset into the provider or derive a standalone theme with
`createSpaciousTypographyTheme`.

```tsx
import { ThemeProvider } from "@mui/material/styles";
import {
  FlashofferThemeProvider,
  createSpaciousTypographyTheme
} from "flashoffer-react";

export function SpaciousLayout({ children }: { children: React.ReactNode }) {
  return (
    <FlashofferThemeProvider
      preset="spaciousTypography"
      colorMode="dark"
      themeOptions={{ typography: { fontSize: 18 } }}
    >
      {children}
    </FlashofferThemeProvider>
  );
}

export function SpaciousThemeProvider({
  children
}: {
  children: React.ReactNode;
}) {
  const theme = createSpaciousTypographyTheme("dark", {
    typography: { fontSize: 18 }
  });
  return <ThemeProvider theme={theme}>{children}</ThemeProvider>;
}
```

Flashoffer React now ships with seven presets tuned for common storytelling
needs:

- `default`: Balanced marketing palette with blue primary accents.
- `spaciousTypography`: Expanded rhythm for editorial hero sections.
- `sunriseGlow`: Warm gradients suited to seasonal or celebratory launches.
- `midnightPulse`: Neon-on-dark treatment ideal for cinematic promotions.
- `oceanBreeze`: Teal palette that feels calm for travel and wellness content.
- `forestCanopy`: Verdant spectrum designed for sustainability narratives.
- `monochromeFocus`: High-contrast monochrome with minimalist detailing.

To experiment with one of the new presets without additional overrides, pass
the preset name directly to the provider:

```tsx
import { FlashofferThemeProvider, HeroBanner } from "flashoffer-react";

export function SeasonalSpotlight() {
  return (
    <FlashofferThemeProvider preset="sunriseGlow">
      <HeroBanner />
    </FlashofferThemeProvider>
  );
}
```

### Component reference

Each component ships with sensible defaults that marketing teams can override
incrementally. All props are optional unless noted otherwise and forward
arbitrary attributes to the underlying Material UI primitive.

- **`PrimaryCtaButton`** – High-emphasis call-to-action rendered as a contained
  button. Provide `label` or custom `children`, and pass any Material UI
  `ButtonProps` (for example `href`, `onClick`, or `startIcon`).
- **`OutlineCtaButton`** – Low-emphasis companion CTA that mirrors the primary
  button API but renders as an outlined variant.
- **`HeroBanner`** – Promotional hero section that combines headline, subtitle,
  and CTA buttons. Set `align="left"` to left-align copy, pass `media` to render
  an illustration, and override `primaryCta`/`secondaryCta` with button props or
  disable the secondary button by supplying `null`.
- **`SectionHeader`** – Standalone heading stack with optional `eyebrow` and
  `title` slots. Defaults render the `"FLASHOFFER"` eyebrow and the "Launch
  faster with reusable content blocks." headline. Use `align="center"`
  (default) or `align="left"` to adjust layout.
- **`Section`** – High-level wrapper that renders `SectionHeader` plus optional
  supporting children. Inherits the same defaults and accepts all
  `SectionHeader` props alongside an optional `id` for anchor linking.
  Render supporting content as natural React children instead of collecting
  paragraphs in arrays; the component handles spacing itself.

  ```tsx
  <Section eyebrow="Customers" title="Loved by operators">
    <p>Flashoffer's automation eliminates manual proposal work.</p>
    <p>Integrate your CRM to close deals faster.</p>
  </Section>
  ```
- **`PreviewCard`** – Feature preview card with optional media and CTA row.
  Provide `primaryCta`/`secondaryCta` props to render button controls, or leave
  them undefined for a purely informational card.
- **`MultipleChoiceQuiz`** – Lightweight quiz block that renders selectable
  answers, highlights the chosen option, and exposes an `onSubmit` callback for
  instrumentation. Use it to capture lightweight intent before handing a lead
  to sales tooling.
- **`CountdownTimer`** – Countdown surface that showcases urgency copy, time
  segments, and optional quantity remaining. Persist offer deadlines in UTC,
  convert them to the viewer's local time before display, and pass the UTC
  timestamp to `endTime` so marketing pages behave consistently worldwide.
- **`Figure`** – Responsive image container that preserves aspect ratio and
  renders an optional caption. Use `imgProps` to forward attributes such as
  `loading="lazy"` or `width`.
- **`InstagramEngagementSection`** – Instagram-style engagement demo that
  renders a Reels-inspired card with heart and share icon buttons. Wrap the
  component in `EngagementProvider` so likes and shares emit interaction events
  alongside view tracking for the mock post.
- **`Footer`** – Content info footer that renders navigation links followed by
  attribution copy. Customize the `links` array or `copyrightText` while the
  layout stays consistent.

### Analytics helpers

`flashoffer-react` also ships instrumentation utilities that record viewability
and interaction events. The helpers expose consistent metadata for downstream
analytics services and gracefully degrade when browser APIs are unavailable.

Wrap the subtree you want to measure in an `EngagementProvider`. The provider
requires a `site` identifier and can optionally post batches to an HTTP
`endpoint`.

```tsx
import {
  EngagementProvider,
  AutoTrack,
  ViewTracker,
  useRecordInteraction,
} from "flashoffer-react";

export function LandingWithAnalytics() {
  const recordInteraction = useRecordInteraction("primary-cta");

  return (
    <EngagementProvider site="marketing-site" endpoint="/api/events">
      <AutoTrack />
      <ViewTracker trackId="hero">
        <HeroBanner
          primaryCta={{ onClick: () => recordInteraction() }}
          secondaryCta={null}
        />
      </ViewTracker>
    </EngagementProvider>
  );
}
```

- **`EngagementProvider`** tracks viewport visibility, scroll depth, and user
  activity. Control sampling with `viewThresholds`, `scrollThresholds`, and
  `heartbeatInterval`, tune inactivity handling with `idleTimeout`, adjust
  batch sizing through `maxBatch`, or disable network flushes entirely by
  setting `flushInterval={null}` when you only need in-memory metrics.
- **`AutoTrack`** watches the DOM for elements marked with `data-track-id`
  attributes. It attaches observers automatically and reads optional
  `data-track-label`/`data-track-meta` attributes for enriched metadata.
- **`ViewTracker`** attaches view tracking to a specific element. Use the
  `useViewTracker` hook to attach the same behavior to custom components.
- **`useRecordInteraction`** returns a callback that records click or custom
  interactions. Call it manually or wire it into event handlers.
- **`EventConsole`** polls a REST endpoint that returns captured engagement
  events and renders them inside a developer-focused console, which is helpful
  when verifying instrumentation in staging environments.

## API documentation

Run the TypeDoc pipeline to generate Markdown reference files for every
component and helper exported from the library. The output lands in
`docs/flashoffer-react/reference` so the Press documentation build can surface
the latest props and usage guidance.

```bash
npm run docs
```

The command reads configuration from `typedoc.json` and reuses the standard
TypeScript project settings defined in `tsconfig.docs.json`.

## Development

- `npm test`: run Jest and React Testing Library suites.
- `npm run build`: compile the component library via Vite, producing ESM/CJS
  bundles and type declarations in `dist/`.
- `npm run lint`: surface cyclomatic complexity warnings (`complexity > 7`)
  across the TypeScript sources so risky functions can be refactored early.
- `npm run lint:ci`: run the ESLint gate used in CI, which fails if any
  function exceeds the hard ceiling of `complexity > 10`.

See `dep.mk` for details on how the top-level build copies the generated
artifacts into the monorepo distribution directories.
