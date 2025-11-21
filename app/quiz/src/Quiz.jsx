import React, { useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { useDispatch, useSelector } from 'react-redux';
import { fetchQuiz, submitQuiz } from './features/quizSlice';

/**
 * @fileoverview Interactive multiple-choice quiz component.
 *
 * The quiz loads questions from a JSON file, tracks a user's selections,
 * and displays a final score once submitted.  Styling is handled via the
 * accompanying `index.css` file.
 */

/**
 * Quiz component that fetches questions from a JSON source, allows users to select answers,
 * submit them, and then displays the score along with each question's correct/incorrect styling
 * and explanations.
 *
 * ### Props
 * @param {Object} props
 * @param {string} [props.src="/study/key_terms.json"] - URL or path to the quiz JSON file.
 *
 * @returns {JSX.Element}
 */
const Quiz = ({ src = "/study/key_terms.json" }) => {
  const dispatch = useDispatch();
  const { answers, error, questions, score, showAnswers, status } = useSelector(
    (state) => state.quiz,
  );

  const {
    handleSubmit,
    register,
    reset,
    watch,
  } = useForm({
    defaultValues: { answers: {} },
  });

  const watchedAnswers = watch('answers');

  // Fetch quiz questions whenever the `src` prop changes.
  useEffect(() => {
    dispatch(fetchQuiz(src));
  }, [dispatch, src]);

  useEffect(() => {
    const defaults = questions.reduce((acc, _question, index) => {
      const persisted = answers[index];
      acc[index] = persisted ?? '';
      return acc;
    }, {});

    reset({ answers: defaults });
  }, [answers, questions, reset]);

  const onSubmit = (data) => {
    dispatch(submitQuiz({ answers: data.answers ?? {} }));
  };

  return (
    <form className="quiz-container" onSubmit={handleSubmit(onSubmit)}>
      {status === 'loading' && <p>Loading quiz...</p>}
      {status === 'failed' && (
        <p className="error">{error || 'Unable to load quiz.'}</p>
      )}

      {questions.map((q, qIndex) => {
        const correctIndex = q.a[0];
        const explanation = q.a[1];
        const currentSelection = showAnswers
          ? answers[qIndex]
          : watchedAnswers?.[qIndex];

        return (
          <div key={qIndex} className="question-block">
            <div
              className="question"
              dangerouslySetInnerHTML={{ __html: q.q }}
            />

            <ul className="choices">
              {q.c.map((choice, cIndex) => {
                const isSelected = String(currentSelection) === String(cIndex);
                const isCorrect = cIndex === correctIndex;
                const isWrong = isSelected && !isCorrect;

                let className = "choice";
                if (showAnswers) {
                  if (isCorrect) className += " correct";
                  else if (isWrong) className += " incorrect";
                } else if (isSelected) {
                  className += " selected";
                }

                return (
                  <li key={cIndex} className={className}>
                    <label>
                      <input
                        type="radio"
                        value={cIndex}
                        disabled={showAnswers}
                        {...register(`answers.${qIndex}`)}
                      />
                      <span
                        dangerouslySetInnerHTML={{ __html: choice }}
                      />
                    </label>
                  </li>
                );
              })}
            </ul>

            {showAnswers && explanation && (
              <div className="explanation">
                <strong>Explanation:</strong>{" "}
                <span
                  dangerouslySetInnerHTML={{ __html: explanation }}
                />
              </div>
            )}
          </div>
        );
      })}

      {!showAnswers ? (
        <button className="submit-btn" type="submit">
          Submit Answers
        </button>
      ) : (
        <div className="score-block">
          <h2>Your Score: {score} / {questions.length}</h2>
        </div>
      )}
    </form>
  );
};

export default Quiz;
