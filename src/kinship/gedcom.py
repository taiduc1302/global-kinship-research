"""Conservative, local-only GEDCOM 5.5.1 to evidence-case import.

This is a deliberately bounded interchange subset. A GEDCOM tree is a *lead*,
not independent proof of ancestry. Sources are citations supplied by the file,
not documents opened or authenticated by this importer.
"""
from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import re

from kinship.audit import audit_case

MAX_BYTES = 512_000
MAX_LINES = 25_000
_LINE = re.compile(r"^(\d+) (?:(@[^@\s]+@) )?([A-Za-z0-9_]+)(?: (.*))?$")
_XREF = re.compile(r"^@[^@\s]+@$", re.ASCII)


@dataclass
class Record:
    level: int
    tag: str
    value: str = ""
    xref: str | None = None
    children: list["Record"] = field(default_factory=list)


def _children(record: Record, tag: str) -> list[Record]:
    return [item for item in record.children if item.tag == tag]


def _first(record: Record, tag: str) -> Record | None:
    return next((item for item in record.children if item.tag == tag), None)


def _text(record: Record | None) -> str:
    if not record:
        return ""
    content = record.value
    for item in record.children:
        if item.tag == "CONT":
            content += "\n" + item.value
        elif item.tag == "CONC":
            content += item.value
    return content.strip()


def _records(text: str) -> list[Record]:
    if not isinstance(text, str):
        raise ValueError("GEDCOM input must be UTF-8 text")
    if len(text.encode("utf-8")) > MAX_BYTES:
        raise ValueError("GEDCOM input is too large (512 KB limit)")
    if "\x00" in text:
        raise ValueError("GEDCOM input contains a NUL byte")
    lines = text.lstrip("\ufeff").splitlines()
    if len(lines) > MAX_LINES:
        raise ValueError("Too many GEDCOM lines")
    roots: list[Record] = []
    stack: list[Record] = []
    for number, line in enumerate(lines, 1):
        if not line.strip():
            continue
        if len(line) > 16_000:
            raise ValueError(f"GEDCOM line {number} exceeds the safety limit")
        matched = _LINE.fullmatch(line)
        if not matched:
            raise ValueError(f"Invalid GEDCOM structure at line {number}")
        level = int(matched.group(1))
        if level > 12:
            raise ValueError("GEDCOM nesting is too deep")
        tag = matched.group(3).upper()
        xref = matched.group(2)
        if xref and level != 0:
            raise ValueError(f"Unexpected record ID at line {number}")
        record = Record(level, tag, matched.group(4) or "", xref)
        while stack and stack[-1].level >= level:
            stack.pop()
        if level == 0:
            roots.append(record)
        elif not stack or stack[-1].level != level - 1:
            raise ValueError(f"Invalid level transition at line {number}")
        else:
            stack[-1].children.append(record)
        stack.append(record)
    if not roots or roots[0].tag != "HEAD" or roots[-1].tag != "TRLR":
        raise ValueError("GEDCOM must begin with HEAD and end with TRLR")
    if len([r for r in roots if r.tag == "HEAD"]) != 1 or len([r for r in roots if r.tag == "TRLR"]) != 1:
        raise ValueError("GEDCOM HEAD/TRLR records must be unique")
    head = roots[0]
    gedc = _first(head, "GEDC")
    version = _text(_first(gedc, "VERS")) if gedc else ""
    if version != "5.5.1":
        raise ValueError(f"Only GEDCOM 5.5.1 is supported; found {version or 'unidentified version'}")
    charset = _text(_first(head, "CHAR")).upper().replace("-", "")
    if charset and charset not in {"UTF8", "ASCII"}:
        raise ValueError(f"Unsupported GEDCOM character set {charset}; export as UTF-8 first")
    if charset == "ASCII" and not text.isascii():
        raise ValueError("GEDCOM declares ASCII but contains non-ASCII characters")
    return roots[1:-1]


def import_gedcom(text: str, *, case_id: str, question: str, region: str = "vietnam") -> dict:
    """Import source references and family structures without claiming proof.

    Returns a case with visibility=private, even for historical source GEDCOMs.
    Unsupported facts and media are intentionally not imported; see warnings.
    """
    if not isinstance(case_id, str) or not case_id.strip() or len(case_id) > 100:
        raise ValueError("A nonempty case_id (max 100 characters) is required")
    if not isinstance(question, str) or not question.strip() or len(question) > 2000:
        raise ValueError("A nonempty research question (max 2000 characters) is required")
    from kinship.profiles import get_profile
    get_profile(region)
    records = _records(text)
    record_by_xref: dict[str, Record] = {}
    for item in records:
        if item.tag not in {"INDI", "FAM", "SOUR", "SUBM", "NOTE", "OBJE", "REPO"}:
            raise ValueError(f"Unsupported top-level record type {item.tag}")
        if item.tag in {"INDI", "FAM", "SOUR"}:
            if not item.xref or not _XREF.fullmatch(item.xref):
                raise ValueError(f"{item.tag} record needs a unique pointer")
            if item.xref in record_by_xref:
                raise ValueError(f"Duplicate GEDCOM pointer {item.xref}")
            record_by_xref[item.xref] = item
    people_records = [r for r in records if r.tag == "INDI"]
    families = [r for r in records if r.tag == "FAM"]
    if len(people_records) > 2_000 or len(families) > 2_000:
        raise ValueError("Too many individual or family records for the local import")
    person_ids = {r.xref: "GD-P" + str(index) for index, r in enumerate(people_records, 1)}
    artifacts: list[dict] = []
    citations: dict[tuple[str, str], str] = {}
    warnings: list[str] = []

    def cite(node: Record) -> tuple[str, bool]:
        pointer = node.value.strip()
        page = _text(_first(node, "PAGE"))
        if not pointer:
            raise ValueError("Blank GEDCOM SOUR citation cannot be used as evidence")
        if _XREF.fullmatch(pointer):
            source = record_by_xref.get(pointer)
            if source is None or source.tag != "SOUR":
                raise ValueError(f"Missing GEDCOM source record {pointer}")
            title = _text(_first(source, "TITL")) or _text(_first(source, "ABBR"))
            label = title or f"Unidentified GEDCOM source {pointer} (needs citation review)"
            group = "GEDCOM-SOURCE:" + pointer
            traceable = bool(title)
        else:
            label = pointer
            group = "GEDCOM-INLINE:" + hashlib.sha256(pointer.encode("utf-8")).hexdigest()[:20]
            traceable = bool(pointer.strip())
        key = (group, page)
        if key not in citations:
            aid = "GD-A" + str(len(artifacts) + 1)
            citations[key] = aid
            artifacts.append({"id": aid, "citation": label + ("; PAGE " + page if page else ""),
                              "independence_group": group, "access": "unknown", "gedcom_source_pointer": pointer,
                              "notes": "GEDCOM citation only; underlying document was not inspected"})
        return citations[key], traceable

    def sources(node: Record) -> tuple[list[str], bool]:
        refs = [cite(n) for n in _children(node, "SOUR")]
        return list(dict.fromkeys(a for a, _ in refs)), bool(refs) and all(known for _, known in refs)

    people: list[dict] = []
    claims: list[dict] = []

    for record in people_records:
        names = []
        for item in _children(record, "NAME"):
            raw = _text(item)
            display = " ".join(raw.replace("/", "").split())
            if display:
                names.append({"original": display, "gedcom_raw": raw})
        if not names:
            names = [{"original": "Unnamed individual (" + str(record.xref) + ")"}]
            warnings.append(f"Individual {record.xref} has no name")
        death = _first(record, "DEAT")
        deceased = death is not None and (death.value.strip().upper() == "Y" or bool(_first(death, "DATE"))
                                          or bool(_first(death, "PLAC")))
        sex = _text(_first(record, "SEX")).upper()
        person = {"id": person_ids[record.xref], "names": names,
                  "living": False if deceased else None, "gedcom_xref": record.xref}
        if sex in {"M", "F", "U"}:
            person["sex"] = sex
        people.append(person)
        for tag, values in (("BIRT", (("DATE", "birth_date"), ("PLAC", "birth_place"))),
                            ("DEAT", (("DATE", "death_date"), ("PLAC", "other")))):
            for event in _children(record, tag):
                cited, traceable = sources(event)
                for fact_tag, fact_type in values:
                    for fact in _children(event, fact_tag):
                        literal = _text(fact)
                        if not literal:
                            continue
                        claims.append({"id": "GD-C" + str(len(claims) + 1),
                                       "subject_id": person_ids[record.xref], "type": fact_type,
                                       "literal_value": ("Death place: " + literal if tag == "DEAT" and fact_tag == "PLAC" else literal),
                                       "status": "single-source" if cited and traceable else "hypothesis",
                                       "artifact_ids": cited, "notes": "Imported GEDCOM fact; verify against originals"})
        if _first(record, "OBJE") or _first(record, "RESI"):
            warnings.append(f"Media or residence details for {record.xref} were not imported")

    for fam in families:
        parents = []
        for role in ("HUSB", "WIFE"):
            for item in _children(fam, role):
                if item.value not in person_ids:
                    raise ValueError(f"Family {fam.xref} refers to missing parent {item.value}")
                parents.append((person_ids[item.value], role))
        children = []
        for item in _children(fam, "CHIL"):
            if item.value not in person_ids:
                raise ValueError(f"Family {fam.xref} refers to missing child {item.value}")
            children.append(person_ids[item.value])
        family_sources, _ = sources(fam)
        for parent_id, role in parents:
            for child_id in children:
                claims.append({"id": "GD-C" + str(len(claims) + 1), "subject_id": parent_id,
                               "object_id": child_id, "type": "parent_of", "status": "hypothesis",
                               "artifact_ids": family_sources, "notes": "Imported GEDCOM family link; genetic/legal parentage not established",
                               "gedcom_family": fam.xref, "gedcom_parent_role": role})
        if len(parents) == 2:
            claims.append({"id": "GD-C" + str(len(claims) + 1),
                           "subject_id": parents[0][0], "object_id": parents[1][0], "type": "spouse_of",
                           "status": "hypothesis", "artifact_ids": family_sources,
                           "notes": "GEDCOM family structure; marriage and dates not independently verified",
                           "gedcom_family": fam.xref})

    case = {"schema_version": "0.1", "case_id": case_id.strip(), "visibility": "private",
            "research_question": question.strip(), "regions": [region],
            "people": people, "artifacts": artifacts, "claims": claims, "search_log": [],
            "import_metadata": {"format": "GEDCOM 5.5.1", "source": "user-supplied local file",
                                "note": "Relationships are unverified hypotheses; citations are GEDCOM assertions, not archival authentication",
                                "warnings": warnings[:100]}}
    audit = audit_case(case)
    if not audit.ok:
        raise ValueError("Imported GEDCOM has invalid or cyclic links: " + ", ".join(sorted({f.code for f in audit.findings if f.level == "error"})))
    return case
