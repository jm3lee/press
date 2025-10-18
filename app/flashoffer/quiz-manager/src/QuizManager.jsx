import React, {
  useCallback,
  useEffect,
  useMemo,
  useState
} from 'react';
import {
  Alert,
  Box,
  Button,
  CircularProgress,
  Divider,
  FormControl,
  IconButton,
  InputLabel,
  MenuItem,
  Paper,
  Select,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TextField,
  Typography
} from '@mui/material';
import AddCircleIcon from '@mui/icons-material/AddCircle';
import DeleteIcon from '@mui/icons-material/Delete';
import RefreshIcon from '@mui/icons-material/Refresh';

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

  const buildPayload = useCallback((options = { silent: false }) => {
    const { silent } = options;
    const trimmedSlug = form.slug.trim();
    if (!trimmedSlug) {
      if (!silent) {
        setFormError('Slug is required.');
      }
      return null;
    }

    const trimmedQuestion = form.question.trim();
    if (!trimmedQuestion) {
      if (!silent) {
        setFormError('Question prompt is required.');
      }
      return null;
    }

    const preparedOptions = form.options
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

    let correctOptionId = form.correct_option_id.trim();
    if (!correctOptionId) {
      correctOptionId = normalizedOptions[0].id;
    }

    if (!uniqueIds.has(correctOptionId)) {
      if (!silent) {
        setFormError('Correct option must reference one of the option ids.');
      }
      return null;
    }

    const publishedOn = form.published_on.trim();
    if (!/^\d{4}-\d{2}-\d{2}$/.test(publishedOn)) {
      if (!silent) {
        setFormError('Published date must be in YYYY-MM-DD format.');
      }
      return null;
    }

    const expiresOn = form.expires_on.trim();

    return {
      slug: trimmedSlug,
      question: trimmedQuestion,
      helper_text: form.helper_text.trim() || undefined,
      explanation: form.explanation.trim() || undefined,
      success_message: form.success_message.trim() || undefined,
      error_message: form.error_message.trim() || undefined,
      options: normalizedOptions,
      correct_option_id: correctOptionId,
      published_on: publishedOn,
      expires_on: expiresOn ? expiresOn : undefined
    };
  }, [form]);

  const preview = useMemo(() => {
    const payload = buildPayload({ silent: true });
    if (!payload) {
      return '';
    }
    return JSON.stringify(payload, null, 2);
  }, [buildPayload]);

  const handleSubmit = useCallback(async () => {
    setFormError('');
    setFormSuccess('');

    const payload = buildPayload();
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
  }, [applyQuestionToForm]);

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
      setFormSuccess(`Drafted question ${body.question.slug}`);
    } catch (error) {
      setGeneratorError(error instanceof Error ? error.message : 'Generation failed');
    } finally {
      setGeneratorStatus('idle');
    }
  }, [
    applyQuestionToForm,
    generatorEndpoint,
    generatorPrompt
  ]);

  const formDisabled = formStatus === 'submitting';
  const canSubmit = Boolean(form.slug.trim() && form.question.trim());

  return (
    <Stack spacing={3} className="quiz-manager">
      <Paper elevation={6} className="quiz-manager__panel">
        <Stack spacing={3}>
          <Stack direction="row" justifyContent="space-between" alignItems="center">
            <Typography variant="h4" component="h1">
              Quiz Manager
            </Typography>
            <Stack direction="row" spacing={1}>
              <Button
                variant="outlined"
                color="secondary"
                onClick={resetForm}
                disabled={formDisabled}
              >
                New Question
              </Button>
              <Button
                component="label"
                variant="contained"
                disableElevation
                disabled={formDisabled}
              >
                Import JSON
                <input
                  hidden
                  type="file"
                  accept="application/json"
                  onChange={handleFileChange}
                  data-testid="quiz-manager-file-input"
                />
              </Button>
            </Stack>
          </Stack>

          <Typography variant="body1" color="textSecondary">
            Fill in the form to craft a quiz question, import an existing JSON payload,
            or draft one with GPT-5 when an OpenAI API key is available.
          </Typography>

          {fileName ? (
            <Typography variant="body2" color="textSecondary">
              Imported file: {fileName}
            </Typography>
          ) : null}

          {fileError ? (
            <Alert severity="error">{fileError}</Alert>
          ) : null}

          {formError ? (
            <Alert severity="error">{formError}</Alert>
          ) : null}

          {formSuccess ? (
            <Alert severity="success">{formSuccess}</Alert>
          ) : null}

          <Divider light />

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
            {generatorError ? (
              <Alert severity="error">{generatorError}</Alert>
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

          <Stack spacing={2} className="quiz-manager__form">
            <Stack direction="row" spacing={2}>
              <TextField
                label="Slug"
                value={form.slug}
                onChange={handleFieldChange('slug')}
                fullWidth
                disabled={formMode === 'update'}
              />
              <TextField
                label="Published On"
                value={form.published_on}
                onChange={handleFieldChange('published_on')}
                type="date"
                fullWidth
                InputLabelProps={{ shrink: true }}
              />
              <TextField
                label="Expires On"
                value={form.expires_on}
                onChange={handleFieldChange('expires_on')}
                type="date"
                fullWidth
                InputLabelProps={{ shrink: true }}
              />
            </Stack>

            <TextField
              label="Question"
              value={form.question}
              onChange={handleFieldChange('question')}
              multiline
              minRows={3}
              fullWidth
            />

            <Stack direction="row" spacing={2}>
              <TextField
                label="Helper Text"
                value={form.helper_text}
                onChange={handleFieldChange('helper_text')}
                fullWidth
              />
              <TextField
                label="Explanation"
                value={form.explanation}
                onChange={handleFieldChange('explanation')}
                fullWidth
              />
            </Stack>

            <Stack direction="row" spacing={2}>
              <TextField
                label="Success Message"
                value={form.success_message}
                onChange={handleFieldChange('success_message')}
                fullWidth
              />
              <TextField
                label="Error Message"
                value={form.error_message}
                onChange={handleFieldChange('error_message')}
                fullWidth
              />
            </Stack>

            <Divider light />

            <Stack spacing={1}>
              <Stack direction="row" alignItems="center" justifyContent="space-between">
                <Typography variant="h6">Answer Options</Typography>
                <Button
                  variant="text"
                  startIcon={<AddCircleIcon />}
                  onClick={handleAddOption}
                  disabled={formDisabled}
                >
                  Add Option
                </Button>
              </Stack>

              {form.options.map((option, index) => (
                <Paper key={index} variant="outlined" className="quiz-manager__option">
                  <Stack spacing={1}>
                    <Stack direction="row" spacing={2} alignItems="center">
                      <TextField
                        label="Option ID"
                        value={option.id}
                        onChange={handleOptionChange(index, 'id')}
                        fullWidth
                      />
                      <IconButton
                        aria-label="Remove option"
                        onClick={() => handleRemoveOption(index)}
                        disabled={form.options.length <= 3 || formDisabled}
                        size="small"
                      >
                        <DeleteIcon fontSize="small" />
                      </IconButton>
                    </Stack>
                    <TextField
                      label="Label"
                      value={option.label}
                      onChange={handleOptionChange(index, 'label')}
                      fullWidth
                    />
                    <TextField
                      label="Description"
                      value={option.description}
                      onChange={handleOptionChange(index, 'description')}
                      fullWidth
                    />
                  </Stack>
                </Paper>
              ))}

              <FormControl fullWidth>
                <InputLabel id="correct-option-label">Correct Option</InputLabel>
                <Select
                  labelId="correct-option-label"
                  label="Correct Option"
                  value={form.correct_option_id}
                  onChange={handleCorrectOptionChange}
                >
                  {form.options.map((option, index) => (
                    <MenuItem
                      key={`${option.id || option.label || 'option'}-${index}`}
                      value={option.id}
                    >
                      {option.id || option.label || '(unnamed option)'}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Stack>

            <Stack direction="row" spacing={2} justifyContent="flex-end">
              <Button
                variant="contained"
                color="primary"
                onClick={handleSubmit}
                disabled={formDisabled || !canSubmit}
              >
                {formMode === 'update' ? 'Update Question' : 'Create Question'}
              </Button>
            </Stack>

            {preview ? (
              <Box className="quiz-manager__preview" component="pre">
                {preview}
              </Box>
            ) : null}
          </Stack>
        </Stack>
      </Paper>

      <Paper elevation={0} className="quiz-manager__table-wrapper">
        <Stack spacing={2}>
          <Stack direction="row" alignItems="center" justifyContent="space-between">
            <Typography variant="h5" component="h2">
              Existing Questions
            </Typography>
            <Button
              variant="text"
              color="inherit"
              startIcon={<RefreshIcon />}
              onClick={() => fetchQuestions().catch(() => {})}
              disabled={questionsStatus === 'loading'}
            >
              Refresh
            </Button>
          </Stack>

          {questionsStatus === 'error' ? (
            <Alert severity="error">{questionsError}</Alert>
          ) : null}

          {questionsStatus === 'loading' ? (
            <Box className="quiz-manager__loader">
              <CircularProgress size={28} />
            </Box>
          ) : null}

          {questionsStatus === 'success' && questions.length === 0 ? (
            <Typography variant="body2" color="textSecondary">
              No questions found. Upload a JSON payload or use the form to seed the
              catalog.
            </Typography>
          ) : null}

          {questions.length > 0 ? (
            <TableContainer className="quiz-manager__table">
              <Table size="small" stickyHeader>
                <TableHead>
                  <TableRow>
                    <TableCell>Slug</TableCell>
                    <TableCell>Prompt</TableCell>
                    <TableCell>Published</TableCell>
                    <TableCell>Expires</TableCell>
                    <TableCell>Correct Option</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {questions.map((item) => (
                    <TableRow
                      key={item.id}
                      hover
                      selected={selectedSlug === item.slug}
                      onClick={() => handleSelectQuestion(item)}
                      sx={{ cursor: 'pointer' }}
                    >
                      <TableCell width={160} sx={{ fontWeight: 600 }}>
                        {item.slug}
                      </TableCell>
                      <TableCell sx={{ maxWidth: 360 }}>
                        <Typography
                          variant="body2"
                          color="textPrimary"
                          noWrap
                          title={item.question}
                        >
                          {item.question}
                        </Typography>
                      </TableCell>
                      <TableCell width={120}>{item.published_on}</TableCell>
                      <TableCell width={120}>{item.expires_on ?? '—'}</TableCell>
                      <TableCell width={160}>{item.correct_option_id}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          ) : null}
        </Stack>
      </Paper>
    </Stack>
  );
}
