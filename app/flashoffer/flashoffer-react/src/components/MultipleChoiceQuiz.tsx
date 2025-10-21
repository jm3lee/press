/*
 * Copyright (c) Flashoffer Developers
 * Released under the MIT license.
 */

import Alert from "@mui/material/Alert";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import Collapse from "@mui/material/Collapse";
import Dialog from "@mui/material/Dialog";
import DialogActions from "@mui/material/DialogActions";
import DialogContent from "@mui/material/DialogContent";
import DialogTitle from "@mui/material/DialogTitle";
import FormControl from "@mui/material/FormControl";
import FormControlLabel from "@mui/material/FormControlLabel";
import FormHelperText from "@mui/material/FormHelperText";
import FormLabel from "@mui/material/FormLabel";
import IconButton from "@mui/material/IconButton";
import SvgIcon from "@mui/material/SvgIcon";
import Radio from "@mui/material/Radio";
import RadioGroup from "@mui/material/RadioGroup";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";
import { alpha } from "@mui/material/styles";
import type { Theme } from "@mui/material/styles";
import { useCallback, useEffect, useId, useMemo, useRef, useState } from "react";
import type { ChangeEvent, ReactNode } from "react";
import type { SvgIconProps } from "@mui/material/SvgIcon";

function CloseIcon(props: SvgIconProps): JSX.Element {
  return (
    <SvgIcon {...props}>
      <path d="M19 6.41 17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z" />
    </SvgIcon>
  );
}

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

function resolveAllowRetryValue(
  allowRetry: boolean | undefined,
  correctOptionId?: string
): boolean {
  if (typeof allowRetry === "boolean") {
    return allowRetry;
  }
  return Boolean(correctOptionId);
}

function evaluateSubmission(
  correctOptionId: string | undefined,
  hasSubmitted: boolean,
  submittedId: string | null
): boolean | undefined {
  if (!correctOptionId || !hasSubmitted || !submittedId) {
    return undefined;
  }
  return submittedId === correctOptionId;
}

function resolveChoiceDisabling({
  disabled,
  hasSubmitted,
  allowRetry,
  evaluation
}: {
  disabled: boolean;
  hasSubmitted: boolean;
  allowRetry: boolean;
  evaluation: boolean | undefined;
}): boolean {
  if (disabled) {
    return true;
  }
  if (!hasSubmitted) {
    return false;
  }
  if (!allowRetry) {
    return true;
  }
  return evaluation === true;
}

function resolveSubmitDisabled({
  selectedId,
  disabled,
  hasSubmitted,
  allowRetry,
  evaluation
}: {
  selectedId: string | null;
  disabled: boolean;
  hasSubmitted: boolean;
  allowRetry: boolean;
  evaluation: boolean | undefined;
}): boolean {
  if (!selectedId || disabled) {
    return true;
  }
  if (hasSubmitted && !allowRetry) {
    return true;
  }
  return evaluation === true;
}

/**
 * Derives quiz behaviour flags from author configuration and user input.
 */
function useQuizState(
  { allowRetry, correctOptionId, disabled }: QuizStateConfig,
  { selectedId, submittedId }: QuizInteractionState
): QuizStateSnapshot {
  const resolvedAllowRetry = useMemo(
    () => resolveAllowRetryValue(allowRetry, correctOptionId),
    [allowRetry, correctOptionId]
  );

  const hasSubmitted = submittedId !== null;

  const evaluation = useMemo(
    () => evaluateSubmission(correctOptionId, hasSubmitted, submittedId),
    [correctOptionId, hasSubmitted, submittedId]
  );

  const disableChoices = useMemo(
    () =>
      resolveChoiceDisabling({
        disabled,
        hasSubmitted,
        allowRetry: resolvedAllowRetry,
        evaluation
      }),
    [disabled, evaluation, hasSubmitted, resolvedAllowRetry]
  );

  const showFeedback = Boolean(hasSubmitted && correctOptionId);
  const revealCorrectAnswer =
    showFeedback && (evaluation === true || !resolvedAllowRetry);
  const submitDisabled = useMemo(
    () =>
      resolveSubmitDisabled({
        selectedId,
        disabled,
        hasSubmitted,
        allowRetry: resolvedAllowRetry,
        evaluation
      }),
    [disabled, evaluation, hasSubmitted, resolvedAllowRetry, selectedId]
  );
  const showRetryButton = Boolean(
    resolvedAllowRetry && hasSubmitted && evaluation !== true && !disabled
  );

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
  showDescription: boolean;
}

interface OptionTalliesSnapshot {
  formattedCount: string;
  responseLabel: string;
  percentLabel: string | null;
}

function resolveOptionTallies(
  tallyInput: MultipleChoiceOption["tally"],
  totalTallies: number
): OptionTalliesSnapshot {
  const tally = Math.max(0, Number(tallyInput ?? 0));
  const countFormatter =
    typeof Intl !== "undefined"
      ? new Intl.NumberFormat(undefined, { maximumFractionDigits: 0 })
      : null;
  const formattedCount = countFormatter ? countFormatter.format(tally) : `${tally}`;
  const responseLabel = tally === 1 ? "response" : "responses";

  if (totalTallies <= 0) {
    return {
      formattedCount,
      responseLabel,
      percentLabel: null
    };
  }

  const percentFormatter =
    typeof Intl !== "undefined"
      ? new Intl.NumberFormat(undefined, { maximumFractionDigits: 0 })
      : null;
  const percentage = (tally / totalTallies) * 100;
  const formattedPercent = percentFormatter
    ? percentFormatter.format(percentage)
    : `${Math.round(percentage)}`;

  return {
    formattedCount,
    responseLabel,
    percentLabel: `${formattedPercent}% of responses`
  };
}

/**
 * Renders the visible label block for a quiz option.
 */
function OptionContent({
  option,
  showTallies,
  totalTallies,
  showDescription
}: OptionContentProps): ReactNode {
  const hasDescriptionContent = Boolean(option.description);
  const shouldDisplayDescription = Boolean(
    option.description && showDescription
  );
  const shouldCenterLabel = !shouldDisplayDescription && !showTallies;
  const labelBlock = (
    <Stack
      spacing={0}
      flex={1}
      minWidth={0}
      justifyContent={shouldCenterLabel ? "center" : "flex-start"}
      sx={shouldCenterLabel ? { minHeight: 40 } : undefined}
    >
      <Typography variant="body1" fontWeight={600}>
        {option.label}
      </Typography>
      {hasDescriptionContent ? (
        <Collapse
          in={shouldDisplayDescription}
          timeout="auto"
          unmountOnExit
          appear
        >
          <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
            {option.description}
          </Typography>
        </Collapse>
      ) : null}
    </Stack>
  );

  if (!showTallies) {
    return labelBlock;
  }

  const { formattedCount, responseLabel, percentLabel } = resolveOptionTallies(
    option.tally,
    totalTallies
  );

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
        {percentLabel ? (
          <Typography variant="caption" color="text.secondary">
            {percentLabel}
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
  const feedbackDialogTitleId = useId();

  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [submittedId, setSubmittedId] = useState<string | null>(null);
  const [isFeedbackDialogOpen, setIsFeedbackDialogOpen] = useState(false);
  const quizContainerRef = useRef<HTMLDivElement | null>(null);

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

  const dialogContainerResolver = useCallback(() => {
    if (quizContainerRef.current) {
      return quizContainerRef.current;
    }
    if (typeof window !== "undefined") {
      return window.document.body;
    }
    return null;
  }, []);

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
    setIsFeedbackDialogOpen(true);
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
    setIsFeedbackDialogOpen(false);
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

  const isFeedbackVisible = Boolean(showFeedback && typeof evaluation === "boolean");

  const openFeedbackDialog = useCallback(() => {
    if (!isFeedbackVisible) {
      return;
    }
    setIsFeedbackDialogOpen(true);
  }, [isFeedbackVisible]);

  const closeFeedbackDialog = useCallback(() => {
    setIsFeedbackDialogOpen(false);
  }, []);

  const feedbackTrigger = useMemo(
    () => (
      <Collapse
        in={isFeedbackVisible}
        timeout="auto"
        unmountOnExit
        mountOnEnter
        appear
      >
        {isFeedbackVisible ? (
          <Button
            variant="text"
            onClick={openFeedbackDialog}
            sx={{ alignSelf: "flex-start" }}
          >
            View feedback
          </Button>
        ) : null}
      </Collapse>
    ),
    [isFeedbackVisible, openFeedbackDialog]
  );

  const feedbackDialogOpen = Boolean(isFeedbackDialogOpen && isFeedbackVisible);
  const feedbackDialogTitle =
    evaluation === true ? "Correct answer" : "Review feedback";

  const retryButton = useMemo(
    () => (
      <Collapse
        in={showRetryButton}
        orientation="horizontal"
        timeout="auto"
        unmountOnExit
        mountOnEnter
        appear
        sx={{ display: "flex" }}
      >
        <Button variant="outlined" onClick={handleRetry}>
          {tryAgainLabel}
        </Button>
      </Collapse>
    ),
    [handleRetry, showRetryButton, tryAgainLabel]
  );

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
        const showOptionDescription = Boolean(
          option.description && (hasSubmitted || resolvedDisabled)
        );
        const alignItemsValue =
          showOptionDescription || isClosed ? "flex-start" : "center";

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
                showDescription={showOptionDescription}
              />
            }
            disabled={disableChoices}
            data-option-state={optionState}
            sx={(theme) => ({
              alignItems: alignItemsValue,
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
      hasSubmitted,
      isClosed,
      resolvedDisabled,
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
    <Box ref={quizContainerRef} sx={{ position: "relative" }}>
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
            {feedbackTrigger}
          </Stack>
        </CardContent>
      </Card>
      <Dialog
        container={dialogContainerResolver}
        fullWidth
        maxWidth={false}
        open={feedbackDialogOpen}
        onClose={closeFeedbackDialog}
        aria-labelledby={feedbackDialogTitleId}
        sx={{
          position: "absolute",
          inset: 0,
          display: "flex",
          alignItems: "stretch",
          justifyContent: "stretch",
          zIndex: (theme) => theme.zIndex.modal
        }}
        BackdropProps={{
          sx: {
            position: "absolute",
            inset: 0,
            backgroundColor: (theme) => alpha(theme.palette.common.black, 0.5)
          }
        }}
        PaperProps={{
          sx: {
            m: 0,
            width: "100%",
            maxWidth: "100%",
            height: "100%",
            display: "flex",
            flexDirection: "column"
          }
        }}
      >
        <DialogTitle id={feedbackDialogTitleId} sx={{ pr: 6 }}>
          {feedbackDialogTitle}
          <IconButton
            aria-label="Close feedback"
            onClick={closeFeedbackDialog}
            sx={{ position: "absolute", right: 16, top: 16 }}
          >
            <CloseIcon />
          </IconButton>
        </DialogTitle>
        <DialogContent
          sx={{
            flex: 1,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            p: 3,
            overflowY: "auto"
          }}
        >
          {feedbackDialogOpen ? (
            <Stack spacing={2} maxWidth={480} width="100%">
              <QuizFeedback
                evaluation={Boolean(evaluation)}
                successMessage={successMessage}
                errorMessage={errorMessage}
                explanation={explanation}
              />
            </Stack>
          ) : null}
        </DialogContent>
        <DialogActions sx={{ px: 3, pb: 3, gap: 1 }}>
          {showRetryButton ? (
            <Button variant="contained" onClick={handleRetry}>
              {tryAgainLabel}
            </Button>
          ) : null}
          <Button
            onClick={closeFeedbackDialog}
            variant={showRetryButton ? "text" : "contained"}
          >
            Close
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}

export type { QuizConfettiOptions, QuizConfettiPreset } from "./QuizCelebrations";
