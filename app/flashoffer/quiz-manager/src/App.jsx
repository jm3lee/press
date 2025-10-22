/*
 * Copyright (c) Flashoffer Developers
 * Released under the MIT license.
 */

import { useCallback, useMemo, useState } from 'react';
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
import ManageQuestionsContainer from './ManageQuestionsContainer.jsx';
import GeneratorPage from './GeneratorPage.jsx';

const NAVIGATION_ITEMS = [
  { id: 'manage', label: 'Manage' },
  { id: 'generate', label: 'Generate' }
];

/**
 * Renders the quiz manager shell with navigation and page state.
 * @returns {JSX.Element} Quiz manager root component.
 */
export default function App() {
  const [activePage, setActivePage] = useState('manage');
  const navigationItems = useMemo(() => NAVIGATION_ITEMS, []);

  const handleSelectPage = useCallback((pageId) => {
    setActivePage(pageId);
  }, []);

  const content = useMemo(() => {
    if (activePage === 'manage') {
      return <ManageQuestionsContainer />;
    }
    return <GeneratorPage />;
  }, [activePage]);

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
            <Stack direction="row" spacing={1} alignItems="center">
              {navigationItems.map((item) => (
                <Button
                  key={item.id}
                  onClick={() => handleSelectPage(item.id)}
                  variant={activePage === item.id ? 'contained' : 'outlined'}
                >
                  {item.label}
                </Button>
              ))}
            </Stack>
          </Toolbar>
        </AppBar>
        <Container maxWidth="lg" className="quiz-manager__content">
          {content}
        </Container>
      </Box>
    </>
  );
}
