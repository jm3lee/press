[**flashoffer-react**](../README.md)

***

# Interface: QuizCompletionPayload

Metadata describing a learner's answer that is forwarded to the quiz analytics
backend.

Defined in: src/analytics/QuizAnalytics.ts:29

## Properties

### selectedOptionId

> **selectedOptionId**: `string`

Identifier for the option the participant selected. This value is included in
analytics metadata to let reporting surfaces highlight the user's choice.

Defined in: src/analytics/QuizAnalytics.ts:30

***

### correctOptionId?

> **correctOptionId?**: `string`

Optional identifier for the option considered correct. Supply this when the
quiz backend should evaluate whether the learner answered correctly.

Defined in: src/analytics/QuizAnalytics.ts:31

***

### isCorrect?

> **isCorrect?**: `boolean`

Indicates whether the selected option matches the authoritative answer. When
omitted, the backend infers correctness from other metadata.

Defined in: src/analytics/QuizAnalytics.ts:32

***

### question

> **question**: `string`

Prompt text presented to the learner. Including the question makes debugging
and ad-hoc analytics easier because payloads remain human-readable.

Defined in: src/analytics/QuizAnalytics.ts:33

***

### attempt

> **attempt**: `number`

Incrementing counter representing which attempt the learner is on. Use this to
track retries without storing results in local storage.

Defined in: src/analytics/QuizAnalytics.ts:34

***

### campaignId?

> **campaignId?**: `string`

Optional marketing campaign identifier associated with the quiz attempt. When
present the backend can attribute outcomes to the related initiative.

Defined in: src/analytics/QuizAnalytics.ts:35

## Usage

```ts
const payload: QuizCompletionPayload = {
  selectedOptionId: "opt-42",
  question: "Which blend has the highest caffeine?",
  attempt: 1,
};
```
