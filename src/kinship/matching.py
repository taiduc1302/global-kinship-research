"""Evidence-first comparison of catalog leads to local people.

No identity scores, merges, automatic claims, network requests or generated ancestry.
Only supplied names and directly cited source facts are considered. Catalog
metadata is not a birth, death, marriage or parentage record.
"""
from __future__ import annotations

from collections.abc import Mapping
import unicodedata

MAX_NAME_LENGTH = 256


def _clean(value: object) -> str:
    return " ".join(value.strip().split()) if isinstance(value, str) else ""


def _fold(value: str) -> str:
    return unicodedata.normalize("NFC", _clean(value)).casefold()


def _person_names(person: Mapping) -> list[str]:
    names = person.get("names", [])
    if not isinstance(names, list):
        raise ValueError("Person names must be a list")
    result: list[str] = []
    for entry in names:
        if not isinstance(entry, Mapping):
            raise ValueError("Person name entry must be an object")
        value = _clean(entry.get("original"))
        if value and len(value) <= MAX_NAME_LENGTH:
            result.append(value)
        # A transliteration is compared only when it was supplied in the case;
        # it must not be synthesized from a surname or guessed Hanja/Nom.
        supplied = _clean(entry.get("transliteration"))
        if supplied and len(supplied) <= MAX_NAME_LENGTH:
            result.append(supplied)
    return list(dict.fromkeys(result))


def compare_catalog_lead(person: Mapping, record: Mapping,
                         *, cited_source_groups: list[str] | None = None) -> dict:
    """Return review signals only. No probabilistic or proven-identity label.

    `record` must use online.py's normalized lead contract. This comparison
    does not authenticate a source or resolve identity. A search result is not
    an independent witness just because it is a different web page.
    """
    if not isinstance(person, Mapping) or not isinstance(record, Mapping):
        raise ValueError("Person and record must be objects")
    person_id = person.get("id")
    record_id = record.get("record_id")
    source_id = record.get("source_id")
    if not isinstance(person_id, str) or not person_id.strip():
        raise ValueError("Person requires an ID")
    if not isinstance(record_id, str) or not record_id.strip():
        raise ValueError("Catalog lead requires a record ID")
    if not isinstance(source_id, str) or not source_id.strip():
        raise ValueError("Catalog lead requires a source ID")
    if record.get("kind") != "archival_catalog_lead":
        raise ValueError("Only normalized archival catalog leads can be compared")
    if record.get("identity_verified") is True:
        raise ValueError("Catalog leads cannot assert verified identity")
    names = _person_names(person)
    title = _clean(record.get("title_as_cataloged"))
    contributor = _clean(record.get("contributors_as_cataloged"))
    haystack = [title, contributor]
    signals = []
    for name in names:
        literal = any(name in candidate for candidate in haystack)
        casefold = any(_fold(name) in _fold(candidate) for candidate in haystack if candidate)
        if literal:
            signals.append({"type": "literal_name_mention", "name_as_supplied": name,
                            "interpretation": "Catalog metadata contains the supplied name; person identity is unverified"})
        elif casefold:
            signals.append({"type": "casefold_name_mention", "name_as_supplied": name,
                            "interpretation": "Case-insensitive catalog mention only; inspect original script"})
    if not signals:
        signals.append({"type": "name_not_present_in_catalog_fields",
                        "interpretation": "No literal supplied-name mention; search query relevance may be indirect"})
    if cited_source_groups is not None and (not isinstance(cited_source_groups, list)
                                            or any(not isinstance(x, str) for x in cited_source_groups)):
        raise ValueError("Source groups must be a list of strings")
    return {
        "person_id": person_id,
        "provider_id": record.get("provider_id"),
        "record_id": record_id,
        "source_id": source_id,
        "signals": signals,
        "catalog_date": record.get("date_as_cataloged"),
        "catalog_place": record.get("location_as_cataloged"),
        "existing_independent_source_groups": sorted(set(cited_source_groups or [])),
        "new_independent_source_count": 0,
        "identity_verified": False,
        "claim_created": False,
        "merge_performed": False,
        "review_required": True,
        "notice": ("Archive catalog descriptions are research leads, not proof of the same person, "
                   "life events, kinship, or independent primary evidence. Review the original "
                   "record, its date, place, provenance and duplicate editions manually."),
    }