# v0.2 quality report — 2026-11-12

## v0.3 incremental QA scope

The GEDCOM importer and relationship graph were exercised with synthetic files: non-Latin names, duplicate pointers, cycles, charset/version failures, missing sources, privacy, absent names, oversized input, and dependent source citations. The new `family.js` also passed JavaScript parser validation. Previous v0.2 browser screenshots should **not** be represented as v0.3 screenshots; physical Windows and real-world files still require validation.

## Automated tests

- Python standard-library `unittest` suite: evidence audit, region guides, identity-safe name search, local case search, strict source independence, Ex-USSR CSV importer, model tool dispatcher with fake client, remote-privacy restrictions, loopback web API, content type, Host/Origin checks, static UI and CSP.
- JavaScript syntax validation with `node --check`.
- No paid GitHub Actions; tests run in a local Linux container.

## Interactive browser smoke

Tested Chromium at 1400×930 desktop and 390×844 mobile viewports using Playwright with an intercepted HTTP transport to the running local server (direct Chromium navigation was blocked by the testing environment). The browser executed the actual shipped HTML, CSS and JavaScript; API calls were forwarded to the local Python server.

Verified interactions:

1. Case initialized with 3 fictional people, 3 records, 2 claims, 2 independent source groups.
2. Diacritic-insensitive text search for `Nguyen Van An` returns the supplied fictional person.
3. Selecting the person opens its source-backed detail and relationships.
4. Changing the archive region to China shows the Shanghai Library genealogy lead.
5. Running the assistant in default mode generates an offline research route, explicitly not a real archive search.
6. Evidence review shows the structural audit result.
7. No JavaScript page errors. No horizontal page overflow at 390px.

**Limitations:** no physical Windows launcher test; no production archive queries; no network AI model with real credentials; not a professional accessibility certification; HTTP proxy interception differs from full local-browser transport. Require further testing before public hosting or private-case deployment.

## Targeted re-check — 2026-11-14 (Linux/container, no Windows)

These tests are narrower than a full v0.3 regression; avoid presenting them as an all-green release gate.

- Re-ran the original v0.1 Python suite from its source archive: **31/31 passed**.
- Reproduced a Python `RecursionError` for a synthetic 1,200-person parent chain; replaced recursion with iterative DFS. A 1,600-person chain then audited successfully and a synthetic cycle was correctly rejected. A persistent regression is included in `tests/test_audit.py`.
- Fuzzed the **v0.1 baseline** auditor against **10,000 mutated synthetic cases** (random invalid field values/types): zero unhandled exceptions. This is input robustness sampling, not a formal security proof or a complete test of v0.3.

- Reconstructed and byte-verified the **exact current feature-branch** `audit.py` (`56aa7ef3`), `gedcom.py` (`ab34d197`), `graph.py` (`40ff580e`), and `tests/test_gedcom.py` (`504d3e26`) against GitHub Git blob SHAs. Running the original v0.1 core tests plus the v0.3 GEDCOM tests together yielded **44/44 passing** (31 baseline + 13 GEDCOM). This is a **partial-module regression**, not the full v0.2 web/agent/legacy suite.
- Mutated the actual v0.3 GEDCOM importer **5,000 times** with randomly modified synthetic GEDCOM strings: 0 unhandled exceptions (invalid variants were rejected with `ValueError`).
- Imported a synthetic **2,000-person, 1,999-family** chain (160,470 UTF-8 bytes) using the exact v0.3 importer and iterative auditor; the generated graph contained 1,999 relations without cycle false positives or recursion failures.
- Confirmed that the checked Chromium component script's Git blob SHA matches GitHub `family.js` (sha `76b3083cb18e739eea91c71e7da385802f9cb0e1`). `node --check` passed.
- Ran a **component-level** Chromium smoke using a simulated `/api/graph` response, at **1440×900** and **390×844**. Vietnamese, Korean and Cyrillic name rendering, family navigation, hypothetical links, claim IDs and independent-source group labels worked without uncaught JavaScript errors.
- Reproduced a race where an old family graph request replaced a newer case in the UI; fixed with a load-generation gate and verified reversed response completion order now keeps the current case.
- Added an **optional** reproducible `python scripts/browser_smoke_family.py` for component smoke (requires Playwright and Chromium, independent of paid GitHub Actions).
- Separately executed the byte-identical v0.3 `src/kinship/graph.py` (Git blob `40ff580e79e48fcd6096e9d4a3522582faad7b2a`) against the synthetic core fixture: verified 3 distinct people, 1 relationship, 2 independent source groups, no external search, and rejection of false corroboration from duplicate scans.
- Added new `tests/test_web.py` cases for the GEDCOM-import HTTP endpoint, graph roundtrip and rejection of an unsupported GEDCOM version. These new HTTP tests **have not yet run together with the full v0.3 suite** in this environment.
- Inspected the highest-risk v0.3 files and found no obvious hard-coded API keys/private keys in that selected set. This is **not** a comprehensive security assessment. Confirmed no GitHub Actions workflow files and original ex-USSR submodule pin is retained.

### Still pending, and why

- **Full merged v0.2 + v0.3 Python unittest suite:** the connected GitHub source is readable remotely, but the entire exact feature branch was not available as a mounted local checkout in this container; individual component tests and the v0.1 archive are not equivalent to full regression.
- **Full end-to-end browser test against actual v0.3 loopback API and real HTML/CSS:** browser navigation to a loopback listener was blocked by the current test environment; component testing used a mocked `fetch`.
- **Real local AI model**, **legally authorized archive API**, **GEDCOM files exported by actual third-party apps**, and **Windows double-click launcher** remain separate integration/compatibility gates.
- Keep PR #1 as **draft** until the full suite and end-to-end integration gates pass. Never merge by substituting component tests for those checks. No user-family data was used.

## 2026-11-15 — Continued hardening and repeatable release gate

- Inspected latest PR #1 head through the connected GitHub API (no checkout of the full head available through local Git DNS).
- Found a privacy bypass: setting `visibility: synthetic` on a real local case used to make it eligible for external model calls. Restricted the agent to **the exact bundled demo JSON** and per-request consent, and added negative tests with altered names and living-person flags. The question text is also sent externally when an external model is explicitly enabled.
- Added rejection of malformed tool-call objects from model replies before dispatch, plus a test with a non-object `tool_calls` entry.
- Created `scripts/verify_release.py`: offline standard-library runner for combined Python unittest, Python compilation, Node.js JavaScript syntax, a **real local loopback API** synthetic GEDCOM/search/graph/agent smoke, and optional Chromium component check (`--browser`). No GitHub Actions or network archive requests.
- **Verified release-runner behavior on the available v0.1 local archive**: Python baseline 31/31 passed; the runner returned `blocked` because v0.1 does not contain v0.3 static JS files or the HTTP server. This is the correct fail-closed behavior, **not** a passing v0.3 release gate.
- New AI privacy/tool-call unit tests are committed but have **not been executed against the full exact v0.3 checkout** in this environment. The combined v0.2+v0.3 regression and genuine full-browser end-to-end tests therefore remain open.
- On non-Windows systems with the full Git checkout, the local repeatable check is `python scripts/verify_release.py --browser`. Requires Node.js; optional browser checks require Playwright and Chromium.

**Release decision:** PR #1 stays draft; do not merge until the full exact-head suite and actual loopback-to-browser integration are run and pass. This note does not claim a tested Windows launcher, real AI model, archival data access, or public deployment security.

### Additional private-output guardrail

- Found that CLI `--out` values for GEDCOM import, Ex-USSR registers and reports could target ordinary public-repository folders, creating an accidental-commit risk. Added `_private_output_path` guard: outputs within a source checkout must resolve under git-ignored `private/` or `cases/`, or be stored outside the checkout.
- Reports now refuse to overwrite an existing file. Added `tests/test_cli.py` negative tests for public-folder paths and overwrite preservation.
- Verified the path-selection algorithm in an isolated temporary project: public documentation folder blocked, `private/` and `cases/` accepted, outside path accepted. **The full exact-branch CLI tests are still pending**.

## Final v0.3 release regression — 2026-11-16

**Baseline:** Exact PR #1 Git tree at commit `24734dd9151c743658aa71eca5194349b3be2a04` was reconstructed from the connected GitHub source. All **59 regular files** were checked against their Git blob SHAs. The reconstructed Git tree, including the pinned Ex-USSR submodule gitlink, matched remote tree `3c9b494425f93bc1330bca183581f252b98d3738` exactly.

- `python scripts/verify_release.py --browser` **PASSED** on reconstructed v0.3: 90/90 Python unit/HTTP/CLI/agent/GEDCOM tests; Python compilation; JavaScript syntax; 10 live loopback API scenarios; Chromium family-component smoke.
- Added `scripts/browser_e2e_bridge.py`, tested against the **real local Python Workbench API** via browser fetch transport interception. It uses the shipped HTML/CSS/JS and synthetic files; desktop **1440×900** and mobile **390×844** both passed: search, record inspection, China archives, offline agent, evidence audit, GEDCOM import, family tree, reset, zero JS page errors, zero page overflow.
- Added `--browser-e2e` option to the release verifier and ran `python scripts/verify_release.py --browser --browser-e2e`: **PASSED all five check groups**, including both viewports. This was run on the locally prepared feature tree immediately before the two test-only scripts were pushed to the feature branch.
- GitHub Actions were not used. No live archive queries, personal GEDCOMs, external LLMs or credentials were used.

**Environment caveat:** Hosted Chromium blocks direct localhost navigation, so UI requests were bridged to the *actual* Python loopback API using Python's urllib. This tests UI/API behavior but **not direct Chromium-to-localhost network transport**. Double-click Windows launcher, installed real LLM, actual third-party GEDCOM compatibility, live archive API and specialist security/accessibility audits are untested and remain post-merge limitations. A successful automated release check is not genealogical evidence validation or authorization for public hosting of family records.

**Decision:** The non-Windows release gates for the local v0.3 feature are complete; merge of the reviewed PR may proceed, with the above limitations prominently documented.
