import json
import threading
import unittest
import urllib.error
import urllib.request

from app.fixtures import public_cases
from server import create_server, Handler, RateLimiter


class HttpTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = create_server('127.0.0.1', 0)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True); cls.thread.start()
        cls.base = f'http://127.0.0.1:{cls.server.server_port}'

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown(); cls.server.server_close(); cls.thread.join()

    def setUp(self): Handler.limiter = RateLimiter()

    def request(self, path, body=None, headers=None):
        req = urllib.request.Request(self.base + path, data=body, headers=headers or {})
        try: response = urllib.request.urlopen(req, timeout=3)
        except urllib.error.HTTPError as exc: response = exc
        with response: return response.status, response.read(), dict(response.headers)

    def test_static_and_health(self):
        for path in ('/', '/styles.css', '/app.js', '/favicon.svg', '/health'):
            with self.subTest(path=path): self.assertEqual(self.request(path)[0], 200)

    def test_private_files_are_never_served(self):
        for path in ('/.env', '/app/engine.py', '/README.md', '/../server.py'):
            with self.subTest(path=path): self.assertEqual(self.request(path)[0], 404)

    def test_config_does_not_expose_key(self):
        result = json.loads(self.request('/api/config')[1])
        self.assertNotIn('OPENAI_API_KEY', result); self.assertIn('ai_available', result)

    def test_cases_do_not_ship_replay_reports(self):
        result = json.loads(self.request('/api/cases')[1]); self.assertEqual(len(result['cases']), 3)
        self.assertNotIn('report', result['cases'][0])

    def test_end_to_end_replay_http(self):
        code, raw, headers = self.request('/api/investigate', json.dumps(public_cases()[0]).encode(), {'Content-Type': 'application/json'})
        self.assertEqual(code, 200); self.assertEqual(json.loads(raw)['meta']['mode'], 'sample')
        self.assertIn("default-src 'self'", headers['Content-Security-Policy'])

    def test_malformed_json_returns_400(self):
        self.assertEqual(self.request('/api/investigate', b'{oops', {'Content-Type': 'application/json'})[0], 400)

    def test_non_json_rejected(self):
        self.assertEqual(self.request('/api/investigate', b'hello')[0], 415)

    def test_oversized_body_rejected(self):
        self.assertEqual(self.request('/api/investigate', b' ' * 250001, {'Content-Type': 'application/json'})[0], 413)

    def test_foreign_origin_rejected(self):
        self.assertEqual(self.request('/api/investigate', b'{}', {'Content-Type': 'application/json', 'Origin': 'https://foreign.example'})[0], 403)

    def test_rate_limit(self):
        limiter = RateLimiter()
        for _ in range(15): self.assertTrue(limiter.allow('test'))
        self.assertFalse(limiter.allow('test')); self.assertTrue(limiter.allow('other'))


if __name__ == '__main__': unittest.main()
