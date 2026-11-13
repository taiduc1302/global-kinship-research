"""Local, literal search over user-supplied case records (no network queries)."""
from __future__ import annotations

from collections.abc import Mapping
import unicodedata

from kinship.audit import audit_case
from kinship.names import _latin_search_fold

MAX_RESULTS = 50


def _fold(text: str) -> str:
    return unicodedata.normalize("NFC", _latin_search_fold(text)).casefold()


def require_valid_case(case: Mapping) -> None:
    report = audit_case(case)
    if not report.ok:
        codes = sorted({f.code for f in report.findings if f.level == "error"})
        raise ValueError("Case audit failed: " + ", ".join(codes))


def case_summary(case: Mapping) -> dict:
    require_valid_case(case)
    return {
        "case_id": case.get("case_id", "unknown"),
        "visibility": case.get("visibility", "private"),
        "question": case.get("research_question", ""),
        "regions": case.get("regions", []),
        "people": len(case.get("people", [])),
        "artifacts": len(case.get("artifacts", [])),
        "claims": len(case.get("claims", [])),
        "source_groups": len({a["independence_group"] for a in case.get("artifacts", [])}),
        "label": "User-supplied records; neither verified nor independently searched",
    }


def search_case(case: Mapping, query: str, *, kind: str = "all", limit: int = 25) -> dict:
    """Return local matches and real IDs. Never infer that two people are the same."""
    require_valid_case(case)
    if not isinstance(query, str) or not query.strip():
        raise ValueError("A nonempty search term is required")
    if len(query) > 200:
        raise ValueError("Search term is too long (max 200 characters)")
    if kind not in {"all", "people", "artifacts", "claims"}:
        raise ValueError("Invalid search kind")
    if not isinstance(limit, int) or isinstance(limit, bool) or not (1 <= limit <= MAX_RESULTS):
        raise ValueError("Limit must be between 1 and 50")
    needle = _fold(" ".join(query.split()))
    people = {p["id"]: p for p in case.get("people", [])}
    artifacts = {a["id"]: a for a in case.get("artifacts", [])}
    results: list[dict] = []

    def add(record_type: str, record_id: str, title: str, description: str, haystack: list[str], **extras) -> None:
        if kind not in ("all", record_type):
            return
        searchable = [_fold(str(x)) for x in [record_id, title, description, *haystack] if isinstance(x, (str, int))]
        if any(needle in text for text in searchable):
            results.append({"kind": record_type, "id": record_id, "title": title,
                            "description": description, **extras})

    for person in case.get("people", []):
        names = [n["original"] for n in person.get("names", [])]
        aliases = [n.get("transliteration", "") for n in person.get("names", [])]
        add("people", person["id"], names[0] if names else person["id"],
            " · ".join(names[1:]) or "Individual record (not an identity match)",
            names + aliases, living=person.get("living"))

    for artifact in case.get("artifacts", []):
        add("artifacts", artifact["id"], artifact["citation"],
            f"Source group {artifact['independence_group']} · {artifact.get('access', 'access unknown')}",
            [artifact.get("url", ""), artifact.get("notes", "")],
            independence_group=artifact["independence_group"], access=artifact.get("access", "unknown"))

    for claim in case.get("claims", []):
        person = people.get(claim.get("subject_id", ""), {})
        names = [n.get("original", "") for n in person.get("names", [])]
        refs = [artifacts[aid]["citation"] for aid in claim.get("artifact_ids", []) if aid in artifacts]
        add("claims", claim["id"], claim.get("literal_value") or claim.get("type", ""),
            f"{claim.get('status')} · {claim.get('type')}",
            [claim.get("notes", ""), *names, *refs, claim.get("subject_id", ""), claim.get("object_id", "")],
            source_ids=list(claim.get("artifact_ids", [])), status=claim.get("status"))

    # No score that could be mistaken for probability of identity; stable order.
    return {"searched": "local-case-only", "query": query, "total": len(results),
            "results": results[:limit], "truncated": len(results) > limit,
            "limitations": "Only exact/diacritic-folded text matches in supplied data; no external archives searched"}


def person_detail(case: Mapping, person_id: str) -> dict:
    require_valid_case(case)
    people = {p["id"]: p for p in case.get("people", [])}
    if person_id not in people:
        raise ValueError("Unknown person ID")
    relationships = [c for c in case.get("claims", [])
                     if c.get("subject_id") == person_id or c.get("object_id") == person_id]
    cited = {a for c in relationships for a in c.get("artifact_ids", [])}
    return {"person": people[person_id], "claims": relationships,
            "artifacts": [a for a in case.get("artifacts", []) if a["id"] in cited],
            "notice": "Claims are allegations with evidence labels; never automatic kinship proof"}


def artifact_detail(case: Mapping, artifact_id: str) -> dict:
    require_valid_case(case)
    artifacts = {a["id"]: a for a in case.get("artifacts", [])}
    if artifact_id not in artifacts:
        raise ValueError("Unknown artifact ID")
    return {"artifact": artifacts[artifact_id],
            "claims": [c for c in case.get("claims", []) if artifact_id in c.get("artifact_ids", [])],
            "independent": [a["id"] for a in case.get("artifacts", [])
                            if a["independence_group"] == artifacts[artifact_id]["independence_group"]],
            "notice": "Same independence_group denotes copies/dependent sources, not independent corroboration"}
