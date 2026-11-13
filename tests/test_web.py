import json
from pathlib import Path
import sys
import threading
import unittest
from urllib.error import HTTPError
from urllib.request import Request, urlopen

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from kinship.web import Workbench


class WebServerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = Workbench(('127.0.0.1', 0))
        cls.port = cls.server.server_port
        cls.host = f'http://127.0.0.1:{cls.port}'
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown(); cls.server.server_close(); cls.thread.join(timeout=2)

    @classmethod
    def req(cls, route, data=None, headers=None):
        kwargs = {'headers': headers or {}}
        if data is not None:
            kwargs['data'] = json.dumps(data).encode('utf-8')
            kwargs['headers']['Content-Type'] = 'application/json'
        try:
            res = urlopen(Request(cls.host+route, **kwargs), timeout=4)
        except HTTPError as e:
            res = e
        try:
            content = res.read()
            status, headers = res.status, res.headers
        finally:
            res.close()
        if 'json' in headers.get('Content-Type', ''): return status, json.loads(content), headers
        return status, content.decode('utf-8'), headers

    def test_html_and_security_headers(self):
        status, text, headers = self.req('/')
        self.assertEqual(status, 200)
        self.assertIn('Every family story', text)
        self.assertIn("default-src 'none'", headers['Content-Security-Policy'])
        self.assertEqual(headers['X-Frame-Options'], 'DENY')
        self.assertEqual(headers['Cache-Control'], 'no-store')

    def test_javascript_is_actual_local_module(self):
        status, text, headers = self.req('/app.js')
        self.assertEqual(status, 200)
        self.assertIn('api(', text)
        self.assertIn('javascript', headers['Content-Type'])

    def test_api_regions_and_catalog(self):
        status, data, _ = self.req('/api/regions')
        self.assertEqual(len(data['regions']), 11)
        status, data, _ = self.req('/api/sources?region=china')
        self.assertEqual(status, 200)
        self.assertFalse(data['searched'])
        self.assertEqual(data['sources'][0]['source_id'], 'china-01')

    def test_synthetic_case_search_roundtrip(self):
        _, example, _ = self.req('/api/demo')
        status, data, _ = self.req('/api/search', {'case': example['case'], 'query': 'Nguyen Van An'})
        self.assertEqual(status, 200)
        self.assertEqual(data['results'][0]['id'], 'P1')
        status, data, _ = self.req('/api/artifact', {'case': example['case'], 'artifact_id':'A1'})
        self.assertEqual(data['independent'], ['A1','A1copy'])

    def test_api_agent_is_guided_without_network(self):
        _, example, _ = self.req('/api/demo')
        status, data, _ = self.req('/api/agent', {'case':example['case'], 'region':'vietnam', 'question':'What next?'})
        self.assertEqual(status, 200)
        self.assertEqual(data['mode'], 'guided-offline')

    def test_missing_header_or_origin_rejected(self):
        _, example, _ = self.req('/api/demo')
        status, data, _ = self.req('/api/audit', {'case':example['case']}, {'Origin':'https://evil.example'})
        self.assertEqual(status, 403)
        req = Request(self.host+'/api/audit', data=b'{"case": {}}', headers={'Content-Type':'text/plain'}, method='POST')
        with self.assertRaises(HTTPError) as ctx: urlopen(req, timeout=4)
        self.assertEqual(ctx.exception.code, 415)

    def test_deny_directory_traversal(self):
        status, _, _ = self.req('/.env')
        self.assertEqual(status, 404)
        status, _, _ = self.req('/../pyproject.toml')
        self.assertEqual(status, 404)

    def test_only_loopback_required(self):
        request = Request(self.host+'/api/regions', headers={'Host':'evil.example'})
        with self.assertRaises(HTTPError) as e: urlopen(request, timeout=4)
        self.assertEqual(e.exception.code, 403)

    def test_reject_bad_region(self):
        status, data, _ = self.req('/api/sources?region=unknown')
        self.assertEqual(status, 400)
        self.assertIn('Unknown region', data['error'])

if __name__ == '__main__': unittest.main()
