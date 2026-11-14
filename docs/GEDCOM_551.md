# GEDCOM 5.5.1 import (v0.3, bounded beta)

**File input is local-only.** GEDCOM is a genealogy *exchange format*, not a historical source and not proof of identity. The import builds a new **private** case and marks all relationships as **hypothesis** even when the original family file includes `SOUR` citations. Source mentions are not a substitute for examining the original image or archive entry.

## Supported subset

- UTF-8 GEDCOM **5.5.1** (with `HEAD / GEDC / VERS 5.5.1` and `TRLR`), plus ASCII-declared files containing only ASCII.
- `INDI`: multiple `NAME` values with preserved slash-delimited raw spelling; `SEX` when explicitly present; `DEAT` Y/date/place determines deceased status; otherwise living status **unknown**, never guessed from year of birth.
- `BIRT / DATE / PLAC`, `DEAT / DATE / PLAC`: exact literal values are preserved. Event-level `SOUR` and `PAGE` become source references; if no citation exists, the fact remains `hypothesis`.
- `FAM / HUSB / WIFE / CHIL`: explicit family claims only; their legal, adoptive or biological status remains **unresolved**. Relationships are never treated as verified just because the imported document shows them.
- `SOUR / TITL / ABBR` and inline citations; copies/pages from one `SOUR` record retain the **same independence group**.
- Untouched case JSON is the canonical project representation. GEDCOM content is not saved by the local server; you can choose to store imported case JSON yourself outside the public repository.

## Not supported yet

- GEDCOM 7, GEDZIP, ANSEL and other legacy encodings. Export old genealogical files as UTF-8 GEDCOM 5.5.1 in your source application first.
- GEDCOM export (planned), full custom event tags, adoptions/pedigree interpretation, alternate calendars, Unicode transliteration, repositories, OBJE media, and multi-line source metadata beyond basic continuation.
- Automated source authentication, remote archive searches, identity matching, duplicate merging, or scans/OCR.

**IMPORTANT:** Residence, addresses, emails, media, and phone details are deliberately not mapped into the resulting case. Check the source GEDCOM before uploading to any outside service; Global Kinship's parser is local but this does not change how the *source app* handled its data.

## CLI

```bash
PYTHONPATH=src python -m kinship import-gedcom \
  path/to/family.ged --region vietnam --case-id my-private-case \
  --question "What is the evidence for this household?" \
  --out private/family-case.json

PYTHONPATH=src python -m kinship graph private/family-case.json
```

The importer fails closed on broken pointers, duplicate IDs, cycles, invalid charset/versions, and oversized input. Existing output files are never overwritten. Keep imported family files under `private/` or another folder excluded from public version control.

## Privacy / no automatic kinship proof

The app does not fetch archives or publish source files. A passing structural audit only means internal references are consistent. It **does not** mean a family's assertions are historically true. Verify each birth, marriage, parent-child relation, migration event and name against original records; document conflicting evidence rather than silently changing relationships.

GEDCOM specification links: [FamilySearch GEDCOM specifications](https://gedcom.io/specs/) and [GEDCOM 5.5.1](https://gedcom.io/specifications/gedcom551.pdf).
