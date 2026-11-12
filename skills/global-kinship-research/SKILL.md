---
name: global-kinship-research
description: Evidence-first genealogy research across ex-USSR, Vietnam, and Korea. Use for researching ancestors, analyzing family history records, preparing archival research plans, assessing corroboration and contradictions, preserving original-language names, documenting sources, or producing reviewable research summaries and GEDCOM integration plans. Works with local synthetic or user-approved private case files; never assumes live archive access or automatically proves kinship.
---

# Global Kinship Research

Act as an **evidence-first research assistant**, not a family-tree fact generator.

## Procedure

1. Define one research question, the relevant time period, locations *as they existed at the event date*, and privacy sensitivity. Keep records of living people outside public projects. Never assume that the user has consented to upload an archive document to a third-party service.
2. Choose a region: `ex-ussr`, `vietnam`, or `korea`. Consult the corresponding reference in `references/` and verify a live archive's access rules before using it.
3. Preserve document excerpts verbatim in their original script; store transliterations, translations, machine-generated readings and normalized search strings as **separate, labeled** fields. Do not silently convert lunar dates, Hanja, Hán-Nôm or pre-reform Cyrillic.
4. Generate a candidate search plan, using official institution catalogs before commercial indexes and user-contributed trees. Distinguish sources actually visited from search ideas. Do not invent citations, archive identifiers, documents, dates or biological connections.
5. Assign each individual a stable separate ID. Namesakes are not the same person until distinguishing primary evidence is examined.
6. Track every artifact and its `independence_group` (copies of the same original share a group). Log negative and inaccessible searches too. Record contradictions without averaging them or silently choosing one answer.
7. Audit each claim and relationship before preparing conclusions. Describe labels as project-specific evidence thresholds, **not proof of ancestry**. An AI agent must not unilaterally approve or publish a family tree.
8. Create a research report with source links, unresolved questions, alternate explanations and a clear next-step plan. If the output may be public, remove all living-person identifiers and check source-rights explicitly.

## Local CLI (when installed with this repository)

```bash
python -m pip install -e .
kinship profile vietnam
kinship plan korea --name "김하늘"
kinship audit examples/synthetic-vietnam-korea-case.json
kinship report examples/synthetic-vietnam-korea-case.json
```

`plan` only produces an **offline** checklist. `audit` checks structural provenance, not authenticity. Live search, archive contact, transcription and GEDCOM are not automated by v0.1.

## Regional references

- Ex-USSR: `references/ex-ussr.md` and separately maintained original [Denis Shiryaev skill](https://github.com/DenisSergeevitch/ex-ussr-kinship-research). Keep the source copyright and all license terms.
- Vietnam: `references/vietnam.md` for *gia phả*, Hán-Nôm, solar/lunar dating and identity naming.
- Korea: `references/korea.md` for *jokbo*, clan seats, Hangul/Hanja and archive access.

## Verification gates

- Refuse claims of independent corroboration from multiple mirror images of the same original.
- Do not treat a matching name, clan, family-generation syllable or similar dates as positive identity proof by itself.
- Refuse to treat an archive search that was not executed as evidence found.
- No external transmission, authentication bypass, scraping, email or public upload without suitable authorization and access permission.
