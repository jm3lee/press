/*
 * Copyright (c) Flashoffer Developers
 * Released under the MIT license.
 */

import {
  Alert,
  Box,
  Button,
  FormControl,
  FormHelperText,
  IconButton,
  InputLabel,
  MenuItem,
  Paper,
  Select,
  Stack,
  TextField,
  Typography,
} from '@mui/material';
import AddCircleIcon from '@mui/icons-material/AddCircle';
import DeleteIcon from '@mui/icons-material/Delete';
import { FlashofferThemeProvider, MultipleChoiceQuiz } from 'flashoffer-react';

/**
 * Renders the interactive form used to build and preview quiz questions.
 * @param {object} props - Component props.
 * @param {boolean} props.canSubmit - Indicates whether the form meets submission requirements.
 * @param {Record<string, string>} props.celebrationLabels - Human readable celebration labels.
 * @param {string[]} props.celebrationOptions - Available celebration presets.
 * @param {string} props.fileError - Error message from file imports.
 * @param {string} props.fileName - Name of the imported file.
 * @param {object} props.form - Mutable form state.
 * @param {boolean} props.formDisabled - Disables controls when true.
 * @param {string} props.formError - Inline form error message.
 * @param {'create' | 'update'} props.formMode - Current form mode.
 * @param {string} props.formSuccess - Success status message.
 * @param {() => void} props.handleAddOption - Handler to append a new answer option.
 * @param {(event: import('react').ChangeEvent<HTMLInputElement>) => void} props.handleCorrectOptionChange - Handler for selecting the correct option.
 * @param {(field: string) => (event: import('react').ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => void} props.handleFieldChange - Field change handler factory.
 * @param {(event: import('react').ChangeEvent<HTMLInputElement>) => void} props.handleFileChange - File upload handler.
 * @param {(index: number, field: string) => (event: import('react').ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => void} props.handleOptionChange - Option change handler factory.
 * @param {(index: number) => void} props.handleRemoveOption - Removes an option at the given index.
 * @param {() => void} props.handleSubmit - Submission handler.
 * @param {string} props.preview - JSON payload preview string.
 * @param {object} [props.previewQuestion] - Preview question payload for live demo.
 * @param {() => void} props.resetForm - Resets the form to its initial state.
 * @returns {JSX.Element} Create question layout.
 */
export default function CreateQuestionPage({
  canSubmit,
  celebrationLabels,
  celebrationOptions,
  fileError,
  fileName,
  form,
  formDisabled,
  formError,
  formMode,
  formSuccess,
  handleAddOption,
  handleCorrectOptionChange,
  handleFieldChange,
  handleFileChange,
  handleOptionChange,
  handleRemoveOption,
  handleSubmit,
  preview,
  previewQuestion,
  resetForm,
}) {
  return (
    <Paper elevation={6} className="quiz-manager__panel">
      <Stack spacing={3}>
        <Stack
          direction="row"
          justifyContent="space-between"
          alignItems="center"
        >
          <Typography variant="h4" component="h2">
            Create Question
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
          Build a quiz question from scratch or import a JSON payload that
          matches the backend schema.
        </Typography>

        {fileName ? (
          <Typography variant="body2" color="textSecondary">
            Imported file: {fileName}
          </Typography>
        ) : null}

        {fileError ? <Alert severity="error">{fileError}</Alert> : null}

        {formError ? <Alert severity="error">{formError}</Alert> : null}

        {formSuccess ? <Alert severity="success">{formSuccess}</Alert> : null}

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
          </Stack>

          <Stack direction="row" spacing={2}>
            <TextField
              label="Expires On"
              value={form.expires_on}
              onChange={handleFieldChange('expires_on')}
              type="date"
              fullWidth
              InputLabelProps={{ shrink: true }}
            />
            <TextField
              label="Helper Text"
              value={form.helper_text}
              onChange={handleFieldChange('helper_text')}
              fullWidth
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
              label="Explanation"
              value={form.explanation}
              onChange={handleFieldChange('explanation')}
              fullWidth
            />
            <TextField
              label="Success Message"
              value={form.success_message}
              onChange={handleFieldChange('success_message')}
              fullWidth
            />
          </Stack>

          <TextField
            label="Error Message"
            value={form.error_message}
            onChange={handleFieldChange('error_message')}
            fullWidth
          />

          <FormControl fullWidth disabled={formDisabled}>
            <InputLabel id="celebration-effect-label">
              Celebration Effect
            </InputLabel>
            <Select
              labelId="celebration-effect-label"
              label="Celebration Effect"
              value={form.celebration}
              onChange={handleFieldChange('celebration')}
            >
              {celebrationOptions.map((value) => (
                <MenuItem key={value} value={value}>
                  {celebrationLabels[value]}
                </MenuItem>
              ))}
            </Select>
            <FormHelperText>
              Choose the confetti animation shown after correct answers.
            </FormHelperText>
          </FormControl>

          <Stack spacing={1}>
            <Stack
              direction="row"
              alignItems="center"
              justifyContent="space-between"
            >
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
              <Paper
                key={`${option.id || option.label || 'option'}-${index}`}
                variant="outlined"
                className="quiz-manager__option"
              >
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

          {previewQuestion ? (
            <Stack spacing={1}>
              <Typography variant="h6" component="h2">
                Live Preview
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Changes appear instantly. Submit an answer to reveal option
                descriptions.
              </Typography>
              <Box className="quiz-manager__quiz-preview">
                <FlashofferThemeProvider>
                  <MultipleChoiceQuiz
                    question={previewQuestion.question}
                    helperText={previewQuestion.helperText}
                    options={previewQuestion.options}
                    correctOptionId={previewQuestion.correctOptionId}
                    explanation={previewQuestion.explanation}
                    successMessage={previewQuestion.successMessage}
                    errorMessage={previewQuestion.errorMessage}
                    confetti={
                      previewQuestion.celebration === 'off'
                        ? undefined
                        : {
                            enabled: true,
                            preset: previewQuestion.celebration,
                          }
                    }
                  />
                </FlashofferThemeProvider>
              </Box>
            </Stack>
          ) : null}

          {preview ? (
            <Stack spacing={1}>
              <Typography variant="h6" component="h2">
                Request Payload
              </Typography>
              <Box className="quiz-manager__preview" component="pre">
                {preview}
              </Box>
            </Stack>
          ) : null}
        </Stack>
      </Stack>
    </Paper>
  );
}
