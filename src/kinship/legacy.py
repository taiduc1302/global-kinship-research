"""Conservative bridge from Denis Shiryaev's pinned ex-USSR CSV registers.

The original project stays a Git submodule. This importer does not read its
instructions as executable commands, visit archives, or infer missing people.
Conversion preserves raw register fields and fails closed when evidence cannot
be mapped without speculation. Private files are never committed by the tool.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path
from urllib.parse import urlsplit

from kinship.audit import VALID_STATUSES, RELATION_TYPES, audit_case


def _rows(folder: Path, name: str, required: set[str]) -> list[dict]:
    path = folder / name
    if not path.is_file():
        raise ValueError(f"Missing required register: {name}")
    if path.stat().st_size > 5_000_000:
        raise ValueError(f"Register too large: {name}")
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames or not required.issubset(reader.fieldnames):
            raise ValueError(f"Invalid {name} register headers; check the pinned upstream template")
        result = []
        for row in reader:
            if not any((v or "").strip() for v in row.values() if isinstance(v, str)):
                continue
            if None in row or any(v is None for v in row.values()):
                raise ValueError(f"Malformed CSV row in {name}")
            result.append(row)
        return result


def _ids(value: str) -> list[str]:
    if not value or not value.strip():
        return []
    value = value.strip()
    if value.startswith("["):
        try:
            items = json.loads(value)
        except json.JSONDecodeError as exc:
            raise ValueError("Invalid JSON array in ID column") from exc
        if not isinstance(items, list) or not all(isinstance(x, str) for x in items):
            raise ValueError("ID arrays must contain strings")
        return [x.strip() for x in items if x.strip()]
    return [x.strip() for x in value.replace("|", ";").split(";") if x.strip()]


def _safe_link(value: str) -> str | None:
    try:
        parsed = urlsplit(value)
        if parsed.scheme == "https" and parsed.hostname and not parsed.username:
            return value
    except ValueError:
        pass
    return None


def import_ex_ussr_registers(folder: str | Path, *, case_id: str, question: str,
                              visibility: str = "private") -> dict:
    directory = Path(folder).resolve()
    if not directory.is_dir():
        raise ValueError("Source register directory does not exist")
    if not case_id.strip() or not question.strip():
        raise ValueError("Case ID and research question are required")
    person_rows = _rows(directory, "person-register.csv", {"person_id", "preferred_label", "living_status", "names_as_written"})
    artifact_rows = _rows(directory, "artifact-register.csv", {"artifact_id", "source_title", "independence_group", "archival_reference"})
    claim_rows = _rows(directory, "claims-register.csv", {"claim_id", "claim_text", "subject_person_ids", "artifact_ids", "status"})
    rel_rows = _rows(directory, "relationship-register.csv", {"relationship_id", "person_a_id", "person_b_id", "relationship_type", "supporting_artifact_ids", "status"})
    search_rows = (_rows(directory, "search-log.csv", {"search_id", "query", "result_status", "source_or_domain"})
                   if (directory / "search-log.csv").exists() else [])
    people = []
    for p in person_rows:
        life = p["living_status"].strip().casefold()
        if life in {"living", "alive", "yes", "true"}:
            living = True
        elif life in {"deceased", "dead", "no", "false"}:
            living = False
        else:
            living = None
        # Do not auto-split multi-script names: the entire original is preserved.
        original = p["names_as_written"].strip() or p["preferred_label"].strip()
        people.append({"id": p["person_id"].strip(), "living": living,
                       "names": [{"original": original}], "legacy_ex_ussr": p})
    artifacts = []
    for a in artifact_rows:
        citation_parts = [a.get("repository_or_archive", "").strip(), a["source_title"].strip(), a["archival_reference"].strip()]
        citation = ", ".join(x for x in citation_parts if x)
        if not citation:
            # An arbitrary URL does not replace an archival citation.
            raise ValueError("Source requires a traceable archive citation: " + a["artifact_id"])
        record = {"id": a["artifact_id"].strip(), "citation": citation,
                  "independence_group": a["independence_group"].strip(),
                  "access": "restricted" if "restrict" in a.get("access_notes", "").lower() else "unknown",
                  "legacy_ex_ussr": a}
        if link := _safe_link(a.get("source_url_or_path", "")):
            record["url"] = link
        artifacts.append(record)
    claims = []
    for c in claim_rows:
        subjects = _ids(c["subject_person_ids"])
        if len(subjects) != 1:
            raise ValueError(f"Claim {c['claim_id']} requires exactly one unambiguous subject_person_id")
        if c["status"].strip() not in VALID_STATUSES:
            raise ValueError(f"Claim {c['claim_id']} has unsupported status; review it manually")
        claims.append({"id": c["claim_id"].strip(), "subject_id": subjects[0],
                       "type": "other", "literal_value": c["claim_text"].strip(),
                       "status": c["status"].strip(), "artifact_ids": _ids(c["artifact_ids"]),
                       "notes": c.get("rationale", ""), "legacy_ex_ussr": c})
    for r in rel_rows:
        if r["relationship_type"].strip() not in RELATION_TYPES:
            raise ValueError(f"Relationship {r['relationship_id']} type needs explicit mapping")
        if r["status"].strip() not in VALID_STATUSES:
            raise ValueError(f"Relationship {r['relationship_id']} status needs explicit mapping")
        claims.append({"id": "rel:" + r["relationship_id"].strip(),
                       "subject_id": r["person_a_id"].strip(), "object_id": r["person_b_id"].strip(),
                       "type": r["relationship_type"].strip(), "status": r["status"].strip(),
                       "artifact_ids": _ids(r["supporting_artifact_ids"]),
                       "notes": r.get("rationale", ""), "legacy_ex_ussr": r})
    case = {"schema_version": "0.1", "case_id": case_id, "visibility": visibility,
            "research_question": question, "regions": ["ex-ussr"],
            "people": people, "artifacts": artifacts, "claims": claims,
            "search_log": search_rows,
            "import_metadata": {"format": "ex-ussr-csv", "original_repository":
                                "DenisSergeevitch/ex-ussr-kinship-research",
                                "notice": "Raw original columns retained, no source authenticity checked"}}
    report = audit_case(case)
    if not report.ok:
        problems = ", ".join(sorted({f.code for f in report.findings if f.level == "error"}))
        raise ValueError(f"Import blocked by evidence audit: {problems}")
    return case
