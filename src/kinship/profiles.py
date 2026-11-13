"""Culturally specific research leads, never an assertion that archives were searched.

Official landing pages were manually reviewed 2026-11-12. A reviewed landing
page is not permission to scrape, access restricted records, or redistribute data.
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
    status: str = "research-guide"
    upstream: str | None = None

    def as_dict(self) -> dict:
        return asdict(self)


REGISTRY: dict[str, Profile] = {
    "ex-ussr": Profile(
        code="ex-ussr", display_name="Former USSR / Russian Empire",
        languages=("ru", "uk", "be", "pl", "other historical local languages"),
        scripts=("Cyrl", "Latn", "other historical scripts"),
        calendar_cautions=("Julian/Gregorian calendar depends on the historical event and jurisdiction",),
        identity_cautions=("Patronymics, changing surnames and historical jurisdictions", "Never merge namesakes by name alone"),
        terms=("метрические книги", "ревизские сказки", "архив", "военные документы"),
        archives=(ArchiveLead("Ex-USSR Kinship Research — upstream guide", "https://github.com/DenisSergeevitch/ex-ussr-kinship-research", "Historical archive routes and evidence protocol; identify the actual custodian for each event"),),
        status="reference-adapter", upstream="DenisSergeevitch/ex-ussr-kinship-research",
    ),
    "vietnam": Profile(
        code="vietnam", display_name="Vietnam / Gia phả",
        languages=("vi", "literary Chinese", "Chữ Nôm"), scripts=("Latn", "Hani", "Hán-Nôm"),
        calendar_cautions=("Keep the literal lunar date and its historical calendar before any independently reviewed conversion",),
        identity_cautions=("Tên húy, tên tự and generation names can differ", "Village and district names may have changed", "Shared surname or clan is not a proven identity"),
        terms=("gia phả", "tộc phả", "Hán Nôm", "chi họ"),
        archives=(
            ArchiveLead("Institute of Hán-Nôm Studies", "https://hannom.vass.gov.vn/", "Historical manuscript and catalog leads; investigate copying rights"),
            ArchiveLead("Vietnamese archive orientation", "https://history.state.gov/countries/archives/vietnam", "Identify likely custodians and check today's official contact details"),
        ),
    ),
    "korea": Profile(
        code="korea", display_name="Korea / Jokbo",
        languages=("ko", "literary Chinese"), scripts=("Hang", "Hani"),
        calendar_cautions=("Lunisolar, regnal and sexagenary dates are not automatically converted",),
        identity_cautions=("Bon-gwan differs from surname", "Never guess Hanja from Hangul", "Hangnyeol generational syllables do not prove parentage"),
        terms=("족보", "본관", "호적", "항렬"),
        archives=(
            ArchiveLead("SKKU Korean Genealogy Database", "https://jokbo.skku.edu/ENG/intro/introduction.jsp", "Jokbo lineage records; verify record edition and page"),
            ArchiveLead("National Archives of Korea", "https://www.archives.go.kr/", "Public finding aids; check privacy and access eligibility"),
            ArchiveLead("Digital Jangseogak", "https://jsg.aks.ac.kr/", "Historical manuscripts and lineage-related collections"),
        ),
    ),
    "china": Profile(
        code="china", display_name="China / Jiapu & Zupu",
        languages=("zh", "historical literary Chinese"), scripts=("Hani",),
        calendar_cautions=("Reign years and lunar dates need source-specific conversion",),
        identity_cautions=("Generation poems and surname do not establish descent", "Different editions of the same jiapu may share a source lineage"),
        terms=("家谱", "族谱", "祠堂", "字辈"),
        archives=(ArchiveLead("Shanghai Library Genealogy Library", "https://www.library.sh.cn/special/GenealogyLibrary/", "Chinese genealogy catalog and family-history research guidance"),),
    ),
    "japan": Profile(
        code="japan", display_name="Japan / Historical records",
        languages=("ja",), scripts=("Jpan", "Hani", "Kana"),
        calendar_cautions=("Japanese era names, historical lunisolar dates and Western dates must remain distinct",),
        identity_cautions=("Koseki family registers have strict access rules", "Old household structure cannot be mapped to modern kinship automatically"),
        terms=("家系図", "戸籍", "家譜", "先祖"),
        archives=(ArchiveLead("National Archives of Japan — access and digital archive", "https://www.archives.go.jp/english/gettingstarted/access.html", "Catalog of historical government records, distinct from protected personal koseki"),),
    ),
    "taiwan": Profile(
        code="taiwan", display_name="Taiwan / Historical family records",
        languages=("zh", "ja", "historical local languages"), scripts=("Hani", "Jpan", "Latn"),
        calendar_cautions=("Japanese-era and Chinese-era dates require jurisdiction-specific treatment",),
        identity_cautions=("Language of an index may differ from the original document", "Household and migration records may contain living relatives"),
        terms=("族譜", "家譜", "戶籍", "契約"),
        archives=(ArchiveLead("Academia Sinica — Taiwan Historical Archives", "https://archives.ith.sinica.edu.tw/services_con_en.php?no=9", "Catalogs, family papers and historical passport records; per-collection rights"),),
    ),
    "philippines": Profile(
        code="philippines", display_name="Philippines / Civil & parish records",
        languages=("fil", "es", "en", "local languages"), scripts=("Latn",),
        calendar_cautions=("Use the original parish or civil record date; be alert to historical calendars and record transcription",),
        identity_cautions=("Spanish-period surnames and locality matter", "Same-name records across provinces are not one identity"),
        terms=("registros civiles", "partidas de bautismo", "registro de matrimonio", "archives"),
        archives=(
            ArchiveLead("National Archives of the Philippines — record requests", "https://reference.nationalarchives.gov.ph/oprequest?page=landing-page", "Historical civil/parish record requests; access requires an application", "request-only"),
            ArchiveLead("National Archives of the Philippines — founding of towns", "https://erecciones.nationalarchives.gov.ph/oprequest", "Historical locality, parish and municipality catalogs"),
        ),
    ),
    "thailand": Profile(
        code="thailand", display_name="Thailand / National archives",
        languages=("th",), scripts=("Thai",),
        calendar_cautions=("Buddhist Era and Gregorian years must be recorded distinctly",),
        identity_cautions=("Names, titles, patronymic conventions and village boundaries can vary by period",),
        terms=("จดหมายเหตุ", "ทะเบียน", "บรรพบุรุษ", "ประวัติครอบครัว"),
        archives=(ArchiveLead("National Archives of Thailand", "https://www.nat.go.th/", "Historical record catalog and onsite research; review the institution's search procedures"),),
    ),
    "indonesia": Profile(
        code="indonesia", display_name="Indonesia / Arsip Nasional",
        languages=("id", "nl", "regional languages"), scripts=("Latn", "Javanese and other local scripts"),
        calendar_cautions=("Record colonial or local calendar systems as found in each source",),
        identity_cautions=("Colonial jurisdiction and varying naming practices require local context",),
        terms=("arsip keluarga", "silsilah", "catatan sipil", "JIKN"),
        archives=(ArchiveLead("ANRI — SIKN/JIKN archival information", "https://www.anri.go.id/en/public-services/national-archival-information-system-and-network-services", "Government and regional archive finding aids; verify the individual node's access"),),
    ),
    "malaysia": Profile(
        code="malaysia", display_name="Malaysia / Historical archives",
        languages=("ms", "en", "zh", "ta", "other local languages"), scripts=("Latn", "Hani", "Taml"),
        calendar_cautions=("Traditional, Islamic and Gregorian date systems may coexist; preserve originals",),
        identity_cautions=("Naming customs vary by community; do not impose a universal surname model",),
        terms=("salasilah", "arkib", "rekod kelahiran", "family history"),
        archives=(ArchiveLead("National Archives of Malaysia — Online Finding Aids", "https://ofa.arkib.gov.my/ofa/group/general/1", "Catalog/finding aids; some record access requires registration"),),
    ),
    "india": Profile(
        code="india", display_name="India / Historical archives",
        languages=("hi", "en", "ur", "regional languages"), scripts=("Deva", "Latn", "Arab", "other Indic scripts"),
        calendar_cautions=("Regional, regnal and traditional calendars require evidence-backed conversion",),
        identity_cautions=("Personal naming and lineage conventions vary by region and community", "Place and district changes require date-specific research"),
        terms=("वंशावली", "अभिलेख", "parish register", "land records"),
        archives=(ArchiveLead("National Archives of India — Abhilekh Patal", "https://www.nationalarchives.nic.in/en/online-portal-abhilekh-patal", "Government archival catalog and digitized finding aids; not a national civil registry"),),
    ),
}


def get_profile(code: str) -> Profile:
    if not isinstance(code, str):
        raise ValueError("Region code must be text")
    try:
        return REGISTRY[code.lower()]
    except KeyError as exc:
        raise ValueError(f"Unknown region {code!r}; choose: {', '.join(sorted(REGISTRY))}") from exc
