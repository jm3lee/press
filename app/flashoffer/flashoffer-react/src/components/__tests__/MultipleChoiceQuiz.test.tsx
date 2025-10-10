/*
 * Copyright (c) Flashoffer Developers
 * Released under the MIT license.
 */

import { act, fireEvent, render, screen } from "@testing-library/react";

import { FlashofferThemeProvider } from "../../theme/FlashofferThemeProvider";
import { MultipleChoiceQuiz } from "../MultipleChoiceQuiz";
import type { MultipleChoiceQuizProps } from "../MultipleChoiceQuiz";

describe("MultipleChoiceQuiz", () => {
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
});
