/*
 * Copyright (c) Flashoffer Developers
 * Released under the MIT license.
 */

import {
  Alert,
  Box,
  Button,
  CircularProgress,
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
 * Renders a tabular overview of existing quiz questions.
 * @param {object} props - Component props.
 * @param {() => Promise<unknown>} props.fetchQuestions - Reload callback.
 * @param {(question: object) => void} props.handleSelectQuestion - Select handler.
 * @param {Array<object>} props.questions - Loaded quiz questions.
 * @param {string} props.questionsError - Error message for failed fetches.
 * @param {'idle' | 'loading' | 'error' | 'success'} props.questionsStatus - Fetch
 * status.
 * @param {string} props.selectedSlug - Currently highlighted question slug.
 * @returns {JSX.Element} Existing questions layout.
 */
export default function ExistingQuestionsPage({
  fetchQuestions,
  handleSelectQuestion,
  questions,
  questionsError,
  questionsStatus,
  selectedSlug
}) {
  return (
    <Paper
      elevation={6}
      className="quiz-manager__panel quiz-manager__table-wrapper"
    >
      <Stack spacing={2}>
        <Stack
          direction="row"
          alignItems="center"
          justifyContent="space-between"
        >
          <Typography variant="h5" component="h2">
            Existing Questions
          </Typography>
          <Button
            variant="outlined"
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
  );
}
