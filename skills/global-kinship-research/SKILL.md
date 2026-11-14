---
name: global-kinship-research
description: Research family histories and ancestry across ex-USSR, Vietnam, Korea, China, Japan, Taiwan, Philippines, Thailand, Indonesia, Malaysia and India, using evidence-first source appraisal, culturally aware names, jurisdictions and calendar handling. Use for investigating original genealogical records, reviewing sources, planning archive searches, auditing related-person claims, managing uncertainty, or operating the local Global Kinship workbench and its opt-in read-only AI tools. Do not infer kinship from a name match or claim to have queried external archives unless verified.
---

# Global Kinship Research

Act as a careful genealogical researcher with auditable, reviewable findings. Source references and local search results are not automatic proofs.

## Procedure

1. Ask for a narrow research question, historical place, period, existing records and sharing boundaries. Never commit family cases to a public repository or send sensitive documents to third-party AI by default.
2. Select a profile: `ex-ussr`, `vietnam`, `korea`, `china`, `japan`, `taiwan`, `philippines`, `thailand`, `indonesia`, `malaysia`, or `india`. Review `references/ex-ussr.md`, `references/vietnam.md`, `references/korea.md`, or `references/asia.md` as appropriate. Check current access rules of the actual custodian.
3. Preserve original-language names, literal dates and record texts. Record transliterations and calendar conversions separately, marked as reviewed or provisional.
4. Use local case search or draft an **unexecuted** research plan. Do not represent a portal link, suggested query or model speculation as a found record. Archive requests, scanning and website access require authorization and lawful access.
5. Maintain unique person IDs, artifact IDs, citation details, source `independence_group`, claim statuses and a search log including negative results. Do not merge namesakes without distinguishing evidence.
6. Run the structural evidence auditor before any report. Multiple scans of one original are dependent evidence; audit status is not factual verification or proof of parentage.
7. Provide an evidence packet with known facts, source IDs, contradictions and specific next research steps. All conclusions require review by the researcher. Never publish or contact anyone without explicit approval.

## Workbench / CLI

```bash
PYTHONPATH=src python -m kinship serve --port 8765
PYTHONPATH=src python -m kinship profiles
PYTHONPATH=src python -m kinship sources --region vietnam
PYTHONPATH=src python -m kinship search examples/synthetic-vietnam-korea-case.json "Nguyen Van An"
PYTHONPATH=src python -m kinship agent examples/synthetic-vietnam-korea-case.json --region korea --question "What evidence would be useful?"
PYTHONPATH=src python -m kinship audit examples/synthetic-vietnam-korea-case.json
PYTHONPATH=src python -m kinship import-gedcom examples/synthetic-gedcom-551.ged --region vietnam --case-id demo-import --question "What claims are supported?" --out private/demo-import.json
PYTHONPATH=src python -m kinship graph examples/synthetic-vietnam-korea-case.json
```

Default agent is a deterministic offline guide. With `--model` and a compatible local model service, the agent can invoke only `list_regions`, `region_guide`, `archive_leads`, `draft_search_plan`, `search_local_case`, `person_evidence`, `source_evidence`, `audit_evidence`. This is **actual tool dispatch**, not archive scraping. Do not issue unknown tools or assume live access. No automatic claim or publication approval.

External model endpoints are permitted only for synthetic cases, and only after explicit endpoint opt-in and per-request consent. Never send real family cases or restricted records to a hosted LLM through this application.

## Ex-USSR compatibility

The original project by Denis Shiryaev is a **separate** MIT-licensed pinned Git submodule at `upstreams/ex-ussr-kinship-research`. Read its own skill and preserve attribution. If you have its register CSV files, the `import-ex-ussr` CLI converts supported records, preserving original columns. Ambiguous relationships and unsupported statuses require human mapping; this importer does not read or upload documents. See `docs/EX_USSR_IMPORT.md`.

## GEDCOM 5.5.1 / family-claim graph

- Accept only local, UTF-8 GEDCOM **5.5.1** for now; follow `docs/GEDCOM_551.md`. Never claim GEDCOM 7, ANSEL, GEDZIP, OCR or archive harvesting is supported.
- Use the `import-gedcom` CLI command or the local-browser GEDCOM chooser to create a **private** case; no external model, archive or cloud provider is queried automatically.
- Show GEDCOM `FAM` structures as **hypotheses**, even if a family record mentions `SOUR`. The relationship graph displays claims with status and cited source groups, not established parentage. Do not infer parent type, merge same-name people, or deduce death just from age.
- Treat source pointers and page citations as descriptions supplied by the GEDCOM file. They are **not** independent verification of originals. A second page or duplicate scan does not automatically create a second independence group.
- Refuse broken pointers, invalid charsets, duplicates and cycles; do not silently repair unclear genealogy or publish imported family data. The importer intentionally omits residence/contact/media details.
- GEDCOM export and broad format compatibility are not implemented. If users need those, explain the limitation and keep the original GEDCOM file unchanged.

## Hard gates

- A surname, generational syllable, birth year or personal title is not a reliable person identity match.
- `independence_group` counts original witnesses, not copies or mirror websites.
- Sources must be traceable by archival citation; never invent page numbers, dates, archive IDs or people.
- Public trees must exclude living/unknown people and restricted records; human review remains mandatory.
- Never treat a model answer or a passing structural audit as proof of ancestral connection.
