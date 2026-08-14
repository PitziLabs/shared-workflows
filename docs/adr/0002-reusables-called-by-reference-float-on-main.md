# ADR-0002: Reusable workflows are called by reference and float on `@main`; tags deferred

**Status:** Accepted (2026-04-25; reconstructed 2026-08-13)

## Context

This repo exists to give the Lentago Labs fleet one place to define CI
behavior — an agentic PR responder, an AI reviewer, a docs-link checker, and
ShellCheck — instead of every repo copying its own workflow YAML. GitHub
Actions' `workflow_call` mechanism lets a caller repo reference a workflow
definition living in another repo (`uses: lentago/shared-workflows/.github/
workflows/<name>.yml@<ref>`) rather than pasting the YAML in. The `<ref>`
is a choice point from the first commit: pin every caller to a fixed
version (a tag or SHA), or point every caller at the moving tip of `main`.

## Decision

Callers use `@main` — the floating tip, not a pinned tag or SHA. This was
the shape of the repo from its first commit
([`a5cdace`](https://github.com/lentago/shared-workflows/commit/a5cdace),
"Add three reusable workflows," 2026-04-25) and is unchanged today: no
version tags have ever been shipped from this repo. `CLAUDE.md` states the
consequence explicitly — "Treat `main` changes as if they were releases
until tagged versions exist" — because a single merged PR here changes CI
behavior across every caller on their next run, with no per-repo redeploy
step. That instant, fleet-wide propagation is treated as the point of the
repo, not an accepted side effect: the README frames "one merged PR here
changes CI everywhere" as the demonstrated pattern (see
[#28](https://github.com/lentago/shared-workflows/pull/28)/[#29](https://github.com/lentago/shared-workflows/pull/29)/[#30](https://github.com/lentago/shared-workflows/pull/30)
for a caller-facing example: a docs-check bug reached every caller on
`main`, and the fix reached them the same way).

Tagging stable versions (`v0.1.0`, `v1`) and migrating callers to them is
named as future work once a workflow's contract solidifies, but has not
been done for any workflow as of this writing.

## Alternatives

- **Recorded at the time:** tag stable versions once a contract solidifies and migrate callers to the tag, deferred rather than done up front — the repo's own stated intent, not yet acted on for any workflow.
- *Retrospective — not considered at the time:* **SHA-pin every caller** (`uses: .../claude-review.yml@<full-sha>`), the standard supply-chain-hardening posture for third-party actions. This is better hygiene in isolation — a compromised or accidentally-broken `main` can't silently reach every caller — but it directly kills the feature this repo is built around: the "one merged PR, fleet-wide propagation" workflow the README calls out as the demonstrated pattern. Every caller would need a follow-up PR bumping its pinned SHA before picking up a fix, turning the fleet-wide-in-one-merge property into fleet-wide-in-N-merges. For a lab-scale, single-operator fleet without third-party contributors to this repo, the supply-chain risk this guards against is lower-stakes than the coordination cost it would add — a fair trade here, though it would be the wrong call for a repo with outside contributors or higher-stakes callers.

## Consequences

- A breaking change merged to `main` reaches every caller on their next
  workflow run, with no opportunity for a caller to opt out or stage the
  upgrade. `CLAUDE.md`'s discipline ("test before publishing on `main`" — push
  to a branch, point one caller at `@<branch-name>` for one merge, then merge
  to `main`) is the only safety net; there is no version-pinning fallback.
  Backwards-compatible-input discipline (ADR-0004) is the main structural
  mitigation.
- Callers cannot pin to a known-good version — every caller is always on the
  latest behavior of every workflow it uses. This is deliberate: it is the
  "define the pipeline once, everyone inherits it" property the README calls
  out as the central pattern this repo demonstrates.
- Introducing tags later is additive (callers migrate `@main` → `@v1` at
  their own pace) and does not require reversing this decision — it was
  scoped as deferred, not rejected, from the start.
