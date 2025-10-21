/*
 * Copyright (c) Flashoffer Developers
 * Released under the MIT license.
 */

import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import {
  AppBar,
  Box,
  Button,
  Container,
  CssBaseline,
  Stack,
  Toolbar,
  Typography
} from '@mui/material';
import CreateQuestionContainer from './CreateQuestionContainer.jsx';
import ExistingQuestionsContainer from './ExistingQuestionsContainer.jsx';
import GeneratorPage from './GeneratorPage.jsx';

const NAVIGATION_ITEMS = [
  { id: 'create', label: 'Create Question' },
  { id: 'questions', label: 'Existing Questions' },
  { id: 'generate', label: 'GPT-5 Drafts' }
];

const QUESTIONS_ENDPOINT = '/api/quiz/questions';
const GENERATOR_ENDPOINT = `${QUESTIONS_ENDPOINT.replace(/\/$/, '')}/generate`;
const GENERATOR_PROMPT_STORAGE_KEY = 'flashoffer.quiz_manager.generator_prompt';

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
 * Renders the quiz manager shell with navigation and page state.
 * @returns {JSX.Element} Quiz manager root component.
 */
export default function App() {
  const [activePage, setActivePage] = useState('create');
  const [generatorPrompt, setGeneratorPrompt] = useState(() => {
    if (typeof window === 'undefined') {
      return '';
    }
    try {
      return window.localStorage.getItem(GENERATOR_PROMPT_STORAGE_KEY) ?? '';
    } catch {
      return '';
    }
  });
  const [generatorStatus, setGeneratorStatus] = useState('idle');
  const [generatorError, setGeneratorError] = useState('');
  const [pendingGeneratedQuestion, setPendingGeneratedQuestion] = useState(null);
  const [pendingGeneratedMessage, setPendingGeneratedMessage] = useState('');
  const createContainerRef = useRef(null);

  const navigationItems = useMemo(() => NAVIGATION_ITEMS, []);

  const handleSelectPage = useCallback((pageId) => {
    setActivePage(pageId);
  }, []);

  const handleGeneratorPromptChange = useCallback((event) => {
    setGeneratorPrompt(event.target.value);
  }, []);

  useEffect(() => {
    if (typeof window === 'undefined') {
      return;
    }
    try {
      if (generatorPrompt) {
        window.localStorage.setItem(GENERATOR_PROMPT_STORAGE_KEY, generatorPrompt);
      } else {
        window.localStorage.removeItem(GENERATOR_PROMPT_STORAGE_KEY);
      }
    } catch {
      /* ignore storage errors */
    }
  }, [generatorPrompt]);

  const handleGenerate = useCallback(async () => {
    setGeneratorError('');
    setGeneratorStatus('loading');
    const trimmedPrompt = generatorPrompt.trim();

    try {
      const body = await requestGeneratedQuestion(
        GENERATOR_ENDPOINT,
        trimmedPrompt
      );
      const slug = body.question?.slug;
      setPendingGeneratedQuestion(body.question);
      setPendingGeneratedMessage(
        slug ? `Drafted question ${slug}` : 'Drafted question ready'
      );
      setActivePage('create');
    } catch (error) {
      setGeneratorError(
        error instanceof Error ? error.message : 'Generation failed'
      );
    } finally {
      setGeneratorStatus('idle');
    }
  }, [generatorPrompt]);

  useEffect(() => {
    if (!pendingGeneratedQuestion || !createContainerRef.current) {
      return;
    }
    createContainerRef.current.applyQuestionToForm(
      pendingGeneratedQuestion,
      'create',
      pendingGeneratedMessage
    );
    setPendingGeneratedQuestion(null);
    setPendingGeneratedMessage('');
  }, [pendingGeneratedMessage, pendingGeneratedQuestion, createContainerRef]);

  return (
    <>
      <CssBaseline />
      <Box className="quiz-manager__layout">
        <AppBar position="static" color="transparent" elevation={0}>
          <Toolbar className="quiz-manager__toolbar">
            <Box className="quiz-manager__title-group">
              <Typography variant="h5" component="h1">
                Quiz Manager
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Create, preview, and manage questions for Flashoffer campaigns.
              </Typography>
            </Box>
            <Box sx={{ flexGrow: 1 }} />
            <Stack direction="column" spacing={1} className="quiz-manager__nav-buttons">
              {navigationItems.map((item) => (
                <Button
                  key={item.id}
                  variant={activePage === item.id ? 'contained' : 'outlined'}
                  onClick={() => handleSelectPage(item.id)}
                >
                  {item.label}
                </Button>
              ))}
            </Stack>
          </Toolbar>
        </AppBar>
        <Container maxWidth="md" className="quiz-manager__content">
          <Box sx={{ display: activePage === 'create' ? 'block' : 'none' }}>
            <CreateQuestionContainer ref={createContainerRef} />
          </Box>
          {activePage === 'questions' ? (
            <ExistingQuestionsContainer />
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
        </Container>
      </Box>
    </>
  );
}
