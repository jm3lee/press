[**flashoffer-react**](../README.md)

***

# Function: logQuizCompletion()

> **logQuizCompletion**(`payload`, `options`): `Promise`\<`void`\>

Post a quiz completion event to the configured analytics endpoint using a
session-scoped identifier when no caller id is provided.

Defined in: src/analytics/QuizAnalytics.ts:57

## Parameters

### payload

`QuizCompletionPayload`

Details describing the learner's answer, including question text and the chosen
option identifier.

### options

`QuizAnalyticsOptions`

Analytics configuration such as the backend endpoint and quiz identifier.

## Returns

> `Promise`\<`void`\>

Resolves once the helper attempts to send the event. The promise never rejects;
callers can inspect browser logs for warnings when a network request fails.

## Usage

```ts
await logQuizCompletion(payload, {
  endpoint: "https://quiz-backend.flashoffer.dev/events",
  quizId: "espresso-basics",
});
```
