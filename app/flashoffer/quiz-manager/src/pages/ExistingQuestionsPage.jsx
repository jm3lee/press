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

export default function ExistingQuestionsPage({
  fetchQuestions,
  handleSelectQuestion,
  questions,
  questionsError,
  questionsStatus,
  selectedSlug
}) {
  return (
    <Paper elevation={0} className="quiz-manager__table-wrapper">
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
            No questions found. Upload a JSON payload or use the form to seed
            the catalog.
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
