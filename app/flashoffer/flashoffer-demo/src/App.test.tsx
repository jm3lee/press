/*
 * Copyright (c) Flashoffer Developers
 * Released under the MIT license.
 */

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

  it("renders the countdown timer showcase", async () => {
    render(<App />);

    expect(
      await screen.findByRole("heading", {
        level: 2,
        name: /drive urgency with countdowns/i
      })
    ).toBeInTheDocument();
    const timers = await screen.findAllByRole("timer");
    expect(timers.length).toBeGreaterThan(0);
  });

  it("renders the quiz showcase question", async () => {
    render(<App />);

    expect(
      await screen.findByRole("heading", {
        level: 2,
        name: /teach best practices with interactive quizzes/i
      })
    ).toBeInTheDocument();
    expect(
      await screen.findByRole("button", { name: /check answer/i })
    ).toBeInTheDocument();
    expect(
      await screen.findByText(/multiplechoicequiz mirrors the feel/i)
    ).toBeInTheDocument();
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

  it.each([
    ["spaciousLight", "rgba(29, 78, 216, 0.14)", "rgba(219, 39, 119, 0.18)"],
    ["spaciousDark", "rgba(96, 165, 250, 0.28)", "rgba(15, 23, 42, 0.85)"]
  ])(
    "updates the hero banner gradient tokens for the %s theme",
    async (preset, gradientStart, gradientStop) => {
      render(<App />);

      const paletteSelect = await screen.findByLabelText(
        /select theme palette/i
      );
      fireEvent.change(paletteSelect, { target: { value: preset } });

      const heroWrapper = (await screen.findByTestId("hero-banner-wrapper")) as HTMLElement;

      await waitFor(() => {
        expect(
          getComputedStyle(heroWrapper).getPropertyValue(
            "--flashoffer-hero-gradient-start"
          ).trim()
        ).toBe(gradientStart);
        expect(
          getComputedStyle(heroWrapper).getPropertyValue(
            "--flashoffer-hero-gradient-stop"
          ).trim()
        ).toBe(gradientStop);
      });
    }
  );
});
