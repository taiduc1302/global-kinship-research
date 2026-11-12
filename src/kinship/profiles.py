"""Research region profiles: curated search guides, not live scraping adapters.

Profiles intentionally avoid suggesting that archival access is automatic.
Each link is a research lead and must be rechecked when used for a real case.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class ArchiveLead:
    name: str
    url: str
    purpose: str
    access: str = "manual-review"


@dataclass(frozen=True)
class Profile:
    code: str
    display_name: str
    languages: tuple[str, ...]
    scripts: tuple[str, ...]
    calendar_cautions: tuple[str, ...]
    identity_cautions: tuple[str, ...]
    terms: tuple[str, ...]
    archives: tuple[ArchiveLead, ...]
    status: str
    upstream: str | None = None

    def as_dict(self) -> dict:
        return asdict(self)


REGISTRY: dict[str, Profile] = {
    "ex-ussr": Profile(
        code="ex-ussr",
        display_name="Former USSR / Russian Empire",
        languages=("ru", "uk", "be", "pl", "other historic local languages"),
        scripts=("Cyrl", "Latn", "other historical scripts"),
        calendar_cautions=("Julian vs Gregorian depending on date and jurisdiction",),
        identity_cautions=("Patronymics and gendered surnames", "Historical jurisdictions and border changes", "Do not merge namesakes by name alone"),
        terms=("метрические книги", "ревизские сказки", "архив", "военные документы"),
        archives=(
            ArchiveLead("ex-USSR Kinship Research upstream source guide", "https://github.com/DenisSergeevitch/ex-ussr-kinship-research", "Regional reference and evidence workflow; verify the specific archive custodian"),
        ),
        status="reference-adapter",
        upstream="DenisSergeevitch/ex-ussr-kinship-research",
    ),
    "vietnam": Profile(
        code="vietnam",
        display_name="Vietnam / Gia phả",
        languages=("vi", "historical literary Chinese", "Chữ Nôm"),
        scripts=("Latn", "Hani", "Hán-Nôm"),
        calendar_cautions=("Lunar dates must retain the source text and conversion method",),
        identity_cautions=("Họ - tên đệm - tên conventions", "Tên húy, tên tự and family-generation names can differ", "Trùng tên: avoid merging namesakes", "Historical district and village boundaries"),
        terms=("gia phả", "tộc phả", "họ", "chi", "giỗ", "Hán Nôm"),
        archives=(
            ArchiveLead("Institute of Hán-Nôm Studies", "https://hannom.vass.gov.vn/", "Search historical documents and collection descriptions; some scans require an onsite request"),
            ArchiveLead("Vietnamese archives overview (US State Department)", "https://history.state.gov/countries/archives/vietnam", "Determine relevant archives and access restrictions; verify with the institution"),
        ),
        status="research-guide",
    ),
    "korea": Profile(
        code="korea",
        display_name="Korea / Jokbo",
        languages=("ko", "literary Chinese"),
        scripts=("Hang", "Hani"),
        calendar_cautions=("Traditional lunisolar dates, regnal eras and sexagenary cycle require explicit conversion notes",),
        identity_cautions=("Bon-gwan / ancestral seat is distinct from surname", "Hanja and Hangul must be preserved separately", "Generational syllables do not prove kinship"),
        terms=("족보", "가계", "본관", "항렬", "호적"),
        archives=(
            ArchiveLead("SKKU Korean Genealogy Database", "https://jokbo.skku.edu/ENG/intro/introduction.jsp", "Search curated genealogical records and lineage metadata"),
            ArchiveLead("National Archives of Korea", "https://www.archives.go.kr/", "Government record discovery; access depends on record classification"),
            ArchiveLead("Digital Jangseogak", "https://jsg.aks.ac.kr/", "Classical Korean historical sources and archival images"),
        ),
        status="research-guide",
    ),
}


def get_profile(code: str) -> Profile:
    try:
        return REGISTRY[code.lower()]
    except KeyError as exc:
        raise ValueError(f"Unknown region {code!r}; choose: {', '.join(sorted(REGISTRY))}") from exc
