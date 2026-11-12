"""No-network CLI: profiles, research plans, evidence audit and report."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from kinship.audit import audit_case
from kinship.plan import make_search_plan
from kinship.profiles import REGISTRY, get_profile
from kinship.report import format_report


def _read_case(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _output(value: object) -> None:
    print(json.dumps(value, ensure_ascii=False, indent=2))


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="kinship", description="Local-first research assistant; not an archive search engine")
    sub = p.add_subparsers(dest="command", required=True)
    sub.add_parser("profiles", help="List supported research regions")
    info = sub.add_parser("profile", help="Show an archive research guide")
    info.add_argument("region", choices=sorted(REGISTRY))
    plan = sub.add_parser("plan", help="Create offline search plan (does not search archives)")
    plan.add_argument("region", choices=sorted(REGISTRY))
    plan.add_argument("--name", required=True)
    plan.add_argument("--variant", action="append", default=[], help="Manually verified alternative spelling")
    audit = sub.add_parser("audit", help="Validate case and evidence provenance")
    audit.add_argument("case_file")
    report = sub.add_parser("report", help="Create Markdown evidence packet after successful audit")
    report.add_argument("case_file")
    report.add_argument("--out", help="Output Markdown path (must not be inside a public source repo for private data)")
    args = p.parse_args(argv)
    try:
        if args.command == "profiles":
            _output([{"code": x.code, "name": x.display_name, "status": x.status} for x in REGISTRY.values()])
        elif args.command == "profile":
            _output(get_profile(args.region).as_dict())
        elif args.command == "plan":
            _output(make_search_plan(args.region, args.name, args.variant))
        elif args.command == "audit":
            result = audit_case(_read_case(args.case_file))
            _output(result.as_dict())
            return 0 if result.ok else 1
        elif args.command == "report":
            case = _read_case(args.case_file)
            result = audit_case(case)
            content = format_report(case, result)
            if args.out:
                path = Path(args.out)
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(content, encoding="utf-8")
                print(f"Saved: {path}")
            else:
                print(content)
        return 0
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
