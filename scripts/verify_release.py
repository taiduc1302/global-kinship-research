"""Offline release gate: Python, JS and live local HTTP. No GitHub Actions.

Run from the project root with: python scripts/verify_release.py [--browser]
Only synthetic samples are used. This does NOT certify archive records or Windows.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import threading
from urllib.error import HTTPError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]


def run_command(command: list[str]):
    env = dict(os.environ)
    env['PYTHONPATH'] = str(ROOT / 'src')
    return subprocess.run(command, cwd=ROOT, env=env, text=True,
                          capture_output=True, timeout=180, check=False)


def suite():
    p = run_command([sys.executable, '-m', 'unittest', 'discover', '-s', 'tests', '-v'])
    match = re.search(r'Ran (\d+) tests? in', p.stderr)
    if p.returncode or match is None or int(match.group(1)) == 0:
        sys.stderr.write(p.stderr[-9000:])
        raise RuntimeError('Python test suite failed or discovered no tests')
    return {'tests': int(match.group(1))}


def syntax():
    import compileall
    for directory in ('src', 'tests', 'scripts'):
        if not compileall.compile_dir(ROOT / directory, quiet=1):
            raise RuntimeError('Python compile failed')
    node = shutil.which('node')
    files = sorted((ROOT / 'src/kinship/static').glob('*.js'))
    if not node or not files:
        raise RuntimeError('Node.js or static app JavaScript unavailable')
    for file in files:
        result = run_command([node, '--check', str(file)])
        if result.returncode:
            raise RuntimeError('JavaScript parsing failed')
    return {'javascript_files': [f.name for f in files]}


def http_smoke():
    sys.path.insert(0, str(ROOT / 'src'))
    from kinship.web import Workbench
    server = Workbench(('127.0.0.1', 0))
    worker = threading.Thread(target=server.serve_forever, daemon=True)
    worker.start()
    origin = f'http://127.0.0.1:{server.server_port}'

    def api(url, payload=None, headers=None):
        data = json.dumps(payload).encode('utf-8') if payload is not None else None
        request_headers = {'Content-Type': 'application/json'} if data is not None else {}
        request_headers.update(headers or {})
        req = Request(origin + url, data=data, headers=request_headers)
        try:
            with urlopen(req, timeout=5) as response:
                result = response.read(1_300_000)
                return response.status, (json.loads(result) if 'json' in response.headers.get('Content-Type', '') else result)
        except HTTPError as exc:
            return exc.code, json.loads(exc.read())

    def require(ok):
        if not ok:
            raise RuntimeError('HTTP smoke returned unexpected result')

    try:
        code, status = api('/api/health')
        require(code == 200 and status['local_only'] is True)
        code, demo = api('/api/demo')
        require(code == 200 and demo['case']['visibility'] == 'synthetic')
        case = demo['case']
        code, audit = api('/api/audit', {'case': case})
        require(code == 200 and audit['ok'])
        code, search = api('/api/search', {'case': case, 'query': 'Nguyen Van An'})
        require(code == 200 and any(x['id'] == 'P1' for x in search['results']))
        code, guide = api('/api/agent', {'case': case, 'region': 'vietnam', 'question': 'What next?'})
        require(code == 200 and guide['mode'] == 'guided-offline')
        code, graph = api('/api/graph', {'case': case})
        require(code == 200 and len(graph['nodes']) == 3)
        fake = (ROOT / 'examples/synthetic-gedcom-551.ged').read_text(encoding='utf-8')
        code, import_result = api('/api/import-gedcom', {'gedcom': fake, 'region': 'vietnam'})
        require(code == 200 and import_result['case']['visibility'] == 'private')
        imported = import_result['case']
        require(all(c['status'] == 'hypothesis' for c in imported['claims']
                    if c['type'] in ('parent_of', 'spouse_of')))
        code, graph = api('/api/graph', {'case': imported})
        require(code == 200 and len(graph['nodes']) == 3 and len(graph['edges']) == 3)
        code, _ = api('/api/graph', {'case': imported}, {'Origin': 'https://invalid.example'})
        require(code == 403)
        code, _ = api('/.env')
        require(code == 404)
        return {'synthetic_http_steps': 10, 'network_archive_queries': 0}
    finally:
        server.shutdown()
        server.server_close()
        worker.join(timeout=5)


def browser():
    path = ROOT / 'scripts/browser_smoke_family.py'
    if not path.is_file():
        raise RuntimeError('Browser component script missing')
    result = run_command([sys.executable, str(path)])
    if result.returncode:
        sys.stderr.write(result.stderr[-3000:])
        raise RuntimeError('Chromium component smoke failed')
    return {'scope': 'family component with mocked graph API, not live end-to-end browser'}


def browser_e2e():
    """Browser UI plus actual local API through explicit test transport bridge."""
    script = ROOT / 'scripts/browser_e2e_bridge.py'
    if not script.is_file():
        raise RuntimeError('Local API browser smoke script missing')
    result = run_command([sys.executable, str(script)])
    if result.returncode:
        sys.stderr.write(result.stderr[-3000:])
        raise RuntimeError('Local API Chromium UI smoke failed')
    payload = json.loads(result.stdout)
    if payload.get('status') != 'passed' or len(payload.get('results', [])) != 2:
        raise RuntimeError('Browser smoke returned an incomplete result')
    return {'scope': 'real loopback API through test transport bridge; not direct Chromium network',
            'viewports': [item['view'] for item in payload['results']]}


def main(argv=None):
    parser = argparse.ArgumentParser(description='Offline release verification; no hosted CI')
    parser.add_argument('--browser', action='store_true', help='Also require Playwright + Chromium component test')
    parser.add_argument('--browser-e2e', action='store_true', help='Also require browser UI against the real local API via a transport bridge')
    parser.add_argument('--json-out', help='Optional output path outside source repository')
    args = parser.parse_args(argv)
    results = []
    checks = [('python_regression', suite), ('compile_and_javascript', syntax), ('live_local_http', http_smoke)]
    if args.browser:
        checks.append(('chromium_component', browser))
    if args.browser_e2e:
        checks.append(('chromium_real_api_bridge', browser_e2e))
    for name, check in checks:
        try:
            results.append({'check': name, 'status': 'passed', 'details': check()})
        except Exception as exc:
            results.append({'check': name, 'status': 'failed', 'error_type': type(exc).__name__})
    passed = all(x['status'] == 'passed' for x in results)
    summary = {'status': 'passed' if passed else 'blocked', 'checks': results,
               'not_covered': ['Windows hardware', 'Real model endpoint', 'Real archives',
                               'Third-party GEDCOM interoperability', 'Historical source authenticity']}
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    if args.json_out:
        target = Path(args.json_out).resolve()
        if target.is_relative_to(ROOT) or target.exists():
            parser.error('QA output must be a new file outside the public repository')
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding='utf-8')
    return 0 if passed else 1


if __name__ == '__main__':
    raise SystemExit(main())