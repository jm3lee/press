import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import App from "./App";

describe("Flashoffer demo", () => {
  it("renders the hero banner from the component library", () => {
    render(<App />);

    expect(screen.getAllByRole("banner").length).toBeGreaterThan(0);
    expect(
      screen.getByRole("heading", {
        level: 1,
        name: /coordinated offers/i
      })
    ).toBeInTheDocument();
    expect(
      screen.getAllByRole("link", { name: /explore flashoffer components/i }).length
    ).toBeGreaterThan(0);
  });

  it("renders preview cards and CTA examples", () => {
    render(<App />);

    expect(
      screen.getByRole("heading", {
        level: 2,
        name: /modular previews for any campaign/i
      })
    ).toBeInTheDocument();
    expect(
      screen.getAllByRole("link", { name: /explore flashoffer components/i }).length
    ).toBeGreaterThan(0);
    expect(screen.getAllByRole("article")).toHaveLength(3);
  });

  it("updates the hero banner gradient tokens for the midnight theme", async () => {
    render(<App />);

    const paletteSelect = screen.getByLabelText(/select theme palette/i);
    fireEvent.change(paletteSelect, { target: { value: "midnight" } });

    const heroBanner = await screen.findByRole("banner", {
      name: /launch coordinated offers/i
    });
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
