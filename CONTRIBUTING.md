# Contributing to NexusRAG

Thanks for contributing to NexusRAG.

This repository is designed to be ambitious, safety-conscious, and production-oriented. The best contributions keep those three qualities intact at the same time.

## Before You Start

- read the [README](./README.md)
- review the architecture docs in [`docs/architecture`](./docs/architecture)
- check for existing issues before opening a new one
- do not open public issues for security vulnerabilities; use the process in [SECURITY.md](./SECURITY.md)

## Development Setup

### Backend

```bash
python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -e .[dev]
```

### Frontend

```bash
cd frontend
npm ci
cd ..
```

### Local configuration

Create a local `.env` from the safe example file and keep real secrets out of Git:

```bash
copy .env.example .env
```

## Workflow

1. Create a branch from `main`
2. Keep changes focused and cohesive
3. Run the relevant validation before opening a pull request
4. Open a pull request using the repository template
5. Resolve feedback and keep the branch up to date with `main`

## Validation Expectations

### Backend

```bash
pytest -q
python -m compileall src apps cli sdk tests eval
```

### Frontend

```bash
cd frontend
npm run lint
npm run typecheck
npm run build
```

## Contribution Guidelines

- prefer small, reviewable pull requests over large, mixed changes
- preserve the layer dependency rules
- add or update tests for behavior changes
- keep user-facing copy clear and intentional
- avoid committing generated files, secrets, local databases, caches, or uploads
- update docs and config examples when behavior or setup changes

## Pull Request Checklist

Before opening a PR, confirm:

- the change is scoped and explained clearly
- relevant tests pass locally
- no secrets were added
- new config or env variables are documented
- user-facing behavior is covered by docs, screenshots, or examples when helpful

## Design Notes

NexusRAG is built as a retrieval operating system, not just a thin RAG demo. Good contributions usually strengthen one or more of these areas:

- correctness and type safety
- system observability
- retrieval quality
- security and failure handling
- developer ergonomics

If you are unsure whether an idea fits, open a feature request and we can shape it together.
