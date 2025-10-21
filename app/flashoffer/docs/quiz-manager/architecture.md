# Quiz Manager Architecture

## Overview
The quiz manager is a standalone React single-page application compiled with
Vite and shipped from the `quiz-manager` Docker image. The bundle boots inside
an element tagged with a `data-endpoint` attribute so operators can retarget
API hosts without rebuilding the frontend. A HashRouter hosts the UI under the
`/` path to keep static hosting requirements minimal while preserving client-
side navigation semantics. The application is served through the quiz-manager
service defined in `app/flashoffer/docker/quiz.yml` alongside the quiz backend.

## Bootstrapping and Routing
`src/main.jsx` mounts the application when `DOMContentLoaded` fires. It reads
`data-endpoint` from the root node, passes the value to `<QuizManager />`, and
installs a hash-based router that renders the manager at `/#/` regardless of the
hosting origin. This approach lets the same static assets run behind Nginx in
Docker or inside the Press site without rewriting links. The router delegates
all sub-routes to `<QuizManager />`, which manages a simple tab navigation
constructed from the `PAGE_DEFINITIONS` table.

## State and Data Flow
`QuizManager.jsx` centralizes application state with React hooks. It builds an
empty form model with helpers such as `createEmptyForm()` and
`buildFormStateForQuestion()` so both manual authoring and existing question
selection reuse the same shape. The component keeps track of async status flags
for the upload form, question list, and generator workflow, allowing the pages
to render contextual spinners and alerts. The manager normalizes inbound data,
coerces date fields, and maintains option arrays with helpers like
`normalizeOptionEntries()` to guarantee payloads align with backend validation.

The component accepts `uploadEndpoint` and `listEndpoint` props, trimming any
trailing slashes before constructing the canonical REST targets. CRUD
operations use the native Fetch API: `fetchQuestions()` lists the latest 50
entries, `submitQuestion()` posts new or updated payloads, and
`requestGeneratedQuestion()` requests AI drafts from the backend. LocalStorage
persists the last generator prompt via `GENERATOR_PROMPT_STORAGE_KEY`, and the
value is hydrated during initialization for better operator ergonomics.

## Page Composition
The manager renders three child pages that receive state and handlers via props:

- **CreateQuestionPage** – Presents the authoring form, file-import flow, and
  Flashoffer React preview. It uses Material UI controls, wires option
  management handlers, and embeds `FlashofferThemeProvider` with
  `MultipleChoiceQuiz` to preview the payload before submission.
- **GeneratorPage** – Captures optional prompts and kicks off the generator
  request. It surfaces async errors and toggles the button label while the
  backend request is pending.
- **ExistingQuestionsPage** – Displays the catalog with Material UI tables,
  offers manual refresh, and reports loading or error states. Selecting a row
  loads the question into the form for edits.

Each page is styled via `src/styles.css`, which defines the responsive layout
classes consumed across the panels. Because the parent manages all mutations,
page components remain stateless and easy to test.

## Backend Integration
By default the manager targets `/api/quiz/questions`, aligning with the quiz
backend REST endpoints. When a deployment requires cross-origin calls, the
backend’s `/config` route and CORS settings allow the UI to point at remote
hosts. The quiz-manager Docker service proxies requests through the
`quiz-backend` container during development, and production traffic should pass
through the same Nginx layer configured in `app/flashoffer/quiz-backend`.
