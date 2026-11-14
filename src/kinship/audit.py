"""Deterministic evidence checks; cannot establish historical truth by itself."""
from __future__ import annotations

from dataclasses import asdict, dataclass
from collections import defaultdict
from collections.abc import Mapping

VALID_STATUSES = {
    "hypothesis", "single-source", "corroborated", "strongly-corroborated", "contradicted", "unresolved"
}
RELATION_TYPES = {"parent_of", "spouse_of", "sibling_of"}
VALID_VISIBILITY = {"private", "synthetic", "public_historical"}


@dataclass(frozen=True)
class Finding:
    level: str
    code: str
    detail: str

    def as_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class Audit:
    case_id: str
    findings: tuple[Finding, ...]

    @property
    def ok(self) -> bool:
        return not any(f.level == "error" for f in self.findings)

    def as_dict(self) -> dict:
        return {"case_id": self.case_id, "ok": self.ok, "findings": [f.as_dict() for f in self.findings]}


def audit_case(case: Mapping) -> Audit:
    findings: list[Finding] = []

    def error(code: str, msg: str) -> None:
        findings.append(Finding("error", code, msg))

    def warning(code: str, msg: str) -> None:
        findings.append(Finding("warning", code, msg))

    if not isinstance(case, Mapping):
        return Audit("unknown", (Finding("error", "case.type", "Expected a JSON object"),))
    case_id = str(case.get("case_id") or "unknown")
    if case.get("schema_version") != "0.1":
        error("schema.version", "schema_version must be '0.1'")
    visibility = case.get("visibility", "private")
    if not isinstance(visibility, str) or visibility not in VALID_VISIBILITY:
        error("case.visibility", f"visibility must be one of {sorted(VALID_VISIBILITY)}")
    if visibility != "synthetic" and not case.get("research_question"):
        warning("case.question", "Provide a specific research_question")

    entries = {}
    for plural in ("people", "artifacts", "claims"):
        rows = case.get(plural, [])
        if not isinstance(rows, list):
            error(f"{plural}.type", f"{plural} must be a list")
            rows = []
        mapped = {}
        for index, row in enumerate(rows):
            if not isinstance(row, Mapping):
                error(f"{plural}.row", f"{plural}[{index}] is not an object")
                continue
            value = row.get("id")
            if not isinstance(value, str) or not value.strip():
                error(f"{plural}.id", f"{plural}[{index}] must have nonempty string id")
                continue
            if value in mapped:
                error(f"{plural}.duplicate", f"Duplicate {plural} id {value}")
            else:
                mapped[value] = row
        entries[plural] = mapped

    people, artifacts, claims = entries["people"], entries["artifacts"], entries["claims"]
    for pid, person in people.items():
        names = person.get("names")
        if not isinstance(names, list) or not names:
            error("person.names", f"Person {pid} must have at least one name record")
        else:
            for name in names:
                if not isinstance(name, Mapping) or not isinstance(name.get("original"), str) or not name.get("original", "").strip():
                    error("person.name.original", f"Person {pid}: every name requires original text")
        if person.get("living") is not None and not isinstance(person.get("living"), bool):
            error("person.living", f"Person {pid}: living must be true, false or null")
        if visibility == "public_historical" and person.get("living") is not False:
            error("privacy.person", f"Public historical case contains living/unknown person {pid}")
    for aid, artifact in artifacts.items():
        if not artifact.get("independence_group") or not isinstance(artifact.get("independence_group"), str):
            error("artifact.independence", f"Artifact {aid} requires explicit independence_group")
        if not artifact.get("citation") or not isinstance(artifact.get("citation"), str):
            error("artifact.citation", f"Artifact {aid} requires a traceable citation")
        if visibility == "public_historical" and (not isinstance(artifact.get("access"), str) or artifact.get("access") in {"private", "restricted", "unknown"}):
            error("privacy.artifact", f"Public case references non-public artifact {aid}")
    edges = defaultdict(set)
    for cid, claim in claims.items():
        status = claim.get("status")
        if not isinstance(status, str) or status not in VALID_STATUSES:
            error("claim.status", f"Claim {cid}: unknown status {status!r}")
        subject = claim.get("subject_id")
        obj = claim.get("object_id")
        kind = claim.get("type")
        if not isinstance(subject, str) or subject not in people:
            error("claim.subject", f"Claim {cid}: missing person {subject}")
        if isinstance(kind, str) and kind in RELATION_TYPES:
            if not isinstance(obj, str) or obj not in people:
                error("claim.object", f"Claim {cid}: missing related person {obj}")
            elif subject == obj:
                error("claim.self_relation", f"Claim {cid}: self-relationship is not allowed")
            if kind == "parent_of" and isinstance(subject, str) and isinstance(obj, str) and subject in people and obj in people and subject != obj:
                edges[subject].add(obj)
        elif not isinstance(kind, str) or kind not in {"birth_place", "birth_date", "death_date", "other"}:
            error("claim.type", f"Claim {cid}: unknown claim type {kind!r}")
        elif not isinstance(claim.get("literal_value"), str) or not claim.get("literal_value").strip():
            error("claim.value", f"Claim {cid}: literal_value required for fact claims")

        ids = claim.get("artifact_ids", [])
        if not isinstance(ids, list) or not all(isinstance(x, str) for x in ids):
            error("claim.artifact_ids", f"Claim {cid}: artifact_ids must be list of strings")
            ids = []
        groups = set()
        for aid in ids:
            if aid not in artifacts:
                error("claim.artifact_missing", f"Claim {cid}: unknown artifact {aid}")
            else:
                group = artifacts[aid].get("independence_group")
                if isinstance(group, str) and group:
                    groups.add(group)
        if status == "single-source" and not groups:
            error("claim.source_required", f"Claim {cid}: single-source requires a cited artifact")
        if status == "corroborated" and len(groups) < 2:
            error("claim.independence", f"Claim {cid}: corroborated needs 2 independent source groups, got {len(groups)}")
        if status == "strongly-corroborated" and len(groups) < 3:
            error("claim.independence", f"Claim {cid}: strongly-corroborated needs 3 independent source groups, got {len(groups)}")
        if status == "contradicted" and not claim.get("notes"):
            warning("claim.conflict_note", f"Claim {cid}: explain the contradiction in notes")
        if status == "hypothesis" and ids:
            warning("claim.hypothesis_with_sources", f"Claim {cid}: sources exist; consider updating its evidence status after review")

    # Iterative DFS avoids RecursionError for long but valid ancestral chains.
    # Repeated source copies and unconfirmed parentage are checked above; a
    # directed parent cycle is structurally impossible regardless of status.
    visited: set[str] = set()
    active: set[str] = set()
    for root in people:
        if root in visited:
            continue
        active.add(root)
        stack = [(root, iter(edges[root]))]
        while stack:
            node, child_iter = stack[-1]
            try:
                child = next(child_iter)
            except StopIteration:
                stack.pop()
                active.discard(node)
                visited.add(node)
                continue
            if child in active:
                error("claim.parent_cycle", f"An impossible parent_of cycle was found at {child}")
            elif child not in visited:
                active.add(child)
                stack.append((child, iter(edges[child])))

    if not claims:
        warning("case.empty", "No claims to evaluate")
    return Audit(case_id, tuple(findings))
