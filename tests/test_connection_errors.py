import io
import json
import unittest
import urllib.error
from unittest.mock import patch
from server import Handler
from app.engine import Investigator
from app.fixtures import CASES
from app.validation import AppError, validate_project

class ConnectionErrors(unittest.TestCase):
    def test_idle_connection_log_without_request(self):
        handler=object.__new__(Handler)
        handler.log_message('Request timed out')
    def test_client_disconnect(self):
        handler=object.__new__(Handler)
        handler.send_response=lambda status: None
        handler.send_header=lambda *args: None
        handler.end_headers=lambda: None
        class Closed:
            def write(self,body): raise ConnectionAbortedError('10053')
        handler.wfile=Closed()
        handler.send_bytes(504,b'error','application/json')
        self.assertTrue(handler.close_connection)
    def test_provider_error_redacts_key(self):
        secret='test-secret-for-redaction'
        with patch.dict('os.environ',{'AI_PROVIDER':'gemini','GEMINI_API_KEY':secret}):
            engine=Investigator();p,s=validate_project(CASES[0])
            error=urllib.error.HTTPError('https://example.invalid',503,'Unavailable',{},io.BytesIO(json.dumps({'error':{'message':'Unavailable '+secret}}).encode()))
            with patch('urllib.request.urlopen',side_effect=error):
                with self.assertRaises(AppError) as caught: engine._call_ai(p,s)
            self.assertIn('GEMINI HTTP 503',str(caught.exception))
            self.assertNotIn(secret,str(caught.exception))
