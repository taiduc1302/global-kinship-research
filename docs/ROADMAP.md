# Roadmap with deliverable gates

Owner: Global Kinship Research contributors. Updated: 2026-11-12. Each phase is a candidate scope, not a release promise.

## P0 — Baseline complete in local starter (v0.1)

- [x] Original Ex-USSR source identified and its MIT license checked.
- [x] Version-pinned Ex-USSR Git submodule, preserving upstream history separately.
- [x] Evidence-source independence check, broken foreign keys, duplicates, parent cycle, living-person publication guard.
- [x] Vietnam and Korea research guides with verified institutional links, manual-only labeling.
- [x] Synthetic case, offline CLI, smoke/regression tests.
- [x] Agent Skill and explicit privacy policy.
- [ ] Publish on `taiduc1302/global-kinship-research` (GitHub repo creation not exposed by current connector).
- [ ] Make an independent GitHub fork of Ex-USSR under `taiduc1302` if desired (requires GitHub fork operation).

## P1 — Real research method without leaking private data

- [ ] Define machine-readable archive source manifest: `source_id`, institution, jurisdiction, historical years, catalog URL, access, terms, last_verified.
- [ ] Ex-USSR integration test between original artifact/claim CSV registers and our JSON case schema; preserve original IDs, independence groups, and authorship.
- [ ] Vietnam record family: Hán-Nôm catalog identifiers, genealogical book generations, lunar date without speculative conversions, source scans with lawful access.
- [ ] Korea record family: jokbo clan/bon-gwan, Hangul/Hanja forms, lunisolar dates, source citations.
- [ ] Archive search log: attempted queries, failed searches and inaccessible-only records as first-class entries.
- [ ] Sample archive request templates, never send without review and explicit user confirmation.
- [ ] 30+ independent synthetic scenario tests and security/privacy review.

**P1 gate:** 0 personally identifying records in public repository; 0 fabricated citations; audit refuses two copies of the same source as independent proof. No automatic identity merges.

## P2 — Interoperability and family tree

- [ ] GEDCOM 5.5.1/7 import-export research with documented lossiness and encoding rules.
- [ ] Cross-language source/transliteration review UI; source text cannot be silently replaced.
- [ ] Local static read-only family graph rendering with provenance visible for each edge.
- [ ] Optional self-hosted private data store, permission model, encryption and backup testing.
- [ ] Evaluate MIT/Apache-compatible upstream apps (Roots of Vietnam / FamilyRoots) for selected components, not a wholesale code merge.

**P2 gate:** No evidence or privacy metadata lost on import/export; private profiles excluded from public outputs.

## P3 — Asia modules by evidence availability

- [ ] China (jiapu/zupu), Japan (koseki and access controls), other Southeast Asia.
- [ ] Re-evaluate official databases and licenses at implementation time.
- [ ] Historical jurisdiction lookup and controlled schema evolution.
- [ ] Country experts review source use and historical/cultural handling.

**P3 gate:** Every country module has provenance, access restrictions, and at least 10 culturally specific tests.

## Contribution workflow without GitHub Actions

1. `python -m unittest discover -s tests -v`
2. `python -m kinship audit examples/synthetic-vietnam-korea-case.json` after `PYTHONPATH=src` or editable install.
3. Human reviewer verifies all new links, attribution, safety, translations and calendar assumptions.
4. Attach local test output to PR; do not post real family documents.
