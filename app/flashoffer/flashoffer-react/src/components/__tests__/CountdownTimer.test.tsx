/*
 * Copyright (c) Flashoffer Developers
 * Released under the MIT license.
 */

import { render, screen } from "@testing-library/react";
import { act } from "react";

import { FlashofferThemeProvider } from "../../theme/FlashofferThemeProvider";
import type { FlashofferThemeProviderProps } from "../../theme/FlashofferThemeProvider";
import { CountdownTimer } from "../CountdownTimer";
import type { CountdownTimerProps } from "../CountdownTimer";

const NOW = new Date("2024-01-01T00:00:00Z");

describe("CountdownTimer", () => {
  const originalFetch = globalThis.fetch;

  beforeEach(() => {
    jest.useFakeTimers();
    jest.setSystemTime(NOW);
    jest.spyOn(console, "warn").mockImplementation(() => {});
  });

  afterEach(() => {
    jest.useRealTimers();
    globalThis.fetch = originalFetch;
    jest.restoreAllMocks();
  });

  function buildProps(
    overrides: Partial<CountdownTimerProps> = {}
  ): CountdownTimerProps {
    if (
      overrides.campaignId === undefined &&
      overrides.timeRemainingMs === undefined &&
      overrides.endTime === undefined
    ) {
      return { ...overrides, endTime: NOW } as CountdownTimerProps;
    }

    return overrides as CountdownTimerProps;
  }

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
    return render(
      <FlashofferThemeProvider
        applyCssBaseline={false}
        {...providerProps}
      >
        <CountdownTimer {...buildProps(props)} />
      </FlashofferThemeProvider>
    );
  }

  it("renders the remaining time segments", () => {
    const endTime = new Date("2024-01-03T05:06:07Z");
    renderTimer({ endTime });

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
    renderTimer({ endTime: new Date("2023-12-31T23:59:58Z") });
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

  it("requests campaign deadlines when a campaign identifier is supplied", async () => {
    const oneHourFromNow = new Date(NOW.getTime() + 3_600_000);
    const mockResponse = {
      ok: true,
      json: async () => ({ end_time: oneHourFromNow.toISOString() })
    } as unknown as Response;
    const fetchSpy = jest.fn().mockResolvedValue(mockResponse);
    globalThis.fetch = fetchSpy as unknown as typeof globalThis.fetch;

    renderTimer({ campaignId: "flashoffer-demo" });

    await act(async () => {
      await Promise.resolve();
    });

    expect(fetchSpy).toHaveBeenCalledWith(
      "/api/campaign/flashoffer-demo/end_time",
      expect.objectContaining({
        headers: { Accept: "application/json" }
      })
    );
    expect(screen.getByLabelText(/hours remaining/i)).toHaveTextContent("01");
  });

  it("falls back to zeroed segments when the campaign lookup fails", async () => {
    const failingFetch = jest
      .fn()
      .mockRejectedValue(new Error("network unavailable"));
    globalThis.fetch = failingFetch as unknown as typeof globalThis.fetch;

    renderTimer({ campaignId: "flashoffer-demo" });

    await act(async () => {
      await Promise.resolve();
    });

    expect(screen.getByLabelText(/seconds remaining/i)).toHaveTextContent("00");
    expect(screen.getByLabelText(/minutes remaining/i)).toHaveTextContent("00");
  });

  it("throws when combining a campaign identifier with an explicit deadline", () => {
    expect(() =>
      render(
        <FlashofferThemeProvider applyCssBaseline={false}>
          {/*
           * Casting keeps TypeScript satisfied while intentionally supplying
           * an invalid prop combination.
           */}
          <CountdownTimer
            {...({
              campaignId: "flashoffer-demo",
              endTime: NOW
            } as CountdownTimerProps)}
          />
        </FlashofferThemeProvider>
      )
    ).toThrow(/cannot mix campaignid/i);
  });

  it("throws when no campaign or time source is provided", () => {
    expect(() =>
      render(
        <FlashofferThemeProvider applyCssBaseline={false}>
          <CountdownTimer {...({} as CountdownTimerProps)} />
        </FlashofferThemeProvider>
      )
    ).toThrow(
      /requires either a campaignid or a timeremainingms\/endtime value/i
    );
  });
});
