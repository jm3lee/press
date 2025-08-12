# Design Philosophy

I design tools with a pragmatic bias. Years of shipping have taught me that code
exists to solve problems, not to impress linters or collect style points.

## What I’ve learned

* I have a distinct point of view on tool design, grounded in production use.
* I used to be pedantic about “code quality.” Much of that was aesthetics.
* Working code beats beautiful code that doesn’t ship or breaks easily.
* Reading a lot of unfamiliar code taught me that “messy” isn’t the same as
  unclear or unmaintainable.
* AI makes safe refactoring cheap and fast.
* Convenience matters. Keep things working, minimize changes, and let tools
  handle the mess.

## How I work

* Optimize for throughput: smallest diff that solves the problem.
* Prefer clarity of behavior over cosmetic perfection.
* Use AI to refactor, rename, and extract once behavior is covered.
* Contain confusion with tooling: Codex, scripts, and repeatable workflows.
* Defer cleanup until there’s a proven maintenance cost.
* Keep the system alive while you improve it; don’t chase rewrites.
