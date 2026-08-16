# Release process

This file covers how to cut a new release of `lentago/shared-workflows` and
how callers upgrade. It is the operational complement to
[ADR-0005](docs/adr/0005-immutable-semver-tags-replace-main-consumption.md),
which records the decision to move from `@main` to immutable semver tags.

## What must be green before tagging

- `docs-check / docs-check` passes on `main` (this is the repo's one required
  check; it runs the relative-link resolver on this repo's own markdown).
- No open PRs are waiting to merge that belong in this release — `main`
  should reflect the intended release state.
- The workflows you are releasing have been validated against at least one
  real caller repo on a branch ref (`uses: lentago/shared-workflows/...@<branch>`)
  before landing on `main`. This is the test-before-publishing discipline from
  [CLAUDE.md](CLAUDE.md); a release does not substitute for it.

## Semver policy for reusable workflows

**What counts as a breaking change (major bump):**

- Removing or renaming an input a caller could have been passing.
- Changing the *default* of an existing input in a way that alters behavior
  for callers that rely on the default (adding a new optional input with a
  sensible default is always backwards-compatible; changing an existing one
  is not automatically so).
- Changing which context a status check reports to (e.g., renaming the job
  so `required-checks.json` no longer matches).
- Tightening permissions beyond what callers have granted via `secrets: inherit`
  or explicit `permissions:` blocks, in a way that causes a caller job to fail.
- Removing a workflow file entirely.

**What counts as a minor release:**

- New optional input with a sensible default.
- New workflow file added to the repo.
- Behavior improvements or new features inside a workflow that do not change
  the caller-facing interface.

**What counts as a patch release:**

- Bug fixes that do not change the caller-facing interface.
- Documentation and comment changes inside workflow files (these don't affect
  behavior but are included in the tag for completeness).
- Dependency updates inside a workflow (e.g., bumping a SHA-pinned third-party
  action to a newer commit).

## How to cut a release

1. Ensure `main` is in the state you want to release and the green-gate above
   is satisfied.
2. Create the GitHub release from the
   [GitHub UI](https://github.com/lentago/shared-workflows/releases/new) or
   via `gh`:
   ```bash
   gh release create v<X.Y.Z> \
     --title "v<X.Y.Z>" \
     --notes "$(cat <<'EOF'
   ## What's new

   <!-- Summarize changes since the previous release.
        For breaking changes, call them out explicitly and
        show the before/after caller snippet. -->

   ## Callers

   Bump your `uses:` refs from `@v<PREV>` to `@v<X.Y.Z>`. Dependabot will
   open these as PRs automatically where it is enabled.
   EOF
   )"
   ```
3. Do **not** create or move a floating `@vX` major tag. Immutable tags only —
   see [ADR-0005](docs/adr/0005-immutable-semver-tags-replace-main-consumption.md)
   for why.

## How callers upgrade

Each caller repo references a specific version in its workflow file:

```yaml
jobs:
  claude:
    uses: lentago/shared-workflows/.github/workflows/claude-responder.yml@v1.0.0
```

To upgrade, open a PR in the caller repo that bumps `@v1.0.0` → `@v1.1.0` (or
whatever the new version is) across its `.github/workflows/` files. Once merged,
that caller picks up the new behavior.

**Dependabot automates this.** Where `dependabot.yml` includes the
`github-actions` ecosystem, Dependabot opens bump PRs automatically when a new
release appears. The fleet-wide Dependabot rollout
([lentago/.github#114](https://github.com/lentago/.github/issues/114)) is in
flight; repos that are not yet enrolled handle bumps manually until they are.

## `@main` is not a supported consumption path

`@main` continues to work mechanically — GitHub does not enforce this — but it
is not a supported consumption path. A change merged to `main` may or may not be
production-ready, may or may not be reflected in release notes, and callers that
float on `@main` accept silent, instant propagation of any merge here with no
staging window. That was the original design (ADR-0002) and is now superseded
(ADR-0005). Migrate to a semver tag.
