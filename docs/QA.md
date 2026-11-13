# v0.2 quality report — 2026-11-12

## Automated tests

- Python standard-library `unittest` suite: evidence audit, region guides, identity-safe name search, local case search, strict source independence, Ex-USSR CSV importer, model tool dispatcher with fake client, remote-privacy restrictions, loopback web API, content type, Host/Origin checks, static UI and CSP.
- JavaScript syntax validation with `node --check`.
- No paid GitHub Actions; tests run in a local Linux container.

## Interactive browser smoke

Tested Chromium at 1400×930 desktop and 390×844 mobile viewports using Playwright with an intercepted HTTP transport to the running local server (direct Chromium navigation was blocked by the testing environment). The browser executed the actual shipped HTML, CSS and JavaScript; API calls were forwarded to the local Python server.

Verified interactions:

1. Case initialized with 3 fictional people, 3 records, 2 claims, 2 independent source groups.
2. Diacritic-insensitive text search for `Nguyen Van An` returns the supplied fictional person.
3. Selecting the person opens its source-backed detail and relationships.
4. Changing the archive region to China shows the Shanghai Library genealogy lead.
5. Running the assistant in default mode generates an offline research route, explicitly not a real archive search.
6. Evidence review shows the structural audit result.
7. No JavaScript page errors. No horizontal page overflow at 390px.

**Limitations:** no physical Windows launcher test; no production archive queries; no network AI model with real credentials; not a professional accessibility certification; HTTP proxy interception differs from full local-browser transport. Require further testing before public hosting or private-case deployment.
