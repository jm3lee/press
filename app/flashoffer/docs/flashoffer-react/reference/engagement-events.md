# Engagement events

The engagement system emits several event types that describe how visitors
observe and interact with tracked elements. Each event payload includes the
`type`, `target`, `meta`, and timestamp (`at`) fields sent by the
`EngagementProvider` queue.

## `view`

The provider emits a `view` event when an observed element first intersects the
viewport. The element must be registered with
[`ViewTracker`](functions/ViewTracker.md) or `useViewTracker`; when the
underlying `IntersectionObserver` reports that the
track id is visible, the event is queued immediately.

The event’s `meta` object merges the metadata supplied during registration and a
normalized intersection `ratio` from the observer. The ratio is clamped between
0 and 1 and rounded to three decimals, showing the fractional portion of the
component that was visible when the view began.

## `view-end`

The `view-end` event fires when a tracked element that was previously visible is
no longer intersecting the viewport. The provider also emits `view-end` when the
component is detached from tracking.

`view-end` metrics capture how long the view lasted and the peak visibility.
The `duration_ms` field is computed from `performance.now()` timestamps recorded
when the view started and stopped, and `ratio` captures the maximum intersection
ratio observed while the element remained on screen.

## `interaction`

An `interaction` event records explicit user activity that is triggered by the
[`useRecordInteraction`](functions/useRecordInteraction.md) hook or the
`recordInteraction` function from the engagement context. The `target` is the
semantic identifier supplied by the caller; the `meta` object merges the
caller’s metadata with automatically captured page state:

- `scroll`: includes `ratio` (0–1) and `pixels` representing the current scroll
  position when the interaction occurred. The ratio is clamped and rounded to
  three decimals.
- `active`: an array of track ids for elements that are actively in view when
  the interaction fires. This field only appears when at least one element is in
  the active set.

## `scroll-depth`

The provider emits `scroll-depth` events when the visitor scrolls beyond the
configured thresholds (default `0.25`, `0.5`, `0.75`, `1`). The event is
triggered once per threshold as soon as the measured scroll ratio meets or
exceeds the value.

The `meta` object contains:

- `depth`: the threshold ratio that was just crossed. A depth of `1` indicates
  the user reached the end of the document.
- `pixels`: the rounded vertical scroll offset when the threshold fired.

## `dwell`

`dwell` events represent continued engagement while the page remains visible and
the visitor is active. The provider sets up a heartbeat interval (default 15
seconds) that emits `dwell` when the page has not gone idle or hidden. If the
user becomes idle longer than the configured timeout, dwell events pause until
activity resumes.

Each `dwell` event includes `interval_ms`, the heartbeat interval duration, so
analytics consumers can aggregate the total engaged time by summing the
intervals.

## `page-load`

The `page-load` event fires once per session when the current document finishes
loading. It uses the `page` target so downstream analytics can pinpoint when a
visitor first became active on the site.

When the Navigation Timing API is available, the provider includes
`load_duration_ms` in the `meta` object. The value reports the rounded interval
between the navigation start and the browser’s load event; the field is omitted
when timing data cannot be measured.
