[**flashoffer-react**](../README.md)

***

# Function: MultipleChoiceQuiz()

> **MultipleChoiceQuiz**(`__namedParameters`): `Element`

Defined in: src/components/MultipleChoiceQuiz.tsx:76

Accessible multiple choice quiz with a full-screen feedback modal.

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
feedback inside a full-screen modal after each submission. The modal can be
reopened via the in-card `View feedback` control. The messaging can be tuned
using the `successMessage`, `errorMessage`, and `explanation` props. If no
correct answer is configured, the component still surfaces the learner's
selection through the `onAnswer` callback without rendering evaluation UI.

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

To minimize visual jumpiness, the component animates layout updates such as
revealing option descriptions, surfacing the feedback trigger, and presenting
the retry button. These smooth transitions help learners follow the flow of
the quiz without abrupt shifts in content.

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
