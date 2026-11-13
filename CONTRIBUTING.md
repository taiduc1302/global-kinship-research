# Contributing safely

This is an evidence-first research toolkit, not an automatic ancestry-approval service. Contributors can propose regional guides, improvements to the local case data model, additional fixtures, UI accessibility, or carefully licensed archive connectors.

## Ground rules

- **No real family data:** never commit living-person records, private GEDCOMs, archival scans, correspondence, addresses, IDs, credentials, or screenshots containing personal details. All fixtures must be synthetic.
- **Official records must be traceable:** add archive URLs and access/terms information, clearly separating a *portal link* from an actual searched record. Provide evidence of current source review.
- **Preserve cultural and historical context:** keep original scripts, calendar descriptions, jurisdiction at event date, and source citations; never guess transliterations, ancestry or source independence.
- **Human-only approvals:** do not automatically accept family links, contact relatives/archives, or publish records without explicit authorization and independent review.
- **License before copy:** MIT/Apache code reuse still needs correct copyright notices; a public repo with no license is not copy-permitted; web archive data has separate terms.
- **No mandatory GitHub Actions:** run local tests with `PYTHONPATH=src python -m unittest discover -s tests -v` and optional `node --check src/kinship/static/app.js`.
- **Document all model calls:** local models default, hosted models synthetic-case only and explicitly consented.

Submit a PR with the purpose, source URLs, permission model, before/after behavior, new tests, local test results, and any migration implications. Review security and accessibility for UI changes. Do not include screenshots of real family records in issues or PRs.
