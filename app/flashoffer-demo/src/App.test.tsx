import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import App from "./App";

describe("Flashoffer demo", () => {
  it("renders the hero banner from the component library", async () => {
    render(<App />);

    const heroBanners = await screen.findAllByRole("banner");
    expect(heroBanners.length).toBeGreaterThan(0);
    expect(
      await screen.findByRole("heading", {
        level: 1,
        name: /coordinated offers/i
      })
    ).toBeInTheDocument();
    const primaryCtas = await screen.findAllByRole("link", {
      name: /explore flashoffer components/i
    });
    expect(primaryCtas.length).toBeGreaterThan(0);
  });

  it("renders preview cards and CTA examples", async () => {
    render(<App />);

    expect(
      await screen.findByRole("heading", {
        level: 2,
        name: /modular previews for any campaign/i
      })
    ).toBeInTheDocument();
    const previewLinks = await screen.findAllByRole("link", {
      name: /explore flashoffer components/i
    });
    expect(previewLinks.length).toBeGreaterThan(0);
    const previewCards = await screen.findAllByRole("article");
    expect(previewCards).toHaveLength(3);
  });

  it("updates the hero banner gradient tokens for the midnight theme", async () => {
    render(<App />);

    const paletteSelect = await screen.findByLabelText(/select theme palette/i);
    fireEvent.change(paletteSelect, { target: { value: "midnight" } });

    const heroBanner = await screen.findByRole("banner", {
      name: /launch coordinated offers/i
    });
    expect(heroBanner).toBeInTheDocument();
    const heroWrapper = document.querySelector(
      '[data-track-id="hero-banner"]'
    ) as HTMLElement | null;

    expect(heroWrapper).not.toBeNull();

    await waitFor(() => {
      expect(
        getComputedStyle(heroWrapper as HTMLElement).getPropertyValue(
          "--flashoffer-hero-gradient-start"
        ).trim()
      ).toBe("#1e293b");
      expect(
        getComputedStyle(heroWrapper as HTMLElement).getPropertyValue(
          "--flashoffer-hero-gradient-stop"
        ).trim()
      ).toBe("#0f172a");
    });
  });
});
