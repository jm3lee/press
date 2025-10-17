[**flashoffer-react**](../README.md)

***

# Interface: MultipleChoiceQuizProps

Defined in: src/components/MultipleChoiceQuiz.tsx:38

## Properties

### question

> **question**: `ReactNode`

Defined in: src/components/MultipleChoiceQuiz.tsx:41

Question or prompt displayed above the answer list.

***

### options

> **options**: [`MultipleChoiceOption`](MultipleChoiceOption.md)[]

Defined in: src/components/MultipleChoiceQuiz.tsx:43

Collection of answer choices presented to the learner.

***

### helperText?

> `optional` **helperText**: `ReactNode`

Defined in: src/components/MultipleChoiceQuiz.tsx:45

Helper text that expands on the question prompt. Falls back to a default
instruction when omitted while the quiz remains open.

***

### correctOptionId?

> `optional` **correctOptionId**: `string`

Defined in: src/components/MultipleChoiceQuiz.tsx:47

Identifier representing the correct answer choice.

***

### explanation?

> `optional` **explanation**: `ReactNode`

Defined in: src/components/MultipleChoiceQuiz.tsx:49

Additional explanation surfaced once the learner submits an answer.

***

### successMessage?

> `optional` **successMessage**: `ReactNode`

Defined in: src/components/MultipleChoiceQuiz.tsx:51

Custom message rendered for successful submissions. Defaults to "Great job!
That answer is correct."

***

### errorMessage?

> `optional` **errorMessage**: `ReactNode`

Defined in: src/components/MultipleChoiceQuiz.tsx:53

Custom message rendered when the submission is incorrect. Defaults to "Not
quite. Give it another look."

***

### onAnswer?

> `optional` **onAnswer**: (`answer`:
> [`MultipleChoiceAnswer`](MultipleChoiceAnswer.md)) => `void`

Defined in: src/components/MultipleChoiceQuiz.tsx:55

Invoked each time the learner submits an answer.

***

### submitLabel?

> `optional` **submitLabel**: `string`

Defined in: src/components/MultipleChoiceQuiz.tsx:57

Label for the submit button. Defaults to "Check answer".

***

### tryAgainLabel?

> `optional` **tryAgainLabel**: `string`

Defined in: src/components/MultipleChoiceQuiz.tsx:59

Label for the retry button. Defaults to "Try again".

***

### allowRetry?

> `optional` **allowRetry**: `boolean`

Defined in: src/components/MultipleChoiceQuiz.tsx:61

Allows additional attempts when the initial submission is incorrect. While
retries remain available, incorrect answers only highlight the submitted
choice so the correct option stays hidden. Defaults to true when a correct
answer is configured.

***

### disabled?

> `optional` **disabled**: `boolean`

Defined in: src/components/MultipleChoiceQuiz.tsx:66

Disables interactions with the quiz component.

***

### endTime?

> `optional` **endTime**: `Date` | `string` | `number`

Defined in: src/components/MultipleChoiceQuiz.tsx:70

Deadline after which the quiz stops accepting new responses and displays
aggregated tallies.

***

### closedMessage?

> `optional` **closedMessage**: `ReactNode`

Defined in: src/components/MultipleChoiceQuiz.tsx:72

Custom message announced to learners once the quiz has closed.

***

### confetti?

> `optional` **confetti**: [`QuizConfettiOptions`](QuizConfettiOptions.md)

Defined in: src/components/MultipleChoiceQuiz.tsx:77

Configures the celebratory confetti animation shown after correct answers. Set
`enabled` to `false` to disable the animation or provide a preset from
`QuizCelebrations` to change the effect.
