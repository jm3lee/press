/*
 * Copyright (c) Flashoffer Developers
 * Released under the MIT license.
 */

import {
  useCallback,
  useDeferredValue,
  useEffect,
  useMemo,
  useState
} from 'react';
import { Box, Stack } from '@mui/material';
import CreateQuestionPage from './CreateQuestionPage.jsx';
import ExistingQuestionsPage from './ExistingQuestionsPage.jsx';

const API_BASE_URL = 'http://localhost:8002';
const QUESTIONS_ENDPOINT = '/api/quiz/questions';
const DEFAULT_CELEBRATION = 'off';
const CELEBRATION_OPTIONS = ['off', 'classic', 'streamers', 'burst'];
const CELEBRATION_LABELS = {
  off: 'None',
  classic: 'Classic confetti',
  streamers: 'Streamer launch',
  burst: 'Grand finale'
};
const MIN_OPTIONS = 3;

/**
 * Indicates that the submitted form data failed validation rules.
 */
class FormValidationError extends Error {
  constructor(message) {
    super(message);
    this.name = 'FormValidationError';
  }
}

/**
 * Produces an empty answer option template.
 * @returns {{ id: string, label: string, description: string }} Blank option.
 */
function emptyOption() {
  return { id: '', label: '', description: '' };
}

/**
 * Resolves the current date in ISO-8601 (YYYY-MM-DD) format.
 * @returns {string} Today's date string.
 */
function todayIso() {
  return new Date().toISOString().slice(0, 10);
}

/**
 * Builds a pristine form object with default values.
 * @returns {object} Empty form state.
 */
function createEmptyForm() {
  return {
    slug: '',
    question: '',
    helper_text: '',
    explanation: '',
    success_message: '',
    error_message: '',
    published_on: todayIso(),
    expires_on: '',
    correct_option_id: '',
    celebration: DEFAULT_CELEBRATION,
    options: [emptyOption(), emptyOption(), emptyOption()]
  };
}

/**
 * Converts unknown values into trimmed strings.
 * @param {unknown} value - Arbitrary input to normalize.
 * @returns {string} Trimmed string representation.
 */
function trimValue(value) {
  return String(value ?? '').trim();
}

/**
 * Normalizes optional string inputs while preserving empty state.
 * @param {unknown} value - Candidate value to normalize.
 * @returns {string} Trimmed value or an empty string.
 */
function optionalTrimmed(value) {
  const trimmed = trimValue(value);
  return trimmed || '';
}

/**
 * Generates a trimmed ISO date, defaulting to a fallback when empty.
 * @param {unknown} value - Candidate date value.
 * @param {string} fallback - Replacement when the value is empty.
 * @returns {string} ISO formatted date.
 */
function isoDateValue(value, fallback) {
  const base = trimValue(value) || fallback;
  return base.slice(0, 10);
}

/**
 * Produces an optional ISO date string truncated to the first ten characters.
 * @param {unknown} value - Date-like value.
 * @returns {string} ISO formatted date or an empty string.
 */
function optionalIsoDate(value) {
  const trimmed = trimValue(value);
  return trimmed ? trimmed.slice(0, 10) : '';
}

/**
 * Normalizes incoming option entries to ensure predictable structure.
 * @param {unknown} options - Raw options from user input or imports.
 * @returns {Array<{ id: string, label: string, description: string }>} Normalized options.
 */
function normalizeOptionEntries(options) {
  if (!Array.isArray(options) || options.length === 0) {
    return [emptyOption(), emptyOption(), emptyOption()];
  }
  return options.map((option) => ({
    id: trimValue(option.id),
    label: trimValue(option.label),
    description: optionalTrimmed(option.description)
  }));
}

/**
 * Maps backend question payloads into the interactive form shape.
 * @param {object} [question] - Optional question payload from storage.
 * @returns {object} Prepared form state.
 */
function buildFormStateForQuestion(question) {
  const normalizedOptions = normalizeOptionEntries(question?.options);
  const formState = {
    ...createEmptyForm(),
    options: normalizedOptions
  };

  if (question) {
    formState.slug = trimValue(question.slug);
    formState.question = String(question.question ?? '');
    formState.helper_text = optionalTrimmed(question.helper_text);
    formState.explanation = optionalTrimmed(question.explanation);
    formState.success_message = optionalTrimmed(question.success_message);
    formState.error_message = optionalTrimmed(question.error_message);
    formState.published_on = isoDateValue(question.published_on, todayIso());
    formState.expires_on = optionalIsoDate(question.expires_on);
    formState.correct_option_id = trimValue(question.correct_option_id);
    const celebration = trimValue(question.celebration);
    formState.celebration = CELEBRATION_OPTIONS.includes(celebration)
      ? celebration
      : DEFAULT_CELEBRATION;
  }

  if (!formState.correct_option_id && normalizedOptions.length > 0) {
    formState.correct_option_id = normalizedOptions[0].id;
  }

  return formState;
}

/**
 * Resolves the most appropriate correct answer identifier.
 * @param {Array<{ id: string }>} normalizedOptions - Validated answer options.
 * @param {string} preferredId - Desired correct answer identifier.
 * @returns {string} Selected correct identifier.
 */
function resolvePreferredCorrectId(normalizedOptions, preferredId) {
  if (preferredId && normalizedOptions.some((option) => option.id === preferredId)) {
    return preferredId;
  }
  return normalizedOptions[0]?.id ?? '';
}

/**
 * Determines the option collection that should power the live preview.
 * @param {object} formState - Current form data.
 * @returns {Array<{ id: string, label: string, description: string }>} Options to preview.
 */
function getPreviewOptionsSource(formState) {
  if (Array.isArray(formState.options) && formState.options.length > 0) {
    return formState.options;
  }
  return [emptyOption(), emptyOption(), emptyOption()];
}

/**
 * Converts a raw option into a preview-safe variant with fallbacks.
 * @param {{ id: string, label: string, description: string }} option - Source option.
 * @param {number} index - Option index for fallback values.
 * @returns {{ id: string, label: string, description?: string }} Preview-ready option.
 */
function toPreviewOption(option, index) {
  const id = trimValue(option.id);
  const label = trimValue(option.label);
  const description = optionalTrimmed(option.description) || undefined;
  return {
    id: id || `option-${index + 1}`,
    label: label || id || `Option ${index + 1}`,
    description
  };
}

/**
 * Determines whether any option contains meaningful preview content.
 * @param {Array<{ label: string, description?: string }>} options - Preview candidates.
 * @returns {boolean} True when at least one option has content.
 */
function previewOptionsHaveContent(options) {
  return options.some((option) => Boolean(option.label || option.description));
}

/**
 * Checks if any preview field includes user-provided data.
 * @param {Array<unknown>} parts - Preview fragments to inspect.
 * @returns {boolean} True when at least one fragment is truthy.
 */
function previewHasContent(parts) {
  return parts.some(Boolean);
}

/**
 * Builds the live preview question payload derived from the form state.
 * @param {object} formState - Current form values.
 * @returns {object | undefined} Preview question or undefined when empty.
 */
function resolvePreviewQuestion(formState) {
  const normalizedOptions = getPreviewOptionsSource(formState).map((option, index) =>
    toPreviewOption(option, index)
  );

  const questionText = trimValue(formState.question);
  const helperText = optionalTrimmed(formState.helper_text);
  const explanation = optionalTrimmed(formState.explanation);
  const successMessage = optionalTrimmed(formState.success_message);
  const errorMessage = optionalTrimmed(formState.error_message);
  const celebrationValue = trimValue(formState.celebration);
  const resolvedCelebration = CELEBRATION_OPTIONS.includes(celebrationValue)
    ? celebrationValue
    : DEFAULT_CELEBRATION;
  const hasOptionContent = previewOptionsHaveContent(normalizedOptions);
  const hasContent = previewHasContent([
    questionText,
    helperText,
    explanation,
    successMessage,
    errorMessage,
    hasOptionContent
  ]);

  if (!hasContent) {
    return undefined;
  }

  const resolvedCorrect = resolvePreferredCorrectId(
    normalizedOptions,
    trimValue(formState.correct_option_id)
  );

  return {
    question: questionText || 'Untitled question',
    helperText: helperText || undefined,
    options: normalizedOptions,
    correctOptionId: resolvedCorrect,
    explanation: explanation || undefined,
    successMessage: successMessage || undefined,
    errorMessage: errorMessage || undefined,
    celebration: resolvedCelebration
  };
}

/**
 * Converts form options into the payload structure expected by the backend.
 * @param {Array<{ id: string, label: string, description: string }>} formOptions - Form options.
 * @returns {Array<{ id: string, label: string, description?: string }>} Payload-ready options.
 */
function normalizePayloadOptions(formOptions) {
  return formOptions
    .map((option) => ({
      id: trimValue(option.id),
      label: trimValue(option.label),
      description: trimValue(option.description)
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
 * Throws a validation error when a constraint is not satisfied.
 * @param {boolean} condition - Constraint to evaluate.
 * @param {string} message - Error message when the condition fails.
 */
function assertCondition(condition, message) {
  if (!condition) {
    throw new FormValidationError(message);
  }
}

/**
 * Validates option input and selects the correct answer identifier.
 * @param {Array<{ id: string, label: string, description: string }>} formOptions - Option entries.
 * @param {string} preferredId - Preferred correct option identifier.
 * @returns {{ normalizedOptions: Array<object>, correctOptionId: string }} Normalized results.
 */
function normalizeAndValidateOptions(formOptions, preferredId) {
  const normalizedOptions = normalizePayloadOptions(formOptions);
  assertCondition(normalizedOptions.length >= MIN_OPTIONS, 'Provide at least three answer options.');

  const optionIds = normalizedOptions.map((option) => option.id);
  assertCondition(optionIds.every((value) => Boolean(value)), 'Each option must include a non-empty id.');
  assertCondition(new Set(optionIds).size === optionIds.length, 'Each option id must be unique.');

  const correctOptionId = resolvePreferredCorrectId(normalizedOptions, trimValue(preferredId));
  assertCondition(Boolean(correctOptionId), 'Correct option must reference one of the option ids.');

  return {
    normalizedOptions,
    correctOptionId
  };
}

/**
 * Converts validation failures into user-facing error messages when appropriate.
 * @param {unknown} error - Error thrown during payload construction.
 * @param {boolean} silent - When true, suppresses inline error messaging.
 * @param {(message: string) => void} setFormError - Setter for form error state.
 * @returns {null} Always returns null for handled validation errors.
 */
function handlePayloadError(error, silent, setFormError) {
  if (!silent && error instanceof FormValidationError) {
    setFormError(error.message);
  }
  if (error instanceof FormValidationError) {
    return null;
  }
  throw error;
}

/**
 * Resolves the confirmation message shown after a successful submission.
 * @param {'create' | 'update'} mode - Submission mode.
 * @param {string} slug - Question slug used in the confirmation copy.
 * @returns {string} Human readable status message.
 */
function resolveSubmissionMessage(mode, slug) {
  return mode === 'update'
    ? `Updated question ${slug}`
    : `Created question ${slug}`;
}

/**
 * Applies post-submission side effects such as resetting the form state.
 * @param {object} params - Side effect configuration.
 * @param {'create' | 'update'} params.mode - Submission mode.
 * @param {object} params.payload - Submitted payload.
 * @param {() => void} params.resetForm - Resets the form to its defaults.
 * @param {(message: string) => void} params.setFormSuccess - Success state setter.
 * @returns {void}
 */
function applySubmissionSideEffects({ mode, payload, resetForm, setFormSuccess }) {
  if (mode === 'create') {
    resetForm();
  }
  setFormSuccess(resolveSubmissionMessage(mode, payload.slug));
}

/**
 * Expands a relative API path into a fully qualified URL for the backend.
 * @param {string} path - Endpoint path beginning with a slash.
 * @returns {string} Fully qualified API URL.
 */
function resolveApiUrl(path) {
  return `${API_BASE_URL}${path}`;
}

/**
 * Safely refreshes the question catalog while swallowing handled errors.
 * @param {() => Promise<unknown>} fetchQuestions - Fetch callback.
 * @returns {Promise<void>} Promise that resolves once the refresh completes.
 */
async function refreshQuestions(fetchQuestions) {
  try {
    await fetchQuestions();
  } catch {
    /* handled in state */
  }
}

/**
 * Sends the normalized payload to the backend for persistence.
 * @param {object} payload - Normalized question payload.
 * @param {'create' | 'update'} mode - Submission mode.
 * @returns {Promise<object>} Parsed backend response body.
 */
async function submitQuestionPayload(payload, mode) {
  const baseUrl = resolveApiUrl(QUESTIONS_ENDPOINT);
  const targetUrl =
    mode === 'update'
      ? `${baseUrl}/${encodeURIComponent(payload.slug)}`
      : baseUrl;

  const response = await fetch(targetUrl, {
    method: mode === 'update' ? 'PUT' : 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(payload)
  });

  const body = await response.json().catch(() => ({}));

  if (!response.ok) {
    const message = body?.error ?? `Request failed (${response.status})`;
    throw new Error(message);
  }

  return body;
}

/**
 * Coordinates submission, handles optimistic updates, and refreshes the list.
 * @param {object} params - Workflow configuration.
 * @param {object} params.form - Raw form state.
 * @param {(form: object, options?: { silent?: boolean }) => object | null} params.buildPayload -
 *  Payload builder.
 * @param {'create' | 'update'} params.formMode - Submission mode.
 * @param {(question: object, mode?: 'create' | 'update') => void} params.applyQuestionToForm -
 *  Syncs the form with the persisted question.
 * @param {() => void} params.resetForm - Resets the form to defaults.
 * @param {(message: string) => void} params.setFormError - Error state setter.
 * @param {(message: string) => void} params.setFormSuccess - Success state setter.
 * @param {(status: 'idle' | 'submitting') => void} params.setFormStatus - Submission status setter.
 * @param {() => Promise<unknown>} params.fetchQuestions - Refresh callback for the catalog.
 * @returns {Promise<void>} Promise that resolves when the submission flow finishes.
 */
async function submitFormWorkflow({
  form,
  buildPayload,
  formMode,
  applyQuestionToForm,
  resetForm,
  setFormError,
  setFormSuccess,
  setFormStatus,
  fetchQuestions
}) {
  setFormError('');
  setFormSuccess('');

  const payload = buildPayload(form);
  if (!payload) {
    return;
  }

  setFormStatus('submitting');

  try {
    const body = await submitQuestionPayload(payload, formMode);

    applyQuestionToForm(body.question, formMode === 'update' ? 'update' : 'create');
    applySubmissionSideEffects({
      mode: formMode,
      payload,
      resetForm,
      setFormSuccess
    });
    await refreshQuestions(fetchQuestions);
  } catch (error) {
    setFormError(error instanceof Error ? error.message : 'Request failed');
  } finally {
    setFormStatus('idle');
  }
}

/**
 * Coordinates form state, question list, and submission workflows.
 * @returns {JSX.Element} Rendered management workflow.
 */
export default function ManageQuestionsContainer() {
  const [form, setForm] = useState(() => createEmptyForm());
  const [formMode, setFormMode] = useState('create');
  const [formStatus, setFormStatus] = useState('idle');
  const [formError, setFormError] = useState('');
  const [formSuccess, setFormSuccess] = useState('');
  const [fileError, setFileError] = useState('');
  const [fileName, setFileName] = useState('');
  const [questions, setQuestions] = useState([]);
  const [questionsStatus, setQuestionsStatus] = useState('idle');
  const [questionsError, setQuestionsError] = useState('');
  const [selectedSlug, setSelectedSlug] = useState('');

  /**
   * Syncs the interactive form with a persisted question payload.
   * @param {object} question - Question data sourced from the backend.
   * @param {'create' | 'update'} [mode='update'] - Desired form mode.
   * @returns {void}
   */
  const applyQuestionToForm = useCallback((question, mode = 'update') => {
    if (!question) {
      return;
    }

    const normalized = buildFormStateForQuestion(question);
    setForm(normalized);
    setFormMode(mode);
    setFormError('');
    setFormSuccess('');
    setSelectedSlug(mode === 'update' ? normalized.slug : '');
  }, []);

  /**
   * Restores the form to a pristine state for authoring a new question.
   * @returns {void}
   */
  const resetForm = useCallback(() => {
    setForm(createEmptyForm());
    setFormMode('create');
    setFormError('');
    setFormSuccess('');
    setFileError('');
    setFileName('');
    setSelectedSlug('');
  }, []);

  /**
   * Loads the latest quiz questions from the backend service.
   * @returns {Promise<Array<object>>} Loaded question collection.
   */
  const fetchQuestions = useCallback(async () => {
    if (typeof window === 'undefined') {
      return [];
    }

    setQuestionsStatus('loading');
    setQuestionsError('');

    try {
      const url = new URL(resolveApiUrl(QUESTIONS_ENDPOINT));
      url.searchParams.set('limit', '50');
      url.searchParams.set('offset', '0');

      const response = await fetch(url.toString());
      const body = await response.json().catch(() => ({}));

      if (!response.ok) {
        const message = body?.error ?? `Failed to load questions (${response.status})`;
        throw new Error(message);
      }

      const items = Array.isArray(body?.questions) ? body.questions : [];
      setQuestions(items);
      setQuestionsStatus('success');
      setSelectedSlug((current) =>
        current && items.some((item) => item.slug === current) ? current : ''
      );
      return items;
    } catch (error) {
      setQuestionsStatus('error');
      setQuestionsError(
        error instanceof Error ? error.message : 'Unable to load questions'
      );
      setQuestions([]);
      setSelectedSlug('');
      throw error;
    }
  }, []);

  useEffect(() => {
    fetchQuestions().catch(() => {
      /* handled in state */
    });
  }, [fetchQuestions]);

  /**
   * Generates a change handler for the provided form field key.
   * @param {string} field - Form field name to update.
   * @returns {(event: import('react').ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => void}
   *  Field change handler.
   */
  const handleFieldChange = useCallback((field) => (event) => {
    const { value } = event.target;
    setForm((prev) => ({
      ...prev,
      [field]: value
    }));
  }, []);

  /**
   * Generates a change handler for a specific answer option entry.
   * @param {number} index - Option index to mutate.
   * @param {string} field - Option field key.
   * @returns {(event: import('react').ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => void}
   *  Option change handler.
   */
  const handleOptionChange = useCallback((index, field) => (event) => {
    const { value } = event.target;
    setForm((prev) => {
      const nextOptions = prev.options.map((option, optionIndex) => {
        if (optionIndex !== index) {
          return option;
        }
        return {
          ...option,
          [field]: value
        };
      });
      return {
        ...prev,
        options: nextOptions
      };
    });
  }, []);

  /**
   * Appends a blank answer option to the form state.
   * @returns {void}
   */
  const handleAddOption = useCallback(() => {
    setForm((prev) => ({
      ...prev,
      options: [...prev.options, emptyOption()]
    }));
  }, []);

  /**
   * Removes an option row while preserving minimum option constraints.
   * @param {number} index - Index of the option slated for deletion.
   * @returns {void}
   */
  const handleRemoveOption = useCallback((index) => {
    setForm((prev) => {
      if (prev.options.length <= MIN_OPTIONS) {
        return prev;
      }
      const nextOptions = prev.options.filter((_, optionIndex) => optionIndex !== index);
      let nextCorrect = prev.correct_option_id;
      if (!nextOptions.some((option) => option.id === nextCorrect)) {
        nextCorrect = nextOptions[0]?.id ?? '';
      }
      return {
        ...prev,
        options: nextOptions,
        correct_option_id: nextCorrect
      };
    });
  }, []);

  /**
   * Updates the form with the selected correct answer identifier.
   * @param {import('react').ChangeEvent<HTMLInputElement>} event - Change event.
   * @returns {void}
   */
  const handleCorrectOptionChange = useCallback((event) => {
    setForm((prev) => ({ ...prev, correct_option_id: event.target.value }));
  }, []);

  /**
   * Constructs the API payload while surfacing validation failures.
   * @param {object} targetForm - Candidate form state.
   * @param {{ silent?: boolean }} [options] - Payload builder options.
   * @returns {object | null} Normalized payload or null on validation error.
   */
  const buildPayload = useCallback((targetForm, options = { silent: false }) => {
    const { silent } = options;

    try {
      const slug = trimValue(targetForm.slug);
      assertCondition(slug, 'Slug is required.');

      const questionText = trimValue(targetForm.question);
      assertCondition(questionText, 'Question prompt is required.');

      const { normalizedOptions, correctOptionId } = normalizeAndValidateOptions(
        targetForm.options,
        targetForm.correct_option_id
      );

      const publishedOn = trimValue(targetForm.published_on);
      assertCondition(/^(\d{4})-(\d{2})-(\d{2})$/.test(publishedOn), 'Published date must be in YYYY-MM-DD format.');

      const expiresOn = trimValue(targetForm.expires_on);
      const celebrationValue = trimValue(targetForm.celebration) || DEFAULT_CELEBRATION;
      const celebration = CELEBRATION_OPTIONS.includes(celebrationValue)
        ? celebrationValue
        : DEFAULT_CELEBRATION;

      return {
        slug,
        question: questionText,
        helper_text: optionalTrimmed(targetForm.helper_text) || undefined,
        explanation: optionalTrimmed(targetForm.explanation) || undefined,
        success_message: optionalTrimmed(targetForm.success_message) || undefined,
        error_message: optionalTrimmed(targetForm.error_message) || undefined,
        options: normalizedOptions,
        correct_option_id: correctOptionId,
        published_on: publishedOn,
        expires_on: expiresOn ? expiresOn : undefined,
        celebration
      };
    } catch (error) {
      return handlePayloadError(error, silent, setFormError);
    }
  }, []);

  const deferredForm = useDeferredValue(form);

  const previewPayload = useMemo(
    () => buildPayload(deferredForm, { silent: true }),
    [buildPayload, deferredForm]
  );

  const preview = useMemo(() => {
    if (!previewPayload) {
      return '';
    }
    return JSON.stringify(previewPayload, null, 2);
  }, [previewPayload]);

  const previewQuestion = useMemo(
    () => resolvePreviewQuestion(deferredForm),
    [deferredForm]
  );

  /**
   * Handles form submission by delegating to the workflow helper.
   * @returns {void}
   */
  const handleSubmit = useCallback(() => {
    submitFormWorkflow({
      form,
      buildPayload,
      formMode,
      applyQuestionToForm,
      resetForm,
      setFormError,
      setFormSuccess,
      setFormStatus,
      fetchQuestions
    });
  }, [
    applyQuestionToForm,
    buildPayload,
    fetchQuestions,
    form,
    formMode,
    resetForm,
    setFormError,
    setFormSuccess,
    setFormStatus
  ]);

  /**
   * Imports JSON payloads and maps them into form state.
   * @param {import('react').ChangeEvent<HTMLInputElement>} event - File input event.
   * @returns {void}
   */
  const handleFileChange = useCallback((event) => {
    const [file] = event.target.files ?? [];
    setFileName('');
    setFileError('');

    if (!file) {
      return;
    }

    setFileName(file.name);
    file
      .text()
      .then((rawText) => {
        try {
          const parsed = JSON.parse(rawText);
          if (Array.isArray(parsed)) {
            if (parsed.length !== 1) {
              throw new Error('When providing an array, include exactly one question');
            }
            applyQuestionToForm(parsed[0], 'create');
          } else {
            applyQuestionToForm(parsed, 'create');
          }
        } catch (parseError) {
          setFileError(
            parseError instanceof Error ? parseError.message : 'Invalid JSON payload'
          );
        }
      })
      .catch(() => {
        setFileError('Unable to read the selected file');
      });
  }, [applyQuestionToForm]);

  /**
   * Hydrates the form with an existing question for editing.
   * @param {object} question - Selected question payload.
   * @returns {void}
   */
  const handleSelectQuestion = useCallback(
    (question) => {
      if (!question) {
        return;
      }
      applyQuestionToForm(question, 'update');
    },
    [applyQuestionToForm]
  );

  const formDisabled = formStatus === 'submitting';
  const canSubmit = Boolean(previewPayload);

  return (
    <Stack spacing={3} sx={{ width: '100%' }}>
      <Stack
        direction={{ xs: 'column', lg: 'row' }}
        spacing={3}
        alignItems="stretch"
        sx={{ width: '100%' }}
      >
        <Box sx={{ flex: { lg: 2 }, width: '100%' }}>
          <CreateQuestionPage
            canSubmit={canSubmit}
            celebrationLabels={CELEBRATION_LABELS}
            celebrationOptions={CELEBRATION_OPTIONS}
            fileError={fileError}
            fileName={fileName}
            form={form}
            formDisabled={formDisabled}
            formError={formError}
            formMode={formMode}
            formSuccess={formSuccess}
            handleAddOption={handleAddOption}
            handleCorrectOptionChange={handleCorrectOptionChange}
            handleFieldChange={handleFieldChange}
            handleFileChange={handleFileChange}
            handleOptionChange={handleOptionChange}
            handleRemoveOption={handleRemoveOption}
            handleSubmit={handleSubmit}
            preview={preview}
            previewQuestion={previewQuestion}
            resetForm={resetForm}
          />
        </Box>
        <Box sx={{ flex: { lg: 1 }, width: '100%' }}>
          <ExistingQuestionsPage
            fetchQuestions={fetchQuestions}
            handleSelectQuestion={handleSelectQuestion}
            questions={questions}
            questionsError={questionsError}
            questionsStatus={questionsStatus}
            selectedSlug={selectedSlug}
          />
        </Box>
      </Stack>
    </Stack>
  );
}
