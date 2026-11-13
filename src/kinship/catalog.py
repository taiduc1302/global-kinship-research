"""Explicit metadata about public archival *leads*, not copied archive records."""
from __future__ import annotations

from kinship.profiles import REGISTRY, get_profile

REVIEWED_ON = "2026-11-12"


def list_archive_leads(region: str | None = None) -> list[dict]:
    """Return curated sources without contacting or scraping their websites."""
    profiles = [get_profile(region)] if region else [REGISTRY[x] for x in sorted(REGISTRY)]
    result = []
    for profile in profiles:
        for idx, source in enumerate(profile.archives, 1):
            result.append({
                "source_id": f"{profile.code}-{idx:02d}",
                "region": profile.code,
                "institution": source.name,
                "url": source.url,
                "purpose": source.purpose,
                "access": source.access,
                "record_search_executed": False,
                "catalog_reviewed_on": REVIEWED_ON,
                "terms_of_reuse_verified": False,
            })
    return result
