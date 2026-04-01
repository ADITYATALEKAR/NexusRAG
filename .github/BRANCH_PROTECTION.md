# Branch Protection Guidance

This repository is public, but it is currently maintained by a single primary author. The settings below keep `main` safe without forcing a workflow that slows down solo progress.

## Recommended baseline for `main`

- Protect the `main` branch
- Require a pull request before merging
- Require status checks to pass before merging
- Require conversation resolution before merging
- Require linear history
- Do not allow force pushes
- Do not allow branch deletion

## Review policy

For the current solo-maintainer stage:

- keep required approvals at `0`
- rely on CI, conversation resolution, and branch protection

When at least one additional maintainer joins:

- increase required approvals to `1`
- consider enabling code owner review

## Status checks to require

After the CI workflow has run at least once on GitHub, mark the checks emitted by `.github/workflows/ci.yml` as required:

- `backend`
- `frontend`

If GitHub shows the checks with workflow prefixes in the UI, select the exact names shown there.

## Suggested GitHub UI path

1. Open `Settings`
2. Open `Branches`
3. Add a branch protection rule for `main`
4. Enable the recommended settings above
5. Save the rule

## Why this setup

This gives NexusRAG a healthy collaboration baseline:

- direct pushes to `main` become harder to do accidentally
- CI protects backend and frontend quality together
- contributors can work through pull requests cleanly
- the rule can scale later without forcing heavyweight process today
