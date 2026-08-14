# ADR-0003: The AI reviewer is advisory and never a merge gate

**Status:** Accepted (2026-07-01; reconstructed 2026-08-13)

## Context

`claude-review.yml` runs an automated Haiku-based review on fleet PRs.
[#14](https://github.com/lentago/shared-workflows/issues/14) (opened
2026-07-01) documented two independent failure modes observed across the
fleet, both of which turned the check red or unstable without ever posting
a usable review:

1. **Turn-budget exhaustion (deterministic).** With a 15-turn cap, the
   reviewer regularly exhausted its budget and exited non-zero *before*
   posting a review. Observed on caller PRs #3/#4/#6/#11 in a sibling repo.
2. **0-byte API response (intermittent).** On other runs the job fast-failed
   (~12s) with an empty API response, posted no findings, and reported
   unstable. Observed on one caller PR (recovered by a manual diff review);
   did not recur on two later runs in the same repo.

Because the check went red or unstable without a verdict either way, it
blocked `gh pr merge --auto` arming and forced manual merges — the review
gate could be trusted neither to run to completion nor to fail cleanly.

The issue brief for this ADR set also asserts that per-PR automated
triggering of the reviewer was disabled fleet-wide on 2026-06-25. That date
and event are not verifiable from this repo — they would be recorded in
caller repos' workflow-run history, which this repo has no visibility into
— so it is recorded here only as an unconfirmed data point, not asserted as
fact.

## Decision

[#15](https://github.com/lentago/shared-workflows/pull/15) (merged
2026-07-01, closing #14) makes the review advisory and non-blocking rather
than fixing the underlying flakiness directly:

- **`continue-on-error: true`** on the review step, and the job always
  exits `0` — a transient failure no longer reddens the check or gates a
  merge.
- **`max_turns` default raised 15 → 40**, addressing the deterministic
  turn-cap exhaustion mode directly.
- **Soft-fail notice** — if the review can't complete, the job posts a
  neutral "advisory, non-blocking" PR comment instead of leaving a bare
  failure.

The framing, recorded in the README's patterns table: "a flaky AI call never stalls delivery."
A retry-with-backoff around the intermittent 0-byte response was
considered and explicitly deferred — the soft-fail already keeps that case
from blocking, and a retry would need the prompt hoisted to a job-level
env to avoid drift, judged a larger change than the reliability fix
warranted.

## Alternatives

- **Recorded at the time (#14):** "raise/remove the turn cap, add retry/backoff around the empty-response path, and have the job post an explicit 'review could not complete' status rather than a bare non-zero exit" — the turn-cap raise and the soft-fail status were both adopted in #15; the retry/backoff option was considered and deferred (see Decision).
- *Retrospective — not considered at the time:* **Required check with a generous manual-override path** (keep the review blocking, but grant repo admins a documented `admin merge` escape hatch for confirmed-flaky runs). This is worse for a small, high-trust fleet: it keeps the coordination cost of "check the failure mode before merging" on every red run, exactly what advisory-and-non-blocking eliminates, in exchange for a marginal increase in review coverage that a soft-fail comment already partially recovers (it still tells a human to look). Not adopted in this reconstruction either — noted only as a worse-fit option.
- *Retrospective — not considered at the time:* **Switch the reviewer to a more capable/expensive model** (e.g., Sonnet) instead of tuning Haiku's turn budget. This is a lateral option: a stronger model plausibly needs fewer turns to complete a review, which would reduce (not eliminate) the deterministic failure mode, but it doesn't touch the intermittent 0-byte-response mode at all and raises the fleet's per-PR review cost across every caller. Advisory-and-non-blocking fixes both failure modes' *consequences* regardless of model; a model swap would only address one failure mode's *cause*, partially.

## Consequences

- A transient API failure or turn-budget exhaustion no longer blocks
  `gh pr merge --auto` arming anywhere in the fleet — the stated goal.
- Review coverage is best-effort: a PR can merge with no AI review having
  completed, silently, unless a human reads the soft-fail comment. The
  README documents this trade-off explicitly ("this is *not* a required
  check, and you should not treat it as one").
- The underlying flakiness (turn-budget pressure, occasional empty API
  responses) is mitigated by the higher turn cap but not eliminated; the
  0-byte response path still has no retry, by deliberate scope decision.
