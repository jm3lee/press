import { createAsyncThunk, createSlice } from '@reduxjs/toolkit';

export const fetchQuiz = createAsyncThunk(
  'quiz/fetchQuiz',
  async (src) => {
    const response = await fetch(src);
    if (!response.ok) {
      throw new Error('Failed to load quiz content');
    }

    return response.json();
  },
);

const initialState = {
  answers: {},
  error: null,
  questions: [],
  score: null,
  showAnswers: false,
  status: 'idle',
};

const quizSlice = createSlice({
  name: 'quiz',
  initialState,
  reducers: {
    resetQuiz: (state) => {
      state.answers = {};
      state.score = null;
      state.showAnswers = false;
    },
    submitQuiz: (state, action) => {
      const submittedAnswers = action.payload?.answers ?? {};
      let computedScore = 0;

      state.questions.forEach((question, index) => {
        const correctIndex = question.a[0];
        const choice = submittedAnswers[index];
        const choiceIndex =
          choice === undefined || choice === '' ? null : Number(choice);

        if (choiceIndex === correctIndex) {
          computedScore += 1;
        }
      });

      state.answers = submittedAnswers;
      state.score = computedScore;
      state.showAnswers = true;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchQuiz.pending, (state) => {
        state.status = 'loading';
        state.error = null;
      })
      .addCase(fetchQuiz.fulfilled, (state, action) => {
        state.status = 'succeeded';
        state.questions = action.payload;
        state.answers = {};
        state.showAnswers = false;
        state.score = null;
      })
      .addCase(fetchQuiz.rejected, (state, action) => {
        state.status = 'failed';
        state.error = action.error.message;
      });
  },
});

export const { resetQuiz, submitQuiz } = quizSlice.actions;
export default quizSlice.reducer;
