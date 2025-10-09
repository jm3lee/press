import Box from "@mui/material/Box";
import Grid from "@mui/material/Grid";
import Typography from "@mui/material/Typography";
import { MultipleChoiceQuiz, Section } from "flashoffer-react";

const QUIZ_OPTIONS = [
  {
    id: "reminder",
    label: "A personalized reminder with a refreshed CTA",
    description:
      "Highlights the offer expiry, reinforces value, and links back to the " +
      "landing page."
  },
  {
    id: "case-study",
    label: "A case study download gate",
    description:
      "Shares social proof but interrupts momentum with an additional form."
  },
  {
    id: "survey",
    label: "A follow-up survey",
    description:
      "Collects insights yet delays the decision to activate the promotion."
  }
];

const QUIZ_META = JSON.stringify({
  question: "Best follow-up after a Flashoffer engagement",
  options: QUIZ_OPTIONS.map((option) => option.id)
});

export function QuizShowcaseSection() {
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
              question="After a prospect explores a Flashoffer landing page, what follow-up drives the highest conversion lift?"
              helperText="Consider which option keeps momentum without adding friction."
              options={QUIZ_OPTIONS}
              correctOptionId="reminder"
              explanation="Timely reminders build on existing intent and keep the offer top of mind without introducing blockers."
              successMessage="Exactly. Reinforcing urgency while keeping the path clear sustains conversion lift."
              errorMessage="Think about which follow-up reduces friction instead of adding new steps."
            />
          </Grid>
        </Grid>
      </Section>
    </Box>
  );
}
