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

describe("CountdownTimer", () => {
  beforeEach(() => {
    jest.useFakeTimers();
    jest.setSystemTime(NOW);
  });

  afterEach(() => {
    jest.useRealTimers();
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
    return render(
      <FlashofferThemeProvider
        applyCssBaseline={false}
        {...providerProps}
      >
        <CountdownTimer endTime={NOW} {...props} />
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
});
