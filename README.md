# Global Kinship Research

**A local-first genealogy research workbench: explore a case, inspect sources, build region-specific research plans, and have an optional AI model call read-only evidence tools.**

**[Product backlog and unfinished work](docs/PRODUCT_BACKLOG.md)** — single maintained list for v0.4 real ancestor search, future UX/visual improvements, regional expansion, interoperability, AI, security and tests. Current priority: verify the first real archive provider and expand authorized historical search. The local-case search remains separate from the new external-search pilot.

> **Status: v0.4 experimental archive-search pilot on the v0.3 core.** **Explore case** searches only supplied data. The separate **Search archives** page can make consented, read-only Library of Congress JSON API requests for catalog metadata. Live endpoint success has **not yet been verified** in the development environment; other region archives are still manual leads. Catalog results are not identified relatives.

## What works

| Capability | Status | Limits |
| --- | --- | --- |
| Browser workbench | **Implemented** | Accessible from `127.0.0.1`; no cloud hosting, accounts or database |
| Search people / artifacts / claims | **Implemented** | Local case only, text search and safe Latin accent folding |
| Library of Congress external catalog pilot | **Offline-tested; live acceptance pending** | Explicit HTTPS/consent, metadata-only, fixed provider, not a global ancestor registry |
| Source inspector / proof-group links | **Implemented** | Shows citations, copied source groups, claim links, verbatim names |
| Regional source directory | **11 profiles** | Ex-USSR, Vietnam, Korea, China, Japan, Taiwan, Philippines, Thailand, Indonesia, Malaysia, India; links must be checked at use time |
| Research assistant | **Implemented** | Offline route by default; optional local OpenAI-compatible model with real read-only tool calls |
| Optional external AI endpoint | **Opt-in only** | HTTPS, synthetic test cases only, explicit server and per-request consent; never real private cases |
| Evidence integrity auditor | **Implemented** | Distinguishes duplicated records, missing proof, bad links; cannot certify historical truth |
| ex-USSR register importer | **Implemented** | Conservative CSV conversion from upstream templates, no ambiguous relationship mapping |
| GEDCOM 5.5.1 import | **Bounded beta** | UTF-8/ASCII, 512 KB cap, safe subset; parent-child claims remain hypotheses, no auto merging |
| One-generation family connections | **Implemented** | Shows supplied relationships, statuses and source groups; not a verified family tree |
| Additional national archives, OCR, GEDCOM export/7.0, authentication | **Not implemented** | Further source permissions and security review required; no global search coverage |

### Screens and workflow

- **Explore case** — open a local JSON case or GEDCOM 5.5.1 file, search people or citations, inspect evidence without losing original spelling. The family connections map shows one generation around a selected person, with warnings and source groups.
- **Search archives** — explicit read-only Library of Congress query, source links, access warnings, and manual addition as **unverified lead** to browser-held case. [Pilot limits](docs/ARCHIVE_PILOT.md).
- **Archive directory** — country and historical-region filtering, institution links and access notices. Portal links are **not** live connectors.
- **Research assistant** — region-aware planning and tool trace; optional model uses **whitelisted** operations to search the *local* case and audit sources.
- **Evidence review** — audit failures, claims and independent source groups. No claim is ever automatically approved.

The interface contains **synthetic sample records only**, until you open a private local file. GEDCOM imports are handled only by the 127.0.0.1 server, then held in browser memory; source files are not persisted by the app. No automatic telemetry, cookies, external fonts, JavaScript CDNs, archive scraping or uploaded data storage.

## Start with **no PowerShell** (Windows)

1. In GitHub, open **Code → Download ZIP** and extract the repository on your computer.
2. If Python 3.10+ is installed, double-click **`scripts/Launch-Global-Kinship.cmd`**.
3. The browser opens at `http://127.0.0.1:8765`. Keep the launcher window open while using the workbench.

No Python packages need to be downloaded for the default workbench. The `Launch-Global-Kinship.cmd` file is plain text you can inspect before running. It is optional; developers can use the CLI directly.

On macOS/Linux or an existing Python installation:

```bash
PYTHONPATH=src python -m kinship serve --port 8765
```

### Research CLI

```bash
PYTHONPATH=src python -m kinship profiles
PYTHONPATH=src python -m kinship sources --region vietnam
PYTHONPATH=src python -m kinship plan korea --name "김하늘"
PYTHONPATH=src python -m kinship search examples/synthetic-vietnam-korea-case.json "Nguyen Van An"
PYTHONPATH=src python -m kinship audit examples/synthetic-vietnam-korea-case.json
PYTHONPATH=src python -m kinship agent examples/synthetic-vietnam-korea-case.json --region vietnam --question "What would count as independent evidence?"
PYTHONPATH=src python -m kinship graph examples/synthetic-vietnam-korea-case.json
PYTHONPATH=src python -m kinship import-gedcom examples/synthetic-gedcom-551.ged --region vietnam --case-id demo --question "Review the family record" --out private/demo.json
```

This agent command runs a **deterministic offline guide** unless `--model` is supplied. No LLM is billed or contacted by default.

### Optional local AI agent

An OpenAI-compatible local model server (e.g. a locally installed Ollama instance, if it exposes `/v1/chat/completions` with function calling) can power real tool-use turns:

```bash
PYTHONPATH=src python -m kinship serve --model "YOUR_LOCAL_MODEL_NAME" --endpoint http://127.0.0.1:11434/v1/chat/completions
```

Model compatibility varies by engine/model. Tool calls are validated against a read-only allowlist; unsupported calls fail closed. Real model service was **not** available during local validation, so model integration was tested with a simulated client, not claimed production-proven.

External models require `--allow-remote` on the server and a per-request consent checkbox, and are restricted to **synthetic cases**. Do not transmit living-person information or restricted records to external AI. API credentials, if needed, come from the `KINSHIP_API_KEY` environment variable and are never stored in a case file.

### Convert Ex-USSR project registers

If you have registers produced with the pinned [ex-USSR Kinship Research](https://github.com/DenisSergeevitch/ex-ussr-kinship-research) templates:

```bash
PYTHONPATH=src python -m kinship import-ex-ussr private/source-registers --case-id my-private-case --question "Which records exist?" --out private/my-private-case.json
```

The importer preserves original CSV fields, name text and independence groups; it refuses ambiguous IDs/statuses instead of guessing. **Never commit the imported JSON**, even if it contains only historical family data. Template format and mapping limits: [docs/EX_USSR_IMPORT.md](docs/EX_USSR_IMPORT.md).

### GEDCOM 5.5.1 (local import; no cloud or automatic family verification)

Use the **Open GEDCOM** control next to **Open case JSON** in the local workbench. It converts a supported UTF-8 5.5.1 family file into this project's private case model. Family links are **hypotheses** and source pointers are leads; no archive is searched, and no original is authenticated. Invalid pointers, cycles, unsupported charsets or versions are rejected. Downloadable/exportable GEDCOM output is **not yet supported**.

See [GEDCOM import limits](docs/GEDCOM_551.md). Do not commit imported files or case JSON to GitHub.

## Archive pilot limits and tests

The first external provider uses the documented Library of Congress JSON API (no API key). This code rate-limits calls to one every five seconds, requires explicit consent and keeps catalog leads in memory unless a user downloads the private case JSON. Live API compatibility and international archive coverage are not yet verified. See [ARCHIVE_PILOT](docs/ARCHIVE_PILOT.md) and [v0.4 QA](docs/QA_V04_PILOT.md).

## Verification

Run the offline release gate from the repository root (requires Python 3.10+ and Node.js):

```bash
python scripts/verify_release.py
python scripts/verify_release.py --browser             # optional Chromium component smoke
python scripts/browser_smoke_online.py                 # optional synthetic archive transport UI smoke
python scripts/verify_release.py --browser --browser-e2e  # UI + real local API via test bridge
```

The gate runs all local Python tests, compiles Python, checks all JavaScript files with Node, and starts a **real loopback HTTP server** for a synthetic GEDCOM import/search/graph/agent/API security smoke. It returns a nonzero exit code and a machine-readable JSON summary if any required check fails. No GitHub Actions, paid CI, archive access or AI keys are needed. The optional browser component test uses a simulated graph API and is **not** a complete live-browser end-to-end test.

> **v0.3 release verification (2026-11-16):** all 90 Python tests, JavaScript checks, 10 live localhost API steps, Chromium family-component smoke and desktop/mobile browser flow through a test transport bridge passed. Direct Chromium-to-localhost navigation was blocked by the hosted test environment. Windows launcher, real AI endpoints and external archive access remain untested; see [docs/QA.md](docs/QA.md).

For targeted development checks:

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
node --check src/kinship/static/app.js
node --check src/kinship/static/family.js
```

All tests use synthetic cases. Real Windows launch, external AI calls, real archive searching and third-party GEDCOM interoperability require separate verification. **No GitHub Actions were added.**

## Regional archive connector readiness and source comparison

See [regional connector access matrix](docs/REGIONAL_ARCHIVE_CONNECTORS.md) for Korea (issued API key), Shanghai Library (developer key), Vietnam (human-facing search, public third-party API not established), ex-USSR (custodian-specific permissions), and the Library of Congress live-validation gap.

The independent `kinship.matching.compare_catalog_lead` helper produces **review-only signals** from a normalized catalog lead and a supplied local person. It does not merge identities, create relationships, assume birth dates, or inflate independent source counts. **It is not yet wired into the web UI or AI agent.** Eight offline unit tests pass; live regional connectors remain blocked on access/verification.

## Architecture and guardrails

Read [ARCHITECTURE](docs/ARCHITECTURE.md), [SECURITY & PRIVACY](docs/SECURITY_PRIVACY.md), [PROVENANCE](docs/PROVENANCE.md), and [ROADMAP](docs/ROADMAP.md).

The original ex-USSR project is a **pinned Git submodule**, not copied into our MIT core. Its own license and history remain intact. To obtain its files from a Git clone: `git submodule update --init --recursive`. The importer itself works with CSV files you already have and does not require the submodule to be checked out.

This project’s original code is MIT-licensed. Other family-tree apps are **candidates for evaluation**, not silently incorporated. No real family records, protected archival scans, model keys or third-party licensed databases belong in this public repository.
