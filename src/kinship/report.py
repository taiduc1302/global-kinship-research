"""Generate a reviewable plain Markdown evidence packet from a local case."""
from __future__ import annotations

from collections.abc import Mapping

from kinship.audit import Audit


def format_report(case: Mapping, audit: Audit) -> str:
    if not audit.ok:
        raise ValueError("Refusing report with audit errors; run 'kinship audit' first")
    rows = [
        f"# Case {case.get('case_id', 'unknown')}",
        "",
        "**Research question:** " + str(case.get("research_question", "not provided")),
        "",
        "**Evidence notice:** An audit pass checks structure, not historical truth or identity. No relationship is automatically approved.",
        "",
        "## Claims",
    ]
    artifacts = {a["id"]: a for a in case.get("artifacts", [])}
    people = {p["id"]: p for p in case.get("people", [])}
    for c in case.get("claims", []):
        subj = people.get(c.get("subject_id"), {}).get("names", [{}])[0].get("original", c.get("subject_id"))
        obj = (people.get(c.get("object_id"), {}).get("names", [{}])[0].get("original", c.get("object_id"))
               if c.get("object_id") else c.get("literal_value", ""))
        rows.extend(["", f"### {c['id']} — {c.get('type')} [{c.get('status')}]", "", f"{subj} → {obj}", ""])
        for aid in c.get("artifact_ids", []):
            a = artifacts[aid]
            rows.append(f"- `{aid}`: {a['citation']} (independence group `{a['independence_group']}`)")
        if c.get("notes"):
            rows.append("- Analyst notes: " + str(c["notes"]))
    if audit.findings:
        rows.extend(["", "## Audit notices", ""])
        rows.extend(f"- {f.level}: `{f.code}` — {f.detail}" for f in audit.findings)
    rows.extend(["", "## Next steps", "", "Manually verify original documents, historical jurisdictions, translations and contradictory evidence.", ""])
    return "\n".join(rows)
