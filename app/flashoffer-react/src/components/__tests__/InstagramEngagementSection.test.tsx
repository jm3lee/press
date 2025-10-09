/*
 * Copyright (c) Flashoffer Developers
 * Released under the MIT license.
 */

import { render, screen, fireEvent } from "@testing-library/react";

import { EngagementProvider } from "../../analytics";
import { FlashofferThemeProvider } from "../../theme/FlashofferThemeProvider";
import { InstagramEngagementSection } from "../InstagramEngagementSection";

describe("InstagramEngagementSection", () => {
  function renderSection() {
    return render(
      <FlashofferThemeProvider applyCssBaseline={false}>
        <EngagementProvider site="test-site" flushInterval={null}>
          <InstagramEngagementSection initialLikes={120} saves={12} />
        </EngagementProvider>
      </FlashofferThemeProvider>
    );
  }

  it("toggles the like button state", () => {
    renderSection();

    const likeButton = screen.getByRole("button", { name: /like reel/i });
    expect(likeButton).toHaveAttribute("aria-pressed", "false");

    fireEvent.click(likeButton);
    expect(likeButton).toHaveAttribute("aria-pressed", "true");
    expect(screen.getByText("121 likes")).toBeInTheDocument();

    fireEvent.click(likeButton);
    expect(likeButton).toHaveAttribute("aria-pressed", "false");
    expect(screen.getByText("120 likes")).toBeInTheDocument();
  });

  it("renders the share button affordance", () => {
    renderSection();

    expect(
      screen.getByRole("button", { name: /share to instagram stories/i })
    ).toBeInTheDocument();
  });
});
