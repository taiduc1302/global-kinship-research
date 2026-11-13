# Security and privacy — v0.2

**The repository is public. Cases are private by default.** Never include identifying data of living people, recent registrations, account details, protected IDs, addresses, family photos, scans, GEDCOM files or third-party credentials in the repository, issues, branches or screenshots.

## Default processing

- UI is served solely from `127.0.0.1` using a local Python process; no remote hosting or database.
- Local case JSON is held in browser memory; sent to the loopback service on explicit local API operations; not written by the server.
- No telemetry, analytics, cookies, CDN, auto-search, emails, or autonomous model execution.
- Request body max 512KB; content-type JSON only, Host and Origin gates; CSP, no-store, no-referrer, X-Frame-Options, safe DOM text insertion and HTTPS-only external links.
- **Not a hardened multi-user app:** anyone with access to the user's browser/computer can still see their currently open case. Do not expose the port to the network, forward it over a tunnel, or deploy this server on a remote host without a complete threat model and authentication.
- `.gitignore` reduces accidents but is not a privacy boundary. Store real family data outside the public source tree and use encrypted devices/backup.

## AI model guardrails

- Default agent uses **offline deterministic tools** and no LLM, so no billable requests or accidental external transfers.
- Optional model client speaks a read-only Chat Completions tool protocol; it cannot browse official archives, send emails or mutate case data.
- Model responses are unverified drafts. Automated audit validates structure only. Model tool calls are bounded and rejected when unknown or malformed.
- Only localhost HTTP or HTTPS endpoints are supported. External HTTPS model usage needs `--allow-remote`, synthetic cases, and per-request consent. Private or public-historical cases are rejected from external model transmission even if a user checks consent.
- Server-side API key comes from `KINSHIP_API_KEY` environment variable; never include secrets in case JSON or user prompts.
- Local LLMs might themselves run other logging/telemetry; check their own data handling separately. No real model endpoint was exercised in the v0.2 test suite.

## Rights and access

- Archive records are copyrighted, restricted or subject to catalog licenses independently of the GitHub repos describing them.
- Do not scrape external services, bypass access controls, recreate or redistribute restricted indexes. Each new connector needs terms, authorization, rate-limit and privacy review.
- Public historical exports still need manual review for living relatives, protected archival metadata and source reproduction rights.

## Known limits

- Imported JSON and model responses can contain sensitive data; the UI does not sanitize documents for public sharing.
- The interface intentionally has no persistence, upload-to-cloud, cross-device sync or roles.
- API JSON from the local server is not encrypted in transit but is bound to localhost; do not route it over untrusted networks.
- Redirecting model endpoints is rejected; arbitrary requests to archives are not permitted.
