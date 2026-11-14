"""Case-safe CLI and local browser workbench. Nothing calls archives automatically."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from kinship.agent import OpenAICompatibleClient, ResearchAgent
from kinship.audit import audit_case
from kinship.catalog import list_archive_leads
from kinship.plan import make_search_plan
from kinship.legacy import import_ex_ussr_registers
from kinship.gedcom import import_gedcom, MAX_BYTES as GEDCOM_MAX_BYTES
from kinship.graph import relationship_graph
from kinship.profiles import REGISTRY, get_profile
from kinship.report import format_report
from kinship.research import search_case


def _read_case(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _output(value: object) -> None:
    print(json.dumps(value, ensure_ascii=False, indent=2))


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="kinship", description="Local evidence workbench and opt-in tool-using agent")
    sub = p.add_subparsers(dest="command", required=True)
    sub.add_parser("profiles", help="List supported research regions")
    info = sub.add_parser("profile", help="Show cultural and archive research guidance")
    info.add_argument("region", choices=sorted(REGISTRY))
    sources = sub.add_parser("sources", help="List curated archive portals (not search results)")
    sources.add_argument("--region", choices=sorted(REGISTRY))
    plan = sub.add_parser("plan", help="Create an unexecuted search plan")
    plan.add_argument("region", choices=sorted(REGISTRY))
    plan.add_argument("--name", required=True)
    plan.add_argument("--variant", action="append", default=[], help="Source-verified alternative spelling")
    audit = sub.add_parser("audit", help="Validate local case structure and provenance")
    audit.add_argument("case_file")
    report = sub.add_parser("report", help="Create local Markdown evidence packet after audit")
    report.add_argument("case_file")
    report.add_argument("--out", help="Write report outside the public repo for private cases")
    legacy = sub.add_parser("import-ex-ussr", help="Convert ex-USSR CSV evidence registers; no identity guessing")
    legacy.add_argument("register_dir")
    legacy.add_argument("--case-id", required=True)
    legacy.add_argument("--question", required=True)
    legacy.add_argument("--out", required=True, help="Private destination JSON path")
    gedcom = sub.add_parser("import-gedcom", help="Convert UTF-8 GEDCOM 5.5.1 into a private unverified case")
    gedcom.add_argument("gedcom_file")
    gedcom.add_argument("--region", required=True, choices=sorted(REGISTRY))
    gedcom.add_argument("--case-id", required=True)
    gedcom.add_argument("--question", required=True)
    gedcom.add_argument("--out", required=True, help="Private destination JSON path; never overwrites")
    graph = sub.add_parser("graph", help="Show locally supplied family-link claims and independent sources")
    graph.add_argument("case_file")
    search = sub.add_parser("search", help="Search names/citations in a local JSON case; not the internet")
    search.add_argument("case_file")
    search.add_argument("query")
    search.add_argument("--kind", choices=("all", "people", "artifacts", "claims"), default="all")
    agent = sub.add_parser("agent", help="Run read-only tools; optionally use a configured model")
    agent.add_argument("case_file")
    agent.add_argument("--region", required=True, choices=sorted(REGISTRY))
    agent.add_argument("--question", required=True)
    agent.add_argument("--model", help="Optional local OpenAI-compatible model name")
    agent.add_argument("--endpoint", default="http://127.0.0.1:11434/v1/chat/completions")
    agent.add_argument("--allow-remote", action="store_true", help="Explicitly allow an external HTTPS model endpoint")
    agent.add_argument("--remote-consent", action="store_true", help="Explicitly consent to send synthetic case question to remote model")
    server = sub.add_parser("serve", help="Run local-only browser app on 127.0.0.1")
    server.add_argument("--port", type=int, default=8765)
    server.add_argument("--browser", action="store_true", help="Open the local workbench after server binds")
    server.add_argument("--model", help="Optional local OpenAI-compatible model name")
    server.add_argument("--endpoint", default="http://127.0.0.1:11434/v1/chat/completions")
    server.add_argument("--allow-remote", action="store_true")
    args = p.parse_args(argv)
    try:
        if args.command == "profiles":
            _output([{"code": x.code, "name": x.display_name, "status": x.status} for x in REGISTRY.values()])
        elif args.command == "profile":
            _output(get_profile(args.region).as_dict())
        elif args.command == "sources":
            _output({"archive_leads": list_archive_leads(args.region), "archive_search_executed": False})
        elif args.command == "plan":
            _output(make_search_plan(args.region, args.name, args.variant))
        elif args.command == "audit":
            result = audit_case(_read_case(args.case_file))
            _output(result.as_dict())
            return 0 if result.ok else 1
        elif args.command == "import-ex-ussr":
            case = import_ex_ussr_registers(args.register_dir, case_id=args.case_id, question=args.question)
            path = Path(args.out)
            if path.exists():
                raise ValueError("Refusing to overwrite an existing case")
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(case, ensure_ascii=False, indent=2), encoding="utf-8")
            print(f"Imported {len(case['people'])} persons, {len(case['artifacts'])} artifacts; private destination: {path}")
        elif args.command == "import-gedcom":
            source = Path(args.gedcom_file)
            if source.stat().st_size > GEDCOM_MAX_BYTES:
                raise ValueError("GEDCOM input is too large (512 KB limit)")
            try:
                source_text = source.read_text(encoding="utf-8-sig")
            except UnicodeError as exc:
                raise ValueError("GEDCOM input must use UTF-8; export from the original app first") from exc
            case = import_gedcom(source_text, case_id=args.case_id, question=args.question, region=args.region)
            target = Path(args.out)
            if target.exists():
                raise ValueError("Refusing to overwrite an existing case")
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(json.dumps(case, ensure_ascii=False, indent=2), encoding="utf-8")
            print(f"Imported {len(case['people'])} people; private destination: {target}")
        elif args.command == "graph":
            _output(relationship_graph(_read_case(args.case_file)))
        elif args.command == "search":
            _output(search_case(_read_case(args.case_file), args.query, kind=args.kind))
        elif args.command == "report":
            case = _read_case(args.case_file)
            content = format_report(case, audit_case(case))
            if args.out:
                path = Path(args.out)
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(content, encoding="utf-8")
                print(f"Saved: {path}")
            else:
                print(content)
        elif args.command == "agent":
            model = OpenAICompatibleClient(args.model, args.endpoint, allow_remote=args.allow_remote) if args.model else None
            _output(ResearchAgent(_read_case(args.case_file), args.region).run(
                args.question, model=model, remote_consent=args.remote_consent))
        elif args.command == "serve":
            from kinship.web import serve
            serve(args.port, model=args.model, endpoint=args.endpoint, allow_remote=args.allow_remote, open_browser=args.browser)
        return 0
    except (ValueError, OSError, json.JSONDecodeError, KeyError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2
    except KeyboardInterrupt:
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
