import Box from "@mui/material/Box";
import Container from "@mui/material/Container";
import Divider from "@mui/material/Divider";
import Paper from "@mui/material/Paper";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";
import { alpha, useTheme } from "@mui/material/styles";
import { useCallback, useMemo, useState } from "react";
import "../polyfills/reactLegacyFactory";
import {
  FlashofferThemeProvider,
  OutlineCtaButton,
  SectionHeader
} from "flashoffer-react";
import { Option, Question, QuestionGroup, Test } from "../compat/reactMultipleChoice";

const QUESTION_NUMBER = 0;

const ANSWER_DETAILS: Record<
  string,
  {
    heading: string;
    description: string;
  }
> = {
  theming: {
    heading: "Correct — consistent theming drives alignment",
    description:
      "Theme presets, typography spacing, and palette controls make campaigns feel cohesive while still flexible."
  },
  assetHosting: {
    heading: "Not quite — hosting lives elsewhere",
    description:
      "Flashoffer-react focuses on rendering surfaces. Media assets remain under your control and can be sourced from any CDN."
  },
  moderation: {
    heading: "Close — policy guidance is adjacent",
    description:
      "The library documents moderation workflows, but consistency comes from the reusable layout primitives themselves."
  },
  analytics: {
    heading: "Insight helps, but design system comes first",
    description:
      "Engagement analytics quantify performance; they do not replace the structured UI toolkit that keeps offers recognizable."
  }
};

function MultipleChoiceDemoContent() {
  const theme = useTheme();
  const [selections, setSelections] = useState<Record<number, string>>({});

  const handleOptionSelect = useCallback((nextSelections: Record<number, string>) => {
    setSelections(nextSelections);
  }, []);

  const activeSelection = selections[QUESTION_NUMBER];

  const optionStyle = useMemo(
    () => ({
      icon: {
        color: theme.palette.primary.main
      },
      option: {
        border: `1px solid ${theme.palette.divider}`,
        borderRadius: theme.spacing(3),
        display: "flex",
        alignItems: "center",
        gap: theme.spacing(1.5),
        padding: theme.spacing(2),
        backgroundColor: theme.palette.background.paper,
        cursor: "pointer",
        transition: "border-color 0.2s ease, box-shadow 0.2s ease"
      }
    }),
    [theme]
  );

  const selectedOptionStyle = useMemo(
    () => ({
      option: {
        borderColor: theme.palette.primary.main,
        backgroundColor: alpha(theme.palette.primary.main, 0.08),
        boxShadow: `0 0 0 4px ${alpha(theme.palette.primary.main, 0.15)}`
      }
    }),
    [theme]
  );

  const feedback = useMemo(() => {
    const selectionDetails =
      activeSelection !== undefined ? ANSWER_DETAILS[activeSelection] : undefined;

    if (!selectionDetails) {
      return {
        heading: "Choose an option to view guidance",
        description:
          "Select the answer that best matches how Flashoffer-react supports consistent go-to-market storytelling."
      };
    }

    return selectionDetails;
  }, [activeSelection]);

  return (
    <Box
      sx={{
        backgroundColor: "var(--flashoffer-color-background)",
        color: "var(--flashoffer-color-text-primary)",
        minHeight: "100vh"
      }}
    >
      <Container component="main" maxWidth="md" sx={{ py: { xs: 6, md: 10 } }}>
        <Stack spacing={{ xs: 6, md: 8 }}>
          <SectionHeader
            align="center"
            eyebrow="LEARNING LAB"
            title="Test your Flashoffer instincts"
            description="Walk through a single-question quiz to see how the multiple choice components capture structured feedback."
          />
          <Paper
            elevation={0}
            sx={{
              p: { xs: 3, md: 4 },
              borderRadius: 4,
              border: `1px solid ${theme.palette.divider}`,
              backgroundColor: alpha(theme.palette.background.paper, 0.9)
            }}
          >
            <Test
              onOptionSelect={handleOptionSelect}
              style={{
                width: "100%",
                display: "flex",
                flexDirection: "column",
                gap: theme.spacing(3)
              }}
            >
              <QuestionGroup
                questionNumber={QUESTION_NUMBER}
                style={{
                  display: "flex",
                  flexDirection: "column",
                  gap: theme.spacing(2)
                }}
              >
                <Question style={{ marginBottom: theme.spacing(1) }}>
                  <Typography component="h3" variant="h5">
                    Which Flashoffer-react capability keeps campaign visuals aligned across every launch?
                  </Typography>
                </Question>
                <Option
                  value="theming"
                  style={optionStyle}
                  selectedStyle={selectedOptionStyle}
                >
                  Theme presets and typography utilities that adapt to palette decisions.
                </Option>
                <Option
                  value="assetHosting"
                  style={optionStyle}
                  selectedStyle={selectedOptionStyle}
                >
                  Built-in asset hosting that stores 8K product footage for each release.
                </Option>
                <Option
                  value="moderation"
                  style={optionStyle}
                  selectedStyle={selectedOptionStyle}
                >
                  Embedded moderation playbooks that mirror partner platform policy updates.
                </Option>
                <Option
                  value="analytics"
                  style={optionStyle}
                  selectedStyle={selectedOptionStyle}
                >
                  Real-time engagement analytics that chart how audiences respond to each CTA.
                </Option>
              </QuestionGroup>
            </Test>
            <Divider sx={{ my: { xs: 3, md: 4 } }} />
            <Stack spacing={1.5}>
              <Typography variant="h6" component="h4">
                {feedback.heading}
              </Typography>
              <Typography color="text.secondary">{feedback.description}</Typography>
            </Stack>
          </Paper>
          <Stack alignItems="center">
            <OutlineCtaButton
              component="a"
              href="/"
              label="Return to the Flashoffer demo"
            />
          </Stack>
        </Stack>
      </Container>
    </Box>
  );
}

export function MultipleChoiceDemoPage() {
  return (
    <FlashofferThemeProvider applyCssBaseline>
      <MultipleChoiceDemoContent />
    </FlashofferThemeProvider>
  );
}
