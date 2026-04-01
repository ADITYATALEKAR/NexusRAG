# Security Policy

Security matters for NexusRAG because the system handles retrieval, provider credentials, audit data, deployment configuration, and user-submitted content.

## Supported Versions

Security fixes are applied to:

- the current `main` branch
- the latest tagged release, once releases are established

## Reporting a Vulnerability

Please do not open a public GitHub issue for security vulnerabilities.

Use one of these private paths instead:

1. GitHub private vulnerability reporting, if enabled on the repository
2. A private security advisory draft at:
   `https://github.com/ADITYATALEKAR/NexusRAG/security/advisories/new`

When reporting, include:

- a clear description of the issue
- impact and affected area
- reproduction steps or proof of concept
- remediation ideas if you have them

Please do not include live credentials in the report. Redact secrets before sharing logs, traces, or payloads.

## Secret Handling

Never commit:

- API keys
- passwords
- tokens
- certificates or private keys
- local `.env` files
- real customer or private internal data

The repository already ignores common secret and runtime file patterns, but contributors are still responsible for checking their changes before pushing.

## Security Expectations for Contributions

Changes should preserve or improve:

- secret masking
- input sanitization and injection defenses
- auth and rate limiting
- auditability and observability
- safe defaults in examples and deployment configs

If a change weakens a control temporarily, call it out clearly in the pull request so it can be reviewed explicitly.
