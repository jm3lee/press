/*
 * Copyright (c) Flashoffer Developers
 * Released under the MIT license.
 */

import Box from "@mui/material/Box";
import FormControl from "@mui/material/FormControl";
import Grid from "@mui/material/Grid";
import MenuItem from "@mui/material/MenuItem";
import Select from "@mui/material/Select";
import type { SelectChangeEvent } from "@mui/material/Select";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";
import { useEffect, useMemo, useRef, useState } from "react";
import {
  MultipleChoiceQuiz,
  Section,
  logQuizCompletion,
} from "flashoffer-react";
import type {
  MultipleChoiceAnswer,
  QuizConfettiOptions
} from "flashoffer-react";
import {
  QUIZ_CELEBRATION_LABELS,
  QUIZ_CELEBRATION_OPTIONS,
  type QuizCelebrationSelection
} from "./types";

interface QuizOption {
  id: string;
  label: string;
  description?: string;
  tally?: number;
}

interface QuestionOfDay {
  id?: number;
  slug: string;
  question: string;
  helperText?: string;
  explanation?: string;
  successMessage?: string;
  errorMessage?: string;
  options: QuizOption[];
  correctOptionId: string;
  publishedOn?: string;
  expiresOn?: string | null;
}

const FALLBACK_OPTIONS: QuizOption[] = [
  {
    id: "reminder",
    label: "A personalized reminder with a refreshed CTA",
    description:
      "Highlights the offer expiry, reinforces value, and links back to the " +
      "landing page.",
    tally: 264
  },
  {
    id: "case-study",
    label: "A case study download gate",
    description:
      "Shares social proof but interrupts momentum with an additional form.",
    tally: 86
  },
  {
    id: "survey",
    label: "A follow-up survey",
    description:
      "Collects insights yet delays the decision to activate the promotion.",
    tally: 41
  }
];

const FALLBACK_QUESTION: QuestionOfDay = {
  id: undefined,
  slug: "flashoffer-demo.best-follow-up",
  question:
    "After a prospect explores a Flashoffer landing page, what follow-up drives " +
    "the highest conversion lift?",
  helperText:
    "Consider which option keeps momentum without adding friction.",
  explanation:
    "Timely reminders build on existing intent and keep the offer top of mind without introducing blockers.",
  successMessage:
    "Exactly. Reinforcing urgency while keeping the path clear sustains conversion lift.",
  errorMessage:
    "Think about which follow-up reduces friction instead of adding new steps.",
  options: FALLBACK_OPTIONS,
  correctOptionId: "reminder",
  publishedOn: undefined,
  expiresOn: undefined
};

const QUIZ_EVENTS_ENDPOINT =
  typeof import.meta.env.VITE_FLASHOFFER_QUIZ_EVENTS_ENDPOINT === "string" &&
  import.meta.env.VITE_FLASHOFFER_QUIZ_EVENTS_ENDPOINT.trim() !== ""
    ? import.meta.env.VITE_FLASHOFFER_QUIZ_EVENTS_ENDPOINT
    : undefined;

const DEMO_CAMPAIGN_ID = "flashoffer-demo";

function normalizeQuestionOfDay(payload: unknown): QuestionOfDay | null {
  if (!payload || typeof payload !== "object") {
    return null;
  }
  const envelope = payload as Record<string, unknown>;
  const questionPayload = envelope["question"];
  if (!questionPayload || typeof questionPayload !== "object") {
    return null;
  }

  const questionRecord = questionPayload as Record<string, unknown>;
  const optionsPayload = questionRecord["options"];
  if (!Array.isArray(optionsPayload)) {
    return null;
  }

  const normalizedOptions: QuizOption[] = [];
  for (const entry of optionsPayload) {
    if (!entry || typeof entry !== "object") {
      continue;
    }
    const option = entry as Record<string, unknown>;
    const idCandidate = option["id"];
    const labelCandidate = option["label"];
    if (typeof idCandidate !== "string" || !idCandidate.trim()) {
      continue;
    }
    const labelText =
      typeof labelCandidate === "string" && labelCandidate.trim() !== ""
        ? labelCandidate
        : typeof labelCandidate === "number"
        ? String(labelCandidate)
        : undefined;
    if (!labelText) {
      continue;
    }
    normalizedOptions.push({
      id: idCandidate,
      label: labelText,
      description:
        typeof option["description"] === "string"
          ? option["description"]
          : undefined,
      tally:
        typeof option["tally"] === "number"
          ? option["tally"]
          : undefined
    });
  }

  if (normalizedOptions.length === 0) {
    return null;
  }

  const questionText = questionRecord["question"];
  if (typeof questionText !== "string" || !questionText.trim()) {
    return null;
  }

  const resolveString = (value: unknown) =>
    typeof value === "string" && value.trim() !== "" ? value : undefined;

  return {
    id: typeof questionRecord["id"] === "number"
      ? questionRecord["id"]
      : undefined,
    slug: resolveString(questionRecord["slug"]) ??
      FALLBACK_QUESTION.slug,
    question: questionText,
    helperText: resolveString(
      questionRecord["helper_text"] ?? questionRecord["helperText"]
    ),
    explanation: resolveString(questionRecord["explanation"]),
    successMessage: resolveString(
      questionRecord["success_message"] ?? questionRecord["successMessage"]
    ),
    errorMessage: resolveString(
      questionRecord["error_message"] ?? questionRecord["errorMessage"]
    ),
    options: normalizedOptions,
    correctOptionId: resolveString(
      questionRecord["correct_option_id"] ?? questionRecord["correctOptionId"]
    ) ?? FALLBACK_QUESTION.correctOptionId,
    publishedOn: resolveString(
      questionRecord["published_on"] ?? questionRecord["publishedOn"]
    ),
    expiresOn: resolveString(
      questionRecord["expires_on"] ?? questionRecord["expiresOn"]
    )
  };
}

export interface QuizShowcaseSectionProps {
  quizCelebration: QuizCelebrationSelection;
  onQuizCelebrationChange: (
    nextCelebration: QuizCelebrationSelection
  ) => void;
}

export function QuizShowcaseSection({
  quizCelebration,
  onQuizCelebrationChange,
}: QuizShowcaseSectionProps) {
  const quizApiBase =
    typeof import.meta.env.VITE_FLASHOFFER_QUIZ_API_BASE === "string" &&
    import.meta.env.VITE_FLASHOFFER_QUIZ_API_BASE.trim() !== ""
      ? import.meta.env.VITE_FLASHOFFER_QUIZ_API_BASE.trim()
      : undefined;
  const [questionOfDay, setQuestionOfDay] =
    useState<QuestionOfDay>(FALLBACK_QUESTION);
  const campaignApiBase =
    typeof import.meta.env.VITE_FLASHOFFER_CAMPAIGN_API_BASE === "string" &&
    import.meta.env.VITE_FLASHOFFER_CAMPAIGN_API_BASE.trim() !== ""
      ? import.meta.env.VITE_FLASHOFFER_CAMPAIGN_API_BASE.trim()
      : undefined;
  const [campaignEndTime, setCampaignEndTime] = useState<Date | null>(null);
  const attemptRef = useRef(0);

  const quizOptions = useMemo(
    () =>
      questionOfDay.options.length > 0
        ? questionOfDay.options
        : FALLBACK_QUESTION.options,
    [questionOfDay]
  );
  const questionSlug = questionOfDay.slug || FALLBACK_QUESTION.slug;
  const questionText =
    questionOfDay.question || FALLBACK_QUESTION.question;
  const helperText =
    questionOfDay.helperText ?? FALLBACK_QUESTION.helperText;
  const explanation =
    questionOfDay.explanation ?? FALLBACK_QUESTION.explanation;
  const successMessage =
    questionOfDay.successMessage ?? FALLBACK_QUESTION.successMessage;
  const errorMessage =
    questionOfDay.errorMessage ?? FALLBACK_QUESTION.errorMessage;
  const correctOptionId =
    questionOfDay.correctOptionId || FALLBACK_QUESTION.correctOptionId;

  const quizAnalyticsConfig = useMemo(
    () => ({
      quizId: questionSlug,
      endpoint: QUIZ_EVENTS_ENDPOINT,
    }),
    [questionSlug]
  );

  const quizMeta = useMemo(
    () =>
      JSON.stringify({
        question: questionText,
        slug: questionSlug,
        options: quizOptions.map((option) => option.id),
        celebration: quizCelebration,
        celebrationLabel: QUIZ_CELEBRATION_LABELS[quizCelebration]
      }),
    [quizCelebration, questionText, questionSlug, quizOptions]
  );

  const quizCelebrationMeta = useMemo(
    () =>
      JSON.stringify({
        celebration: quizCelebration,
        celebrationLabel: QUIZ_CELEBRATION_LABELS[quizCelebration]
      }),
    [quizCelebration]
  );

  const quizConfetti = useMemo<QuizConfettiOptions | undefined>(() => {
    if (quizCelebration === "off") {
      return { enabled: false };
    }

    return {
      enabled: true,
      preset: quizCelebration
    };
  }, [quizCelebration]);

  useEffect(() => {
    if (!quizApiBase || typeof fetch !== "function") {
      return;
    }

    let cancelled = false;
    const AbortCtor =
      typeof AbortController === "function" ? AbortController : null;
    const controller = AbortCtor ? new AbortCtor() : null;
    const baseUrl = quizApiBase.replace(/\/+$/, "");
    const endpoint = `${baseUrl}/api/quiz/today`;

    const loadQuestion = async () => {
      try {
        const response = await fetch(endpoint, {
          method: "GET",
          headers: { Accept: "application/json" },
          signal: controller?.signal
        });

        if (!response.ok) {
          throw new Error(`Quiz API responded with ${response.status}`);
        }

        const data = await response.json();
        if (cancelled) {
          return;
        }

        const normalized = normalizeQuestionOfDay(data);
        if (normalized) {
          setQuestionOfDay(normalized);
        }
      } catch (error) {
        console.warn("Unable to load question of the day", error);
      }
    };

    void loadQuestion();

    return () => {
      cancelled = true;
      controller?.abort();
    };
  }, [quizApiBase]);

  const handleAnswer = (answer: MultipleChoiceAnswer) => {
    attemptRef.current += 1;
    void logQuizCompletion({
      attempt: attemptRef.current,
      question: questionText,
      selectedOptionId: answer.optionId,
      correctOptionId,
      isCorrect: answer.isCorrect,
      campaignId: DEMO_CAMPAIGN_ID,
    }, quizAnalyticsConfig);
  };

  useEffect(() => {
    if (!campaignApiBase || typeof fetch !== "function") {
      return;
    }

    let cancelled = false;
    const AbortCtor = typeof AbortController === "function" ? AbortController : null;
    const controller = AbortCtor ? new AbortCtor() : null;
    const baseUrl = campaignApiBase.replace(/\/+$/, "");
    const endpoint = `${baseUrl}/api/campaign/${DEMO_CAMPAIGN_ID}/end_time`;

    const loadDeadline = async () => {
      try {
        const response = await fetch(endpoint, {
          method: "GET",
          headers: { Accept: "application/json" },
          signal: controller?.signal
        });

        if (!response.ok) {
          throw new Error(`Campaign API responded with ${response.status}`);
        }

        const data = (await response.json()) as Record<string, unknown>;
        if (cancelled) {
          return;
        }

        const endTimeCandidate = data["end_time"] ?? data["endTime"];
        if (typeof endTimeCandidate === "string") {
          const parsed = new Date(endTimeCandidate);
          if (Number.isFinite(parsed.getTime())) {
            setCampaignEndTime(parsed);
            return;
          }
        }

        const remainingCandidate = data["remaining_ms"] ?? data["remainingMs"];
        if (typeof remainingCandidate === "number" && Number.isFinite(remainingCandidate)) {
          setCampaignEndTime(new Date(Date.now() + Math.max(0, remainingCandidate)));
        }
      } catch (error) {
        console.warn("Unable to load flashoffer-demo campaign deadline", error);
      }
    };

    void loadDeadline();

    return () => {
      cancelled = true;
      controller?.abort();
    };
  }, [campaignApiBase]);

  return (
    <Box
      component="section"
      data-track-id="quiz-showcase"
      data-track-label="Interactive quiz showcase"
      data-track-meta={quizMeta}
    >
      <Section
        eyebrow="INTERACTIVE"
        title="Teach best practices with interactive quizzes"
        align="left"
      >
        <Grid container spacing={4}>
          <Grid size={{ xs: 12, md: 5 }}>
            <Typography color="text.secondary">
              Embed knowledge checks to reinforce campaign strategy within your
              onboarding flows. MultipleChoiceQuiz mirrors the feel of
              Reactor's learning components while remaining dependency light.
            </Typography>
          </Grid>
          <Grid size={{ xs: 12, md: 7 }}>
            <Stack spacing={2}>
              <Box>
                <Typography variant="overline" color="text.secondary">
                  Celebration effect
                </Typography>
                <FormControl fullWidth sx={{ mt: 1.5 }}>
                  <Select
                    value={quizCelebration}
                    onChange={(
                      event: SelectChangeEvent<QuizCelebrationSelection>
                    ) => {
                      const nextCelebration =
                        event.target.value as QuizCelebrationSelection;
                      onQuizCelebrationChange(nextCelebration);
                    }}
                    inputProps={{ "aria-label": "Select quiz celebration" }}
                    data-track-id="quiz-celebration"
                    data-track-label="Quiz celebration selector"
                    data-track-meta={quizCelebrationMeta}
                  >
                    {QUIZ_CELEBRATION_OPTIONS.map((value) => (
                      <MenuItem key={value} value={value}>
                        {QUIZ_CELEBRATION_LABELS[value]}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Box>
              <MultipleChoiceQuiz
                question={questionText}
                helperText={helperText}
                options={quizOptions}
                correctOptionId={correctOptionId}
                explanation={explanation}
                successMessage={successMessage}
                errorMessage={errorMessage}
                onAnswer={handleAnswer}
                endTime={campaignEndTime ?? undefined}
                confetti={quizConfetti}
              />
            </Stack>
          </Grid>
        </Grid>
      </Section>
    </Box>
  );
}
