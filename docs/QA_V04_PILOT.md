# v0.4 partial pilot QA — 2026-11-17

**Implemented in code (pilot, not a full v0.4 release):** optional Library of Congress JSON metadata search, separated from local search, explicit network-consent gate, strict fixed-host adapter, bounded query/pagination/rate/timeout/response, error states, source-first cards, and an unverified-only manual import to local case JSON. No automatic familial relationship decisions or cloud storage.

**Test results (synthetic/no external network):**

- Previous 90-test baseline passed before edits.
- Complete current Python unittest suite: **102/102 passed** (adds 12 archive contract/security/API tests).
- JavaScript syntax checks passed for `app.js`, `family.js` and `online.js`.
- Full v0.3 baseline local HTTP smoke passed (10/10 existing scenarios).
- Chromium browser smoke on **1440x900** and **390x844** passed with the shipped HTML, CSS and scripts, and the actual local Python API. Only the **external archive HTTP transport** was replaced by synthetic responses; loopback navigation itself is bridged owing to hosted browser policy. Confirmed user consent before network call, result links, pagination, error/no-result differentiation, a new unverified artifact without new claims, and no JS errors or horizontal overflow.
- GitHub Actions not used. No real family names, restricted records, passwords or provider API credentials committed.

**Not verified:** successful request to the **live** Library of Congress API (development DNS blocked), per-collection response variations from real endpoints, third-party real GEDCOMs, real local LLM tool calling, Windows installer/launcher compatibility, cross-region live search, and accessibility/security audit.

**Release decision:** safe to merge a labelled experimental pilot after full offline checks; **do not mark GKR-S04/S11 or v0.4 release complete until a real provider response is validated**, and do not claim search coverage across Asian regions.

## PR #3 combined regression — 2026-11-22

- Reconstructed the exact PR #3 tree from individually SHA-verified GitHub blobs on a local Linux checkout, using the prior v0.3 source archive as the verified base.
- `PYTHONPATH=src python -m unittest discover -s tests -q`: **110/110 tests passed** (including eight new matching tests).
- `python scripts/verify_release.py --browser`: **PASS** — all 110 Python tests, Python compilation, three JS syntax checks, 10 live local HTTP smoke steps, Chromium family component.
- `python scripts/browser_smoke_online.py`: **PASS** at 1440×900 and 390×844, checking consent, results, pagination, empty results and 429. External archive JSON was simulated: **this is not confirmation of a live LoC response**.
- The exact current `scripts/verify_release.py` supports `--browser`, not `--browser-e2e`; this run does not claim the latter option. Source authenticity, remote service response, Windows and real-model calls remain untested.
- Pure matching module remains **review-only and not yet connected to the UI**. No automatic family links or approval.
- PR #3 may be merged as a tested code + documentation increment; do not mark regional live API access complete.
