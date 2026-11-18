"""Opt-in read-only archive metadata search; no family identity resolution.

The only enabled adapter is the documented Library of Congress JSON API.
External requests require user consent, are strictly host/path bounded, and
never import or approve historical claims without researcher review.
"""
from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha256
import json
from threading import Lock
from time import monotonic
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlsplit, urlunsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener


PROVIDER_ID = "loc"
PROVIDER_NAME = "Library of Congress"
COLLECTIONS = {"manuscripts": "/manuscripts/", "newspapers": "/newspapers/", "all": "/search/"}
MAX_PAGE = 5
PAGE_SIZE = 10
MIN_INTERVAL_SECONDS = 5  # < 20 calls/min published by Library of Congress.
MAX_RESPONSE_BYTES = 1_500_000


class ArchiveSearchError(ValueError):
    def __init__(self, code: str, message: str, http_status: int = 400, retry_after: int | None = None):
        super().__init__(message)
        self.code = code
        self.http_status = http_status
        self.retry_after = retry_after

    def as_dict(self):
        value = {"error": str(self), "code": self.code, "provider": PROVIDER_ID,
                 "record_search_executed": self.code not in {"consent_required", "invalid_query", "rate_limited"}}
        if self.retry_after is not None:
            value["retry_after_seconds"] = self.retry_after
        return value


class _NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise ArchiveSearchError("provider_redirect", "Archive API redirected the request; no further requests were made", 502)


def _transport(url: str) -> dict:
    request = Request(url, headers={"Accept": "application/json",
                                    "User-Agent": "GlobalKinshipResearch/0.4 (read-only archive research)"})
    opener = build_opener(_NoRedirect())
    try:
        with opener.open(request, timeout=9) as response:
            if "json" not in response.headers.get("Content-Type", "").lower():
                raise ArchiveSearchError("provider_format", "Archive returned a non-JSON response", 502)
            raw = response.read(MAX_RESPONSE_BYTES + 1)
            if len(raw) > MAX_RESPONSE_BYTES:
                raise ArchiveSearchError("provider_response_too_large", "Archive response exceeded the safety limit", 502)
    except HTTPError as exc:
        if exc.code == 429:
            raise ArchiveSearchError("provider_rate_limited", "Archive rate limit reached; retry later", 429) from None
        if exc.code in {401, 403}:
            raise ArchiveSearchError("provider_forbidden", "Archive denied access; no results were assumed", 502) from None
        raise ArchiveSearchError("provider_unavailable", "Archive returned a request error", 502) from None
    except (URLError, TimeoutError, OSError):
        raise ArchiveSearchError("provider_unavailable", "Archive cannot be reached; no results were assumed", 503) from None
    try:
        result = json.loads(raw)
    except (ValueError, UnicodeError):
        raise ArchiveSearchError("provider_format", "Archive response was not valid JSON", 502) from None
    if not isinstance(result, dict):
        raise ArchiveSearchError("provider_format", "Archive response was not a JSON object", 502)
    return result


def _plain(value, limit: int = 250) -> str:
    if isinstance(value, str):
        return value.strip()[:limit]
    if isinstance(value, list):
        return "; ".join(v.strip() for v in value if isinstance(v, str))[:limit]
    return ""


def _item_url(value) -> str | None:
    if not isinstance(value, str):
        return None
    try:
        url = urlsplit(value)
        if (url.scheme not in {"https", "http"} or
            url.hostname not in {"www.loc.gov", "loc.gov"} or
            url.username is not None or url.password is not None or url.port is not None or
            not url.path.startswith(("/item/", "/resource/"))):
            return None
        return urlunsplit(("https", "www.loc.gov", url.path, "", ""))
    except ValueError:
        return None


def _normalize(row: dict) -> dict | None:
    if not isinstance(row, dict):
        return None
    url = _item_url(row.get("id")) or _item_url(row.get("url"))
    if not url:
        return None
    title = _plain(row.get("title"), 300) or "Untitled catalog item"
    return {
        "provider_id": PROVIDER_ID,
        "record_id": url, "record_url": url,
        "source_id": "LOC-" + sha256(url.encode("utf-8")).hexdigest()[:16],
        "title_as_cataloged": title,
        "date_as_cataloged": _plain(row.get("date")) or None,
        "location_as_cataloged": _plain(row.get("location")) or None,
        "description": _plain(row.get("description"), 500),
        "contributors_as_cataloged": _plain(row.get("contributor"), 240),
        "rights_note": _plain(row.get("rights"), 300) or None,
        "access_restricted": row.get("access_restricted") if isinstance(row.get("access_restricted"), bool) else None,
        "kind": "archival_catalog_lead", "identity_verified": False,
        "record_original_inspected": False,
    }


def _normalize_response(payload, request: dict, endpoint: str) -> dict:
    if not isinstance(payload, dict) or not isinstance(payload.get("results"), list):
        raise ArchiveSearchError("provider_format", "Archive API response lacked a results list", 502)
    seen = set()
    records = []
    omitted = 0
    for raw in payload["results"][:PAGE_SIZE]:
        record = _normalize(raw)
        if not record:
            omitted += 1
            continue
        if record["record_id"] in seen:
            omitted += 1
            continue
        seen.add(record["record_id"])
        records.append(record)
    pagination = payload.get("pagination")
    meta = pagination if isinstance(pagination, dict) else {}
    total = meta.get("total")
    if not isinstance(total, int) or isinstance(total, bool) or total < 0:
        total = None
    has_next = bool(meta.get("next")) if meta else False
    if total is not None:
        has_next = has_next or total > request["page"] * PAGE_SIZE
    if request["page"] >= MAX_PAGE:
        has_next = False
    status = "results" if records else "no_results"
    if omitted:
        status = "partial" if records else "incomplete"
    return {
        "status": status, "provider_id": PROVIDER_ID, "provider": PROVIDER_NAME,
        "record_search_executed": True, "archive_endpoint": endpoint,
        "searched_at_utc": datetime.now(timezone.utc).isoformat(),
        "query": request, "results": records, "omitted_unusable_or_duplicate_rows": omitted,
        "pagination": {"page": request["page"], "page_size": PAGE_SIZE, "total": total, "has_next": has_next},
        "records_are": "Catalog metadata leads, NOT identity matches or proven relatives",
        "external_transfer_notice": "Search name, optional place and catalog year range were sent to Library of Congress",
    }


class LibraryOfCongressSearch:
    """One request per explicit search, bounded throttle, no hidden retries."""

    def __init__(self, *, fetch=None, clock=None, interval: float = MIN_INTERVAL_SECONDS):
        self.fetch = fetch or _transport
        self.clock = clock or monotonic
        self.interval = interval
        self._lock = Lock()
        self._previous = float("-inf")

    def search(self, *, name, place="", start_year=None, end_year=None,
               collection="manuscripts", page=1, consent=False) -> dict:
        if consent is not True:
            raise ArchiveSearchError("consent_required", "Please confirm the search terms may be sent to Library of Congress", 400)
        if not isinstance(name, str) or not 2 <= len(name.strip()) <= 160 or any(ord(c) < 32 for c in name):
            raise ArchiveSearchError("invalid_query", "Enter a search name of 2-160 characters", 400)
        if not isinstance(place, str) or len(place) > 100 or any(ord(c) < 32 for c in place):
            raise ArchiveSearchError("invalid_query", "Place must be plain text up to 100 characters", 400)
        if collection not in COLLECTIONS:
            raise ArchiveSearchError("invalid_query", "Unsupported Library of Congress collection", 400)
        if not isinstance(page, int) or isinstance(page, bool) or not 1 <= page <= MAX_PAGE:
            raise ArchiveSearchError("invalid_query", "Page must be between 1 and 5", 400)
        for value in (start_year, end_year):
            if value is not None and (not isinstance(value, int) or isinstance(value, bool) or not 1500 <= value <= 2100):
                raise ArchiveSearchError("invalid_query", "Catalog year must be between 1500 and 2100", 400)
        if start_year is not None and end_year is not None and start_year > end_year:
            raise ArchiveSearchError("invalid_query", "Start year must not be after end year", 400)
        if (start_year is None) != (end_year is None):
            raise ArchiveSearchError("invalid_query", "Supply both record years, or neither", 400)
        request = {"name": name.strip(), "place": place.strip(), "start_year": start_year,
                   "end_year": end_year, "collection": collection, "page": page}
        terms = " ".join(x for x in (request["name"], request["place"]) if x)
        params = {"fo": "json", "at": "results,pagination", "q": terms, "c": PAGE_SIZE, "sp": page}
        if start_year is not None:
            params["dates"] = f"{start_year}/{end_year}"
        endpoint = "https://www.loc.gov" + COLLECTIONS[collection]
        url = endpoint + "?" + urlencode(params)
        with self._lock:
            elapsed = self.clock() - self._previous
            if elapsed < self.interval:
                delay = max(1, int(self.interval - elapsed + 0.999))
                raise ArchiveSearchError("rate_limited", "Please wait before making another archive request", 429, delay)
            self._previous = self.clock()
        try:
            raw = self.fetch(url)
        except ArchiveSearchError:
            raise
        except (OSError, ValueError, TimeoutError):
            raise ArchiveSearchError("provider_unavailable", "Archive request failed; no results were assumed", 503) from None
        return _normalize_response(raw, request, endpoint)
