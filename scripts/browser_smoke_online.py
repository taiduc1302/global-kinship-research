"""Opt-in browser smoke against the real Python HTTP API (synthetic LOC transport).

Runs without external archive access or GitHub Actions. Chrome localhost requests are
intercepted only because this hosted Chromium blocks direct loopback navigation.
"""
from __future__ import annotations

import json
from pathlib import Path
import shutil
import sys
import threading
from urllib.error import HTTPError
from urllib.request import Request, urlopen

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from kinship.online import ArchiveSearchError, LibraryOfCongressSearch
from kinship.web import Workbench
from playwright.sync_api import sync_playwright


class SyntheticCatalog:
    def __init__(self):
        self.requests = []

    def __call__(self, url):
        self.requests.append(url)
        if "NoResult" in url:
            return {"results": [], "pagination": {"total": 0}}
        if "RateLimit" in url:
            raise ArchiveSearchError("provider_rate_limited", "Archive rate limit reached", 429)
        return {"results": [{"id": "https://www.loc.gov/item/fictional-123/", "title": "Synthetic catalog manuscript", "date": "1901"}],
                "pagination": {"total": 16, "next": "sp=2"}}


def main():
    catalog = SyntheticCatalog()
    server = Workbench(("127.0.0.1", 0), archive_client=LibraryOfCongressSearch(fetch=catalog, interval=0))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base = f"http://127.0.0.1:{server.server_port}"
    try:
        with sync_playwright() as pw:
            args = {"headless": True}
            binary = shutil.which("chromium") or shutil.which("google-chrome")
            if binary:
                args.update(executable_path=binary, args=["--no-sandbox"])
            browser = pw.chromium.launch(**args)
            try:
                for width, height in ((1440, 900), (390, 844)):
                    page = browser.new_page(viewport={"width": width, "height": height})
                    errors = []
                    page.on("pageerror", lambda e: errors.append(str(e)))

                    def backend(source, args):
                        endpoint = args['path']
                        assert endpoint.startswith('/api/'), endpoint
                        data = args.get('body')
                        req = Request(base + endpoint, data=data.encode('utf-8') if data is not None else None,
                                      headers={'Content-Type': 'application/json'} if data is not None else {},
                                      method='POST' if data is not None else 'GET')
                        try:
                            response = urlopen(req, timeout=5)
                        except HTTPError as exc:
                            response = exc
                        try:
                            return {'status': response.status, 'json': json.loads(response.read())}
                        finally:
                            response.close()

                    page.expose_binding('fetchBridge', backend)
                    import re
                    root = Path(__file__).resolve().parents[1]
                    html = (root / 'src/kinship/static/index.html').read_text('utf-8')
                    html = re.sub(r'<link rel="stylesheet" href="/[^" ]+">', '', html)
                    html = re.sub(r'<script type="module" src="/[^" ]+"></script>', '', html)
                    page.set_content(html, wait_until='load')
                    page.evaluate("""() => {window.fetch = async (path, options={}) => {
                      const data = await window.fetchBridge({path: String(path), body: options.body || null});
                      return {ok: data.status >= 200 && data.status < 300,
                              status: data.status, json: async () => data.json};
                    }; }""")
                    for css in ['styles.css', 'family.css']:
                        page.add_style_tag(content=(root / 'src/kinship/static' / css).read_text('utf-8'))
                    for js in ['family.js', 'online.js', 'app.js']:
                        page.add_script_tag(content=(root / 'src/kinship/static' / js).read_text('utf-8'))
                    page.locator("#case-tag").get_by_text("Synthetic sample", exact=False).wait_for(timeout=7000)
                    page.locator('[data-view="online"]').click()
                    page.get_by_text("No external request has been made").wait_for(timeout=4000)
                    before = len(catalog.requests)
                    assert len(catalog.requests) == before, "External archive queried without user consent"
                    page.locator("#online-name").fill("Jason Huang")
                    page.locator("#online-consent").check()
                    page.locator("#online-submit").click()
                    page.get_by_text("Synthetic catalog manuscript").wait_for(timeout=5000)
                    assert len(catalog.requests) == before + 1
                    assert page.locator("#online-results .online-result").count() == 1
                    assert "catalog leads" in page.locator("#online-search-status").inner_text()
                    assert page.locator("#online-results a").get_attribute("href") == "https://www.loc.gov/item/fictional-123/"
                    page.locator("#online-results .online-compare").click()
                    page.locator(".catalog-compare-panel select").first.wait_for(timeout=4000)
                    page.locator(".catalog-compare-panel button").first.click()
                    page.get_by_text("No identity or family relationship was confirmed.", exact=False).first.wait_for(timeout=5000)
                    assert page.locator("#stat-claims").inner_text() == "2"
                    page.locator("#online-results .online-add").click()
                    page.wait_for_function("document.querySelector('#stat-artifacts').textContent === '4'", timeout=5000)
                    assert page.locator('#stat-claims').inner_text() == '2', 'A catalog lead created a genealogy claim without review'
                    assert page.locator('#case-tag').get_attribute('title').startswith('Sensitive case')
                    page.locator("#online-next").click()
                    page.get_by_text("Page 2", exact=True).wait_for(timeout=5000)
                    assert len(catalog.requests) == before + 2
                    page.locator("#online-name").fill("NoResult")
                    page.locator("#online-submit").click()
                    page.get_by_text("No catalog items were returned").wait_for(timeout=5000)
                    assert "not proof" in page.locator("#online-search-status").inner_text().lower()
                    page.locator("#online-name").fill("RateLimit")
                    page.locator("#online-submit").click()
                    page.get_by_text("Search failed, not zero matches").wait_for(timeout=5000)
                    assert "rate limit" in page.locator("#online-search-status").inner_text().lower()
                    assert not errors, errors
                    overflow = page.evaluate("document.documentElement.scrollWidth > window.innerWidth")
                    assert not overflow, f"Horizontal overflow at {width}"
                    print(f"PASS online pilot view {width}x{height}; explicit external request, results, paging, empty and 429")
                    page.close()
            finally:
                browser.close()
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


if __name__ == "__main__":
    main()