import {
  Alert,
  Button,
  Paper,
  Stack,
  TextField,
  Typography
} from '@mui/material';

export default function GeneratorPage({
  generatorError,
  generatorPrompt,
  generatorStatus,
  handleGenerate,
  handleGeneratorPromptChange
}) {
  return (
      <Stack spacing={2}>
        <Typography variant="h5" component="h2">
          GPT-5 Drafts
        </Typography>
        <Typography variant="body2">
          Provide a short prompt and the manager will request a draft question
          from the backend generator endpoint.
        </Typography>
        <Stack spacing={2}>
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
              onClick={handleGenerate}
              disabled={generatorStatus === 'loading'}
            >
              {generatorStatus === 'loading' ? 'Generating…' : 'Generate with GPT-5'}
            </Button>
          </Stack>
        </Stack>
      </Stack>
  );
}
