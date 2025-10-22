/*
 * Copyright (c) Flashoffer Developers
 * Released under the MIT license.
 */

import { useCallback, useEffect, useState } from 'react';
import ExistingQuestionsPage from './ExistingQuestionsPage.jsx';

const QUESTIONS_ENDPOINT = '/api/quiz/questions';

/**
 * Manages loading and selection state for the existing questions view.
 * @returns {JSX.Element} Existing questions container.
 */
export default function ExistingQuestionsContainer() {
  const [questions, setQuestions] = useState([]);
  const [questionsStatus, setQuestionsStatus] = useState('idle');
  const [questionsError, setQuestionsError] = useState('');
  const [selectedSlug, setSelectedSlug] = useState('');

  const fetchQuestions = useCallback(async () => {
    if (typeof window === 'undefined') {
      return [];
    }

    setQuestionsStatus('loading');
    setQuestionsError('');

    try {
      const url = new URL(
        'http://localhost:8002' + QUESTIONS_ENDPOINT,
        window.location.origin,
      );
      url.searchParams.set('limit', '50');
      url.searchParams.set('offset', '0');

      const response = await fetch(url.toString());
      const body = await response.json().catch(() => ({}));

      if (!response.ok) {
        const message =
          body?.error ?? `Failed to load questions (${response.status})`;
        throw new Error(message);
      }

      const items = Array.isArray(body?.questions) ? body.questions : [];
      setQuestions(items);
      setQuestionsStatus('success');
      return items;
    } catch (error) {
      setQuestionsStatus('error');
      setQuestionsError(
        error instanceof Error ? error.message : 'Unable to load questions',
      );
      setQuestions([]);
      throw error;
    }
  }, []);

  const handleSelectQuestion = useCallback((question) => {
    if (!question) {
      return;
    }
    setSelectedSlug(question.slug ?? '');
  }, []);

  useEffect(() => {
    fetchQuestions().catch(() => {
      /* error captured in state */
    });
  }, [fetchQuestions]);

  return (
    <ExistingQuestionsPage
      fetchQuestions={fetchQuestions}
      handleSelectQuestion={handleSelectQuestion}
      questions={questions}
      questionsError={questionsError}
      questionsStatus={questionsStatus}
      selectedSlug={selectedSlug}
    />
  );
}
