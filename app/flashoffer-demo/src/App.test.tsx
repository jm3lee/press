import { render, screen } from "@testing-library/react";
import App from "./App";

describe("Flashoffer demo", () => {
  it("renders the hero banner from the component library", async () => {
    render(<App />);

    expect((await screen.findAllByRole("banner")).length).toBeGreaterThan(0);
    expect(
      await screen.findByRole("heading", {
        level: 1,
        name: /coordinated offers/i
      })
    ).toBeInTheDocument();
    expect(
      (await screen.findAllByRole("link", { name: /explore flashoffer components/i })).length
    ).toBeGreaterThan(0);
  });

  it("renders preview cards and CTA examples", async () => {
    render(<App />);

    expect(
      await screen.findByRole("heading", {
        level: 2,
        name: /modular previews for any campaign/i
      })
    ).toBeInTheDocument();
    expect(
      (await screen.findAllByRole("link", { name: /explore flashoffer components/i })).length
    ).toBeGreaterThan(0);
    expect(await screen.findAllByRole("article")).toHaveLength(3);
  });
});
