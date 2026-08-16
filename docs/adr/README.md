# Architecture decision records

These records were reconstructed 2026-08-13 from repo history — commits,
issues, pull requests, `CLAUDE.md`, and prior fleet incident reports — as
part of a fleet-wide ADR reconstruction effort. They were not written at
the time each decision was made; each entry's **Status** line carries the
original decision date alongside the 2026-08-13 reconstruction date.
Every issue/PR number, file, and date cited was checked against this
repo's actual history before being asserted; anything that could not be
verified from this repo is called out as uncertain in the entry itself
rather than presented as fact.

Format follows the fleet's existing ADR style (`drosera/docs/adr/`,
`solidago/docs/decisions/`): `# ADR-NNNN: <title>`, a **Status** line,
then **Context**, **Decision**, **Alternatives**, and **Consequences**.
Each entry's **Alternatives** section separates what was actually
considered at the time from options added in retrospect (marked
*"retrospective — not considered at the time"*) — the latter are honest
after-the-fact assessments, not a claim that they were weighed when the
decision was made.

## Index

| ADR | Decision | Original date |
|---|---|---|
| [0001](0001-canonical-fleet-policy-with-declared-mirrors.md) | Canonical fleet policy lives in-git, with declared, manually-audited mirrors | 2026-06-07 |
| [0002](0002-reusables-called-by-reference-float-on-main.md) | Reusable workflows are called by reference and float on `@main`; tags deferred | 2026-04-25 |
| [0003](0003-ai-reviewer-advisory-never-a-merge-gate.md) | The AI reviewer is advisory and never a merge gate | 2026-07-01 |
| [0004](0004-backwards-compatible-contracts-and-self-dogfooding.md) | Backwards-compatible `workflow_call` contracts only, dogfooded via a local-path ref | 2026-05-26 (extended 2026-07-25) |
| [0005](0005-immutable-semver-tags-replace-main-consumption.md) | Callers migrate from `@main` to immutable semver tags; `@main` no longer supported | 2026-08-16 |
