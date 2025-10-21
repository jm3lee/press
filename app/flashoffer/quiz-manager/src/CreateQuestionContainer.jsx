/*
 * Copyright (c) Flashoffer Developers
 * Released under the MIT license.
 */

import { forwardRef, useCallback, useImperativeHandle, useMemo, useState } from 'react';
import CreateQuestionPage from './CreateQuestionPage.jsx';

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
 * Coordinates form state and interaction handlers for the create-question view.
 * @returns {JSX.Element} Rendered create question workflow.
 */
const CreateQuestionContainer = forwardRef(function CreateQuestionContainer(props, ref) {
  void props;
  const [form, setForm] = useState(() => createEmptyForm());
  const [formMode, setFormMode] = useState('create');
  const [formError, setFormError] = useState('');
  const [formSuccess, setFormSuccess] = useState('');
  const [fileError, setFileError] = useState('');
  const [fileName, setFileName] = useState('');

  const applyQuestionToForm = useCallback((question, mode, successMessage = '') => {
    setForm(buildFormStateForQuestion(question));
    setFormMode(mode);
    setFormError('');
    setFormSuccess(successMessage);
    setFileError('');
    setFileName('');
  }, []);

  const resetForm = useCallback(() => {
    setForm(createEmptyForm());
    setFormMode('create');
    setFormError('');
    setFormSuccess('');
    setFileError('');
    setFileName('');
  }, []);

  useImperativeHandle(
    ref,
    () => ({
      applyQuestionToForm,
      resetForm,
      setFormSuccess(message) {
        setFormSuccess(message);
      }
    }),
    [applyQuestionToForm, resetForm]
  );

  const handleFieldChange = useCallback((field) => (event) => {
    const { value } = event.target;
    setForm((prev) => ({
      ...prev,
      [field]: value
    }));
  }, []);

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

  const handleAddOption = useCallback(() => {
    setForm((prev) => ({
      ...prev,
      options: [...prev.options, emptyOption()]
    }));
  }, []);

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

  const handleCorrectOptionChange = useCallback((event) => {
    setForm((prev) => ({ ...prev, correct_option_id: event.target.value }));
  }, []);

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
      assertCondition(/^\d{4}-\d{2}-\d{2}$/.test(publishedOn), 'Published date must be in YYYY-MM-DD format.');

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

  const previewPayload = useMemo(() => buildPayload(form, { silent: true }), [buildPayload, form]);

  const preview = useMemo(() => {
    if (!previewPayload) {
      return '';
    }
    return JSON.stringify(previewPayload, null, 2);
  }, [previewPayload]);

  const previewQuestion = useMemo(() => resolvePreviewQuestion(form), [form]);

  const handleSubmit = useCallback(() => {
    const payload = buildPayload(form);
    if (!payload) {
      return;
    }
    setFormSuccess(`Preview ready for question ${payload.slug}`);
  }, [buildPayload, form]);

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

  const formDisabled = false;
  const canSubmit = Boolean(previewPayload);

  return (
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
  );
});

export default CreateQuestionContainer;
