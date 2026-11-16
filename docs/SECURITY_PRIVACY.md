# Security and privacy — v0.3

**The repository is public. Cases are private by default.** Never include identifying data of living people, recent registrations, account details, protected IDs, addresses, family photos, scans, GEDCOM files or third-party credentials in the repository, issues, branches or screenshots.

## GEDCOM import guardrails

Only UTF-8/ASCII GEDCOM 5.5.1 local text import is enabled. The server stores no GEDCOM uploads. The resulting case remains private, and all imported family relationships remain `hypothesis`. Dates are not used to assume death. Addresses, contact data and media are not copied into the case. Unsupported GEDCOM and invalid pointers fail closed. Browser transfer is loopback-only, not an external upload. Do not place real GEDCOM or case files in this public repository.

## Default processing

- UI is served solely from `127.0.0.1` using a local Python process; no remote hosting or database.
- Local case JSON is held in browser memory; sent to the loopback service on explicit local API operations; not written by the server.
- No telemetry, analytics, cookies, CDN, auto-search, emails, or autonomous model execution.
- GEDCOM text max 512,000 UTF-8 bytes, browser case file max 512,000 bytes, and JSON HTTP request body max 1,200,000 bytes (for escaped GEDCOM text); content-type JSON only, Host and Origin gates; CSP, no-store, no-referrer, X-Frame-Options, safe DOM text insertion and HTTPS-only external links.
- **Not a hardened multi-user app:** anyone with access to the user's browser/computer can still see their currently open case. Do not expose the port to the network, forward it over a tunnel, or deploy this server on a remote host without a complete threat model and authentication.
- `.gitignore` reduces accidents but is not a privacy boundary. Store real family data outside the public source tree and use encrypted devices/backup.

## CLI export placement

- `import-gedcom`, `import-ex-ussr` and `report --out` reject output paths **inside this public source checkout** unless they resolve under the git-ignored `private/` or `cases/` directories. Outputs outside the repository remain allowed.
- Imported cases and generated reports are never silently overwritten. Do not move these files into public example/documentation folders, and keep local backups encrypted.
- This path guard reduces accidental Git commits, but it is not OS-level sandboxing or a substitute for filesystem permissions and human review. Standard output can still be redirected by the calling shell.

## AI model guardrails

- Default agent uses **offline deterministic tools** and no LLM, so no billable requests or accidental external transfers.
- Optional model client speaks a read-only Chat Completions tool protocol; it cannot browse official archives, send emails or mutate case data.
- Model responses are unverified drafts. Automated audit validates structure only. Model tool calls are bounded and rejected when unknown or malformed.
- Only localhost HTTP or HTTPS endpoints are supported. External HTTPS model usage needs `--allow-remote`, an **unmodified copy of the bundled fictional demo case** (not merely a user-set `visibility: synthetic` label), and explicit per-request consent. Private, historical and altered demo cases are rejected before any model request. **The research question is also transmitted**; do not include private names or sensitive details in a remote-model question. The remote provider's data policies still apply.
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
