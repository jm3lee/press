[**flashoffer-react**](../README.md)

***

# Function: MultipleChoiceQuiz()

> **MultipleChoiceQuiz**(`__namedParameters`): `Element`

Defined in: src/components/MultipleChoiceQuiz.tsx:76

Accessible multiple choice quiz with inline evaluation feedback.

## Parameters

### __namedParameters

[`MultipleChoiceQuizProps`](../interfaces/MultipleChoiceQuizProps.md)

## Returns

`Element`

## Usage

The component renders a self-contained quiz that presents a question,
collects a selection, and exposes immediate feedback. A basic quiz can be
rendered by passing the required `question` and `options` props.

```tsx
import { MultipleChoiceQuiz } from "flashoffer-react";

<MultipleChoiceQuiz
  question="What channel is most effective for product launches?"
  options={[
    { id: "email", label: "Email newsletter" },
    { id: "sms", label: "SMS blast" },
    { id: "social", label: "Social media campaign" }
  ]}
  correctOptionId="social"
  explanation="Social channels deliver real-time feedback loops."
/>;
```

When a `correctOptionId` is provided, the quiz displays success or error
alerts after each submission. The messaging can be tuned using the
`successMessage`, `errorMessage`, and `explanation` props. If no correct
answer is configured, the component still surfaces the learner's selection
through the `onAnswer` callback without rendering evaluation UI.

To celebrate correct answers, provide the `confetti` prop with a
`QuizConfettiOptions` object. The helper resolves presets declared in
`QuizCelebrations` and automatically disables animations when `enabled` is set
to `false`.

```tsx
<MultipleChoiceQuiz
  question="Which preset ships the boldest Flashoffer gradients?"
  options={[
    { id: "forest", label: "Forest Canopy" },
    { id: "monochrome", label: "Monochrome Focus" },
    { id: "midnight", label: "Midnight Pulse" }
  ]}
  correctOptionId="midnight"
  confetti={{ enabled: true, preset: "burst" }}
/>;
```

## Submission flow

By default, learners can retry after an incorrect attempt when a correct
answer is defined. During these retries the component only highlights the
submitted option, keeping the correct choice hidden until the learner
either responds accurately or retries are disabled. The behaviour can be
changed by setting `allowRetry` to `false`. The component disables the
submit button until an option is selected and automatically locks choices
after a correct response. Every submission triggers `onAnswer` with the
selected option identifier and the computed correctness flag when
available.

## Deadlines and tallies

Provide an `endTime` to automatically close the quiz at a scheduled
deadline. Once the current time surpasses the end time, the component locks
interactions, surfaces the configured `closedMessage` (or a default note),
and displays the tallies attached to each option via the `tally` field.
Tallies should represent the total number of submissions recorded for each
choice.

## Accessibility

The quiz wraps its content in semantic form elements and keeps the prompt
linked to the group of radio buttons for assistive technologies. A visually
hidden `FormLabel` ensures screen reader users hear the question context,
and helper text is exposed via `FormHelperText`. Buttons remain reachable via
the keyboard, enabling accessible navigation across all supported states.
