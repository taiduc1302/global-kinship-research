# Architecture v0.2: local workbench + constrained research agent

## Data flow

```text
Local JSON case / synthetic demo (browser memory only)
  ↕ JSON POST (127.0.0.1, same-origin, bounded, not persisted)
Python stdlib HTTP server (kinship.web)
  ├── region registry (kinship.profiles) → source lead manifest (kinship.catalog)
  ├── literal local search (kinship.research) → person/artifact/claim inspector
  ├── deterministic structural audit (kinship.audit) → review-only evidence notices
  └── research agent (kinship.agent) → whitelisted read-only tools
       ├── region_guide / archive_leads / draft_search_plan
       ├── search_local_case / person_evidence / source_evidence
       └── audit_evidence
       ↕ optional OpenAI-compatible local model (or explicit synthetic-only remote)
```

No cloud state, code execution, email, website scraping, autonomous approval, automatic file writes or background agents. The UI fetches the synthetic example from the same local process. All sensitive case data remain in browser memory during a session; local HTTP transports case JSON to localhost for research operations, without persistence.

## Design boundaries

1. **Region modules** contain historical name, calendar, jurisdiction and official source guidance. They supply research plans and a source directory; they do not query a live archive database.
2. **Case data** stay in schema v0.1 for backward compatibility. People, artifacts, claims and search logs are separate. Names are preserved exactly; Latin accent folds are *supplementary* text match variants.
3. **Source independence** is tracked with `independence_group`. A duplicate scan or a website mirror does not raise corroboration counts.
4. **LLM tool loop** uses standard chat-completions function calling through `ChatClient`. Hard caps: 8 turns, 20 calls, 1MB response, bounded request content. Unsupported tool names and extra arguments are rejected. No tool mutates or uploads cases.
5. **Source provenance** in `kinship.catalog` includes a stable `source_id`, region, institution, purpose, access label and explicit `record_search_executed=false`, `terms_of_reuse_verified=false`.
6. **Ex-USSR adapter** imports original CSV register fields into a local case, preserving raw text and IDs. It does not execute upstream skill instructions or publish sensitive data.
7. **Local web UI** is static HTML, CSS, JavaScript from the same Python package (no CDN). No authentication because it is strictly loopback. Hosting it on a public server is **unsupported** without designing auth, CSRF, encryption, retention and permissions.

## Evidence model

Same schema and status thresholds as v0.1. A structural audit pass is *not* proof of origin, person identity, document authenticity, full search coverage or GPS certification. Only a human can approve or publish a research conclusion.

## Known architectural gaps

- No licensed live archive search connector or archival API access; archive links need user actions.
- No OCR/HTR; source text is supplied by the user and is not translated/modified automatically.
- No GEDCOM 5.5.1/7 interoperability yet; no persistent graph database or multi-user service.
- Local tool-driven AI compatibility is tested with a fake model but not a running Ollama or OpenAI account.
- Historical jurisdiction/place gazetteers and automated calendar conversion require authoritative data and remain manual.

Potential future official APIs must be reviewed separately for permissions, rate limits, auth, regional restrictions, provenance quality and privacy. Do not treat a public website as an API contract.
