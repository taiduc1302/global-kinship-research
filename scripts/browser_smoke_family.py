"""Optional Chromium component smoke for the REAL family.js with a mocked graph API.

Usage: python scripts/browser_smoke_family.py
Requires Playwright and a Chromium executable. No external network, no real family data.
This does not substitute for full app/API integration or Windows launcher tests.
"""
from pathlib import Path
import shutil
import sys

try:
    from playwright.sync_api import sync_playwright
except ImportError as exc:
    raise SystemExit("Optional dependency: install Playwright to run this browser smoke") from exc

SCRIPT = (Path(__file__).resolve().parents[1] / "src" / "kinship" / "static" / "family.js").read_text(encoding="utf-8")
GRAPH = {
    "case_id": "synthetic",
    "nodes": [
        {"id": "P1", "label": "Nguyễn Văn An", "living": False, "claims": 2},
        {"id": "P2", "label": "김하늘", "living": None, "claims": 2},
        {"id": "P3", "label": "Софія", "living": None, "claims": 1},
    ],
    "edges": [
        {"claim_id": "C1", "from": "P1", "to": "P3", "relationship": "parent_of", "status": "hypothesis", "source_ids": ["A1"], "independent_source_groups": ["G1"]},
        {"claim_id": "C2", "from": "P2", "to": "P3", "relationship": "parent_of", "status": "hypothesis", "source_ids": [], "independent_source_groups": []},
        {"claim_id": "C3", "from": "P1", "to": "P2", "relationship": "spouse_of", "status": "hypothesis", "source_ids": [], "independent_source_groups": []},
    ],
    "notice": "Synthetic links; no ancestry claim is proven",
}
HTML = '<!doctype html><html><body><select id="tree-focus"></select><div id="family-map"></div></body></html>'


def check_browser(page):
    errors = []
    page.on("pageerror", lambda err: errors.append(str(err)))
    page.set_content(HTML)
    page.evaluate("g => { window.fetch = async () => ({ok: true, json: async () => g}); }", GRAPH)
    page.add_script_tag(content=SCRIPT)
    page.evaluate("document.dispatchEvent(new CustomEvent('kinship-case-loaded', {detail: {case: {case_id: 'synthetic'}}}))")
    page.get_by_text("Possible parents").wait_for(timeout=4000)
    assert page.locator("#tree-focus").input_value() == "P3"
    assert page.locator(".family-person-card strong", has_text="Nguyễn Văn An").count() == 1
    assert page.locator(".family-person-card strong", has_text="김하늘").count() == 1
    assert "hypothesis" in page.locator("#family-map").inner_text()
    assert "1 source groups" in page.locator("#family-map").inner_text()
    page.locator(".family-person-card", has_text="Nguyễn Văn An").click()
    assert page.locator("#tree-focus").input_value() == "P1"
    assert page.locator(".family-person-card strong", has_text="Софія").count() == 1
    assert not errors, errors


def check_stale_case(page):
    page.set_content(HTML)
    page.evaluate("""() => {
        window.fetch = async (_url, request) => {
          const id = JSON.parse(request.body).case.case_id;
          await new Promise(resolve => setTimeout(resolve, id === 'old' ? 180 : 12));
          return {ok:true, json:async()=>({case_id:id, nodes:[{id, label:id, living:null, claims:0}], edges:[], notice:id})};
        };
    }""")
    page.add_script_tag(content=SCRIPT)
    page.evaluate("document.dispatchEvent(new CustomEvent('kinship-case-loaded',{detail:{case:{case_id:'old'}}}))")
    page.evaluate("document.dispatchEvent(new CustomEvent('kinship-case-loaded',{detail:{case:{case_id:'new'}}}))")
    page.wait_for_timeout(260)
    assert page.locator("#tree-focus").input_value() == "new", "An old case replaced the currently selected case"


def main():
    with sync_playwright() as p:
        exe = shutil.which("chromium") or shutil.which("google-chrome")
        opts = {"headless": True}
        if exe:
            opts["executable_path"] = exe
            opts["args"] = ["--no-sandbox"]
        browser = p.chromium.launch(**opts)
        try:
            for width, height in [(1440, 900), (390, 844)]:
                page = browser.new_page(viewport={"width": width, "height": height})
                try:
                    check_browser(page)
                    print(f"PASS family graph component at {width}x{height}")
                finally:
                    page.close()
            page = browser.new_page()
            try:
                check_stale_case(page)
                print("PASS stale case response protection")
            finally:
                page.close()
        finally:
            browser.close()
    print("All synthetic component browser smoke checks passed; full app remains untested")


if __name__ == "__main__":
    main()