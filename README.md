# Global Kinship Research

**Local-first, evidence-first genealogy research across historical borders.**

A small, testable Python research assistant and Agent Skill starter. It separates source records, interpretive claims, search plans, and case reports, with regional research profiles for **ex-USSR, Vietnam, and Korea**. This is **not** a live archive search service, automatic ancestor finder, commercial family tree service, or a tool that proves biological relationships.

## Status (v0.1)

| Capability | State |
| --- | --- |
| Local case JSON + evidence audit | Implemented; tested with synthetic cases |
| Independent-source group checks | Implemented; duplicate image is not a second witness |
| Local text/diacritic-safe name query variants | Implemented; no speculative identity matching |
| Ex-USSR research profile | Reference adapter; upstream pinned Git submodule |
| Vietnam historical research profile | Curated guide (manual links, no scraping) |
| Korea jokbo research profile | Curated guide (manual links, no scraping) |
| Draft offline archive research plans | Implemented; they are *not* search results |
| Local Markdown evidence packet | Implemented; fails closed on audit errors |
| Agent Skill for Codex/Claude | Installable package under `skills/` |
| GEDCOM import/export; OCR; live archive querying | **Not implemented**; planned with safety review |
| Web UI; multiuser authentication; hosted database | **Not implemented** |

## 2-minute local start

Requires Python 3.10+; no cloud accounts, credentials, network, or paid services.

```bash
python -m pip install -e .
kinship profiles
kinship profile vietnam
kinship plan vietnam --name "Nguyễn Văn An" --variant "Nguyen Van An"
kinship audit examples/synthetic-vietnam-korea-case.json
kinship report examples/synthetic-vietnam-korea-case.json --out reports/demo.md
```

If not installed, use `PYTHONPATH=src python -m kinship ...` on Linux/macOS, or `$env:PYTHONPATH='src'; python -m kinship ...` in Windows PowerShell.

Local tests require only the Python standard library:

```bash
python -m unittest discover -s tests -v
```

**Never commit real genealogy cases**: `cases/`, `private/`, `data/`, and `reports/` are ignored, but Git ignores are not a privacy guarantee. Keep real cases in encrypted private storage outside this public repository. Do not add scans, GEDCOMs, birth certificates or personally identifying details to issues, PRs, or prompts without reviewing their privacy and sharing permissions.

## Architectural principles

1. **Evidence before conclusions** — every claim must cite traceable artifacts and distinguish dependent copies from independent records.
2. **Original scripts preserved** — do not replace Hán-Nôm, Hangul, Hanja, Cyrillic or other historic spellings with guessed romanizations.
3. **Jurisdiction as of event date** — do not route a 19th-century event based solely on modern national borders.
4. **Local-first by default** — no invisible scraping, uploading, or messaging; external archive access must be explicitly requested and lawful.
5. **Human approval** — a passing structural audit does not independently prove ancestry, authenticity or source reliability.
6. **Licenses isolated** — original repositories stay attributed, version-pinned, and individually licensed.

## Upstream Ex-USSR research skill

The original [DenisSergeevitch/ex-ussr-kinship-research](https://github.com/DenisSergeevitch/ex-ussr-kinship-research) is pinned as a Git submodule at `upstreams/ex-ussr-kinship-research`. Fetch it after cloning:

```bash
git submodule update --init --recursive
```

The submodule contains the **original upstream source and copyright**, and can be independently forked through GitHub. No upstream code was silently rewritten inside our core. Its skill is **not yet wired into this CLI**; v0.1 points researchers to its evidence and archival workflow. See [PROVENANCE.md](docs/PROVENANCE.md).

## Files

```text
src/kinship/       Python CLI, profile registry, source-independence auditor, report
skills/            Agent Skill instructions + regional reference guides
docs/              Architecture, provenance, privacy, contributor policy, backlog
examples/          Synthetic demonstration data ONLY
tests/             Stdlib unittest regression tests
upstreams/         Version-pinned original ex-USSR project (git submodule)
```

## Roadmap

See [docs/ROADMAP.md](docs/ROADMAP.md) for phases and acceptance tests. To publish this starter in your GitHub account, follow [docs/PUBLISH.md](docs/PUBLISH.md). Additional regions should arrive as plugins, not as copied databases. Contributions to Vietnam and Korea source guides are welcome, but cite authoritative archives and distinguish manual services from APIs.

## License and upstream rights

This repository's original code and docs use [MIT](LICENSE). Pinned upstream content retains its own MIT license and copyright. Other projects are *candidates*, **not included** in our codebase; see [docs/SOURCE_REVIEW.md](docs/SOURCE_REVIEW.md). A repository being public is not itself permission to reuse its content. Website content and archival records have separate terms and privacy restrictions.
