import { render, screen } from "@testing-library/react";
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
});
