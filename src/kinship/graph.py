"""Relationship graph over local claims; graph geometry is not evidence of kinship."""
from __future__ import annotations

from collections import Counter
from collections.abc import Mapping

from kinship.audit import RELATION_TYPES
from kinship.audit import audit_case


def require_valid_case(case):
    checked = audit_case(case)
    if not checked.ok:
        raise ValueError("Case audit failed: " + ", ".join(sorted({f.code for f in checked.findings if f.level == "error"})))


def relationship_graph(case: Mapping) -> dict:
    """Expose separate people and claims; do not infer or merge identity."""
    require_valid_case(case)
    people = case.get("people", [])
    artifacts = {a["id"]: a for a in case.get("artifacts", [])}
    counts = Counter(c["subject_id"] for c in case.get("claims", []))
    counts.update(c["object_id"] for c in case.get("claims", []) if isinstance(c.get("object_id"), str))
    nodes = [{"id": p["id"], "label": p["names"][0]["original"],
              "living": p.get("living"), "claims": counts[p["id"]]}
             for p in people]
    edges = []
    for c in case.get("claims", []):
        if c.get("type") not in RELATION_TYPES:
            continue
        aids = c.get("artifact_ids", [])
        groups = sorted({artifacts[aid]["independence_group"] for aid in aids})
        edges.append({"claim_id": c["id"], "from": c["subject_id"], "to": c["object_id"],
                      "relationship": c["type"], "status": c["status"], "source_ids": list(aids),
                      "independent_source_groups": groups, "original_family": c.get("gedcom_family"),
                      "warning": "Claim status measures structural evidence, not historical proof"})
    return {"case_id": case.get("case_id", "unknown"), "nodes": nodes, "edges": edges,
            "notice": "Unverified relationship graph: genealogical truth, biological parentage and identity require human assessment",
            "external_search_executed": False}
