# Ex-USSR CSV bridge — v0.2

Compatible input format: the 2026-11-12 upstream Git tree at commit `f4b6b3ffc99ccdcb3e4b6bbfad3fca51b09bd23c`, containing `assets/person-register.csv`, `artifact-register.csv`, `claims-register.csv`, `relationship-register.csv`, optional `search-log.csv`.

## Conversion rules

- Person `person_id` becomes the same JSON ID; `names_as_written` is retained verbatim; `preferred_label` is a fallback only; all original columns are copied to `legacy_ex_ussr`.
- `living_status` is mapped to `true`, `false` or `null`. Unknown is not silently changed to deceased.
- Artifact `artifact_id`, `independence_group` and original fields are preserved. Citation combines supplied repository, title and archive reference. It is **not invented**. An HTTPS link is carried only when actually present; local file paths remain private legacy metadata.
- Claim with exactly one `subject_person_ids` entry becomes a text claim (`type=other`, `literal_value=claim_text`). No speculative connection is inferred. Unsupported statuses or ambiguous subject IDs block import.
- Supported relationships (`parent_of`, `spouse_of`, `sibling_of`) become separate claim records with IDs prefixed `rel:`. Other relationship types must be reviewed and explicitly mapped by a human.
- A relationship or claim declaring corroboration without the required *distinct cited artifact groups* fails import. Duplicated scans are not independent witnesses.
- Search-log rows, including negative results, are preserved as original dictionaries when provided.

The importer fails closed if source headers are incompatible, the input case is incomplete or audit errors exist. This conservative process is **not lossless GEDCOM conversion** and does not establish document authenticity. A private case destination is mandatory. Do not put real CSVs, imports or model prompts in public GitHub issues or PRs.
