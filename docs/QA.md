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
