# v0.4 online archive search pilot (read-only, explicitly opted in)

Reviewed on: 2026-11-17. This is **not** a production-wide ancestor-finding service.
The pilot searches publicly available metadata of selected digital collections at the U.S. Library of Congress. It is not a vital-records registry or evidence of who is related to whom. Historical archives for Vietnam, Korea, China and the former USSR remain separate manual research routes until a searchable and authorized API is independently selected.

## Official sources and integration eligibility

| Institution | Verified developer documentation | API access | Decision |
| --- | --- | --- | --- |
| U.S. Library of Congress | https://www.loc.gov/apis/json-and-yaml/ and https://www.loc.gov/apis/json-and-yaml/requests/endpoints/ | Public JSON API, **no API key**; official rate limit **20 requests per minute**; digitized collections and metadata, not the entire library catalog | **Connected as a pilot in code**, live-response acceptance test pending independent network access |
| U.S. National Archives (NARA) | https://www.archives.gov/research/catalog/help/api and https://www.archives.gov/research/catalog/help/api-getting-started | Catalog API v2 requires an issued API key | **BLOCKED until an issued key and usage review**; no key was used or committed |
| Europeana | https://www.europeana.eu/en/how-to-register-for-and-manage-an-api-key | API key required | Candidate for future evaluation; **not connected** |
| Vietnam, China, Korea and other region profiles | See [SOURCE_REVIEW.md](SOURCE_REVIEW.md), [profiles.py](../src/kinship/profiles.py) | Most referenced pages are portals/finding aids, not documented open search APIs | **Manual leads only**, no silent scraping or invented results |

Rights for individual Library of Congress items vary. Viewing an item online does **not** confer rights to copy its image or republish it; see https://guides.loc.gov/digital-scholarship/faq . The app stores and displays only bounded catalog metadata, item link and a local unverified source identifier, never remote images or OCR text.

## What the implementation does

- The UI **Search archives** is separate from **Search my local case**. Typing a name in the local box never invokes the internet.
- An external request is made only after the user enters the name, explicitly checks consent and clicks **Search external archive**. Name, optional place, selected collection and catalog item date range are sent over HTTPS to the Library of Congress. Avoid entering confidential information about living people.
- Supported collections are `manuscripts`, `newspapers` and `all` (`/search/` can also return contemporary website content). Query params follow the official `fo=json`, `at=results,pagination`, `q`, `c`, `sp`, `dates` contract.
- Fixed trusted outbound host `https://www.loc.gov`; no user-configurable provider URL, cookies, credentials, archive scraping, redirect following, OAuth bypass or infinite retries.
- Single requests are rate-limited to one every **5 seconds** per local server process (no more than 12/min); maximum 10 records/page, five pages, 9-second timeout and 1.5-MB response bound. Overload and access errors are surfaced as errors, **never as zero matches**.
- Results include provider record URL/ID, source ID, unaltered catalog title and available date/place, optional contributor/rights metadata, query and UTC timestamp. Duplicate same-item URLs within a page are not repeated. There is no scored identity match and no automatic linking to a person.
- **Add as unverified lead** creates a metadata-only artifact in the user's current browser-held case; it sets `visibility=private` and does not create a genealogy claim. The user must explicitly click **Download current case JSON** to retain it; save outside a public repository.

## What the implementation does NOT do

- No verified live successful Library of Congress API response was obtained from the development environment (outbound DNS and direct browser-to-localhost navigation are blocked). The adapter is implemented from current official documentation and tested against strictly synthetic HTTP/JSON fixtures; production live compatibility is still a gate.
- No cross-provider archive search, person identification, matching to a supplied GEDCOM person, record authenticity checking, extended source provenance review, automatic real-family linking, remote hosting, cloud backup or protected data acquisition.
- Some archive fields vary by collection and era; absent data are left unknown and unusable/noncanonical links are omitted rather than fabricated. Catalog search is **not** an exhaustive historical search, and results for a name may refer to different people or only mention the name in another context.

## Reproducible local acceptance checks

```bash
python scripts/verify_release.py
python scripts/browser_smoke_online.py  # optional Playwright + Chromium; synthetic API transport
```

The Python tests use an injected fake provider transport with the **real local HTTP server**, assert that consent is required, and verify malformed links, 429, missing metadata, timeouts, source IDs and no kinship claims. Browser smoke uses the actual shipped HTML/CSS/JS and Python API at 1440x900 and 390x844 through a loopback bridge. No paid CI, API keys or real family information required.

### Live provider acceptance — pending

On a workstation with internet access, open the workbench and **Search archives**, submit a non-sensitive historically public query, inspect the returned official item URL and request timestamp, then separately inspect the original record in the Library of Congress browser. Record schema, fields, no-result queries, 429/unavailable handling and restrictions. Only after a documented successful real result with stable ID can the live provider acceptance gate be checked off in [PRODUCT_BACKLOG.md](PRODUCT_BACKLOG.md). A screenshot of a mocked result cannot pass this gate.
