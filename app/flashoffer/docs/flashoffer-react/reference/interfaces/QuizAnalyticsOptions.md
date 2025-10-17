[**flashoffer-react**](../README.md)

***

# Interface: QuizAnalyticsOptions

Configuration required to submit quiz completion events to the Flashoffer
analytics service.

Defined in: src/analytics/QuizAnalytics.ts:41

## Properties

### endpoint?

> **endpoint?**: `string`

Fully qualified HTTPS endpoint that accepts quiz analytics payloads. Leave this
undefined to disable logging without changing call sites.

Defined in: src/analytics/QuizAnalytics.ts:42

***

### quizId

> **quizId**: `string`

Stable identifier for the quiz the learner completed. The backend uses this to
bucket analytics and derive aggregate metrics.

Defined in: src/analytics/QuizAnalytics.ts:43

***

### userId?

> **userId?**: `string`

Optional caller-supplied identifier for the learner. Provide this when a host
application manages session identifiers externally; otherwise the helper
supplies a page-scoped identifier.

Defined in: src/analytics/QuizAnalytics.ts:47

## Usage

```ts
const options: QuizAnalyticsOptions = {
  endpoint: "https://quiz-backend.flashoffer.dev/events",
  quizId: "espresso-basics",
};
```
