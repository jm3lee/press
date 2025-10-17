/*
 * Copyright (c) Flashoffer Developers
 * Released under the MIT license.
 */

import { act, fireEvent, render, screen } from "@testing-library/react";

import { FlashofferThemeProvider } from "../../theme/FlashofferThemeProvider";
import { MultipleChoiceQuiz } from "../MultipleChoiceQuiz";
import type { MultipleChoiceQuizProps } from "../MultipleChoiceQuiz";
import { launchConfetti } from "../QuizCelebrations";

jest.mock("../QuizCelebrations", () => {
  const actual = jest.requireActual("../QuizCelebrations");
  return {
    ...actual,
    launchConfetti: jest.fn().mockResolvedValue(undefined)
  };
});

describe("MultipleChoiceQuiz", () => {
  const launchConfettiMock =
    launchConfetti as jest.MockedFunction<typeof launchConfetti>;

  beforeEach(() => {
    launchConfettiMock.mockClear();
  });

  const BASE_OPTIONS: MultipleChoiceQuizProps["options"] = [
    {
      id: "story",
      label: "Story taps forward",
      description: "Viewers who tap forward without exiting.",
      tally: 18
    },
    {
      id: "save",
      label: "Saves per reel",
      description: "Average number of saves across promoted reels.",
      tally: 42
    },
    {
      id: "session",
      label: "Average session duration",
      description: "Time spent engaging with bundled offers.",
      tally: 9
    }
  ];

  function renderQuiz(props: Partial<MultipleChoiceQuizProps> = {}) {
    return render(
      <FlashofferThemeProvider applyCssBaseline={false}>
        <MultipleChoiceQuiz
          question="Which metric indicates the strongest engagement lift?"
          helperText="Select the option that best demonstrates sustained performance."
          options={BASE_OPTIONS}
          correctOptionId="save"
          {...props}
        />
      </FlashofferThemeProvider>
    );
  }

  it("submits the selected answer and surfaces success feedback", () => {
    const handleAnswer = jest.fn();
    renderQuiz({ onAnswer: handleAnswer });

    fireEvent.click(
      screen.getByRole("radio", { name: /saves per reel/i })
    );
    fireEvent.click(screen.getByRole("button", { name: /check answer/i }));

    expect(handleAnswer).toHaveBeenCalledWith({
      optionId: "save",
      isCorrect: true
    });
    expect(
      screen.getByText(/great job! that answer is correct\./i)
    ).toBeInTheDocument();
  });

  it("triggers confetti when a correct answer is submitted", async () => {
    renderQuiz({ confetti: { enabled: true, preset: "streamers" } });

    fireEvent.click(
      screen.getByRole("radio", { name: /saves per reel/i })
    );

    await act(async () => {
      fireEvent.click(screen.getByRole("button", { name: /check answer/i }));
    });

    expect(launchConfettiMock).toHaveBeenCalledWith("streamers");
  });

  it("does not launch confetti for incorrect submissions", async () => {
    renderQuiz({ confetti: { enabled: true } });

    fireEvent.click(
      screen.getByRole("radio", { name: /story taps forward/i })
    );

    await act(async () => {
      fireEvent.click(screen.getByRole("button", { name: /check answer/i }));
    });

    expect(launchConfettiMock).not.toHaveBeenCalled();
  });

  it("renders the explanation when feedback is shown", () => {
    renderQuiz({ explanation: "The save rate exceeded projections." });

    fireEvent.click(
      screen.getByRole("radio", { name: /saves per reel/i })
    );
    fireEvent.click(screen.getByRole("button", { name: /check answer/i }));

    expect(
      screen.getByText(/the save rate exceeded projections\./i)
    ).toBeInTheDocument();
  });

  it("allows retrying incorrect responses", () => {
    renderQuiz();

    fireEvent.click(
      screen.getByRole("radio", { name: /story taps forward/i })
    );
    fireEvent.click(screen.getByRole("button", { name: /check answer/i }));

    expect(
      screen.getByText(/not quite. give it another look\./i)
    ).toBeInTheDocument();

    const tryAgainButton = screen.getByRole("button", { name: /try again/i });
    fireEvent.click(tryAgainButton);

    expect(
      screen.queryByText(/not quite. give it another look\./i)
    ).not.toBeInTheDocument();
    expect(
      (screen.getByRole("radio", { name: /story taps forward/i }) as HTMLInputElement)
        .checked
    ).toBe(false);
  });

  it("hides the correct answer highlight when retries are allowed", () => {
    renderQuiz();

    fireEvent.click(
      screen.getByRole("radio", { name: /story taps forward/i })
    );
    fireEvent.click(screen.getByRole("button", { name: /check answer/i }));

    const incorrectOptionLabel = screen
      .getByText(/story taps forward/i)
      .closest("label");
    const correctOptionLabel = screen
      .getByText(/saves per reel/i)
      .closest("label");

    expect(incorrectOptionLabel?.dataset.optionState).toBe("incorrect");
    expect(correctOptionLabel?.dataset.optionState).toBe("default");
  });

  it("reveals the correct answer when retries are disabled", () => {
    renderQuiz({ allowRetry: false });

    fireEvent.click(
      screen.getByRole("radio", { name: /story taps forward/i })
    );
    fireEvent.click(screen.getByRole("button", { name: /check answer/i }));

    const correctOptionLabel = screen
      .getByText(/saves per reel/i)
      .closest("label");

    expect(correctOptionLabel?.dataset.optionState).toBe("correct");
  });

  it("disables interactions and displays tallies when the quiz is closed", () => {
    const pastDeadline = new Date(Date.now() - 1000);
    renderQuiz({ endTime: pastDeadline });

    expect(screen.getByText(/this quiz closed on/i)).toBeInTheDocument();
    expect(
      screen.getByRole("radio", { name: /saves per reel/i })
    ).toBeDisabled();
    expect(
      screen.getByRole("button", { name: /check answer/i })
    ).toBeDisabled();
    expect(screen.getByText(/42 responses/i)).toBeInTheDocument();
    expect(
      screen.queryByRole("button", { name: /try again/i })
    ).not.toBeInTheDocument();
    expect(
      screen.queryByText(/Select the response that best answers the question./i)
    ).not.toBeInTheDocument();
  });

  it("automatically closes once the deadline passes", () => {
    jest.useFakeTimers();
    const now = new Date("2024-01-01T00:00:00Z");
    jest.setSystemTime(now);

    try {
      renderQuiz({ endTime: new Date(now.getTime() + 2500) });

      expect(
        screen.queryByText(/this quiz closed on/i)
      ).not.toBeInTheDocument();

      act(() => {
        jest.advanceTimersByTime(3000);
      });

      expect(screen.getByText(/this quiz closed on/i)).toBeInTheDocument();
    } finally {
      jest.useRealTimers();
    }
  });

  it.each([
    ["numeric", () => Date.now() - 5000],
    [
      "iso string",
      () => new Date(Date.now() - 5000).toISOString()
    ]
  ])("closes quizzes for %s endTime values", (_, resolveEndTime) => {
    jest.useFakeTimers();
    const now = new Date("2024-02-12T00:00:00Z");
    jest.setSystemTime(now);

    try {
      renderQuiz({ endTime: resolveEndTime() as Date | string | number });
      expect(screen.getByText(/this quiz closed on/i)).toBeInTheDocument();
    } finally {
      jest.useRealTimers();
    }
  });

  it("skips scheduling deadlines when the window object is unavailable", () => {
    jest.useFakeTimers();
    const originalWindow = globalThis.window;

    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    (globalThis as any).window = undefined;

    try {
      expect(() =>
        renderQuiz({ endTime: new Date(Date.now() + 5000) })
      ).not.toThrow();
    } finally {
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      (globalThis as any).window = originalWindow;
      jest.useRealTimers();
    }
  });

  it("logs a warning when confetti effects fail outside production", async () => {
    const confettiError = new Error("render-failure");
    launchConfettiMock.mockRejectedValueOnce(confettiError);
    const warnSpy = jest.spyOn(console, "warn").mockImplementation(() => {});

    try {
      renderQuiz({ confetti: { enabled: true } });

      fireEvent.click(
        screen.getByRole("radio", { name: /saves per reel/i })
      );

      await act(async () => {
        fireEvent.click(screen.getByRole("button", { name: /check answer/i }));
      });

      expect(warnSpy).toHaveBeenCalledWith(
        "Failed to launch quiz confetti",
        confettiError
      );
    } finally {
      launchConfettiMock.mockResolvedValue(undefined);
      warnSpy.mockRestore();
    }
  });

  it("ignores submit attempts when no option is selected", () => {
    const handleAnswer = jest.fn();
    renderQuiz({ onAnswer: handleAnswer });

    const submitButton = screen.getByRole("button", { name: /check answer/i });
    submitButton.removeAttribute("disabled");
    fireEvent.click(submitButton);

    expect(handleAnswer).not.toHaveBeenCalled();
  });

  it("prevents submissions once the quiz closes", () => {
    const handleAnswer = jest.fn();
    jest.useFakeTimers();
    const now = new Date("2024-03-10T00:00:00Z");
    jest.setSystemTime(now);

    try {
      renderQuiz({
        onAnswer: handleAnswer,
        endTime: new Date(now.getTime() + 1500)
      });

      fireEvent.click(
        screen.getByRole("radio", { name: /saves per reel/i })
      );

      act(() => {
        jest.advanceTimersByTime(2000);
      });

      const submitButton = screen.getByRole("button", { name: /check answer/i });
      expect(submitButton).toBeDisabled();
      submitButton.removeAttribute("disabled");
      fireEvent.click(submitButton);

      expect(handleAnswer).not.toHaveBeenCalled();
    } finally {
      jest.useRealTimers();
    }
  });

  it("shows a fallback helper message when helper text is omitted", () => {
    renderQuiz({ helperText: undefined });

    expect(
      screen.getByText(/select the response that best answers the question./i)
    ).toBeInTheDocument();
    expect(
      screen.queryByText(/sustained performance/i)
    ).not.toBeInTheDocument();
  });

  it("retains tallies when ignoring non-finite values", () => {
    const now = new Date(Date.now() - 1000);
    renderQuiz({
      endTime: now,
      options: [
        {
          id: "story",
          label: "Story taps forward",
          tally: Number.NaN
        },
        {
          id: "save",
          label: "Saves per reel",
          tally: 12
        }
      ]
    });

    expect(screen.getByText(/12 responses/i)).toBeInTheDocument();
    expect(screen.getByText(/100% of responses/i)).toBeInTheDocument();
  });

  it("renders a custom closure message when provided", () => {
    const closedCopy = "This quiz is now closed to new responses.";
    renderQuiz({
      endTime: new Date(Date.now() - 1000),
      closedMessage: closedCopy
    });

    expect(screen.getByText(closedCopy)).toBeInTheDocument();
  });
});
