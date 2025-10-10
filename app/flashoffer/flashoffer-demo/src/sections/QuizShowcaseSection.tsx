/*
 * Copyright (c) Flashoffer Developers
 * Released under the MIT license.
 */

import Box from "@mui/material/Box";
import Grid from "@mui/material/Grid";
import Typography from "@mui/material/Typography";
import { useEffect, useRef, useState } from "react";
import { MultipleChoiceQuiz, Section } from "flashoffer-react";
import type { MultipleChoiceAnswer } from "flashoffer-react";
import { logQuizCompletion } from "../quizAnalytics";

const QUIZ_OPTIONS = [
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

const QUIZ_META = JSON.stringify({
  question: "Best follow-up after a Flashoffer engagement",
  options: QUIZ_OPTIONS.map((option) => option.id)
});

const QUIZ_QUESTION =
  "After a prospect explores a Flashoffer landing page, what follow-up drives " +
  "the highest conversion lift?";

const DEMO_CAMPAIGN_ID = "flashoffer-demo";

export function QuizShowcaseSection() {
  const campaignApiBase =
    typeof import.meta.env.VITE_FLASHOFFER_CAMPAIGN_API_BASE === "string" &&
    import.meta.env.VITE_FLASHOFFER_CAMPAIGN_API_BASE.trim() !== ""
      ? import.meta.env.VITE_FLASHOFFER_CAMPAIGN_API_BASE.trim()
      : undefined;
  const [campaignEndTime, setCampaignEndTime] = useState<Date | null>(null);
  const attemptRef = useRef(0);

  const handleAnswer = (answer: MultipleChoiceAnswer) => {
    attemptRef.current += 1;
    void logQuizCompletion({
      attempt: attemptRef.current,
      question: QUIZ_QUESTION,
      selectedOptionId: answer.optionId,
      correctOptionId: "reminder",
      isCorrect: answer.isCorrect,
      campaignId: DEMO_CAMPAIGN_ID,
    });
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
      data-track-meta={QUIZ_META}
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
            <MultipleChoiceQuiz
              question={QUIZ_QUESTION}
              helperText="Consider which option keeps momentum without adding friction."
              options={QUIZ_OPTIONS}
              correctOptionId="reminder"
              explanation="Timely reminders build on existing intent and keep the offer top of mind without introducing blockers."
              successMessage="Exactly. Reinforcing urgency while keeping the path clear sustains conversion lift."
              errorMessage="Think about which follow-up reduces friction instead of adding new steps."
              onAnswer={handleAnswer}
              endTime={campaignEndTime ?? undefined}
            />
          </Grid>
        </Grid>
      </Section>
    </Box>
  );
}
