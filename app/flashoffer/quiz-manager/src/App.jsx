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
import GeneratorPage from './GeneratorPage.jsx';

const NAVIGATION_ITEMS = [
  { id: 'create', label: 'Create Question' },
  { id: 'generate', label: 'GPT-5 Drafts' }
];

/**
 * Renders the quiz manager shell with navigation and page state.
 * @returns {JSX.Element} Quiz manager root component.
 */
export default function App() {
  const [activePage, setActivePage] = useState('create');
  const [generatorPrompt, setGeneratorPrompt] = useState('');
  const [generatorStatus, setGeneratorStatus] = useState('idle');
  const [generatorError, setGeneratorError] = useState('');
  const generationTimerRef = useRef();

  const navigationItems = useMemo(() => NAVIGATION_ITEMS, []);

  const handleSelectPage = useCallback((pageId) => {
    setActivePage(pageId);
  }, []);

  const handleGeneratorPromptChange = useCallback((event) => {
    setGeneratorPrompt(event.target.value);
  }, []);

  const handleGenerate = useCallback(() => {
    setGeneratorError('');
    setGeneratorStatus('loading');

    if (generationTimerRef.current) {
      window.clearTimeout(generationTimerRef.current);
    }

    generationTimerRef.current = window.setTimeout(() => {
      setGeneratorStatus('idle');
      setGeneratorError('Generation API is not connected yet.');
    }, 600);
  }, []);

  useEffect(() => {
    return () => {
      if (generationTimerRef.current) {
        window.clearTimeout(generationTimerRef.current);
      }
    };
  }, []);

  const content = useMemo(() => {
    if (activePage === 'create') {
      return <CreateQuestionContainer />;
    }
    return (
      <GeneratorPage
        generatorError={generatorError}
        generatorPrompt={generatorPrompt}
        generatorStatus={generatorStatus}
        handleGenerate={handleGenerate}
        handleGeneratorPromptChange={handleGeneratorPromptChange}
      />
    );
  }, [
    activePage,
    generatorError,
    generatorPrompt,
    generatorStatus,
    handleGenerate,
    handleGeneratorPromptChange
  ]);

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
            <Stack direction="row" spacing={1} className="quiz-manager__nav-buttons">
              {navigationItems.map((item) => (
                <Button
                  key={item.id}
                  color="inherit"
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
          {content}
        </Container>
      </Box>
    </>
  );
}
