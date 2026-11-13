"""Local-only static workbench and read-only research API, Python stdlib only."""
from __future__ import annotations

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from importlib.resources import files
from urllib.parse import parse_qs, urlsplit
import json

from kinship.agent import OpenAICompatibleClient, ResearchAgent
from kinship.audit import audit_case
from kinship.catalog import list_archive_leads
from kinship.plan import make_search_plan
from kinship.profiles import REGISTRY, get_profile
from kinship.research import artifact_detail, case_summary, person_detail, search_case

MAX_BODY = 512_000
STATIC = {"/": ("index.html", "text/html; charset=utf-8"),
          "/app.js": ("app.js", "application/javascript; charset=utf-8"),
          "/styles.css": ("styles.css", "text/css; charset=utf-8")}


class Workbench(ThreadingHTTPServer):
    daemon_threads = True

    def __init__(self, address, model=None):
        super().__init__(address, WorkbenchHandler)
        self.model_client = model


class WorkbenchHandler(BaseHTTPRequestHandler):
    server_version = "KinshipWorkbench/0.2"

    def log_message(self, fmt, *args):
        # Never log path queries, user content, payloads or model transcripts.
        return

    def _headers(self, content_type: str, status: int = 200) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header("Content-Security-Policy", "default-src 'none'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self'; base-uri 'none'; object-src 'none'; form-action 'self'; frame-ancestors 'none'")
        self.end_headers()

    def _respond(self, value, status: int = 200) -> None:
        body = json.dumps(value, ensure_ascii=False).encode("utf-8")
        self._headers("application/json; charset=utf-8", status)
        self.wfile.write(body)

    def _valid_host(self) -> bool:
        # Prevent DNS-rebinding access to locally held family records.
        host = self.headers.get("Host", "")
        return host.split(":", 1)[0].lower() in {"localhost", "127.0.0.1"}

    def _valid_origin(self) -> bool:
        origin = self.headers.get("Origin")
        if not origin:
            return True  # Non-browser clients cannot bypass the JSON content gate by using a form.
        url = urlsplit(origin)
        host = urlsplit("http://" + self.headers.get("Host", ""))
        return (url.scheme == "http" and url.hostname == host.hostname and
                url.port == host.port and url.username is None and url.password is None)

    def do_GET(self):
        if not self._valid_host():
            return self._respond({"error": "Invalid Host header"}, 403)
        path = urlsplit(self.path).path
        if path in STATIC:
            filename, mime = STATIC[path]
            body = files("kinship").joinpath("static", filename).read_bytes()
            self._headers(mime)
            self.wfile.write(body)
            return
        if path == "/api/health":
            model = getattr(self.server, "model_client", None)
            return self._respond({"status": "ready", "local_only": True, "data_persisted": False,
                                  "agent_mode": "model-assisted" if model else "guided-offline",
                                  "remote_model": bool(model and model.is_remote)})
        if path == "/api/regions":
            return self._respond({"regions": [{"code": p.code, "name": p.display_name,
                                                 "status": p.status, "sources": len(p.archives)}
                                                for p in REGISTRY.values()]})
        if path == "/api/demo":
            example = files("kinship").joinpath("static", "demo.json").read_text(encoding="utf-8")
            return self._respond({"case": json.loads(example), "label": "Synthetic test data only"})
        if path == "/api/sources":
            region = parse_qs(urlsplit(self.path).query).get("region", [None])[0]
            try:
                return self._respond({"sources": list_archive_leads(region), "searched": False})
            except ValueError as exc:
                return self._respond({"error": str(exc)}, 400)
        return self._respond({"error": "Not found"}, 404)

    def do_POST(self):
        if not self._valid_host() or not self._valid_origin():
            return self._respond({"error": "Forbidden request origin"}, 403)
        if self.headers.get("Content-Type", "").split(";", 1)[0].strip().lower() != "application/json":
            return self._respond({"error": "Only application/json is accepted"}, 415)
        try:
            size = int(self.headers.get("Content-Length", "-1"))
        except ValueError:
            return self._respond({"error": "Invalid Content-Length"}, 400)
        if size < 0 or size > MAX_BODY:
            return self._respond({"error": "Request too large or missing Content-Length"}, 413)
        try:
            payload = json.loads(self.rfile.read(size))
            if not isinstance(payload, dict):
                raise ValueError("JSON body must be an object")
            path = urlsplit(self.path).path
            if path == "/api/plan":
                result = make_search_plan(payload["region"], payload["name"], payload.get("variants"))
            elif path == "/api/audit":
                result = audit_case(payload["case"]).as_dict()
            elif path == "/api/search":
                result = search_case(payload["case"], payload["query"], kind=payload.get("kind", "all"))
            elif path == "/api/person":
                result = person_detail(payload["case"], payload["person_id"])
            elif path == "/api/artifact":
                result = artifact_detail(payload["case"], payload["artifact_id"])
            elif path == "/api/case-summary":
                result = case_summary(payload["case"])
            elif path == "/api/agent":
                agent = ResearchAgent(payload["case"], payload["region"])
                result = agent.run(payload["question"], model=getattr(self.server, "model_client", None),
                                   remote_consent=payload.get("remote_consent") is True)
            else:
                return self._respond({"error": "Not found"}, 404)
            return self._respond(result)
        except (ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
            return self._respond({"error": str(exc)[:300]}, 400)
        except Exception:
            # Do not expose local file paths, model keys or user records in error messages.
            return self._respond({"error": "Request failed without saving or publishing data"}, 500)


def serve(port: int = 8765, *, model: str | None = None,
          endpoint: str = "http://127.0.0.1:11434/v1/chat/completions",
          allow_remote: bool = False, open_browser: bool = False) -> None:
    if not isinstance(port, int) or not (0 <= port <= 65535):
        raise ValueError("Port must be between 0 and 65535")
    client = OpenAICompatibleClient(model, endpoint, allow_remote=allow_remote) if model else None
    with Workbench(("127.0.0.1", port), model=client) as server:
        url = f"http://127.0.0.1:{server.server_port}"
        print(f"Local-only workbench: {url}", flush=True)
        if open_browser:
            import webbrowser
            webbrowser.open_new_tab(url)
        server.serve_forever(poll_interval=0.25)
