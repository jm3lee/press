/*
 * Copyright (c) Flashoffer Developers
 * Released under the MIT license.
 */

import { render, waitFor } from "@testing-library/react";
import AutoTrack from "../AutoTrack";

const detachElement = jest.fn<void, [Element | null]>();
const attachElement = jest.fn<
  () => void,
  [string, Element | null, Record<string, unknown> | undefined]
>();

jest.mock("../EngagementProvider", () => ({
  useEngagement: () => ({
    attachElement,
    detachElement,
  }),
}));

describe("AutoTrack", () => {
  beforeEach(() => {
    attachElement.mockReset();
    detachElement.mockReset();
    attachElement.mockImplementation((_, element) => () => {
      detachElement(element);
    });
  });

  afterEach(() => {
    document.body.innerHTML = "";
  });

  it("reconnects tracked nodes once when metadata changes", async () => {
    const container = document.createElement("div");
    container.innerHTML = `
      <div data-track-id="alpha" data-track-meta='{"palette":"ocean"}'></div>
      <section data-track-id="beta" data-track-meta='{"palette":"ocean"}'>
        <button data-track-id="beta-cta" data-track-meta='{"palette":"ocean"}'>CTA</button>
      </section>
    `;
    document.body.appendChild(container);

    const view = render(<AutoTrack />);

    await waitFor(() => {
      expect(attachElement).toHaveBeenCalledTimes(3);
    });

    attachElement.mockClear();
    detachElement.mockClear();

    const trackedNodes = Array.from(
      document.querySelectorAll<HTMLElement>("[data-track-id]")
    );
    trackedNodes.forEach((node, index) => {
      node.setAttribute(
        "data-track-meta",
        JSON.stringify({ palette: "sunset", index })
      );
    });

    await waitFor(() => {
      expect(detachElement).toHaveBeenCalledTimes(trackedNodes.length);
      expect(attachElement).toHaveBeenCalledTimes(trackedNodes.length);
    });

    await waitFor(() => {
      expect(detachElement).toHaveBeenCalledTimes(trackedNodes.length);
    });

    view.unmount();
  });
});
