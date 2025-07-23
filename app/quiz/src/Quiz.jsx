import React, { useEffect, useState } from 'react';

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
  const [questions, setQuestions] = useState([]);
  const [selected, setSelected] = useState({});
  const [showAnswers, setShowAnswers] = useState(false);
  const [score, setScore] = useState(null);

  useEffect(() => {
    fetch(src)
      .then((res) => res.json())
      .then(setQuestions)
      .catch(console.error);
  }, [src]);

  /**
   * Handle a user selecting a choice.
   *
   * @param {number} qIndex - Index of the question
   * @param {number} cIndex - Index of the choice
   */
  const handleSelect = (qIndex, cIndex) => {
    if (showAnswers) return;
    setSelected((prev) => ({ ...prev, [qIndex]: cIndex }));
  };

  /**
   * Calculate the user's score and reveal correct answers.
   */
  const handleSubmit = () => {
    const newScore = questions.reduce((acc, q, qIndex) => {
      const correctIndex = q.a[0];
      return acc + (selected[qIndex] === correctIndex ? 1 : 0);
    }, 0);

    setScore(newScore);
    setShowAnswers(true);
  };

  return (
    <div className="quiz-container">
      {questions.map((q, qIndex) => {
        const correctIndex = q.a[0];
        const explanation = q.a[1];

        return (
          <div key={qIndex} className="question-block">
            <div
              className="question"
              dangerouslySetInnerHTML={{ __html: q.q }}
            />

            <ul className="choices">
              {q.c.map((choice, cIndex) => {
                const isSelected = selected[qIndex] === cIndex;
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
                  <li
                    key={cIndex}
                    className={className}
                    onClick={() => handleSelect(qIndex, cIndex)}
                    dangerouslySetInnerHTML={{ __html: choice }}
                  />
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
        <button className="submit-btn" onClick={handleSubmit}>
          Submit Answers
        </button>
      ) : (
        <div className="score-block">
          <h2>Your Score: {score} / {questions.length}</h2>
        </div>
      )}
    </div>
  );
};

export default Quiz;
