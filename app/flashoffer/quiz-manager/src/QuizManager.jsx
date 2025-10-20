/*
 * Copyright (c) Flashoffer Developers
 * Released under the MIT license.
 */

import React, {
  useCallback,
  useDeferredValue,
  useEffect,
  useMemo,
  useState
} from 'react';
import {
  Paper,
  Stack,
  Tab,
  Tabs
} from '@mui/material';
import CreateQuestionPage from './pages/CreateQuestionPage.jsx';
import ExistingQuestionsPage from './pages/ExistingQuestionsPage.jsx';
import GeneratorPage from './pages/GeneratorPage.jsx';

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
  const [activePage, setActivePage] = useState('create');

  const normalizedUploadEndpoint = useMemo(
    () => uploadEndpoint.replace(/\/+$/, ''),
    [uploadEndpoint]
  );
  const generatorEndpoint = `${normalizedUploadEndpoint}/generate`;
  const questionsEndpoint = listEndpoint ?? normalizedUploadEndpoint;

  const normalizeOptions = useCallback((options) => {
    if (!Array.isArray(options) || options.length === 0) {
      return [emptyOption(), emptyOption(), emptyOption()];
    }
    return options.map((option) => ({
      id: String(option.id ?? '').trim(),
      label: String(option.label ?? '').trim(),
      description: option.description ? String(option.description).trim() : ''
    }));
  }, []);

  const applyQuestionToForm = useCallback((question, mode = 'update') => {
    if (!question) {
      return;
    }
    const normalized = {
      slug: String(question.slug ?? '').trim(),
      question: String(question.question ?? ''),
      helper_text: question.helper_text ? String(question.helper_text) : '',
      explanation: question.explanation ? String(question.explanation) : '',
      success_message: question.success_message
        ? String(question.success_message)
        : '',
      error_message: question.error_message
        ? String(question.error_message)
        : '',
      published_on: String(question.published_on ?? todayIso()).slice(0, 10),
      expires_on: question.expires_on ? String(question.expires_on).slice(0, 10) : '',
      correct_option_id: String(question.correct_option_id ?? ''),
      options: normalizeOptions(question.options)
    };

    if (!normalized.correct_option_id && normalized.options.length > 0) {
      normalized.correct_option_id = normalized.options[0].id;
    }

    setForm(normalized);
    setFormMode(mode);
    setFormError('');
    setFormSuccess('');
    if (mode === 'update') {
      setSelectedSlug(normalized.slug);
    } else {
      setSelectedSlug('');
    }
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
    const trimmedSlug = targetForm.slug.trim();
    if (!trimmedSlug) {
      if (!silent) {
        setFormError('Slug is required.');
      }
      return null;
    }

    const trimmedQuestion = targetForm.question.trim();
    if (!trimmedQuestion) {
      if (!silent) {
        setFormError('Question prompt is required.');
      }
      return null;
    }

    const preparedOptions = targetForm.options
      .map((option) => ({
        id: option.id.trim(),
        label: option.label.trim(),
        description: option.description.trim()
      }))
      .filter((option) => option.id || option.label);

    const normalizedOptions = preparedOptions.map((option) => {
      const nextOption = {
        id: option.id,
        label: option.label || option.id,
      };
      const desc = option.description.trim();
      if (desc) {
        nextOption.description = desc;
      }
      return nextOption;
    });

    if (normalizedOptions.length < 3) {
      if (!silent) {
        setFormError('Provide at least three answer options.');
      }
      return null;
    }

    const optionIds = normalizedOptions.map((option) => option.id);
    if (optionIds.some((value) => !value)) {
      if (!silent) {
        setFormError('Each option must include a non-empty id.');
      }
      return null;
    }

    const uniqueIds = new Set(optionIds);
    if (uniqueIds.size !== optionIds.length) {
      if (!silent) {
        setFormError('Each option id must be unique.');
      }
      return null;
    }

    let correctOptionId = targetForm.correct_option_id.trim();
    if (!correctOptionId) {
      correctOptionId = normalizedOptions[0].id;
    }

    if (!uniqueIds.has(correctOptionId)) {
      if (!silent) {
        setFormError('Correct option must reference one of the option ids.');
      }
      return null;
    }

    const publishedOn = targetForm.published_on.trim();
    if (!/^\d{4}-\d{2}-\d{2}$/.test(publishedOn)) {
      if (!silent) {
        setFormError('Published date must be in YYYY-MM-DD format.');
      }
      return null;
    }

    const expiresOn = targetForm.expires_on.trim();

    return {
      slug: trimmedSlug,
      question: trimmedQuestion,
      helper_text: targetForm.helper_text.trim() || undefined,
      explanation: targetForm.explanation.trim() || undefined,
      success_message: targetForm.success_message.trim() || undefined,
      error_message: targetForm.error_message.trim() || undefined,
      options: normalizedOptions,
      correct_option_id: correctOptionId,
      published_on: publishedOn,
      expires_on: expiresOn ? expiresOn : undefined
    };
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

  const previewQuestion = useMemo(() => {
    if (!previewPayload) {
      return undefined;
    }
    return {
      question: previewPayload.question,
      helperText: previewPayload.helper_text ?? undefined,
      options: previewPayload.options.map((option) => ({
        id: option.id,
        label: option.label,
        description: option.description ?? undefined
      })),
      correctOptionId: previewPayload.correct_option_id,
      explanation: previewPayload.explanation ?? undefined,
      successMessage: previewPayload.success_message ?? undefined,
      errorMessage: previewPayload.error_message ?? undefined
    };
  }, [previewPayload]);

  const handleSubmit = useCallback(async () => {
    setFormError('');
    setFormSuccess('');

    const payload = buildPayload(form);
    if (!payload) {
      return;
    }

    const targetUrl =
      formMode === 'update'
        ? `${normalizedUploadEndpoint}/${encodeURIComponent(payload.slug)}`
        : normalizedUploadEndpoint;
    const method = formMode === 'update' ? 'PUT' : 'POST';

    setFormStatus('submitting');

    try {
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

      applyQuestionToForm(body.question, formMode === 'update' ? 'update' : 'create');
      if (formMode === 'create') {
        resetForm();
      }
      setFormSuccess(
        formMode === 'update'
          ? `Updated question ${payload.slug}`
          : `Created question ${payload.slug}`
      );
      await fetchQuestions().catch(() => {
        /* handled */
      });
    } catch (error) {
      setFormError(error instanceof Error ? error.message : 'Request failed');
    } finally {
      setFormStatus('idle');
    }
  }, [
    applyQuestionToForm,
    buildPayload,
    fetchQuestions,
    form,
    formMode,
    normalizedUploadEndpoint,
    resetForm
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
    setActivePage('create');
  }, [applyQuestionToForm, setActivePage]);

  const handleGeneratorPromptChange = useCallback((event) => {
    setGeneratorPrompt(event.target.value);
  }, []);

  const handleGenerate = useCallback(async () => {
    setGeneratorError('');
    setFormError('');
    setFormSuccess('');
    setGeneratorStatus('loading');

    try {
      const response = await fetch(generatorEndpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          prompt: generatorPrompt.trim() || undefined
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

      applyQuestionToForm(body.question, 'create');
      setFormMode('create');
      setActivePage('create');
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
    setActivePage
  ]);

  const formDisabled = formStatus === 'submitting';
  const canSubmit = Boolean(form.slug.trim() && form.question.trim());
  const handlePageChange = useCallback((event, value) => {
    setActivePage(value);
  }, [setActivePage]);

  return (
    <Stack spacing={3} className="quiz-manager">
      <Paper elevation={6} className="quiz-manager__nav">
        <Tabs
          value={activePage}
          onChange={handlePageChange}
          variant="fullWidth"
          textColor="inherit"
          indicatorColor="primary"
        >
          <Tab label="Create Question" value="create" />
          <Tab label="GPT Drafts" value="generate" />
          <Tab label="Existing Questions" value="questions" />
        </Tabs>
      </Paper>

      {activePage === 'create' ? (
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
      ) : null}

      {activePage === 'generate' ? (
        <GeneratorPage
          generatorError={generatorError}
          generatorPrompt={generatorPrompt}
          generatorStatus={generatorStatus}
          handleGenerate={handleGenerate}
          handleGeneratorPromptChange={handleGeneratorPromptChange}
        />
      ) : null}

      {activePage === 'questions' ? (
        <ExistingQuestionsPage
          fetchQuestions={fetchQuestions}
          handleSelectQuestion={handleSelectQuestion}
          questions={questions}
          questionsError={questionsError}
          questionsStatus={questionsStatus}
          selectedSlug={selectedSlug}
        />
      ) : null}
    </Stack>
  );
}
