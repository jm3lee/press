# Quiz Manager Maintenance Guide

## API Targets
`ManageQuestionsContainer` builds REST URLs with `resolveApiUrl()`. Update the
`API_BASE_URL` constant when environments shift, and ensure the quiz backend
exposes `/api/quiz/questions` for list, create, and update operations. When the
backend schema evolves, mirror the changes in `buildFormStateForQuestion()` and
`buildPayload()` so the UI validates inputs consistently.

## Dependency Health
Run `npm test` within `app/flashoffer/quiz-manager` after upgrading dependencies
or modifying the bundler configuration. The project relies on React, Material
UI, and Flashoffer React; update the preview implementation if the Flashoffer
components ship breaking changes to their props or theme contract.

## Operational Checks
Use the built-in refresh button to confirm the catalog can load within new
environments. Form submissions should flip the status message returned by
`resolveSubmissionMessage()`. Verify JSON imports with both array and object
payloads whenever the import logic changes to avoid regressions.
