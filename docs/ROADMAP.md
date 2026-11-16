# Development roadmap and exit gates

Owner: Global Kinship Research maintainers. Updated: 2026-11-12. **No issue or agent may approve genealogy evidence or archive access on behalf of a researcher.**

## v0.1 — Evidence core (complete)

- [x] Pinned original Ex-USSR project as attributed Git submodule, no silent code copying.
- [x] Separate source artifacts, claims, people and independence groups.
- [x] Local CLI audit/report and synthetic fixture.
- [x] Three initial research guides: Ex-USSR, Vietnam, Korea.

## v0.2 — Integrated local workbench (implemented; pending user test on Windows)

- [x] Read-only AI tool dispatcher with 8-turn/20-tool limits and model transport opt-in.
- [x] Offline guide mode and optional localhost OpenAI-compatible chat-completions function calling.
- [x] Strict privacy gate for external model: synthetic only, explicit opt-in.
- [x] Search within local case and review people, records and claims.
- [x] Responsive static browser UI served on localhost with upload/reset/demo, research assistant, sources and audit views.
- [x] Expand country profiles to 11: Ex-USSR, Vietnam, Korea, China, Japan, Taiwan, Philippines, Thailand, Indonesia, Malaysia, India.
- [x] Keep official archive leads separately labeled **manual-only** and **not searched**.
- [x] Conservative Ex-USSR CSV importer retaining raw columns, negative search logs and provenance.
- [x] Extend Python unit/HTTP/agent and browser-smoke tests using synthetic records.
- [ ] Run double-click Windows launcher on a real Windows workstation (not covered by Linux container).
- [ ] Validate real local Ollama tool calls with selected model (fake client covered now; no live model endpoint was used).

**v0.2 exit gate:** local Python suite passes, desktop/mobile browser interaction passes, no private data in repo, no production claim of live archive searching, no mandatory GitHub Actions.

## v0.3 — GEDCOM import and local relationship explorer (implemented; Windows verification pending)

- [x] Add bounded UTF-8 GEDCOM 5.5.1 **import** with event-level sources and original ID traceability.
- [x] Keep imported family edges at `hypothesis` and group citations by original GEDCOM source pointer.
- [x] Add read-only relation graph for CLI, agent and local browser; do not infer biological parentage.
- [x] Add browser GEDCOM picker and one-generation responsive family-connections view.
- [x] Add synthetic regression tests for Unicode names, broken pointers, cycles, duplicate source pages, privacy and unsupported format versions.
- [ ] Run on physical Windows workstation and check imported output with independently validated GEDCOM samples.

## Planned — Real source-aware research connectors

- [ ] Review one legally authorized archive API/IIIF catalog per priority region; document ToS, authentication, fees, privacy and rate limits.
- [ ] Implement a read-only connector that records exact query, time, authority, result metadata and a reproducible source ID. **A web page link is not a query result.**
- [ ] Offline fixtures for pagination, duplicate images, conflicting records, partial results, downtime, permission failures and language variations.
- [ ] Consent gate before retrieving any potentially protected records and review of cross-border data transfers.
- [ ] Manual side-by-side original/transcription/translation/researcher correction view.
- [ ] Human-confirmed notes to convert leads to citations; never automatic match or approval.

## Planned — Family tree and interoperability

- [x] Bounded GEDCOM 5.5.1 import subset; source references retained with limitations.
- [ ] GEDCOM 5.5.1 export and broader GEDCOM 7 import/export with round-trip tests and source references.
- [x] Local read-only one-generation relationship explorer with provenance per claim.
- [ ] Complete multi-generation family visualization with contradictions and unknowns.
- [ ] Private encrypted persistence and backups after explicit threat model and authentication design.
- [ ] Review selected MIT/Apache 2.0 parts of Roots of Vietnam / FamilyRoots; preserve attributions and license notices.

## v0.5 — Region depth / production readiness

- [ ] Historical jurisdiction maps and date-aware archive custodians.
- [ ] Deeper country-specific family naming and calendar conversion reviews by specialists.
- [ ] Proper search coverage for Southeast Asia and migrations (not simply lists of countries).
- [ ] External security assessment, auth, audit logs, deletion and access control before hosting any real family cases.
- [ ] Full Windows/macOS/Linux packaging, backup/recovery and accessibility audits.

## Contribution workflow, without GitHub Actions

Run `PYTHONPATH=src python -m unittest discover -s tests -v` and optionally `node --check src/kinship/static/app.js`. For UI changes run a local browser smoke and note tested viewport sizes; include output, privacy impact and license changes in PR description. Never upload real cases into GitHub. If a test fails, no merge.
