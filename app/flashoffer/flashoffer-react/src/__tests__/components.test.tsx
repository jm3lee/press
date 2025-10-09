import { render, screen } from "@testing-library/react";
import Typography from "@mui/material/Typography";
import {
  FlashofferThemeProvider,
  createFlashofferTheme,
  createSpaciousTypographyTheme
} from "../index";
import { Footer } from "../components/Footer";
import { HeroBanner } from "../components/HeroBanner";
import { OutlineCtaButton } from "../components/OutlineCtaButton";
import { PreviewCard } from "../components/PreviewCard";
import { PrimaryCtaButton } from "../components/PrimaryCtaButton";
import { Section } from "../components/Section";
import { SectionHeader } from "../components/SectionHeader";
import { Figure } from "../components/Figure";
import { useTheme } from "@mui/material/styles";
import type { ReactElement } from "react";

describe("Flashoffer React primitives", () => {
  const renderWithTheme = (ui: ReactElement) =>
    render(
      <FlashofferThemeProvider applyCssBaseline={false}>
        {ui}
      </FlashofferThemeProvider>
    );

  it("renders primary CTA with default copy", () => {
    renderWithTheme(<PrimaryCtaButton />);
    expect(
      screen.getByRole("button", { name: /explore flashoffer components/i })
    ).toBeInTheDocument();
  });

  it("passes arbitrary props to CTA elements", () => {
    renderWithTheme(
      <PrimaryCtaButton
        href="https://presslabs.com"
        target="_blank"
        rel="noreferrer"
        label="Explore"
      />
    );
    const link = screen.getByRole("link", { name: "Explore" });
    expect(link).toHaveAttribute("href", "https://presslabs.com");
    expect(link).toHaveAttribute("target", "_blank");
    expect(link).toHaveAttribute("rel", "noreferrer");
  });

  it("renders hero banner with accessible labelling", () => {
    renderWithTheme(<HeroBanner />);
    const banner = screen.getByRole("banner");
    const headingId = banner.getAttribute("aria-labelledby");
    expect(headingId).toBeTruthy();
    if (headingId) {
      const heading = document.getElementById(headingId);
      expect(heading).not.toBeNull();
      expect(heading).toHaveTextContent(/coordinated offers/i);
    }
    expect(banner).toHaveAttribute("aria-describedby");
    expect(
      screen.getByRole("link", { name: /explore flashoffer components/i })
    ).toBeInTheDocument();
    expect(
      screen.getByRole("link", { name: /contact support/i })
    ).toBeInTheDocument();
  });

  it("allows hero banner CTA overrides", () => {
    renderWithTheme(
      <HeroBanner
        primaryCta={{ label: "Start trial" }}
        secondaryCta={{ label: "Contact sales" }}
      />
    );
    expect(screen.getByRole("button", { name: "Start trial" })).toBeVisible();
    expect(
      screen.getByRole("button", { name: "Contact sales" })
    ).toBeVisible();
  });

  it("renders supporting components with defaults", () => {
    renderWithTheme(
      <>
        <Section />
        <SectionHeader />
        <PreviewCard />
        <Footer />
      </>
    );
    expect(
      screen.getAllByRole("heading", {
        level: 2,
        name: /reusable content blocks/i
      })
    ).toHaveLength(2);
    expect(
      screen.getByRole("heading", { level: 3, name: /preview a flashoffer/i })
    ).toBeInTheDocument();
    expect(screen.getByRole("contentinfo")).toBeInTheDocument();
    expect(screen.getAllByRole("link").length).toBeGreaterThanOrEqual(1);
  });

  it("renders SectionHeader defaults when props are omitted", () => {
    renderWithTheme(<SectionHeader />);

    expect(
      screen.getByRole("heading", {
        level: 2,
        name: /reusable content blocks/i
      })
    ).toBeVisible();
    expect(screen.getByText("FLASHOFFER")).toBeVisible();
  });

  it("aligns SectionHeader content when left-aligned", () => {
    renderWithTheme(
      <SectionHeader align="left" eyebrow="Highlights" title="Aligned" />
    );

    const heading = screen.getByRole("heading", { level: 2, name: "Aligned" });
    const header = heading.closest("header");
    expect(header).not.toBeNull();
    expect(header).toHaveStyle({ textAlign: "left" });
    expect(header).toHaveStyle({ alignItems: "flex-start" });
  });

  it("renders supplied children inside section", () => {
    renderWithTheme(
      <Section align="left" title="Release highlights">
        <Typography>First paragraph</Typography>
        <Typography>Second paragraph</Typography>
      </Section>
    );

    expect(
      screen.getByRole("heading", { level: 2, name: "Release highlights" })
    ).toBeVisible();
    const paragraphs = screen.getAllByText(/paragraph$/);
    expect(paragraphs).toHaveLength(2);
  });

  it("applies alignment styles to section copy", () => {
    renderWithTheme(
      <Section align="left" title="Aligned section">
        <Typography>Aligned content</Typography>
      </Section>
    );

    const heading = screen.getByRole("heading", { level: 2, name: "Aligned section" });
    const section = heading.closest("section");
    expect(section).not.toBeNull();
    expect(section).toHaveStyle({ textAlign: "left" });
  });

  it("supports Outline CTA default label", () => {
    renderWithTheme(<OutlineCtaButton />);
    expect(
      screen.getByRole("button", { name: /contact support/i })
    ).toBeInTheDocument();
  });

  it("renders figure with empty defaults", () => {
    const { container } = renderWithTheme(
      <Figure src="https://example.com/test.png" />
    );
    const image = container.querySelector("img");
    if (!(image instanceof HTMLImageElement)) {
      throw new Error("Expected figure to render an image element");
    }
    expect(image).toHaveAttribute("alt", "");
    expect(image).toHaveAttribute("src", "https://example.com/test.png");
    const caption = container.querySelector("figcaption");
    expect(caption).not.toBeNull();
    expect(caption?.textContent).toBe("");
  });

  it("supports custom figure caption", () => {
    renderWithTheme(
      <Figure
        src="https://example.com/test.png"
        alt="Dashboard screenshot"
        caption="Flashoffer dashboard overview"
      />
    );
    expect(
      screen.getByText("Flashoffer dashboard overview")
    ).toBeInTheDocument();
    expect(
      screen.getByRole("img", { name: "Dashboard screenshot" })
    ).toBeInTheDocument();
  });

  it("exposes theme factory for overrides", () => {
    const theme = createFlashofferTheme({
      palette: { primary: { main: "#123456" } }
    });
    expect(theme.palette.primary.main).toBe("#123456");
  });

  it("offers spacious typography theme variants", () => {
    const lightTheme = createSpaciousTypographyTheme("light");
    const darkTheme = createSpaciousTypographyTheme("dark");

    expect(lightTheme.palette.mode).toBe("light");
    expect(lightTheme.typography.body1?.lineHeight).toBe(1.75);
    expect(darkTheme.palette.mode).toBe("dark");
    expect(darkTheme.palette.background.default).toBe("#0b1120");
  });

  it("propagates custom theme options through provider", () => {
    function ThemeProbe() {
      const theme = useTheme();
      return (
        <span
          data-testid="theme-probe"
          data-color={theme.palette.secondary.main}
        />
      );
    }

    render(
      <FlashofferThemeProvider
        applyCssBaseline={false}
        themeOptions={{ palette: { secondary: { main: "#ff00aa" } } }}
      >
        <ThemeProbe />
      </FlashofferThemeProvider>
    );

    expect(screen.getByTestId("theme-probe")).toHaveAttribute(
      "data-color",
      "#ff00aa"
    );
  });

  it("allows selecting the spacious typography preset", () => {
    function ThemeProbe() {
      const theme = useTheme();
      return (
        <span
          data-testid="spacious-typography"
          data-line-height={theme.typography.body1?.lineHeight}
          data-background={theme.palette.background.default}
        />
      );
    }

    render(
      <FlashofferThemeProvider
        applyCssBaseline={false}
        preset="spaciousTypography"
        colorMode="dark"
      >
        <ThemeProbe />
      </FlashofferThemeProvider>
    );

    const probe = screen.getByTestId("spacious-typography");
    expect(probe).toHaveAttribute("data-line-height", "1.75");
    expect(probe).toHaveAttribute("data-background", "#0b1120");
  });
});
