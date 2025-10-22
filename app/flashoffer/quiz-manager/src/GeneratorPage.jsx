/*
 * Copyright (c) Flashoffer Developers
 * Released under the MIT license.
 */

import { useCallback, useEffect, useMemo, useState } from 'react';
import {
  Accordion,
  AccordionDetails,
  AccordionSummary,
  AlertTitle,
  Box,
  Alert,
  Button,
  Paper,
  Stack,
  TextField,
  Typography
} from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import { FlashofferThemeProvider, MultipleChoiceQuiz } from 'flashoffer-react';

const GENERATOR_ENDPOINT = '/api/quiz/questions/generate';
const GENERATOR_PROMPT_STORAGE_KEY = 'quiz-manager:last-generator-prompt';

/**
 * Presents the generator workflow used to request GPT-assisted quiz drafts.
 * Manages the prompt form state and coordinates the async draft request.
 * @returns {JSX.Element} Generator layout.
 */
export default function GeneratorPage() {
  const [generatorPrompt, setGeneratorPrompt] = useState(() => {
    if (typeof window === 'undefined') {
      return '';
    }
    try {
      return window.localStorage.getItem(GENERATOR_PROMPT_STORAGE_KEY) ?? '';
    } catch {
      return '';
    }
  });
  const [generatorStatus, setGeneratorStatus] = useState('idle');
  const [generatorError, setGeneratorError] = useState('');
  const [generatorSuccess, setGeneratorSuccess] = useState('');
  const [generatedQuestion, setGeneratedQuestion] = useState(null);

  const previewQuestion = useMemo(() => {
    if (!generatedQuestion || typeof generatedQuestion !== 'object') {
      return null;
    }

    const questionText =
      typeof generatedQuestion.question === 'string'
        ? generatedQuestion.question.trim()
        : '';

    const helperText =
      typeof generatedQuestion.helper_text === 'string'
        ? generatedQuestion.helper_text.trim()
        : '';

    const explanation =
      typeof generatedQuestion.explanation === 'string'
        ? generatedQuestion.explanation.trim()
        : '';

    const successMessage =
      typeof generatedQuestion.success_message === 'string'
        ? generatedQuestion.success_message.trim()
        : '';

    const errorMessage =
      typeof generatedQuestion.error_message === 'string'
        ? generatedQuestion.error_message.trim()
        : '';

    const options = Array.isArray(generatedQuestion.options)
      ? generatedQuestion.options
          .map((option) => ({
            id: typeof option?.id === 'string' ? option.id : '',
            label: typeof option?.label === 'string' ? option.label : '',
            description:
              typeof option?.description === 'string' && option.description
                ? option.description
                : undefined
          }))
          .filter((option) => option.id && option.label)
      : [];

    if (!questionText || options.length === 0) {
      return null;
    }

    const correctOptionId =
      typeof generatedQuestion.correct_option_id === 'string'
        ? generatedQuestion.correct_option_id
        : undefined;

    const celebration =
      typeof generatedQuestion.celebration === 'string' && generatedQuestion.celebration
        ? generatedQuestion.celebration
        : undefined;

    return {
      question: questionText,
      helperText: helperText || undefined,
      options,
      correctOptionId,
      explanation: explanation || undefined,
      successMessage: successMessage || undefined,
      errorMessage: errorMessage || undefined,
      celebration
    };
  }, [generatedQuestion]);

  const handleGeneratorPromptChange = useCallback((event) => {
    setGeneratorPrompt(event.target.value);
    setGeneratorError('');
  }, []);

  const handleGenerate = useCallback(async () => {
    if (typeof window === 'undefined') {
      setGeneratorError('Generator is not available in this environment.');
      return;
    }

    const trimmedPrompt = generatorPrompt.trim();

    setGeneratorStatus('loading');
    setGeneratorError('');
    setGeneratorSuccess('');

    try {
      const url = new URL("http://localhost:8002" + GENERATOR_ENDPOINT, window.location.origin);
      const response = await fetch(url.toString(), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          prompt: trimmedPrompt || undefined
        })
      });

      const body = await response.json().catch(() => ({}));

      if (!response.ok) {
        const message = body?.error ?? `Generation failed (${response.status})`;
        throw new Error(message);
      }

      if (!body?.question) {
        throw new Error('Generation did not return a question payload.');
      }

      setGeneratedQuestion(body.question);
      const slug = body.question?.slug?.trim();
      const questionLabel = slug ? `Drafted question ${slug}` : 'Drafted question';
      setGeneratorSuccess(`${questionLabel} from GPT-5.`);
    } catch (error) {
      setGeneratedQuestion(null);
      setGeneratorError(
        error instanceof Error ? error.message : 'Generation failed unexpectedly.'
      );
    } finally {
      setGeneratorStatus('idle');
    }
  }, [generatorPrompt]);

  useEffect(() => {
    if (typeof window === 'undefined') {
      return;
    }

    try {
      if (generatorPrompt) {
        window.localStorage.setItem(GENERATOR_PROMPT_STORAGE_KEY, generatorPrompt);
      } else {
        window.localStorage.removeItem(GENERATOR_PROMPT_STORAGE_KEY);
      }
    } catch (error) {
      console.warn('Unable to persist generator prompt', error);
    }
  }, [generatorPrompt]);

  return (
    <Paper elevation={6} className="quiz-manager__panel">
      <Stack spacing={2}>
        <Typography variant="h5" component="h2">
          GPT-5 Drafts
        </Typography>
        <Typography variant="body2" color="textSecondary">
          Provide a short prompt and the manager will request a draft question
          from the backend generator endpoint.
        </Typography>
        <Stack spacing={2} className="quiz-manager__generator">
          <TextField
            label="AI Prompt (optional)"
            value={generatorPrompt}
            onChange={handleGeneratorPromptChange}
            placeholder="e.g., Highlight best practices for nurturing mid-funnel prospects."
            multiline
            minRows={3}
            fullWidth
          />
          {generatorError ? <Alert severity="error">{generatorError}</Alert> : null}
          {generatorSuccess ? (
            <Alert severity="success">{generatorSuccess}</Alert>
          ) : null}
          {generatedQuestion ? (
            <Stack spacing={2}>
              {previewQuestion ? (
                <Paper variant="outlined" sx={{ p: 2 }}>
                  <Stack spacing={2}>
                    <Alert severity="info">
                      <AlertTitle>Live Preview</AlertTitle>
                      Interact with the draft question exactly as learners will see it.
                    </Alert>
                    <FlashofferThemeProvider>
                      <Box className="quiz-manager__quiz-preview">
                        <MultipleChoiceQuiz
                          question={previewQuestion.question}
                          helperText={previewQuestion.helperText}
                          options={previewQuestion.options}
                          correctOptionId={previewQuestion.correctOptionId}
                          explanation={previewQuestion.explanation}
                          successMessage={previewQuestion.successMessage}
                          errorMessage={previewQuestion.errorMessage}
                          allowRetry
                          confetti={
                            previewQuestion.celebration === 'off'
                              ? { enabled: false }
                              : previewQuestion.celebration
                              ? { enabled: true, preset: previewQuestion.celebration }
                              : undefined
                          }
                        />
                      </Box>
                    </FlashofferThemeProvider>
                  </Stack>
                </Paper>
              ) : null}
              <Accordion>
                <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                  <Typography variant="subtitle1">Raw JSON payload</Typography>
                </AccordionSummary>
                <AccordionDetails>
                  <Box
                    component="pre"
                    sx={{
                      m: 0,
                      whiteSpace: 'pre-wrap',
                      wordBreak: 'break-word',
                      fontFamily: 'Menlo, Consolas, "Liberation Mono", monospace'
                    }}
                  >
                    {JSON.stringify(generatedQuestion, null, 2)}
                  </Box>
                </AccordionDetails>
              </Accordion>
            </Stack>
          ) : null}
          <Stack direction="row" spacing={2} justifyContent="flex-end">
            <Button
              variant="outlined"
              color="inherit"
              onClick={handleGenerate}
              disabled={generatorStatus === 'loading'}
            >
              {generatorStatus === 'loading' ? 'Generating…' : 'Generate with GPT-5'}
            </Button>
          </Stack>
        </Stack>
      </Stack>
    </Paper>
  );
}
