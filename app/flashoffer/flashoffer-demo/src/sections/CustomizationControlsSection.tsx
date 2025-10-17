/*
 * Copyright (c) Flashoffer Developers
 * Released under the MIT license.
 */

import Box from "@mui/material/Box";
import Divider from "@mui/material/Divider";
import Paper from "@mui/material/Paper";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";
import { Section } from "flashoffer-react";
import type {
  HeroAlignment,
  QuizCelebrationSelection,
  ThemePreset
} from "./types";
import {
  QUIZ_CELEBRATION_LABELS,
  QUIZ_CELEBRATION_ORDER,
  THEME_PRESET_LABELS,
  THEME_PRESET_ORDER
} from "./types";

export interface CustomizationControlsSectionProps {
  palettePreset: ThemePreset;
  onPalettePresetChange: (nextPreset: ThemePreset) => void;
  heroAlignment: HeroAlignment;
  onHeroAlignmentChange: (nextAlignment: HeroAlignment) => void;
  quizCelebrationPreset: QuizCelebrationSelection;
  onQuizCelebrationPresetChange: (
    nextPreset: QuizCelebrationSelection
  ) => void;
  controlsMeta: string;
}

export function CustomizationControlsSection({
  palettePreset,
  onPalettePresetChange,
  heroAlignment,
  onHeroAlignmentChange,
  quizCelebrationPreset,
  onQuizCelebrationPresetChange,
  controlsMeta
}: CustomizationControlsSectionProps) {
  return (
    <Paper
      elevation={0}
      sx={{ p: { xs: 3, md: 4 } }}
      data-track-id="customization-panel"
      data-track-label="Customization controls"
      data-track-meta={controlsMeta}
    >
      <Stack spacing={3}>
        <Section
          align="left"
          eyebrow="CUSTOMIZE"
          title="Customize the showcase"
        >
          <Typography color="text.secondary">
            Switch palettes, adjust hero alignment, or pick a celebration
            preset to preview how Flashoffer primitives adapt.
          </Typography>
        </Section>
        <Divider flexItem sx={{ borderColor: "divider" }} />
        <Stack
          direction={{ xs: "column", sm: "row" }}
          spacing={3}
          divider={
            <Divider
              orientation="vertical"
              flexItem
              sx={{ display: { xs: "none", sm: "block" } }}
            />
          }
          useFlexGap
        >
          <Box>
            <Typography variant="overline" color="text.secondary">
              Palette
            </Typography>
            <select
              value={palettePreset}
              onChange={(event) => {
                const nextPreset = event.target.value as ThemePreset;
                onPalettePresetChange(nextPreset);
              }}
              aria-label="Select theme palette"
              style={{
                marginTop: "0.5rem",
                padding: "0.5rem 0.75rem",
                borderRadius: "0.75rem",
                border: "1px solid rgba(148, 163, 184, 0.4)",
                backgroundColor: "var(--flashoffer-color-surface)",
                color: "var(--flashoffer-color-text-primary)",
                fontSize: "0.95rem"
              }}
              data-track-id="palette-selector"
              data-track-label="Palette selector"
              data-track-meta={JSON.stringify({ palette: palettePreset })}
            >
              {THEME_PRESET_ORDER.map((value) => (
                <option key={value} value={value}>
                  {THEME_PRESET_LABELS[value]}
                </option>
              ))}
            </select>
          </Box>
          <Box>
            <Typography variant="overline" color="text.secondary">
              Hero alignment
            </Typography>
            <select
              value={heroAlignment}
              onChange={(event) => {
                const nextAlignment = event.target.value as HeroAlignment;
                onHeroAlignmentChange(nextAlignment);
              }}
              aria-label="Select hero alignment"
              style={{
                marginTop: "0.5rem",
                padding: "0.5rem 0.75rem",
                borderRadius: "0.75rem",
                border: "1px solid rgba(148, 163, 184, 0.4)",
                backgroundColor: "var(--flashoffer-color-surface)",
                color: "var(--flashoffer-color-text-primary)",
                fontSize: "0.95rem"
              }}
              data-track-id="hero-alignment"
              data-track-label="Hero alignment selector"
              data-track-meta={JSON.stringify({ alignment: heroAlignment })}
            >
              <option value="center">Centered</option>
              <option value="left">Left aligned</option>
            </select>
          </Box>
          <Box>
            <Typography variant="overline" color="text.secondary">
              Quiz celebration
            </Typography>
            <select
              value={quizCelebrationPreset}
              onChange={(event) => {
                const nextPreset = event.target
                  .value as QuizCelebrationSelection;
                onQuizCelebrationPresetChange(nextPreset);
              }}
              aria-label="Select quiz celebration"
              style={{
                marginTop: "0.5rem",
                padding: "0.5rem 0.75rem",
                borderRadius: "0.75rem",
                border: "1px solid rgba(148, 163, 184, 0.4)",
                backgroundColor: "var(--flashoffer-color-surface)",
                color: "var(--flashoffer-color-text-primary)",
                fontSize: "0.95rem"
              }}
              data-track-id="quiz-celebration"
              data-track-label="Quiz celebration selector"
              data-track-meta={JSON.stringify({ preset: quizCelebrationPreset })}
            >
              {QUIZ_CELEBRATION_ORDER.map((value) => (
                <option key={value} value={value}>
                  {QUIZ_CELEBRATION_LABELS[value]}
                </option>
              ))}
            </select>
          </Box>
        </Stack>
      </Stack>
    </Paper>
  );
}
