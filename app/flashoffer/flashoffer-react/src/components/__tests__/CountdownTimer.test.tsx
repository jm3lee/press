/*
 * Copyright (c) Flashoffer Developers
 * Released under the MIT license.
 */

import { act, render, screen } from "@testing-library/react";

import { FlashofferThemeProvider } from "../../theme/FlashofferThemeProvider";
import type { FlashofferThemeProviderProps } from "../../theme/FlashofferThemeProvider";
import { CountdownTimer } from "../CountdownTimer";
import type { CountdownTimerProps } from "../CountdownTimer";

const NOW = new Date("2024-01-01T00:00:00Z");
const REMAINING_MS =
  ((2 * 24 + 5) * 60 * 60 + 6 * 60 + 7) * 1000; // 2d 5h 6m 7s

const ORIGINAL_FETCH = global.fetch;

describe("CountdownTimer", () => {
  beforeEach(() => {
    jest.useFakeTimers();
    jest.setSystemTime(NOW);
  });

  afterEach(() => {
    jest.useRealTimers();
    if (ORIGINAL_FETCH) {
      global.fetch = ORIGINAL_FETCH;
    } else {
      // eslint-disable-next-line @typescript-eslint/no-dynamic-delete -- test cleanup
      delete (global as { fetch?: typeof fetch }).fetch;
    }
    jest.resetAllMocks();
  });

  /**
   * Renders the countdown timer within the Flashoffer theme.
   *
   * @param props - Countdown timer overrides to apply during rendering.
   * @param providerProps - Theme provider overrides enabling palette testing.
   */
  function renderTimer(
    props: Partial<CountdownTimerProps> = {},
    providerProps: Partial<FlashofferThemeProviderProps> = {}
  ) {
    const baseProps: CountdownTimerProps = {
      timeRemainingMs: REMAINING_MS,
      ...props
    };

    return render(
      <FlashofferThemeProvider
        applyCssBaseline={false}
        {...providerProps}
      >
        <CountdownTimer {...baseProps} />
      </FlashofferThemeProvider>
    );
  }

  it("renders the remaining time segments", () => {
    renderTimer({ timeRemainingMs: REMAINING_MS });

    expect(
      screen.getByLabelText(/\d+ days remaining/i)
    ).toHaveTextContent("02");
    expect(
      screen.getByLabelText(/\d+ hours remaining/i)
    ).toHaveTextContent("05");
    expect(
      screen.getByLabelText(/\d+ minutes remaining/i)
    ).toHaveTextContent("06");
    expect(
      screen.getByLabelText(/\d+ seconds remaining/i)
    ).toHaveTextContent("07");
  });

  it("stops at zero once the deadline passes", () => {
    renderTimer({ timeRemainingMs: 2_000 });
    act(() => {
      jest.advanceTimersByTime(2_000);
    });

    expect(screen.getByLabelText(/seconds remaining/i)).toHaveTextContent("00");
    expect(screen.getByLabelText(/minutes remaining/i)).toHaveTextContent("00");
    expect(screen.getByLabelText(/hours remaining/i)).toHaveTextContent("00");
    expect(screen.getByLabelText(/days remaining/i)).toHaveTextContent("00");
  });

  it("highlights the remaining quantity when provided", () => {
    renderTimer({
      quantityRemaining: 42,
      quantityLabel: "kits left"
    });

    expect(screen.getByText(/kits left/i)).toBeInTheDocument();
    expect(screen.getByText("42")).toBeInTheDocument();
  });

  it("applies the active theme palette to urgency styling", () => {
    renderTimer(
      {},
      {
        themeOptions: {
          palette: {
            primary: { main: "#22c55e", contrastText: "#01220f" }
          }
        }
      }
    );

    expect(screen.getByRole("timer")).toHaveStyle(
      "border-color: rgba(34, 197, 94, 0.4)"
    );
  });

  it("fetches campaign time when a campaign identifier is provided", async () => {
    const responsePayload = { time_remaining_ms: 65_000 };
    global.fetch = jest
      .fn()
      .mockResolvedValue({
        ok: true,
        json: async () => responsePayload
      } as unknown as Response) as unknown as typeof fetch;

    renderTimer({ campaignId: "flashoffer-demo", timeRemainingMs: undefined });

    expect(global.fetch).toHaveBeenCalledWith(
      "/api/campaign/flashoffer-demo/time_remaining?ct=countdown-timer&cid=flashoffer-demo",
      expect.objectContaining({ method: "GET" })
    );

    await act(async () => {
      await Promise.resolve();
    });

    expect(screen.getByLabelText(/minutes remaining/i)).toHaveTextContent("01");
    expect(screen.getByLabelText(/seconds remaining/i)).toHaveTextContent("05");
  });

  it("renders zero when campaign time retrieval fails", async () => {
    global.fetch = jest
      .fn()
      .mockResolvedValue({
        ok: false,
        json: async () => ({})
      } as unknown as Response) as unknown as typeof fetch;

    renderTimer({ campaignId: "unknown", timeRemainingMs: undefined });

    await act(async () => {
      await Promise.resolve();
    });

    expect(screen.getByLabelText(/seconds remaining/i)).toHaveTextContent("00");
  });

  it("throws when neither campaign nor duration inputs are supplied", () => {
    expect(() => renderTimer({ timeRemainingMs: undefined })).toThrow(
      /requires either a campaignId, timeRemainingMs, or endTime/i
    );
  });
});
