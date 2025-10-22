# Quiz Manager Design Notes

## Combined Management Experience
The quiz manager now presents creation and browsing capabilities within a
single two-pane view driven by `ManageQuestionsContainer`. The left pane hosts
the authoring form while the right pane lists previously published questions.
Selecting a question populates the form for editing so operators never leave
the page. The container shares memoized handlers between panes to keep state
synchronized.

## Data Entry Experience
The authoring panel relies on Material UI inputs grouped by semantic field
groups. Option rows expand dynamically and enforce a minimum of three entries to
mirror backend validation. Inline alerts surface validation failures, API
errors, and success feedback so operators understand the next action.

## File Import Workflow
`handleFileChange()` powers the JSON import button. The helper parses either a
single object or a one-element array, normalizes the structure via
`buildFormStateForQuestion()`, and resets the form mode to `create`. Error
messages bubble into the existing alert surface to keep the workflow consistent.

## Preview Strategy
Live previews reuse the Flashoffer React `MultipleChoiceQuiz` component wrapped
in `FlashofferThemeProvider`. Preview data is derived from the form through
`resolvePreviewQuestion()`, ensuring trimmed text and fallback values to present
usable scaffolding even when required fields are empty.
