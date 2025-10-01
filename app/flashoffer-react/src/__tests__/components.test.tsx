import { render, screen } from "@testing-library/react";
import { FlashofferThemeProvider, createFlashofferTheme } from "../index";
import { Footer } from "../components/Footer";
import { HeroBanner } from "../components/HeroBanner";
import { OutlineCtaButton } from "../components/OutlineCtaButton";
import { PreviewCard } from "../components/PreviewCard";
import { PrimaryCtaButton } from "../components/PrimaryCtaButton";
import { Section } from "../components/Section";
import { SectionHeader } from "../components/SectionHeader";
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

  it("renders supplied paragraphs inside section", () => {
    renderWithTheme(
      <Section
        align="left"
        title="Release highlights"
        paragraphs={["First paragraph", "Second paragraph"]}
      />
    );

    expect(
      screen.getByRole("heading", { level: 2, name: "Release highlights" })
    ).toBeVisible();
    const paragraphs = screen.getAllByText(/paragraph$/);
    expect(paragraphs).toHaveLength(2);
    paragraphs.forEach((paragraph) => {
      expect(paragraph.tagName.toLowerCase()).toBe("p");
    });
  });

  it("applies themed palette colors to section copy", () => {
    render(
      <FlashofferThemeProvider
        applyCssBaseline={false}
        themeOptions={{
          palette: { text: { primary: "#111827", secondary: "#0ea5e9" } }
        }}
      >
        <Section title="Themed section" paragraphs={["Custom paragraph"]} />
      </FlashofferThemeProvider>
    );

    const paragraph = screen.getByText("Custom paragraph");
    expect(window.getComputedStyle(paragraph).color).toBe("rgb(14, 165, 233)");
  });

  it("supports Outline CTA default label", () => {
    renderWithTheme(<OutlineCtaButton />);
    expect(
      screen.getByRole("button", { name: /contact support/i })
    ).toBeInTheDocument();
  });

  it("exposes theme factory for overrides", () => {
    const theme = createFlashofferTheme({
      palette: { primary: { main: "#123456" } }
    });
    expect(theme.palette.primary.main).toBe("#123456");
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
});
