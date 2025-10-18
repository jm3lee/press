import React, { useCallback, useEffect, useMemo, useState } from 'react';
import {
  Alert,
  Box,
  Button,
  CircularProgress,
  Divider,
  Paper,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Typography
} from '@mui/material';
import RefreshIcon from '@mui/icons-material/Refresh';

/**
 * QuizManager allows operators to ingest quiz questions into the backend.
 *
 * @param {{ uploadEndpoint?: string, listEndpoint?: string }} props
 * @returns {JSX.Element}
 */
export default function QuizManager({ uploadEndpoint = '/api/quiz/questions', listEndpoint }) {
  const [fileName, setFileName] = useState('');
  const [questionPayload, setQuestionPayload] = useState(null);
  const [preview, setPreview] = useState('');
  const [status, setStatus] = useState('idle');
  const [error, setError] = useState('');
  const [serverResponse, setServerResponse] = useState(null);
  const [questions, setQuestions] = useState([]);
  const [questionsStatus, setQuestionsStatus] = useState('idle');
  const [questionsError, setQuestionsError] = useState('');

  const questionsEndpoint = listEndpoint ?? uploadEndpoint;

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
    } catch (fetchError) {
      setQuestionsStatus('error');
      setQuestionsError(fetchError instanceof Error ? fetchError.message : 'Unable to load questions');
      setQuestions([]);
      throw fetchError;
    }
  }, [questionsEndpoint]);

  useEffect(() => {
    fetchQuestions().catch(() => {
      /* handled in state */
    });
  }, [fetchQuestions]);

  const resetUploadState = useCallback(() => {
    setFileName('');
    setQuestionPayload(null);
    setPreview('');
    setStatus('idle');
    setError('');
  }, []);

  const handleFileChange = useCallback((event) => {
    const [file] = event.target.files ?? [];
    setServerResponse(null);

    if (!file) {
      resetUploadState();
      return;
    }

    setStatus('parsing');
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
          setQuestionPayload(parsed[0]);
          setPreview(JSON.stringify(parsed[0], null, 2));
        } else {
          setQuestionPayload(parsed);
          setPreview(JSON.stringify(parsed, null, 2));
        }
        setStatus('ready');
        setError('');
      } catch (parseError) {
        setQuestionPayload(null);
        setPreview('');
        setStatus('error');
        setError(`Invalid JSON: ${parseError instanceof Error ? parseError.message : parseError}`);
      }
    };
    reader.onerror = () => {
      setStatus('error');
      setError('Unable to read the selected file');
      setQuestionPayload(null);
      setPreview('');
    };
    reader.readAsText(file);
  }, [resetUploadState]);

  const handleSubmit = useCallback(async () => {
    if (!questionPayload) {
      return;
    }
    setStatus('submitting');
    setError('');
    setServerResponse(null);

    try {
      const response = await fetch(uploadEndpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(questionPayload)
      });

      const body = await response.json().catch(() => ({}));
      if (!response.ok) {
        const message = body?.error ?? 'Upload failed';
        throw new Error(message);
      }

      setServerResponse(body?.question ?? body);
      setStatus('success');
      resetUploadState();
      fetchQuestions().catch(() => {
        /* handled in state */
      });
    } catch (submitError) {
      setStatus('error');
      setError(submitError instanceof Error ? submitError.message : 'Upload failed');
    }
  }, [fetchQuestions, questionPayload, resetUploadState, uploadEndpoint]);

  const canSubmit = useMemo(
    () => status === 'ready' && questionPayload,
    [status, questionPayload]
  );

  return (
    <Paper
      className="quiz-manager"
      elevation={6}
    >
      <Stack spacing={3}>
        <Box>
          <Typography variant="h4" component="h1" gutterBottom>
            Quiz Manager
          </Typography>
          <Typography variant="body1" color="textSecondary">
            Upload a JSON blob describing a quiz question. The manager submits
            it to the quiz backend and creates a new catalog entry.
          </Typography>
        </Box>

        <Divider light />

        <Box>
          <Button
            component="label"
            variant="contained"
            disableElevation
          >
            Select JSON File
            <input
              hidden
              type="file"
              accept="application/json"
              onChange={handleFileChange}
              data-testid="quiz-manager-file-input"
            />
          </Button>
          {fileName ? (
            <Typography
              variant="body2"
              color="textSecondary"
              sx={{ marginTop: 1 }}
            >
              Selected file: {fileName}
            </Typography>
          ) : null}
        </Box>

        {preview ? (
          <Box className="quiz-manager__preview" component="pre">
            {preview}
          </Box>
        ) : null}

        {error ? (
          <Alert severity="error">
            {error}
          </Alert>
        ) : null}

        {serverResponse ? (
          <Alert severity="success">
            Created question with slug "{serverResponse.slug}".
          </Alert>
        ) : null}

        <Box>
          <Stack direction="row" spacing={2}>
            <Button
              variant="contained"
              color="primary"
              disabled={!canSubmit}
              onClick={handleSubmit}
            >
              Submit Question
            </Button>
            <Button
              variant="outlined"
              color="secondary"
              onClick={resetUploadState}
            >
              Clear Selection
            </Button>
          </Stack>
          <Typography
            variant="caption"
            color="textSecondary"
            sx={{ display: 'block', marginTop: 1 }}
          >
            Accepted payload keys: slug, question, helper_text, explanation,
            success_message, error_message, options, correct_option_id,
            published_on, expires_on.
          </Typography>
        </Box>

        <Divider light />

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
            <Alert severity="error">
              {questionsError}
            </Alert>
          ) : null}

          {questionsStatus === 'loading' ? (
            <Box className="quiz-manager__loader">
              <CircularProgress size={28} />
            </Box>
          ) : null}

          {questionsStatus === 'success' && questions.length === 0 ? (
            <Typography variant="body2" color="textSecondary">
              No questions found. Upload a JSON payload to seed the catalog.
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
                    <TableRow key={item.id} hover>
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
      </Stack>
    </Paper>
  );
}
