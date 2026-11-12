# Architecture v0.1

## Intent

A family-history research **workbench** rather than a single monolithic genealogy app. Archive discovery, genealogical data persistence, publication, and authorization are distinct concerns.

### Modules and boundaries

- `kinship.profiles`: curated country- and region-specific guides, requiring verification at use time.
- `kinship.names`: safe query variants, preserving literals; not transliteration or cross-document identity matching.
- `kinship.audit`: structural quality gates for the case schema and provenance; no source authenticity claims.
- `kinship.plan`: offline search checklist and archive leads, explicitly marked `draft-not-searched`.
- `kinship.report`: local reviewable Markdown evidence packet, blocked for malformed cases.
- `upstreams/ex-ussr-kinship-research`: pinned original skill; currently reference-only, not auto-executed.
- `skills/global-kinship-research`: instructions coordinating approved tools with private-case data protection.

### Case model

Case JSON v0.1: `case_id`, `schema_version`, `visibility`, `research_question`, `regions`, `people`, `artifacts`, `claims`, `search_log`.

- Person: stable synthetic/random `id`, original-script `names[]`, `living` true/false/null. Namesakes remain distinct IDs.
- Artifact: original citation, source access, explicit `independence_group`. Independent scans from one page still share a group.
- Claim: `subject_id`, `type`, relationship `object_id` OR factual `literal_value`, `artifact_ids[]`, `status`, analyst `notes`.
- No claim *status* implies identity has been established automatically; audit checks minimum counted groups, not reliability.

### Status thresholds for structural review

| status | Minimum referenced evidence groups | Meaning |
| --- | --- | --- |
| `hypothesis` | 0 | Unverified idea |
| `single-source` | 1 | At least one cited source |
| `corroborated` | 2 | At least two independent source groups |
| `strongly-corroborated` | 3 | Three distinct groups (a conservative project rule) |
| `contradicted` | 0 | Evidence conflict; explain context |
| `unresolved` | 0 | Insufficient or inconsistent evidence |

These are project validation gates, **not** universal proof thresholds, a mathematical confidence score, or Genealogical Proof Standard certification.

### Human and legal gates

1. No automatic portal form submission or email sending.
2. No collection of living-person or closed civil-registration records without permission.
3. No GitHub Actions, cloud database, remote telemetry or uploads in the MVP.
4. Any future archive connector must document terms, allowed automated access, rate limits, auth handling, data retention and expected errors.
5. Any future GIS/time-aware jurisdiction model requires authoritative province/district boundaries and date-specific sources.
6. Any future GEDCOM import/export must explicitly handle privacy, sources, data loss and round-trip regression tests.
