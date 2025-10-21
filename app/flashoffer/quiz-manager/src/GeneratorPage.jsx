/*
 * Copyright (c) Flashoffer Developers
 * Released under the MIT license.
 */

import {
  Alert,
  Button,
  Paper,
  Stack,
  TextField,
  Typography
} from '@mui/material';

/**
 * Presents the generator workflow used to request GPT-assisted quiz drafts.
 * @param {object} props - Component props.
 * @param {string} props.generatorError - Current generator error message.
 * @param {string} props.generatorPrompt - Prompt text supplied by the operator.
 * @param {'idle' | 'loading'} props.generatorStatus - Generator request status.
 * @param {() => void} props.handleGenerate - Callback triggered to draft a question.
 * @param {(event: import('react').ChangeEvent<HTMLInputElement>) => void} props.handleGeneratorPromptChange - Prompt change handler.
 * @returns {JSX.Element} Generator layout.
 */
export default function GeneratorPage({
  generatorError = '',
  generatorPrompt = '',
  generatorStatus = 'idle',
  handleGenerate,
  handleGeneratorPromptChange
}) {
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
