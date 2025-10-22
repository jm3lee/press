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
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle,
  Paper,
  Stack,
  TextField,
  Typography
} from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import { FlashofferThemeProvider, MultipleChoiceQuiz } from 'flashoffer-react';

const GENERATOR_ENDPOINT = '/api/quiz/questions/generate';
const QUESTIONS_ENDPOINT = '/api/quiz/questions';
const GENERATOR_PROMPT_STORAGE_KEY = 'quiz-manager:last-generator-prompt';
const DEFAULT_CELEBRATION = 'off';

/**
 * Trims arbitrary values into normalized strings.
 * @param {unknown} value - Candidate value to normalize.
 * @returns {string} Trimmed string value.
 */
function trimValue(value) {
  return String(value ?? '').trim();
}

/**
 * Returns a trimmed string while preserving empty values.
 * @param {unknown} value - Optional input to normalize.
 * @returns {string} Trimmed string or an empty string.
 */
function optionalTrimmed(value) {
  const trimmed = trimValue(value);
  return trimmed || '';
}

/**
 * Resolves an ISO date string using a fallback when missing.
 * @param {unknown} value - Date-like input value.
 * @param {string} fallback - Replacement when the value is empty.
 * @returns {string} ISO formatted date string.
 */
function isoDateValue(value, fallback) {
  const base = trimValue(value) || fallback;
  return base.slice(0, 10);
}

/**
 * Produces an optional ISO date truncated to ten characters.
 * @param {unknown} value - Candidate optional date.
 * @returns {string} ISO date string or an empty string.
 */
function optionalIsoDate(value) {
  const trimmed = trimValue(value);
  return trimmed ? trimmed.slice(0, 10) : '';
}

/**
 * Maps raw options into payload-ready entries.
 * @param {unknown} options - Arbitrary option collection.
 * @returns {Array<{ id: string, label: string, description?: string }>} Normalized options.
 */
function normalizePayloadOptions(options) {
  return (Array.isArray(options) ? options : [])
    .map((option) => ({
      id: trimValue(option?.id),
      label: trimValue(option?.label),
      description: trimValue(option?.description)
    }))
    .filter((option) => option.id || option.label)
    .map((option) => {
      const nextOption = {
        id: option.id,
        label: option.label || option.id
      };
      if (option.description) {
        nextOption.description = option.description;
      }
      return nextOption;
    });
}

/**
 * Validates option content and resolves the correct answer identifier.
 * @param {unknown} options - Generated question options.
 * @param {unknown} preferredId - Desired correct option identifier.
 * @returns {{ normalizedOptions: Array<object>, correctOptionId: string }} Normalized results.
 */
function normalizeAndValidateOptions(options, preferredId) {
  const normalizedOptions = normalizePayloadOptions(options);

  if (normalizedOptions.length < 3) {
    throw new Error('Generated question must include at least three answer options.');
  }

  const optionIds = normalizedOptions.map((option) => option.id);
  if (!optionIds.every((value) => Boolean(value))) {
    throw new Error('Each answer option must include a non-empty id.');
  }

  if (new Set(optionIds).size !== optionIds.length) {
    throw new Error('Each answer option id must be unique.');
  }

  let correctOptionId = trimValue(preferredId);
  const hasPreferred =
    correctOptionId && normalizedOptions.some((option) => option.id === correctOptionId);
  if (!hasPreferred) {
    correctOptionId = normalizedOptions[0]?.id ?? '';
  }

  if (!correctOptionId) {
    throw new Error('Generated question is missing a valid correct option id.');
  }

  return {
    normalizedOptions,
    correctOptionId
  };
}

/**
 * Builds the payload used to persist a generated question.
 * @param {unknown} generated - Question returned from the generator endpoint.
 * @returns {object} Backend payload ready for creation.
 */
function buildCreationPayload(generated) {
  if (!generated || typeof generated !== 'object') {
    throw new Error('Generate a question before creating it.');
  }

  const slug = trimValue(generated.slug);
  if (!slug) {
    throw new Error('Generated question is missing a slug.');
  }

  const questionText = trimValue(generated.question);
  if (!questionText) {
    throw new Error('Generated question is missing the prompt.');
  }

  const { normalizedOptions, correctOptionId } = normalizeAndValidateOptions(
    generated.options,
    generated.correct_option_id
  );

  const today = new Date().toISOString().slice(0, 10);
  const publishedOn = isoDateValue(generated.published_on, today);
  const expiresOn = optionalIsoDate(generated.expires_on);

  const celebrationValue = trimValue(generated.celebration);
  const celebration = celebrationValue || DEFAULT_CELEBRATION;

  const payload = {
    slug,
    question: questionText,
    helper_text: optionalTrimmed(generated.helper_text) || undefined,
    explanation: optionalTrimmed(generated.explanation) || undefined,
    success_message: optionalTrimmed(generated.success_message) || undefined,
    error_message: optionalTrimmed(generated.error_message) || undefined,
    options: normalizedOptions,
    correct_option_id: correctOptionId,
    published_on: publishedOn,
    celebration
  };

  if (expiresOn) {
    payload.expires_on = expiresOn;
  }

  return payload;
}

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
  const [createStatus, setCreateStatus] = useState('idle');
  const [createDialog, setCreateDialog] = useState({
    open: false,
    severity: 'success',
    message: ''
  });

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
      setCreateDialog({ open: false, severity: 'success', message: '' });
    } catch (error) {
      setGeneratedQuestion(null);
      setGeneratorError(
        error instanceof Error ? error.message : 'Generation failed unexpectedly.'
      );
    } finally {
      setGeneratorStatus('idle');
    }
  }, [generatorPrompt]);

  const handleCreateQuestion = useCallback(async () => {
    if (typeof window === 'undefined') {
      setCreateDialog({
        open: true,
        severity: 'error',
        message: 'Creation is not available in this environment.'
      });
      return;
    }

    setCreateStatus('loading');
    setCreateDialog({ open: false, severity: 'success', message: '' });

    try {
      const payload = buildCreationPayload(generatedQuestion);
      const url = new URL(
        "http://localhost:8002" + QUESTIONS_ENDPOINT,
        window.location.origin
      );
      const response = await fetch(url.toString(), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload)
      });

      const body = await response.json().catch(() => ({}));

      if (!response.ok) {
        const message = body?.error ?? `Creation failed (${response.status})`;
        throw new Error(message);
      }

      if (body?.question && typeof body.question === 'object') {
        setGeneratedQuestion(body.question);
      }

      const slug = trimValue(body?.question?.slug ?? payload.slug);
      const questionLabel = slug ? `Created question ${slug}` : 'Created question';
      setCreateDialog({ open: true, severity: 'success', message: questionLabel });
    } catch (error) {
      setCreateDialog({
        open: true,
        severity: 'error',
        message:
          error instanceof Error ? error.message : 'Creation failed unexpectedly.'
      });
    } finally {
      setCreateStatus('idle');
    }
  }, [generatedQuestion]);

  /**
   * Closes the modal dialog used to communicate creation results.
   */
  const handleCloseCreateDialog = useCallback(() => {
    setCreateDialog((previous) => ({ ...previous, open: false }));
  }, []);

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
    <>
      <Paper elevation={6} className="quiz-manager__panel">
        <Stack spacing={2}>
        <Typography variant="h5" component="h2">
          GPT-5 Drafts
        </Typography>
        <Typography variant="body2" color="textSecondary">
          Provide a short prompt and the manager will request a draft question
          from the backend generator endpoint.
        </Typography>
      </Stack>
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
              variant="contained"
              color="primary"
              onClick={handleCreateQuestion}
              disabled={createStatus === 'loading' || !generatedQuestion}
            >
              {createStatus === 'loading' ? 'Creating…' : 'Create question'}
            </Button>
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
      </Paper>
      <Dialog open={createDialog.open} onClose={handleCloseCreateDialog}>
        <DialogTitle>
          {createDialog.severity === 'success' ? 'Question created' : 'Creation failed'}
        </DialogTitle>
        <DialogContent>
          <DialogContentText>{createDialog.message}</DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseCreateDialog} autoFocus>
            Close
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
}
