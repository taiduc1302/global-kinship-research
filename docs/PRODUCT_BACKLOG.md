# Product backlog — Global Kinship Research

**Canonical planning register.** Last reviewed: 2026-11-18. Baseline: v0.3 merged to main (PR #1, commit 9d1b76cf). Maintainers and agents should consult this file before proposing changes; update it when work is implemented, deferred, superseded or newly discovered. The version-level summary remains in [ROADMAP.md](ROADMAP.md); evidence of tests is in [QA.md](QA.md).

**Current product direction:** priority #1 is **real, legally authorized ancestor and historical-record search** (v0.4). Keep later visual and UX ideas here so they are not lost. Implement the minimum honest search UI now, not an unrelated redesign. **Explore case** still searches only local data. The new **Search archives** experimental page supports explicit user-consented Library of Congress catalog requests; the code passes synthetic tests, but a live response and global/regional coverage remain unverified. No claim of identified relatives is made.

## Maintenance conventions

- **Status:** IMPLEMENTED = present in main and locally regression-tested within stated scope; PARTIAL = working subset but missing important functionality or independent validation; NOT STARTED = no implementation in main; BLOCKED = dependent on access, permission, source terms, real hardware, or external service. Never conflate a draft plan or mock with implemented live search.
- **Priority:** P0 = next milestone / immediate user value; P1 = follow-up after first real connector; P2 = saved UX/visual/feature improvements; P3 = long-term / production. Priorities can be reordered in a reviewed PR, not silently forgotten.
- Every PR should name relevant **GKR IDs**, provide evidence, update status/acceptance criteria, list permissions and privacy effects, and link tests. New items receive durable IDs (do not renumber existing ones). A completed item should retain its entry with a commit or PR link.
- Only synthetic examples and fake names belong in this public repository. No real family records, living-person identifiers, login tokens, original private scans, or external model prompts from real research.

## A. What is already in v0.3 (do not rebuild)

| ID | Status | Delivered capability | Current limitation / evidence |
| --- | --- | --- | --- |
| GKR-D01 | IMPLEMENTED | Local-only Python workbench and browser UI | Only loopback service; no hosted search; src/kinship/web.py and static/ |
| GKR-D02 | IMPLEMENTED | Search within opened case: people, artifacts, claims | No outside records; src/kinship/research.py and /api/search |
| GKR-D03 | IMPLEMENTED | Separate persons, claims, source artifacts and independence groups; structural audit | Structural consistency is not proof of ancestry or record authenticity; src/kinship/audit.py |
| GKR-D04 | IMPLEMENTED | 11 historical/cultural research guides and curated portal leads | Region guides are **not archive search connectors**; profiles.py and catalog.py |
| GKR-D05 | IMPLEMENTED | Deterministic offline research route and read-only AI tool interface | Real local-model tool use remains unverified; agent.py |
| GKR-D06 | IMPLEMENTED | Ex-USSR CSV register import | Conservative subset; live upstream archive querying not included; legacy.py |
| GKR-D07 | PARTIAL | UTF-8 GEDCOM 5.5.1 subset import, 512 KB / 2,000-person limits | No GEDCOM 7, export, wide third-party compatibility, or custom event coverage; gedcom.py |
| GKR-D08 | PARTIAL | One-generation local relationship-claim map | Not a full multi-generation interactive tree, and imported links are hypotheses; graph.py and static/family.js |
| GKR-D09 | IMPLEMENTED | No-GitHub-Actions local release gate, 90-test Python baseline, live HTTP smoke and bridged Chromium UI | Not a physical Windows or real-archive/model certification; scripts/verify_release.py and QA.md |
| GKR-D10 | PARTIAL | Default private cases, restricted exports and hosted-model demo-only/consent rule | Not a secure multi-user system, persistence service or audited threat model; SECURITY_PRIVACY.md |

The shipped pilot UI has **Explore case (local)**, **Search archives (experimental Library of Congress)**, **Archive directory**, **Research assistant**, and **Evidence review**. A source directory card is only a link to an institution and must never be labelled a record match.

## B. P0 — v0.4: genuine online ancestor search (do first)

**Pilot progress (2026-11-18):** separated local and external search, added a consent-gated Library of Congress JSON adapter, source-first cards, bounded retrieval, local unverified-lead capture and JSON case export. [Provider/rights details](ARCHIVE_PILOT.md) and [synthetic test evidence](QA_V04_PILOT.md). **Not finished:** a confirmed live provider response, regional archive coverage, cross-provider dedupe and fuller record-provenance contracts. All postponed UX/visual ideas in section D remain tracked. v0.4 is **not** declared complete.

**Exit criterion for v0.4:** From a clearly labelled online search form, a researcher can submit a name and useful historical context to **at least one actually authorized, searchable public archival corpus**; receive genuine records or an honest no-result/error response; inspect the institution's persistent record URL and exact provenance; and save a lead *locally* only after human review. This must be demonstrated with a permitted real query plus offline deterministic tests. The list of 11 portal links alone does not satisfy this milestone. More archives will follow as permissions are established.

| ID | Priority / status | Work to implement | Acceptance / verification |
| --- | --- | --- | --- |
| GKR-S01 | P0 / IMPLEMENTED | **Distinguish Search my case vs Search historical records online** in navigation, headings, explanatory copy and zero-results state. | Searching an empty local case does not imply the internet was searched; online search is visibly separate and explicitly initiated. |
| GKR-S02 | P0 / PARTIAL | **Source feasibility and permissions matrix:** investigate candidate official catalogs/APIs (begin with Vietnam, China, Korea and Ex-USSR needs); capture operator, jurisdiction, actual searchable fields, API/docs, public vs restricted datasets, auth, terms, robots, reuse, request limits and fees. | One selected pilot corpus has documented permission/contract and reproducible query; unsupported portals are labelled manual-only or BLOCKED, not silently scraped. |
| GKR-S03 | P0 / PARTIAL | Define provider-neutral **ArchiveQuery / ArchiveRecord / SearchRun** contracts distinct from local person and genealogy claim models. | Every returned item contains provider ID, source record ID, title/name-as-written, record URL, institution, collection, historical place/date as recorded, query, search timestamp, access and license notes, extraction method, and original text where permitted. Missing fields remain unknown. |
| GKR-S04 | P0 / BLOCKED on real live-response validation | Build one real, **read-only, terms-compliant connector** using a published API or otherwise explicitly permitted access method; no bypass of login or anti-bot measures. | A controlled live test returns real source metadata and reproducible links; validates errors and absence of results; no fictitious hits or fabricated citations. |
| GKR-S05 | P0 / PARTIAL | Add an intentional online search form: original-script name, optional alternate name, country, historically applicable place, date range, record type and provider; default to no network call until user presses Search. | Empty/invalid inputs prevented; name and range encoded safely, controls clearly show external transmission/permissions; searches can be cancelled. |
| GKR-S06 | P0 / PARTIAL | Build clear search-result states: not searched, searching, results, **no results**, rate limited, unauthorized, provider unavailable, stale, partially completed. | Each state has meaningful user instructions, provider attribution and timestamp. No zero local matches shown as proof of zero historical records. |
| GKR-S07 | P0 / PARTIAL | Show **source-first results cards** with exact archival record links, original title/name and access restrictions; open a source before suggesting it belongs to a person. | Users can distinguish observed returned record, catalog-only lead and a candidate identity; no identity confidence presented as fact. Source IDs and page references are never invented. |
| GKR-S08 | P0 / PARTIAL | Preserve independent-source provenance and identify duplicate pages, mirror sites, alternative indexes and conflicting entries. | One original witness counts once regardless of copies; identity/relationship merging requires manual action; contradictory records remain visible. |
| GKR-S09 | P0 / PARTIAL | Allow **Review lead → Add to my private case** only with explicit user action, provenance and research notes; no automatic parent-child claims or public posting. | The source remains a candidate until reviewed; permissions and uncertainty survive import; no storage of restricted media without license. |
| GKR-S10 | P0 / PARTIAL | Read-only online search orchestration with bounded requests, timeout, retry/backoff, 429/rate limits, paging, partial provider failures and an honest per-source completion summary. | Fixed limits, no infinite loops/scraping; fixture tests cover empty, ambiguous, duplicated, paginated, malformed, forbidden and unavailable results. |
| GKR-S11 | P0 / BLOCKED on permitted live integration check | Add a **real-source integration test** separate from the offline CI-free suite, gated by access and provider stability. | Successful permitted query and exact provider ID are logged without publishing a real user's query; offline mock/contract tests always work without paid Actions. |
| GKR-S12 | P0 / PARTIAL | Specify query privacy and safety before external lookup (including potentially living relatives). | State which institution receives the query, collect only needed fields, no automatic cloud sync/telemetry, no tokens in browser; terms and living-person protections reviewed. |

**Do not advertise “search all Asian archives” until each named source is actually connected and independently checked.** Some institutions offer only a finding aid, research appointment, manual request or restricted access. Respect those boundaries.

### v0.4 delivery sequence / dependencies

1. **S01 + S02 + S03:** remove misleading UI expectation, pick the first legitimate search provider, freeze record/provenance contract.
2. **S04 + S10 + S11:** implement one real provider and test it against the actual API, including rejected/no-result conditions.
3. **S05 + S06 + S07:** integrate form, progress/errors, and verifiable records into the browser.
4. **S08 + S09 + S12:** safe review-to-case workflow, evidence independence and privacy.
5. Run existing release-check + new offline fixtures + controlled live query; update README claims, QA evidence and this backlog before declaring v0.4 complete.

### Regional connector discovery and cautious matching — 2026-11-18

- **GKR-R01 remains PARTIAL:** [REGIONAL_ARCHIVE_CONNECTORS.md](REGIONAL_ARCHIVE_CONNECTORS.md) now records concrete official API/docs, key requirements and next access gates for Korea, Shanghai Library (China), Vietnam, ex-USSR and LoC. This is a feasibility matrix, **not** live search for those regions.
- **GKR-R08 remains PARTIAL:** `src/kinship/matching.py` supplies deterministic *review-only* name-mention and source-independence signals, with eight unit tests. No identity confidence, person merge or kinship claim is created. Read-only local HTTP and case-person selection in archive result cards are now implemented; direct independent source authentication, date/place semantic comparisons and real providers are still open.
- **GKR-S04/S11 remain BLOCKED on a live LoC response:** official documentation is reachable, but automated `fo=json` requests were blocked by web-reader policy; the container's direct test failed DNS resolution. Do not mark this milestone complete from mock replies.
- Future UX/tree/OCR/GEDCOM work in section D/E is intentionally retained.

## C. P1 — expand useful research after pilot works

| ID | Status | Future task / rationale | Acceptance target |
| --- | --- | --- | --- |
| GKR-R01 | NOT STARTED | Add multiple independent, authorized region/provider adapters; maintain a **source support matrix** by country and collection, not merely a country flag. | Every provider has owner, contract, coverage, access, tests, limitations and supported query fields. |
| GKR-R02 | NOT STARTED | Multilingual search variants: literal Vietnamese diacritics, Cyrillic, Hangul/Hanja, Chinese characters, Japanese, Spanish colonial records; opt-in reversible transliterations. | Show exact vs transformed query sent; never infer ethnicity/identity from name or manufacture unverified Hanja/Nôm. |
| GKR-R03 | NOT STARTED | Historical jurisdictions and aliases of places at event dates, national/regional/local archive custodian mapping. | All place expansions attributable to authoritative gazetteers and marked provisional until reviewed. |
| GKR-R04 | NOT STARTED | Search sessions/history including negative findings, source coverage, exclusion filters and provenance. | Local/private audit log has query, provider, UTC time, completion status, identifiers and reason; export only by explicit user action. |
| GKR-R05 | NOT STARTED | Public catalog vs digitized-image detection; metadata-only retrieval when originals are restricted. | View/download is permission-aware, explicit, bounded and legally compliant; no content copied when only catalog viewing is authorized. |
| GKR-R06 | NOT STARTED | Research workspace connecting person hypotheses, citations, unresolved identities, contradictions and next queries. | Researcher can keep competing explanations without silently merging people or changing evidence states. |
| GKR-R07 | NOT STARTED | Offline/local index and caching for **licensed** permitted public metadata, with expiration and removal controls. | Provenance/rights retained, sensitive queries not logged by default; never bulk-download a restricted archive. |
| GKR-R08 | PARTIAL | Assisted record comparisons and name/date/place similarity prompts. | Ranked **research leads**, not probabilities of proven kinship; human confirms each linkage and sees why suggested. |
| GKR-R09 | NOT STARTED | Expand region-specific depth for Vietnam, China, Korea, Ex-USSR first; then Japan, Taiwan, Philippines, Thailand, Indonesia, Malaysia, India. | Each new region ships with actual licensed source coverage or explicitly manual-only workflow; culturally correct scripts/calendars. |
| GKR-R10 | NOT STARTED | Cross-border migration and multi-archive research routes linking events in different jurisdictions. | Search plans track migrations and time windows without assuming people with similar names are identical. |

## D. P2 — saved UX/UI and visual ideas (PARKING LOT; return after v0.4)

**Do not delete these ideas while working on online search.** Ship only S01/S05/S06/S07 UI necessary for v0.4 now. Deeper visual rework is deliberately deferred, not forgotten.

| ID | Status | Visual / interaction enhancement | Done when |
| --- | --- | --- | --- |
| GKR-U01 | NOT STARTED | Clear landing/dashboard with two primary actions **Search historical archives** and **Open my family case**, plus truthful coverage/status. | A new user knows what is offline vs online in under one glance; no deceptive search promises. |
| GKR-U02 | NOT STARTED | Search wizard with basic and advanced modes; country, historical place, time range, name-script variants, record kind and source selection. | Easy default plus expert controls, accessible keyboard flow and understandable empty states. |
| GKR-U03 | NOT STARTED | Search results sidebar with facets, filters, source chips, stable sorting, pagination and comparison tray. | Large result sets usable on desktop/mobile; exact archive ID accessible without opening every card. |
| GKR-U04 | NOT STARTED | Rich record inspector: original document image **only when licensed**, archive metadata, transcription, citation, source group, translation and corrections side by side. | Original and AI-generated text clearly separated; user can trace every statement to an image/page or its absent status. |
| GKR-U05 | NOT STARTED | Multi-generation family tree with zoom/pan, focus mode, direct ancestor/descendant paths, uncertain/contradictory links and review status. | Never renders guessed relatives as confirmed; handles large trees without freezing. |
| GKR-U06 | NOT STARTED | Family timeline / event view by person and household, with explicit alternate calendars and uncertainty. | Unknown dates stay unknown; sources visible on click and sorting avoids false exactness. |
| GKR-U07 | NOT STARTED | Historical location and migration map with period-aware boundaries and source references (only appropriately licensed basemaps). | Geography is descriptive, not identity proof; permissions and uncertain locations stated. |
| GKR-U08 | NOT STARTED | Case dashboard with progress on **sources reviewed**, unresolved leads, conflicting evidence, negative searches and coverage gaps. | KPIs measure research work, not “ancestry accuracy” or ungrounded proof scores. |
| GKR-U09 | NOT STARTED | Guided first-run workflow, tooltips, demo-to-private-case boundary and sample search walkthrough. | Users understand why a new surname returns zero in the demo and where live search starts. |
| GKR-U10 | NOT STARTED | Review queue for duplicate candidates, contradictory documents and user decisions with reversible history. | Keep original records intact; each manual decision has rationale and undo/rollback. |
| GKR-U11 | NOT STARTED | Accessibility review: labels, focus, high contrast, keyboard, zoom, screen readers, touch targets and reduced motion. | Tested with representative accessibility workflows, not only screenshots. |
| GKR-U12 | NOT STARTED | Cohesive design system: spacing, colors, typography, components, loading/empty/error patterns, navigation and reusable tokens. | Consistent responsive hierarchy and polished charts/maps instead of decorative AI-style visuals. |
| GKR-U13 | NOT STARTED | Mobile-specific document comparison, collapsible filters, responsive family graph and offline-first interactions. | 390 px layout with no horizontal overflow and meaningful touch/keyboard controls. |
| GKR-U14 | NOT STARTED | Source citation/export panel and printer-friendly evidence packet including audit disclaimers. | Preserves exact citations, review history and restricted-source notices; never exports real cases publicly by default. |
| GKR-U15 | NOT STARTED | UI language support (English, Russian, Vietnamese first; other original scripts kept unchanged); accessible translations. | Interface language changes without altering names, citations or historical calendar text. |
| GKR-U16 | NOT STARTED | Optional theme/dark mode, saved local UI preferences and layout presets **after** persistence threat model. | No privacy leaks/third-party telemetry; does not delay actual archive search. |

## E. P1/P2 — records, formats, sources and model capabilities

| ID | Priority / status | Missing capability | Completion target |
| --- | --- | --- | --- |
| GKR-F01 | P1 / PARTIAL | GEDCOM 5.5.1 broader field support, adoption/relationship qualifiers, repository links and source references; test imported real third-party *non-private* samples. | Explicit compatibility matrix; no ambiguity silently repaired; round-trip invariants where supported. |
| GKR-F02 | P1 / NOT STARTED | GEDCOM 5.5.1 **export**, deterministic mapping to evidence model and warnings for lost information. | Source pointers and original names preserved; import/export tests with known fixtures. |
| GKR-F03 | P2 / NOT STARTED | GEDCOM 7 import/export, GEDZIP and older encodings such as ANSEL (after rights/security review). | Strict version/charset detection, no destructive conversion and separate compatibility tests. |
| GKR-F04 | P1 / NOT STARTED | Private original image/document viewer and source metadata storage strategy. | Permission-controlled originals and derivatives clearly distinct; local encryption before persistence of personal scans. |
| GKR-F05 | P2 / NOT STARTED | OCR/HTR for old handwriting, Hán-Nôm, Hangul/Hanja, Cyrillic and printed registers; human-corrected text layer. | Measured quality and explicit uncertainty; no automatic identity recognition or fabricated readings. |
| GKR-F06 | P2 / NOT STARTED | Researcher-approved translation/transliteration and reviewed historical calendar conversion. | Original never overwritten; conversion rationale, tool/model and uncertainty traceable. |
| GKR-F07 | P1 / NOT STARTED | More complete source-provenance schema: custodian, original/copy, collection, call number, page, date, rights, derivative hierarchy. | Copied scans cannot inflate independent corroboration; schema migration tested. |
| GKR-F08 | P2 / NOT STARTED | Scalable indexing/graph rendering for larger genealogies beyond current bounded GEDCOM import. | Performance budgets, lazy loading and memory tests, with configurable safe size limits. |
| GKR-F09 | P2 / NOT STARTED | Manual import bridges for other permitted genealogy tools/apps and CSV formats. | Documented mapping, no loss of source warnings and no license violations. |

## F. AI-agent work — after (and in support of) verified search

| ID | Priority / status | Task | Required proof |
| --- | --- | --- | --- |
| GKR-A01 | P1 / BLOCKED on compatible local model | End-to-end function calling with an actual **local** OpenAI-compatible model (e.g. a chosen installed Ollama model). | Real-tool-turn smoke, timeout, malformed calls, model switching and no unapproved external transfer. |
| GKR-A02 | P1 / NOT STARTED | Add a constrained, auditable tool to query **only approved** archive connectors after S04; no arbitrary URLs or hidden background research. | Per-source permission, user consent, rate limits, transparent executed-vs-planned trace, records with real IDs. |
| GKR-A03 | P1 / NOT STARTED | Require grounded citations and hallucination checks in assistant answers, with source-unavailable/contradiction handling. | An output without records says not found/not searched; independent review required for all kinship claims. |
| GKR-A04 | P2 / NOT STARTED | Prompt-injection and hostile source-text robustness, model evaluation and regression sets across languages. | Archive records cannot override allowed tools, consent, privacy policy or approval gates. |
| GKR-A05 | P2 / NOT STARTED | Optional assistive transcription, translation and extraction with human verification queues. | Origin, model, confidence/uncertainty, manual corrections and licensing preserved. |
| GKR-A06 | P2 / NOT STARTED | Local model setup/health UX, resource budgeting and reproducible deployment profile. | Optional models never required for deterministic search or evidence review. |

## G. Privacy, quality, packaging and operations (must not be forgotten)

| ID | Priority / status | Work | Gate |
| --- | --- | --- | --- |
| GKR-Q01 | P0 / PARTIAL | Continuous offline regression and real-connector contract tests without mandatory GitHub Actions. | Preserve v0.3 test suite plus connector unit/mock/HTTP contract tests; tests fail on missing permission and fabricated results. |
| GKR-Q02 | P1 / PARTIAL | **Physical Windows** launch/stop, file-picker and privacy smoke. | User can open at localhost (a browser screenshot exists), but launcher/process/shutdown/real-file regression needs independent verification; no premature Windows certification. |
| GKR-Q03 | P1 / NOT STARTED | Distribution as a trustworthy signed installer or portable package, plus Linux/macOS packaging. | No forced admin rights, verified versions/signatures and reproducible clean installation; Store/MSIX only if supported and maintained. |
| GKR-Q04 | P1 / NOT STARTED | Public-source permission/security review of each online connector, data retention, opt-in networking and tokens. | Provider-specific written approval/checklist before live use; forbid unauthorized scraping and privileged bypass. |
| GKR-Q05 | P2 / NOT STARTED | Private encrypted case persistence, backups, restore/delete, retention and migration. | Threat model, recovery drill, access boundaries and explicit user opt-in. |
| GKR-Q06 | P3 / BLOCKED on threat model | Multi-user accounts, remote hosting, authentication/authorization, audit logs and privacy compliance. | Independent security review before any cloud hosting of real family documents. |
| GKR-Q07 | P1 / NOT STARTED | Usability/accessibility and independent privacy review before wider beta. | Real tasks, diverse scripts, keyboard/mobility testing, privacy checks and documented fixes. |
| GKR-Q08 | P1 / PARTIAL | Repository maintenance: keep roadmap, QA, backlog and README in sync; pin source code and licensed upstreams. | Every completed task updated here and traced to a commit; no unreviewed upstream copy or license drift. |
| GKR-Q09 | P2 / NOT STARTED | Dependency/supply-chain audit and a non-GitHub-Actions reproducible release process. | Local command and explicit reports without paid CI or hidden checks. |
| GKR-Q10 | P1 / NOT STARTED | User-facing explanation of unsupported functions, errors, privacy and source quality. | No “AI found a relative” claim unless genuine inspected evidence; source-catalog lead is never presented as a verified record. |

## H. Risks, unresolved decisions and exit gates

1. **Provider access is the biggest blocker.** A public archive landing page is not a licensed API. Evaluate permission/terms and actual record-search capability **before** building an adapter. Do not claim success from a simulated result.
2. **Coverage differs by source and era.** Many regions lack public searchable genealogy data; show manual request routes as such. Never invent completeness percentages, missing records or familial connections.
3. **Searching for living people is sensitive.** Explicitly separate public historical research from current residence, confidential civil registries and people's private profiles. User requests do not override third-party access rules.
4. **One witness is not many.** Mirrors, repeated indexes, duplicate scans and copied books may be the same provenance group; preserve contradictions and failed searches.
5. **Cost is optional, not assumed.** Default version remains usable with free local core and lawful publicly accessible sources; disclose paid provider subscriptions if ever proposed.
6. **External-model privacy:** current feature restricts remote use to unchanged bundled synthetic demo and explicit request consent. Real cases must stay local by default; a real local model is not yet tested.
7. **Post-merge v0.3 limits:** historical archive search, OCR, GEDCOM export/7, true multi-generation graphs and hosted deployment are not implemented. Windows comprehensive testing, real model and third-party GEDCOM compatibility remain open.
8. **Release gate:** no merge when full current tests fail; track one tested live source, all user-visible result states, safe import, explicit privacy and manual evidence review. Test no-result, forbidden and unavailable providers, not just happy paths.

### First actionable next increment

**Implement GKR-S01 through GKR-S04 first.** Write a real source/API feasibility report and select an authorized pilot before coding any scraping. Then wire up S05–S12 and finish v0.4 on real, legally accessed metadata. Keep section D intact for the subsequent UI iteration. If the pilot source does not permit automated searching, mark that provider BLOCKED, pick another approved one, and retain a manual research guide.

### Traceability to existing code and documents

- Local search and records: [research.py](../src/kinship/research.py), [web.py](../src/kinship/web.py), [static/app.js](../src/kinship/static/app.js).
- Region-only research leads: [profiles.py](../src/kinship/profiles.py), [catalog.py](../src/kinship/catalog.py), [SOURCE_REVIEW.md](SOURCE_REVIEW.md).
- Agent and provenance: [agent.py](../src/kinship/agent.py), [audit.py](../src/kinship/audit.py), [PROVENANCE.md](PROVENANCE.md).
- GEDCOM, graph and local UI: [gedcom.py](../src/kinship/gedcom.py), [graph.py](../src/kinship/graph.py), [family.js](../src/kinship/static/family.js), [GEDCOM_551.md](GEDCOM_551.md).
- Existing gates and privacy: [QA.md](QA.md), [SECURITY_PRIVACY.md](SECURITY_PRIVACY.md), [verify_release.py](../scripts/verify_release.py).

### 2026-11-23 integration update (GKR-R08, GKR-Q01)

- [x] Connect review-only catalog comparisons to the localhost API (`/api/compare-catalog-lead`) and the Search archives UI without exposing private cases to the external archive provider. Person selection and comparison are initiated locally by the user.
- [x] Enforce local person ID lookup, official catalog URL and no invented confirmed identity/kinship outcome. The helper remains deliberately non-probabilistic. Imported archive metadata is **not** a primary witness.
- [x] Full regression: **112 Python tests**, compile/JS checks, 10 HTTP smoke steps, Chromium family component, and desktop/mobile archive-search smoke with synthetic external response; no GitHub Actions.
- [ ] Live LoC JSON response/record ID still unverified; Korea/Shanghai require issued keys; Vietnam/ex-USSR remain manual-only until a permitted source contract exists.
- [ ] Future improvements kept open: manual decision history, independent-original verification, historical date/place equivalence, cross-provider duplicates, multi-generation family tree, maps, OCR and GEDCOM 7.