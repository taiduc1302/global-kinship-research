# Security and privacy constraints

**Default:** perform research locally and keep family data out of public git, cloud agents, remote issue trackers and model inputs unless the user explicitly approves a suitable private environment.

- No real personal or medical data in test fixtures. Synthetic names are fictitious and cannot stand for known individuals.
- Never publish a living/unknown person's case as `public_historical`; this is checked by the audit.
- Even deceased ancestors' recent records may include living relatives. Review individually.
- No real archival PDFs, family photos, GEDCOM, passport/ID cards, contact details, registry numbers or account credentials in source repository.
- `visibility` and `.gitignore` alone do **not** guarantee privacy. Never include real cases in project zip / GitHub issue or commit.
- Preserve original script, literal transcription, provenance and correction notes. Do not replace them with model guesses.
- Archive websites may forbid bulk download or restrict access; the program makes **zero network calls** and has no hidden analytics.
- When an official database requires authentication or legal proof of family relationship, follow its process and do not bypass it.
- Before adding third-party code, scan dependencies and licenses; the starter has **no runtime third-party dependencies**.
- Avoid exposing private source paths in reports destined for a public audience.
