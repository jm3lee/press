/*
 * Copyright (c) Flashoffer Developers
 * Released under the MIT license.
 */

import Alert from "@mui/material/Alert";
import Button from "@mui/material/Button";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import FormControl from "@mui/material/FormControl";
import FormControlLabel from "@mui/material/FormControlLabel";
import FormHelperText from "@mui/material/FormHelperText";
import FormLabel from "@mui/material/FormLabel";
import Radio from "@mui/material/Radio";
import RadioGroup from "@mui/material/RadioGroup";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";
import { alpha } from "@mui/material/styles";
import type { Theme } from "@mui/material/styles";
import { useCallback, useEffect, useId, useMemo, useRef, useState } from "react";
import type { ChangeEvent, ReactNode } from "react";

import type { QuizConfettiOptions } from "./QuizCelebrations";
import { launchConfetti, resolveConfettiOptions } from "./QuizCelebrations";

export interface MultipleChoiceOption {
  /** Unique identifier used for option selection. */
  id: string;
  /** Primary label describing the answer choice. */
  label: ReactNode;
  /** Optional supporting copy rendered beneath the label. */
  description?: ReactNode;
  /** Number of submissions associated with the answer choice. */
  tally?: number;
}

export interface MultipleChoiceAnswer {
  /** Identifier of the selected option. */
  optionId: string;
  /** Whether the option matches the configured correct answer. */
  isCorrect?: boolean;
}

export interface MultipleChoiceQuizProps {
  /** Question or prompt displayed above the answer list. */
  question: ReactNode;
  /** Collection of answer choices presented to the learner. */
  options: MultipleChoiceOption[];
  /** Helper text that expands on the question prompt. */
  helperText?: ReactNode;
  /** Identifier representing the correct answer choice. */
  correctOptionId?: string;
  /** Additional explanation surfaced once the learner submits. */
  explanation?: ReactNode;
  /** Custom message rendered for successful submissions. */
  successMessage?: ReactNode;
  /** Custom message rendered when the submission is incorrect. */
  errorMessage?: ReactNode;
  /** Invoked each time the learner submits an answer. */
  onAnswer?: (answer: MultipleChoiceAnswer) => void;
  /** Label for the submit button. */
  submitLabel?: string;
  /** Label for the retry button. */
  tryAgainLabel?: string;
  /**
   * Allows additional attempts when the initial submission is incorrect.
   * Defaults to true when a correct answer is configured.
   */
  allowRetry?: boolean;
  /** Disables interactions with the quiz component. */
  disabled?: boolean;
  /** Deadline after which the quiz stops accepting new responses. */
  endTime?: Date | string | number;
  /** Custom message announced when the quiz is closed. */
  closedMessage?: ReactNode;
  /** Configures confetti celebrations for correct answers. */
  confetti?: QuizConfettiOptions;
}

const DEFAULT_SUCCESS = "Great job! That answer is correct.";
const DEFAULT_ERROR = "Not quite. Give it another look.";
const DEFAULT_SUBMIT_LABEL = "Check answer";
const DEFAULT_TRY_AGAIN_LABEL = "Try again";

type OptionState = "correct" | "incorrect" | "selected" | "default";

interface QuizStateConfig {
  allowRetry?: boolean;
  correctOptionId?: string;
  disabled: boolean;
}

interface QuizInteractionState {
  selectedId: string | null;
  submittedId: string | null;
}

interface QuizStateSnapshot {
  hasSubmitted: boolean;
  evaluation: boolean | undefined;
  disableChoices: boolean;
  showFeedback: boolean;
  revealCorrectAnswer: boolean;
  submitDisabled: boolean;
  showRetryButton: boolean;
}

/**
 * Derives quiz behaviour flags from author configuration and user input.
 */
function useQuizState(
  { allowRetry, correctOptionId, disabled }: QuizStateConfig,
  { selectedId, submittedId }: QuizInteractionState
): QuizStateSnapshot {
  const resolvedAllowRetry = useMemo(() => {
    if (typeof allowRetry === "boolean") {
      return allowRetry;
    }
    return Boolean(correctOptionId);
  }, [allowRetry, correctOptionId]);

  const hasSubmitted = submittedId !== null;

  const evaluation = useMemo(() => {
    if (!correctOptionId || !hasSubmitted || !submittedId) {
      return undefined;
    }
    return submittedId === correctOptionId;
  }, [correctOptionId, hasSubmitted, submittedId]);

  const disableChoices = useMemo(() => {
    if (disabled) {
      return true;
    }
    if (!hasSubmitted) {
      return false;
    }
    if (!resolvedAllowRetry) {
      return true;
    }
    return evaluation === true;
  }, [disabled, evaluation, hasSubmitted, resolvedAllowRetry]);

  const showFeedback = Boolean(hasSubmitted && correctOptionId);
  const revealCorrectAnswer =
    showFeedback && (evaluation === true || !resolvedAllowRetry);
  const submitDisabled =
    !selectedId ||
    disabled ||
    (hasSubmitted && !resolvedAllowRetry) ||
    evaluation === true;
  const showRetryButton =
    resolvedAllowRetry && hasSubmitted && evaluation !== true && !disabled;

  return {
    hasSubmitted,
    evaluation,
    disableChoices,
    showFeedback,
    revealCorrectAnswer,
    submitDisabled,
    showRetryButton
  };
}

interface OptionStateInput {
  optionId: string;
  selectedId: string | null;
  submittedId: string | null;
  correctOptionId?: string;
  showFeedback: boolean;
  revealCorrectAnswer: boolean;
}

interface OptionStateSnapshot {
  highlight: boolean;
  highlightAnswer: boolean;
  optionState: OptionState;
  isSelected: boolean;
}

/**
 * Computes styling state for a single option in the quiz.
 */
function resolveOptionState({
  optionId,
  selectedId,
  submittedId,
  correctOptionId,
  showFeedback,
  revealCorrectAnswer
}: OptionStateInput): OptionStateSnapshot {
  const isSelected = selectedId === optionId;
  const isAnswer = correctOptionId === optionId;
  const isSubmittedSelection = submittedId === optionId;
  const highlightSelection = showFeedback && isSubmittedSelection;
  const highlightAnswer = revealCorrectAnswer && isAnswer;
  const highlight = highlightAnswer || highlightSelection;

  let optionState: OptionState = "default";
  if (highlight) {
    optionState = highlightAnswer ? "correct" : "incorrect";
  } else if (isSelected) {
    optionState = "selected";
  }

  return {
    highlight,
    highlightAnswer,
    optionState,
    isSelected
  };
}

interface OptionVisualSnapshot {
  highlight: boolean;
  highlightAnswer: boolean;
  isSelected: boolean;
}

/**
 * Derives the base color used when an option is highlighted.
 */
function resolveOptionHighlightColor(
  theme: Theme,
  { highlightAnswer }: OptionVisualSnapshot
): string {
  return highlightAnswer
    ? theme.palette.success.main
    : theme.palette.error.main;
}

/**
 * Computes the border color for an option without relying on nested ternaries.
 */
function resolveOptionBorderColor(
  theme: Theme,
  snapshot: OptionVisualSnapshot
): string {
  if (snapshot.highlight) {
    return resolveOptionHighlightColor(theme, snapshot);
  }
  if (snapshot.isSelected) {
    return theme.palette.primary.main;
  }
  return theme.palette.divider;
}

/**
 * Computes the option background color based on highlight state.
 */
function resolveOptionBackgroundColor(
  theme: Theme,
  snapshot: OptionVisualSnapshot
): string {
  if (!snapshot.highlight) {
    return theme.palette.background.paper;
  }
  const highlightColor = resolveOptionHighlightColor(theme, snapshot);
  return alpha(highlightColor, 0.08);
}

interface OptionContentProps {
  option: MultipleChoiceOption;
  showTallies: boolean;
  totalTallies: number;
}

/**
 * Renders the visible label block for a quiz option.
 */
function OptionContent({
  option,
  showTallies,
  totalTallies
}: OptionContentProps): ReactNode {
  const labelBlock = (
    <Stack spacing={option.description ? 0.5 : 0} flex={1} minWidth={0}>
      <Typography variant="body1" fontWeight={600}>
        {option.label}
      </Typography>
      {option.description ? (
        <Typography variant="body2" color="text.secondary">
          {option.description}
        </Typography>
      ) : null}
    </Stack>
  );

  if (!showTallies) {
    return labelBlock;
  }

  const tally = Math.max(0, option.tally ?? 0);
  const countFormatter =
    typeof Intl !== "undefined"
      ? new Intl.NumberFormat(undefined, { maximumFractionDigits: 0 })
      : null;
  const percentFormatter =
    typeof Intl !== "undefined"
      ? new Intl.NumberFormat(undefined, { maximumFractionDigits: 0 })
      : null;
  const formattedCount = countFormatter ? countFormatter.format(tally) : `${tally}`;
  const responseLabel = tally === 1 ? "response" : "responses";
  const percentage = totalTallies > 0 ? (tally / totalTallies) * 100 : 0;
  const formattedPercent = percentFormatter
    ? percentFormatter.format(percentage)
    : `${Math.round(percentage)}`;

  return (
    <Stack
      direction="row"
      spacing={2}
      justifyContent="space-between"
      alignItems="flex-start"
      sx={{ width: "100%" }}
    >
      {labelBlock}
      <Stack spacing={0} alignItems="flex-end">
        <Typography variant="body2" fontWeight={600}>
          {formattedCount} {responseLabel}
        </Typography>
        {totalTallies > 0 ? (
          <Typography variant="caption" color="text.secondary">
            {formattedPercent}% of responses
          </Typography>
        ) : null}
      </Stack>
    </Stack>
  );
}

interface QuizFeedbackProps {
  evaluation: boolean;
  successMessage: ReactNode;
  errorMessage: ReactNode;
  explanation?: ReactNode;
}

/**
 * Presents contextual feedback after a learner submits a response.
 */
function QuizFeedback({
  evaluation,
  successMessage,
  errorMessage,
  explanation
}: QuizFeedbackProps): ReactNode {
  return (
    <Alert severity={evaluation ? "success" : "error"}>
      <Stack spacing={1}>
        <Typography variant="body2">
          {evaluation ? successMessage : errorMessage}
        </Typography>
        {explanation ? (
          <Typography variant="body2" color="text.secondary">
            {explanation}
          </Typography>
        ) : null}
      </Stack>
    </Alert>
  );
}

/**
 * Accessible multiple choice quiz with inline evaluation feedback.
 */
export function MultipleChoiceQuiz({
  question,
  options,
  helperText,
  correctOptionId,
  explanation,
  successMessage = DEFAULT_SUCCESS,
  errorMessage = DEFAULT_ERROR,
  onAnswer,
  submitLabel = DEFAULT_SUBMIT_LABEL,
  tryAgainLabel = DEFAULT_TRY_AGAIN_LABEL,
  allowRetry,
  disabled = false,
  endTime,
  closedMessage,
  confetti
}: MultipleChoiceQuizProps) {
  const questionId = useId();
  const groupId = useId();

  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [submittedId, setSubmittedId] = useState<string | null>(null);

  const endTimestamp = useMemo(() => {
    if (typeof endTime === "undefined" || endTime === null) {
      return null;
    }
    if (endTime instanceof Date) {
      const value = endTime.getTime();
      return Number.isFinite(value) ? value : null;
    }
    if (typeof endTime === "number") {
      return Number.isFinite(endTime) ? endTime : null;
    }
    if (typeof endTime === "string") {
      const parsed = new Date(endTime);
      const value = parsed.getTime();
      return Number.isFinite(value) ? value : null;
    }
    return null;
  }, [endTime]);

  const [isClosed, setIsClosed] = useState(() => {
    if (!endTimestamp) {
      return false;
    }
    return Date.now() >= endTimestamp;
  });

  useEffect(() => {
    if (!endTimestamp) {
      setIsClosed(false);
      return;
    }

    const now = Date.now();
    if (now >= endTimestamp) {
      setIsClosed(true);
      return;
    }

    setIsClosed(false);

    if (typeof window === "undefined") {
      return;
    }

    const timeoutId = window.setTimeout(() => {
      setIsClosed(true);
    }, endTimestamp - now);

    return () => {
      window.clearTimeout(timeoutId);
    };
  }, [endTimestamp]);

  const resolvedDisabled = disabled || isClosed;

  const {
    hasSubmitted,
    evaluation,
    disableChoices,
    showFeedback,
    revealCorrectAnswer,
    submitDisabled,
    showRetryButton
  } = useQuizState(
    { allowRetry, correctOptionId, disabled: resolvedDisabled },
    { selectedId, submittedId }
  );

  const resolvedConfetti = useMemo(() => resolveConfettiOptions(confetti), [confetti]);
  const { enabled: confettiEnabled, preset: confettiPreset } = resolvedConfetti;
  const hasCelebratedRef = useRef(false);

  useEffect(() => {
    if (!confettiEnabled) {
      hasCelebratedRef.current = false;
      return;
    }

    const shouldCelebrate = hasSubmitted && evaluation === true;
    if (!shouldCelebrate) {
      hasCelebratedRef.current = false;
      return;
    }

    if (hasCelebratedRef.current) {
      return;
    }

    launchConfetti(confettiPreset).catch((error) => {
      if (process.env.NODE_ENV !== "production") {
        console.warn("Failed to launch quiz confetti", error);
      }
    });
    hasCelebratedRef.current = true;
  }, [confettiEnabled, confettiPreset, evaluation, hasSubmitted]);

  const handleSelectionChange = useCallback(
    (event: ChangeEvent<HTMLInputElement>) => {
      setSelectedId(event.target.value);
    },
    []
  );

  const handleSubmit = useCallback(() => {
    if (!selectedId || isClosed) {
      return;
    }
    setSubmittedId(selectedId);
    onAnswer?.({
      optionId: selectedId,
      isCorrect: correctOptionId
        ? selectedId === correctOptionId
        : undefined
    });
  }, [correctOptionId, isClosed, onAnswer, selectedId]);

  const handleRetry = useCallback(() => {
    setSelectedId(null);
    setSubmittedId(null);
  }, []);

  const promptHelper = useMemo(() => {
    if (!helperText) {
      return null;
    }
    return (
      <Typography variant="body2" color="text.secondary">
        {helperText}
      </Typography>
    );
  }, [helperText]);

  const fallbackHelper = useMemo(() => {
    if (helperText || isClosed) {
      return null;
    }
    return (
      <FormHelperText sx={{ mt: 2 }}>
        Select the response that best answers the question.
      </FormHelperText>
    );
  }, [helperText, isClosed]);

  const feedbackContent = useMemo(() => {
    if (!showFeedback || typeof evaluation !== "boolean") {
      return null;
    }
    return (
      <QuizFeedback
        evaluation={evaluation}
        successMessage={successMessage}
        errorMessage={errorMessage}
        explanation={explanation}
      />
    );
  }, [errorMessage, evaluation, explanation, showFeedback, successMessage]);

  const retryButton = useMemo(() => {
    if (!showRetryButton) {
      return null;
    }
    return (
      <Button variant="outlined" onClick={handleRetry}>
        {tryAgainLabel}
      </Button>
    );
  }, [handleRetry, showRetryButton, tryAgainLabel]);

  const totalTallies = useMemo(
    () =>
      options.reduce((total, option) => {
        const tally = Number(option.tally ?? 0);
        if (!Number.isFinite(tally)) {
          return total;
        }
        return total + Math.max(0, tally);
      }, 0),
    [options]
  );

  const optionItems = useMemo(
    () =>
      options.map((option) => {
        const { highlight, highlightAnswer, optionState, isSelected } =
          resolveOptionState({
            optionId: option.id,
            selectedId,
            submittedId,
            correctOptionId,
            showFeedback,
            revealCorrectAnswer
          });

        const visualSnapshot: OptionVisualSnapshot = {
          highlight,
          highlightAnswer,
          isSelected
        };

        return (
          <FormControlLabel
            key={option.id}
            value={option.id}
            control={<Radio />}
            label={
              <OptionContent
                option={option}
                showTallies={isClosed}
                totalTallies={totalTallies}
              />
            }
            disabled={disableChoices}
            data-option-state={optionState}
            sx={(theme) => ({
              alignItems: "flex-start",
              m: 0,
              px: 2,
              py: 1.5,
              borderRadius: 2,
              borderWidth: 1,
              borderStyle: "solid",
              borderColor: resolveOptionBorderColor(theme, visualSnapshot),
              backgroundColor: resolveOptionBackgroundColor(
                theme,
                visualSnapshot
              ),
              transition: theme.transitions.create([
                "background-color",
                "border-color"
              ]),
              ".MuiRadio-root": {
                mt: 0.25
              }
            })}
          />
        );
      }),
    [
      correctOptionId,
      disableChoices,
      options,
      revealCorrectAnswer,
      selectedId,
      showFeedback,
      submittedId,
      isClosed,
      totalTallies
    ]
  );

  const closureNotice = useMemo(() => {
    if (!isClosed) {
      return null;
    }

    const formattedDeadline = endTimestamp
      ? new Date(endTimestamp).toLocaleString(undefined, {
          dateStyle: "medium",
          timeStyle: "short"
        })
      : null;

    const defaultMessage = (
      <Typography component="span" variant="body2">
        This quiz closed on{" "}
        <Typography component="span" variant="body2" fontWeight={600}>
          {formattedDeadline ?? "the scheduled deadline"}
        </Typography>
        . Review the response tallies below.
      </Typography>
    );

    return (
      <Alert severity="info">
        {closedMessage ? (
          <Typography variant="body2" component="span">
            {closedMessage}
          </Typography>
        ) : (
          defaultMessage
        )}
      </Alert>
    );
  }, [closedMessage, endTimestamp, isClosed]);

  return (
    <Card component="section" elevation={3} sx={{ borderRadius: 3 }}>
      <CardContent>
        <Stack spacing={3}>
          <Stack spacing={1}>
            <Typography
              component="h2"
              variant="h6"
              id={questionId}
              sx={{ fontWeight: 600 }}
            >
              {question}
            </Typography>
            {promptHelper}
          </Stack>
          {closureNotice}
          <FormControl component="fieldset" disabled={disableChoices}>
            <FormLabel
              htmlFor={groupId}
              sx={{
                position: "absolute",
                height: 0,
                width: 0,
                overflow: "hidden"
              }}
            >
              Multiple choice question
            </FormLabel>
            <RadioGroup
              aria-labelledby={questionId}
              id={groupId}
              name={groupId}
              value={selectedId ?? ""}
              onChange={handleSelectionChange}
            >
              <Stack spacing={1.5}>
                {optionItems}
              </Stack>
            </RadioGroup>
            {fallbackHelper}
          </FormControl>
          <Stack direction={{ xs: "column", sm: "row" }} spacing={1.5}>
            <Button
              variant="contained"
              color="primary"
              onClick={handleSubmit}
              disabled={submitDisabled}
            >
              {submitLabel}
            </Button>
            {retryButton}
          </Stack>
          {feedbackContent}
        </Stack>
      </CardContent>
    </Card>
  );
}

export type { QuizConfettiOptions, QuizConfettiPreset } from "./QuizCelebrations";
