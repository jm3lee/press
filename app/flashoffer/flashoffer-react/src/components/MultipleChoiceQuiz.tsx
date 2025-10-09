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
import { useId, useMemo, useState } from "react";
import type { ReactNode } from "react";

export interface MultipleChoiceOption {
  /** Unique identifier used for option selection. */
  id: string;
  /** Primary label describing the answer choice. */
  label: ReactNode;
  /** Optional supporting copy rendered beneath the label. */
  description?: ReactNode;
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
}

const DEFAULT_SUCCESS = "Great job! That answer is correct.";
const DEFAULT_ERROR = "Not quite. Give it another look.";
const DEFAULT_SUBMIT_LABEL = "Check answer";
const DEFAULT_TRY_AGAIN_LABEL = "Try again";

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
  disabled = false
}: MultipleChoiceQuizProps) {
  const resolvedAllowRetry = useMemo(() => {
    if (typeof allowRetry === "boolean") {
      return allowRetry;
    }
    return Boolean(correctOptionId);
  }, [allowRetry, correctOptionId]);

  const questionId = useId();
  const groupId = useId();

  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [submittedId, setSubmittedId] = useState<string | null>(null);

  const hasSubmitted = submittedId !== null;
  const evaluation = useMemo(() => {
    if (!correctOptionId || !hasSubmitted || !submittedId) {
      return undefined;
    }
    return submittedId === correctOptionId;
  }, [correctOptionId, hasSubmitted, submittedId]);

  const handleSubmit = () => {
    if (!selectedId) {
      return;
    }
    setSubmittedId(selectedId);
    onAnswer?.({
      optionId: selectedId,
      isCorrect: correctOptionId
        ? selectedId === correctOptionId
        : undefined
    });
  };

  const handleRetry = () => {
    setSelectedId(null);
    setSubmittedId(null);
  };

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
    resolvedAllowRetry && hasSubmitted && evaluation !== true;

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
            {helperText ? (
              <Typography variant="body2" color="text.secondary">
                {helperText}
              </Typography>
            ) : null}
          </Stack>
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
              onChange={(event) => {
                setSelectedId(event.target.value);
              }}
            >
              <Stack spacing={1.5}>
                {options.map((option) => {
                  const isSelected = selectedId === option.id;
                  const isAnswer = correctOptionId === option.id;
                  const isSubmittedSelection = submittedId === option.id;
                  const highlightSelection = showFeedback && isSubmittedSelection;
                  const highlightAnswer = revealCorrectAnswer && isAnswer;
                  const highlight = highlightAnswer || highlightSelection;
                  const optionState = highlight
                    ? highlightAnswer
                      ? "correct"
                      : "incorrect"
                    : isSelected
                    ? "selected"
                    : "default";

                  return (
                    <FormControlLabel
                      key={option.id}
                      value={option.id}
                      control={<Radio />}
                      label={
                        <Stack spacing={option.description ? 0.5 : 0}>
                          <Typography variant="body1" fontWeight={600}>
                            {option.label}
                          </Typography>
                          {option.description ? (
                            <Typography
                              variant="body2"
                              color="text.secondary"
                            >
                              {option.description}
                            </Typography>
                          ) : null}
                        </Stack>
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
                        borderColor: highlight
                          ? highlightAnswer
                            ? theme.palette.success.main
                            : theme.palette.error.main
                          : isSelected
                          ? theme.palette.primary.main
                          : theme.palette.divider,
                        backgroundColor: highlight
                          ? alpha(
                              highlightAnswer
                                ? theme.palette.success.main
                                : theme.palette.error.main,
                              0.08
                            )
                          : theme.palette.background.paper,
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
                })}
              </Stack>
            </RadioGroup>
            {helperText ? null : (
              <FormHelperText sx={{ mt: 2 }}>
                Select the response that best answers the question.
              </FormHelperText>
            )}
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
            {showRetryButton ? (
              <Button variant="outlined" onClick={handleRetry}>
                {tryAgainLabel}
              </Button>
            ) : null}
          </Stack>
          {showFeedback ? (
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
          ) : null}
        </Stack>
      </CardContent>
    </Card>
  );
}
