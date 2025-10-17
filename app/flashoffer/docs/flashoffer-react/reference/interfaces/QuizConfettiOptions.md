[**flashoffer-react**](../README.md)

***

# Interface: QuizConfettiOptions

Configuration describing when to play a celebratory confetti animation.

Defined in: src/components/QuizCelebrations.ts:16

## Properties

### enabled

> **enabled**: `boolean`

Turns the animation on or off. Set this to `false` to suppress confetti even
when a quiz answer is correct.

Defined in: src/components/QuizCelebrations.ts:18

***

### preset?

> `optional` **preset**:
> [`QuizConfettiPreset`](../type-aliases/QuizConfettiPreset.md)

Selects the visual preset to render. Defaults to `"classic"` when omitted.

Defined in: src/components/QuizCelebrations.ts:20

## Usage

```ts
const celebration: QuizConfettiOptions = {
  enabled: true,
  preset: "streamers",
};
```
