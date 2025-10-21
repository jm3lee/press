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
import {
  Button,
  Paper,
  Stack,
  Typography
} from '@mui/material';
import {
  Link as RouterLink,
  Navigate,
  Route,
  Routes,
  useLocation,
  useNavigate
} from 'react-router-dom';
import CreateQuestionPage from './pages/CreateQuestionPage.jsx';
import ExistingQuestionsPage from './pages/ExistingQuestionsPage.jsx';
import GeneratorPage from './pages/GeneratorPage.jsx';

const PAGE_DEFINITIONS = [
  { id: 'create', path: '/create', label: 'Create Question' },
  { id: 'generate', path: '/generate', label: 'GPT Drafts' },
  { id: 'questions', path: '/questions', label: 'Existing Questions' }
];

const DEFAULT_PAGE_PATH = '/create';

const emptyOption = () => ({
  id: '',
  label: '',
  description: ''
});

const todayIso = () => new Date().toISOString().slice(0, 10);

const createEmptyForm = () => ({
  slug: '',
  question: '',
  helper_text: '',
  explanation: '',
  success_message: '',
  error_message: '',
  published_on: todayIso(),
  expires_on: '',
  correct_option_id: '',
  options: [emptyOption(), emptyOption(), emptyOption()]
});

class FormValidationError extends Error {
  constructor(message) {
    super(message);
    this.name = 'FormValidationError';
  }
}

const MIN_OPTIONS = 3;

function trimValue(value) {
  return String(value ?? '').trim();
}

function optionalTrimmed(value) {
  const trimmed = trimValue(value);
  return trimmed || '';
}

function isoDateValue(value, fallback) {
  const base = trimValue(value) || fallback;
  return base.slice(0, 10);
}

function optionalIsoDate(value) {
  const trimmed = trimValue(value);
  return trimmed ? trimmed.slice(0, 10) : '';
}

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

function buildFormStateForQuestion(question, normalizeOptionsFn) {
  const normalizedOptions = normalizeOptionsFn(question?.options);
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
  }

  if (!formState.correct_option_id && normalizedOptions.length > 0) {
    formState.correct_option_id = normalizedOptions[0].id;
  }

  return formState;
}

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

function normalizeAndValidateOptions(formOptions, preferredId) {
  const normalizedOptions = normalizePayloadOptions(formOptions);
  assertCondition(
    normalizedOptions.length >= MIN_OPTIONS,
    'Provide at least three answer options.'
  );

  const optionIds = normalizedOptions.map((option) => option.id);
  assertCondition(
    optionIds.every((value) => Boolean(value)),
    'Each option must include a non-empty id.'
  );
  assertCondition(
    new Set(optionIds).size === optionIds.length,
    'Each option id must be unique.'
  );

  const correctOptionId = resolvePreferredCorrectId(
    normalizedOptions,
    trimValue(preferredId)
  );
  assertCondition(
    Boolean(correctOptionId),
    'Correct option must reference one of the option ids.'
  );

  return {
    normalizedOptions,
    correctOptionId
  };
}

function handlePayloadError(error, silent, setFormError) {
  if (!silent && error instanceof FormValidationError) {
    setFormError(error.message);
  }
  if (error instanceof FormValidationError) {
    return null;
  }
  throw error;
}

function assertCondition(condition, message) {
  if (!condition) {
    throw new FormValidationError(message);
  }
}

function resolvePreferredCorrectId(normalizedOptions, preferredId) {
  if (preferredId && normalizedOptions.some((option) => option.id === preferredId)) {
    return preferredId;
  }
  return normalizedOptions[0]?.id ?? '';
}

function getPreviewOptionsSource(formState) {
  if (Array.isArray(formState.options) && formState.options.length > 0) {
    return formState.options;
  }
  return [emptyOption(), emptyOption(), emptyOption()];
}

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

function previewOptionsHaveContent(options) {
  return options.some((option) => Boolean(option.label || option.description));
}


function previewHasContent(parts) {
  return parts.some(Boolean);
}

function resolvePreviewQuestion(formState) {
  const normalizedOptions = getPreviewOptionsSource(formState).map((option, index) =>
    toPreviewOption(option, index)
  );

  const questionText = trimValue(formState.question);
  const helperText = optionalTrimmed(formState.helper_text);
  const explanation = optionalTrimmed(formState.explanation);
  const successMessage = optionalTrimmed(formState.success_message);
  const errorMessage = optionalTrimmed(formState.error_message);
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
    errorMessage: errorMessage || undefined
  };
}


function resolveSubmissionMessage(mode, slug) {
  return mode === 'update'
    ? `Updated question ${slug}`
    : `Created question ${slug}`;
}

function applySubmissionSideEffects({ mode, payload, resetForm, setFormSuccess }) {
  if (mode === 'create') {
    resetForm();
  }
  setFormSuccess(resolveSubmissionMessage(mode, payload.slug));
}

async function submitFormWorkflow({
  form,
  buildPayload,
  formMode,
  normalizedUploadEndpoint,
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
    const body = await submitQuestionPayload(payload, formMode, normalizedUploadEndpoint);

    applyQuestionToForm(
      body.question,
      formMode === 'update' ? 'update' : 'create'
    );
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

async function refreshQuestions(fetchQuestions) {
  try {
    await fetchQuestions();
  } catch {
    /* handled in callers */
  }
}

async function submitQuestionPayload(payload, mode, endpoint) {
  const isUpdate = mode === 'update';
  const targetUrl = isUpdate
    ? `${endpoint}/${encodeURIComponent(payload.slug)}`
    : endpoint;
  const method = isUpdate ? 'PUT' : 'POST';

  const response = await fetch(targetUrl, {
    method,
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

async function requestGeneratedQuestion(endpoint, prompt) {
  const response = await fetch(endpoint, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      prompt: prompt || undefined
    })
  });

  const body = await response.json().catch(() => ({}));
  if (!response.ok) {
    const message = body?.error ?? `Generation failed (${response.status})`;
    throw new Error(message);
  }

  if (!body?.question) {
    throw new Error('Generation did not return a question payload');
  }

  return body;
}
/**
 * QuizManager allows operators to ingest quiz questions into the backend.
 *
 * @param {{ uploadEndpoint?: string, listEndpoint?: string }} props
 * @returns {JSX.Element}
 */
export default function QuizManager({
  uploadEndpoint = '/api/quiz/questions',
  listEndpoint
}) {
  const [form, setForm] = useState(createEmptyForm());
  const [formMode, setFormMode] = useState('create');
  const [formStatus, setFormStatus] = useState('idle');
  const [formError, setFormError] = useState('');
  const [formSuccess, setFormSuccess] = useState('');
  const [fileName, setFileName] = useState('');
  const [fileError, setFileError] = useState('');
  const [questions, setQuestions] = useState([]);
  const [questionsStatus, setQuestionsStatus] = useState('idle');
  const [questionsError, setQuestionsError] = useState('');
  const [selectedSlug, setSelectedSlug] = useState('');
  const [generatorPrompt, setGeneratorPrompt] = useState('');
  const [generatorStatus, setGeneratorStatus] = useState('idle');
  const [generatorError, setGeneratorError] = useState('');
  const navigate = useNavigate();
  const location = useLocation();

  const activePath = useMemo(() => {
    const currentPath = location.pathname || DEFAULT_PAGE_PATH;
    const matched = PAGE_DEFINITIONS.find((page) => page.path === currentPath);
    return matched ? matched.path : DEFAULT_PAGE_PATH;
  }, [location.pathname]);

  const normalizedUploadEndpoint = useMemo(
    () => uploadEndpoint.replace(/\/+$/, ''),
    [uploadEndpoint]
  );
  const generatorEndpoint = `${normalizedUploadEndpoint}/generate`;
  const questionsEndpoint = listEndpoint ?? normalizedUploadEndpoint;

  const normalizeOptions = useCallback(
    (options) => normalizeOptionEntries(options),
    []
  );

  const applyQuestionToForm = useCallback((question, mode = 'update') => {
    if (!question) {
      return;
    }

    const normalized = buildFormStateForQuestion(question, normalizeOptions);
    setForm(normalized);
    setFormMode(mode);
    setFormError('');
    setFormSuccess('');
    setSelectedSlug(mode === 'update' ? normalized.slug : '');
  }, [normalizeOptions]);

  const resetForm = useCallback(() => {
    setForm(createEmptyForm());
    setFormMode('create');
    setFormError('');
    setFormSuccess('');
    setFileName('');
    setFileError('');
    setSelectedSlug('');
  }, []);

  const fetchQuestions = useCallback(async () => {
    setQuestionsStatus('loading');
    setQuestionsError('');

    try {
      const url = new URL(questionsEndpoint, window.location.origin);
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
      return items;
    } catch (error) {
      setQuestionsStatus('error');
      setQuestionsError(
        error instanceof Error ? error.message : 'Unable to load questions'
      );
      setQuestions([]);
      throw error;
    }
  }, [questionsEndpoint]);

  useEffect(() => {
    fetchQuestions().catch(() => {
      /* handled in state */
    });
  }, [fetchQuestions]);

  const handleFieldChange = useCallback((field) => (event) => {
    const value = event.target.value;
    setForm((prev) => ({ ...prev, [field]: value }));
  }, []);

  const handleOptionChange = useCallback((index, field) => (event) => {
    const value = event.target.value;
    setForm((prev) => {
      const nextOptions = prev.options.map((option, optionIndex) => (
        optionIndex === index ? { ...option, [field]: value } : option
      ));
      return { ...prev, options: nextOptions };
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
      if (prev.options.length <= 3) {
        return prev;
      }
      const nextOptions = prev.options.filter((_, optionIndex) => optionIndex !== index);
      let nextCorrect = prev.correct_option_id;
      if (!nextOptions.find((option) => option.id === nextCorrect) && nextOptions.length > 0) {
        nextCorrect = nextOptions[0].id;
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
      assertCondition(
        /^\d{4}-\d{2}-\d{2}$/.test(publishedOn),
        'Published date must be in YYYY-MM-DD format.'
      );

      const expiresOn = trimValue(targetForm.expires_on);

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
        expires_on: expiresOn ? expiresOn : undefined
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

  const handleSubmit = useCallback(async () => {
    await submitFormWorkflow({
      form,
      buildPayload,
      formMode,
      normalizedUploadEndpoint,
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
    normalizedUploadEndpoint,
    resetForm,
    setFormError,
    setFormSuccess,
    setFormStatus
  ]);

  const handleFileChange = useCallback((event) => {
    const [file] = event.target.files ?? [];
    setFileName('');
    setFileError('');

    if (!file) {
      return;
    }

    setFileName(file.name);
    const reader = new FileReader();
    reader.onload = () => {
      try {
        const rawText = String(reader.result ?? '');
        const parsed = JSON.parse(rawText);
        if (Array.isArray(parsed)) {
          if (parsed.length !== 1) {
            throw new Error('When providing an array, include exactly one question');
          }
          applyQuestionToForm(parsed[0], 'create');
        } else {
          applyQuestionToForm(parsed, 'create');
        }
        setFormMode('create');
      } catch (parseError) {
        setFileError(
          parseError instanceof Error ? parseError.message : 'Invalid JSON payload'
        );
      }
    };
    reader.onerror = () => {
      setFileError('Unable to read the selected file');
    };
    reader.readAsText(file);
  }, [applyQuestionToForm]);

  const handleSelectQuestion = useCallback((question) => {
    applyQuestionToForm(question, 'update');
    navigate(DEFAULT_PAGE_PATH);
  }, [applyQuestionToForm, navigate]);

  const handleGeneratorPromptChange = useCallback((event) => {
    setGeneratorPrompt(event.target.value);
  }, []);

  const handleGenerate = useCallback(async () => {
    setGeneratorError('');
    setFormError('');
    setFormSuccess('');
    setGeneratorStatus('loading');

    try {
      const body = await requestGeneratedQuestion(
        generatorEndpoint,
        generatorPrompt.trim()
      );
      applyQuestionToForm(body.question, 'create');
      setFormMode('create');
      navigate(DEFAULT_PAGE_PATH);
      setFormSuccess(`Drafted question ${body.question.slug}`);
    } catch (error) {
      setGeneratorError(error instanceof Error ? error.message : 'Generation failed');
    } finally {
      setGeneratorStatus('idle');
    }
  }, [
    applyQuestionToForm,
    generatorEndpoint,
    generatorPrompt,
    navigate
  ]);

  const formDisabled = formStatus === 'submitting';
  const canSubmit = Boolean(form.slug.trim() && form.question.trim());

  return (
    <Stack spacing={3} className="quiz-manager">
      <Paper elevation={6} className="quiz-manager__nav">
        <Stack
          direction={{ xs: 'column', md: 'row' }}
          spacing={2}
          alignItems={{ xs: 'flex-start', md: 'center' }}
          justifyContent="space-between"
        >
          <Stack spacing={0.5}>
            <Typography variant="h5" component="h1">
              Quiz Manager
            </Typography>
            <Typography variant="body2" color="textSecondary">
              Choose a workflow to create, draft, or review quiz questions.
            </Typography>
          </Stack>
          <Stack
            direction={{ xs: 'column', sm: 'row' }}
            spacing={1}
            flexWrap="wrap"
          >
            {PAGE_DEFINITIONS.map((page) => (
              <Button
                key={page.id}
                component={RouterLink}
                to={page.path}
                variant={activePath === page.path ? 'contained' : 'outlined'}
                color="primary"
                aria-current={activePath === page.path ? 'page' : undefined}
              >
                {page.label}
              </Button>
            ))}
          </Stack>
        </Stack>
      </Paper>

      <Routes>
        <Route
          path="/"
          element={<Navigate to={DEFAULT_PAGE_PATH} replace />}
        />
        <Route
          path={DEFAULT_PAGE_PATH}
          element={
            <CreateQuestionPage
              canSubmit={canSubmit}
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
          }
        />
        <Route
          path="/generate"
          element={
            <GeneratorPage
              generatorError={generatorError}
              generatorPrompt={generatorPrompt}
              generatorStatus={generatorStatus}
              handleGenerate={handleGenerate}
              handleGeneratorPromptChange={handleGeneratorPromptChange}
            />
          }
        />
        <Route
          path="/questions"
          element={
            <ExistingQuestionsPage
              fetchQuestions={fetchQuestions}
              handleSelectQuestion={handleSelectQuestion}
              questions={questions}
              questionsError={questionsError}
              questionsStatus={questionsStatus}
              selectedSlug={selectedSlug}
            />
          }
        />
        <Route
          path="*"
          element={<Navigate to={DEFAULT_PAGE_PATH} replace />}
        />
      </Routes>
    </Stack>
  );
}
