# Global Kinship Research

**A local-first genealogy research workbench: explore a case, inspect sources, build region-specific research plans, and have an optional AI model call read-only evidence tools.**

> **Status: v0.3 local prototype.** The app searches only documents and person records you supply in its case JSON. It **does not** search external archive records, identify relatives automatically, prove parentage, or contact archives. Official external websites are **research leads**, not verified matches.

## What works

| Capability | Status | Limits |
| --- | --- | --- |
| Browser workbench | **Implemented** | Accessible from `127.0.0.1`; no cloud hosting, accounts or database |
| Search people / artifacts / claims | **Implemented** | Local case only, text search and safe Latin accent folding |
| Source inspector / proof-group links | **Implemented** | Shows citations, copied source groups, claim links, verbatim names |
| Regional source directory | **11 profiles** | Ex-USSR, Vietnam, Korea, China, Japan, Taiwan, Philippines, Thailand, Indonesia, Malaysia, India; links must be checked at use time |
| Research assistant | **Implemented** | Offline route by default; optional local OpenAI-compatible model with real read-only tool calls |
| Optional external AI endpoint | **Opt-in only** | HTTPS, synthetic test cases only, explicit server and per-request consent; never real private cases |
| Evidence integrity auditor | **Implemented** | Distinguishes duplicated records, missing proof, bad links; cannot certify historical truth |
| ex-USSR register importer | **Implemented** | Conservative CSV conversion from upstream templates, no ambiguous relationship mapping |
| GEDCOM 5.5.1 import | **Bounded beta** | UTF-8/ASCII, 512 KB cap, safe subset; parent-child claims remain hypotheses, no auto merging |
| One-generation family connections | **Implemented** | Shows supplied relationships, statuses and source groups; not a verified family tree |
| Live government archive searching, automatic OCR, GEDCOM export/7.0, authentication | **Not implemented** | Require legal/technical review before deployment |

### Screens and workflow

- **Explore case** — open a local JSON case or GEDCOM 5.5.1 file, search people or citations, inspect evidence without losing original spelling. The family connections map shows one generation around a selected person, with warnings and source groups.
- **Archive directory** — country and historical-region filtering, institution links and access notices.
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

## Verification

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
node --check src/kinship/static/app.js
python scripts/browser_smoke_family.py      # optional: Playwright + Chromium, mocked graph API
node --check src/kinship/static/family.js
```

Tests use the standard library, a fake model client and synthetic cases. The browser interface was also inspected at desktop and mobile sizes; see [docs/QA.md](docs/QA.md). **No GitHub Actions were added.**

## Architecture and guardrails

Read [ARCHITECTURE](docs/ARCHITECTURE.md), [SECURITY & PRIVACY](docs/SECURITY_PRIVACY.md), [PROVENANCE](docs/PROVENANCE.md), and [ROADMAP](docs/ROADMAP.md).

The original ex-USSR project is a **pinned Git submodule**, not copied into our MIT core. Its own license and history remain intact. To obtain its files from a Git clone: `git submodule update --init --recursive`. The importer itself works with CSV files you already have and does not require the submodule to be checked out.

This project’s original code is MIT-licensed. Other family-tree apps are **candidates for evaluation**, not silently incorporated. No real family records, protected archival scans, model keys or third-party licensed databases belong in this public repository.
