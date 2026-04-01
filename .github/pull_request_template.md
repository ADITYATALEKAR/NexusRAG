## Summary

Describe what changed in this PR.

## Why

Explain the user, engineering, or operational reason for the change.

## Scope

- [ ] Backend
- [ ] Frontend
- [ ] CLI / SDK
- [ ] Deployment / CI
- [ ] Docs

## Validation

List the commands, tests, or manual checks you ran.

```text
pytest -q
python -m compileall src apps cli sdk tests eval
cd frontend && npm run lint && npm run typecheck && npm run build
```

## Security and operations checklist

- [ ] No secrets or credentials were added
- [ ] New config or env vars are documented
- [ ] Error handling and logs avoid leaking sensitive data
- [ ] Monitoring, rate limiting, or auth implications were considered

## Screenshots or API examples

Add screenshots, curl examples, or payload samples when helpful.

