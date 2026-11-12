"""Generate a transparent OFFLINE research plan, not purported search results."""
from __future__ import annotations

from datetime import date
from kinship.names import query_variants
from kinship.profiles import get_profile


def make_search_plan(region: str, name: str, variants: list[str] | None = None) -> dict:
    profile = get_profile(region)
    if not name or not name.strip():
        raise ValueError("Name is required")
    names = query_variants(name, variants)
    queries = [f"{n} {term}" for n in names for term in profile.terms[:2]]
    return {
        "generated_on": date.today().isoformat(),
        "region": profile.code,
        "status": "draft-not-searched",
        "subject_name_original": name,
        "variants_supplied_or_folded": names,
        "queries_to_try": list(dict.fromkeys(queries)),
        "archive_leads": [a.__dict__ for a in profile.archives],
        "checks_before_conclusion": [
            "Resolve event-date historical jurisdiction and record custodian",
            "Preserve original script and literal dates; record calendar conversion method",
            "Keep similarly named individuals separate until distinguishing evidence appears",
            "Record exact archive references and the outcome of failed searches",
            "Get permission and check terms before accessing or reproducing records",
        ],
        "limitations": "No archive searched; no identity matched; no records downloaded",
    }
