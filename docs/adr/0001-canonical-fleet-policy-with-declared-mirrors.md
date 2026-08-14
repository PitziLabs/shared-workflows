# ADR-0001: Canonical fleet policy lives in-git, with declared, manually-audited mirrors

**Status:** Accepted (2026-06-07; reconstructed 2026-08-13)

## Context

Before this decision, the fleet's PR-workflow conventions lived only in
`~/repos/CLAUDE.md` — a local, non-git file on one operator's machine
([#5](https://github.com/lentago/shared-workflows/issues/5)). Two consuming
surfaces could not read it at all:

- The CI `claude-code-action` reviewer runs in a fresh GitHub Actions runner
  with no home directory.
- Fresh clones and sandboxed sessions have no `~/repos/CLAUDE.md` either.

A pointer (a reference to "go read `~/repos/CLAUDE.md`") cannot cross a
repo/directory boundary for either surface — only a copy delivers where the
reader can't reach the original.

## Decision

`shared-workflows`' `CLAUDE.md` becomes the **canonical, in-git source of
truth** for the fleet PR-workflow rules. `~/repos/CLAUDE.md` becomes a
**declared local-tree mirror**, kept only so local Claude Code sessions pick
the rules up via the directory-tree walk. A third mirror exists inside this
repo: the `review_prompt` template in `.github/workflows/claude-review.yml`
inverts the same rules into review criteria so the CI reviewer can flag
violations. Each mirror exists because its reader can only see its own
copy — the canonical file's header states the sync obligation explicitly and
names both mirrors.

This is manual, audited duplication, not automated sync: whoever edits the
canonical section is responsible for propagating the change to both mirrors
in the same session. That obligation was tested on 2026-08-12, when the
`~/repos/CLAUDE.md` mirror was found to hold a newer, verified fact (the
correct Route 53/DNS owner and the closed status of solidago#142) that the
canonical `CLAUDE.md` here still had wrong
([#33](https://github.com/lentago/shared-workflows/pull/33), closing
[#32](https://github.com/lentago/shared-workflows/issues/32)). The fix
brought the canonical file back in line with the mirror rather than the
other way around — i.e., when a mirror is caught ahead of the canonical
source with a verified correction, the correction flows *into* the
canonical file. That resolution pattern isn't written down anywhere as a
standing rule; it's inferred here from how #33 was actually resolved.

## Alternatives

- **Recorded at the time ([#5](https://github.com/lentago/shared-workflows/issues/5)):** leave `~/repos/CLAUDE.md` in place and add nothing in-git. Rejected outright — it's the status quo that motivated this decision, since neither CI nor fresh clones can read a home directory.
- *Retrospective — not considered at the time:* **CI-generated mirrors** (a script or CI job that regenerates `~/repos/CLAUDE.md` and the `claude-review.yml` prompt block from the canonical section on every merge). Arguably better than the manual-audit approach adopted here — it would remove the sync obligation entirely and make the 2026-08-12 drift structurally impossible rather than something a later audit had to catch. It was not built; the manual approach was accepted as "good enough" for a two-mirror, low-churn document. Worth building if a third mirror is ever added or drift recurs.

## Consequences

- Editing the fleet PR-workflow section requires touching up to three files
  in one session: this `CLAUDE.md`, `~/repos/CLAUDE.md`, and the
  `review_prompt` block in `claude-review.yml`. Nothing enforces this beyond
  the stated obligation and manual review.
- The canonical file is readable by CI and by fresh clones, closing the two
  gaps that motivated the change. The local-only mirror still serves its one
  remaining purpose: the directory-tree memory walk for local sessions.
  Fresh-clone sessions that never inherit `~/repos/CLAUDE.md` are an accepted
  residual gap (out of scope per #5).
- Drift is possible whenever an edit lands in only one location; the
  2026-08-12 incident shows the audit trail needed to detect and correct it
  (a later issue filed against the canonical source, cross-checked against
  the mirror) but not a mechanism that prevents it.
