# Flashoffer Documentation Index

The Flashoffer documentation suite provides deep dives into the services and
frontends that power limited-time promotions. Use this index to orient new team
members and quickly locate the guide that answers your current question.

## Quick start

If you are onboarding to Flashoffer, begin with the conceptual overview in
`flashoffer-react.md`. That primer explains the domain language, the design
system principles, and how the React components assemble into production-ready
experiences. Follow it with `flashoffer-demo.md` to explore the interactive
playground and learn how to iterate on content safely.

## Reference map

- `flashoffer-react/` contains component-specific deep dives, Storybook
  controls, and migration notes for the Flashoffer UI library.
- `api/` documents the HTTP and gRPC services that underpin quiz delivery,
  offer redemption, and analytics exports.
- `quiz-backend/` describes the server-side quiz engines, database schemas, and
  operational runbooks used during high-traffic campaigns.
- `quiz-manager/` explains the authoring UI, GPT-assisted question generation,
  and the publication workflows content teams rely on.

Each directory follows the same structure: a high-level README, task-focused
recipes, and troubleshooting appendices. Start with the README for orientation,
then drill into the recipe that matches your workflow.

## Support channels

Open documentation gaps, clarity questions, or proposed improvements in the
`#flashoffer-docs` Slack channel. The Flashoffer engineering leads triage that
queue daily and will assign reviewers when a change requires code updates in
addition to documentation.
