"""Offline tests for approved archive metadata search and zero-leak invariants."""
from __future__ import annotations

import json
from pathlib import Path
import sys
import threading
import unittest
from urllib.error import HTTPError
from urllib.parse import parse_qs, urlsplit
from urllib.request import Request, urlopen

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from kinship.online import (ArchiveSearchError, LibraryOfCongressSearch,
                            _NoRedirect, _normalize_response)
from kinship.web import Workbench


EXAMPLE = {
    "results": [
        {"id": "http://www.loc.gov/item/2024000001/", "title": "Synthetic manuscript finding aid",
         "date": "1902", "description": ["Invented metadata only"], "location": ["New York"],
         "contributor": ["Catalog contributor"], "access_restricted": False},
        {"id": "http://www.loc.gov/item/2024000001/", "title": "Duplicate mock page"},
        {"id": "https://malicious.example/secret", "title": "Do not render this external URL"},
        {"id": "https://www.loc.gov/item/2024000002/", "title": "Second synthetic item"},
    ],
    "pagination": {"total": 14, "next": "https://www.loc.gov/manuscripts/?sp=2"},
}


class ProviderTests(unittest.TestCase):
    def test_real_endpoint_shape_and_utf8_query_encoded(self):
        seen = []
        client = LibraryOfCongressSearch(fetch=lambda url: (seen.append(url), EXAMPLE)[1], interval=0)
        result = client.search(name="Nguy\u1ec5n V\u0103n An", place="H\u00e0 N\u1ed9i", start_year=1880,
                               end_year=1950, collection="manuscripts", page=1, consent=True)
        self.assertEqual(len(seen), 1)
        parsed = urlsplit(seen[0])
        self.assertEqual(parsed.scheme, "https")
        self.assertEqual(parsed.hostname, "www.loc.gov")
        self.assertEqual(parsed.path, "/manuscripts/")
        args = parse_qs(parsed.query)
        self.assertEqual(args["q"], ["Nguy\u1ec5n V\u0103n An H\u00e0 N\u1ed9i"])
        self.assertEqual(args["dates"], ["1880/1950"])
        self.assertEqual(args["fo"], ["json"])
        self.assertEqual(args["c"], ["10"])
        self.assertEqual(result["status"], "partial")
        self.assertEqual(len(result["results"]), 2)
        self.assertFalse(result["results"][0]["identity_verified"])
        self.assertFalse(result["results"][0]["record_original_inspected"])
        self.assertEqual(result["results"][0]["record_url"], "https://www.loc.gov/item/2024000001/")
        self.assertEqual(result["omitted_unusable_or_duplicate_rows"], 2)
        self.assertTrue(result["pagination"]["has_next"])

    def test_explicit_consent_required_before_any_request(self):
        calls = []
        client = LibraryOfCongressSearch(fetch=lambda url: calls.append(url), interval=0)
        with self.assertRaises(ArchiveSearchError) as ctx:
            client.search(name="Jason Huang", consent=False)
        self.assertEqual(ctx.exception.code, "consent_required")
        self.assertEqual(calls, [])

    def test_bad_inputs_never_contact_archive(self):
        calls = []
        client = LibraryOfCongressSearch(fetch=lambda url: calls.append(url), interval=0)
        cases = [{"name": "x"}, {"name": "a\nsecret"}, {"name": "John", "place": 24},
                 {"name": "John", "collection": "https://example.com"},
                 {"name": "John", "page": 0}, {"name": "John", "page": True},
                 {"name": "John", "start_year": 1900},
                 {"name": "John", "start_year": 2010, "end_year": 1900},
                 {"name": "John", "start_year": "1900", "end_year": 1950}]
        for params in cases:
            with self.subTest(params=params), self.assertRaises(ArchiveSearchError):
                client.search(consent=True, **params)
        self.assertEqual(calls, [])

    def test_bounded_throttle_does_not_retry_or_contact(self):
        now = [120.]
        calls = []
        client = LibraryOfCongressSearch(fetch=lambda url: (calls.append(url), {"results": []})[1],
                                        clock=lambda: now[0], interval=5)
        client.search(name="Jason Huang", consent=True)
        with self.assertRaises(ArchiveSearchError) as ctx:
            client.search(name="Jason Huang", consent=True)
        self.assertEqual(ctx.exception.code, "rate_limited")
        self.assertEqual(ctx.exception.http_status, 429)
        self.assertEqual(len(calls), 1)
        now[0] += 5
        client.search(name="Jason Huang", consent=True)
        self.assertEqual(len(calls), 2)

    def test_empty_results_not_confused_with_provider_error(self):
        client = LibraryOfCongressSearch(fetch=lambda url: {"results": [], "pagination": {"total": 0}}, interval=0)
        self.assertEqual(client.search(name="fictional name", consent=True)["status"], "no_results")
        invalid = LibraryOfCongressSearch(fetch=lambda url: {"error": "temporarily unavailable"}, interval=0)
        with self.assertRaises(ArchiveSearchError) as ctx:
            invalid.search(name="fictional name", consent=True)
        self.assertEqual(ctx.exception.code, "provider_format")

    def test_network_failure_not_zero_records(self):
        def fail(url):
            raise OSError("blocked outbound DNS")
        client = LibraryOfCongressSearch(fetch=fail, interval=0)
        with self.assertRaises(ArchiveSearchError) as ctx:
            client.search(name="Jason Huang", consent=True)
        self.assertEqual(ctx.exception.code, "provider_unavailable")
        self.assertEqual(ctx.exception.http_status, 503)

    def test_reject_untrusted_links_and_keep_independent_ids(self):
        rows = {"results": [{"id": "https://www.loc.gov.evil.test/item/xxx", "title": "Bad"},
                            {"url": "https://www.loc.gov:8888/item/xxx", "title": "Port"},
                            {"id": "https://www.loc.gov/item/2024000003/", "title": "Good"}]}
        result = _normalize_response(rows, {"page": 1}, "https://www.loc.gov/manuscripts/")
        self.assertEqual(len(result["results"]), 1)
        self.assertEqual(result["omitted_unusable_or_duplicate_rows"], 2)
        self.assertTrue(result["results"][0]["source_id"].startswith("LOC-"))

    def test_redirect_is_rejected_before_leaving_approved_origin(self):
        with self.assertRaises(ArchiveSearchError):
            _NoRedirect().redirect_request(None, None, 302, "moved", {}, "https://evil.test/collect")

    def test_collection_paging_is_capped(self):
        client = LibraryOfCongressSearch(fetch=lambda url: EXAMPLE, interval=0)
        data = client.search(name="fictional", collection="newspapers", page=5, consent=True)
        self.assertFalse(data["pagination"]["has_next"])
        with self.assertRaises(ArchiveSearchError):
            client.search(name="fictional", page=6, consent=True)


class HTTPArchiveSearchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.calls = []
        cls.archive = LibraryOfCongressSearch(fetch=lambda url: (cls.calls.append(url), EXAMPLE)[1], interval=0)
        cls.server = Workbench(("127.0.0.1", 0), archive_client=cls.archive)
        cls.host = f"http://127.0.0.1:{cls.server.server_port}"
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=3)

    def request(self, path, data=None, headers=None):
        payload = json.dumps(data).encode("utf-8") if data is not None else None
        common = {"Content-Type": "application/json"} if data is not None else {}
        common.update(headers or {})
        try:
            with urlopen(Request(self.host + path, data=payload, headers=common), timeout=5) as response:
                return response.status, json.loads(response.read())
        except HTTPError as response:
            return response.code, json.loads(response.read())

    def test_provider_catalog_and_explicit_search(self):
        status, providers = self.request("/api/archive-providers")
        self.assertEqual(status, 200)
        self.assertEqual(providers["providers"][0]["id"], "loc")
        before = len(self.calls)
        status, result = self.request("/api/search-archives", {"provider_id": "loc", "name": "Jason Huang", "consent": True})
        self.assertEqual(status, 200)
        self.assertGreater(len(self.calls), before)
        self.assertTrue(result["record_search_executed"])
        self.assertEqual(len(result["results"]), 2)

    def test_http_blocks_without_consent_or_wrong_provider(self):
        before = len(self.calls)
        for data in ({"provider_id": "loc", "name": "Jason Huang", "consent": False},
                     {"provider_id": "random", "name": "Jason Huang", "consent": True}):
            status, response = self.request("/api/search-archives", data)
            self.assertEqual(status, 400)
            self.assertIn("code", response)
        self.assertEqual(len(self.calls), before)

    def test_http_review_only_comparison_of_supplied_person(self):
        from kinship.online import _normalize
        status, demo = self.request("/api/demo")
        self.assertEqual(status, 200)
        case = demo["case"]
        person = case["people"][0]
        name = person["names"][0]["original"]
        record = _normalize({"id": "https://www.loc.gov/item/synthetic-compare/",
                             "title": f"{name} archival correspondence", "date": "1901"})
        before = len(self.calls)
        status, result = self.request("/api/compare-catalog-lead", {
            "case": case, "person_id": person["id"], "record": record})
        self.assertEqual(status, 200, result)
        self.assertEqual(len(self.calls), before, "Comparison must be offline")
        self.assertTrue(result["review_required"])
        self.assertFalse(result["identity_verified"])
        self.assertFalse(result["claim_created"])
        self.assertFalse(result["merge_performed"])
        self.assertEqual(result["new_independent_source_count"], 0)
        self.assertEqual(result["signals"][0]["type"], "literal_name_mention")

    def test_http_comparison_rejects_unknown_person_and_forged_source(self):
        from kinship.online import _normalize
        _, demo = self.request("/api/demo")
        case = demo["case"]
        record = _normalize({"id": "https://www.loc.gov/item/synthetic-compare/", "title": "Sample"})
        for person_id, candidate in [
            ("missing", record),
            (case["people"][0]["id"], dict(record, record_url="https://evil.example/item/secret")),
            (case["people"][0]["id"], dict(record, identity_verified=True)),
        ]:
            with self.subTest(person_id=person_id, record_url=candidate.get("record_url")):
                status, body = self.request("/api/compare-catalog-lead", {
                    "case": case, "person_id": person_id, "record": candidate})
                self.assertEqual(status, 400, body)

    def test_http_cross_site_origin_is_forbidden(self):
        before = len(self.calls)
        status, response = self.request("/api/search-archives", {"provider_id": "loc", "name": "Jason Huang", "consent": True},
                                        {"Origin": "https://untrusted.example"})
        self.assertEqual(status, 403)
        self.assertEqual(len(self.calls), before)


if __name__ == "__main__":
    unittest.main()