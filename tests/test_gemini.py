import copy
import io
import json
import os
import unittest
from unittest.mock import patch
from app.engine import Investigator
from app.fixtures import CASES
from app.validation import AppError, validate_project

class GeminiTests(unittest.TestCase):
    def setUp(self):
        self.env=patch.dict(os.environ, {'AI_PROVIDER':'gemini','GEMINI_API_KEY':'test-only-not-a-real-key','GEMINI_MODEL':'gemini-3.8-flash','GEMINI_REVIEW_MODEL':''})
        self.env.start();self.addCleanup(self.env.stop)
        self.engine=Investigator()
    def envelope(self,value,reason='STOP'):
        return io.BytesIO(json.dumps({'candidates':[{'finishReason':reason,'content':{'parts':[{'text':json.dumps(value)}]}}]}).encode())
    def test_report_request_and_validation(self):
        with patch('urllib.request.urlopen',return_value=self.envelope(CASES[0]['report'])) as send:
            result=self.engine.run(dict(project=CASES[0]['project'],sources=CASES[0]['sources'],mode='live'))
        req=send.call_args.args[0];body=json.loads(req.data)
        self.assertIn('generativelanguage.googleapis.com',req.full_url)
        self.assertNotIn('test-only',req.full_url)
        self.assertEqual(body['generationConfig']['responseMimeType'],'application/json')
        self.assertIn('responseJsonSchema',body['generationConfig'])
        self.assertIn('UNTRUSTED',body['systemInstruction']['parts'][0]['text'])
        self.assertGreater(result['meta']['verified_references'],0)
    def test_ask(self):
        answer=copy.deepcopy(CASES[0]['report']['summary'])
        with patch('urllib.request.urlopen',return_value=self.envelope(answer)):
            result=self.engine.ask(dict(project=CASES[0]['project'],sources=CASES[0]['sources'],question='What happened?'))
        self.assertEqual(result['answer'],answer)
    def test_incomplete_not_accepted(self):
        p,s=validate_project(CASES[0])
        with patch('urllib.request.urlopen',return_value=self.envelope({},'MAX_TOKENS')):
            with self.assertRaises(AppError): self.engine._call_ai(p,s)
    def test_empty_candidates(self):
        p,s=validate_project(CASES[0])
        with patch('urllib.request.urlopen',return_value=io.BytesIO(b'{}')):
            with self.assertRaises(AppError): self.engine._call_ai(p,s)
    def test_missing_gemini_key_does_not_use_openai(self):
        with patch.dict(os.environ,{'GEMINI_API_KEY':'','OPENAI_API_KEY':'not-used'}):
            self.assertFalse(self.engine.config()['ai_available'])
            p,s=validate_project(CASES[0])
            with self.assertRaisesRegex(AppError,'GEMINI_API_KEY'): self.engine._call_ai(p,s)
    def test_config_no_secret(self):
        self.assertNotIn('test-only',json.dumps(self.engine.config()))
        self.assertEqual(self.engine.config()['provider'],'gemini')
    def test_invalid_provider(self):
        with patch.dict(os.environ,{'AI_PROVIDER':'unknown'}):
            with self.assertRaises(AppError): self.engine.config()
