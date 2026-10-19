import json
import os
import threading
import unittest
from unittest.mock import patch
from app.engine import Investigator, REQUEST_AI
from app.fixtures import CASES

class OwnKeyTests(unittest.TestCase):
    def test_override_and_reset(self):
        with patch.dict(os.environ,{'AI_PROVIDER':'openai','OPENAI_API_KEY':'server-key','OPENAI_MODEL':'server-model'}):
            engine=Investigator()
            token=REQUEST_AI.set(dict(provider='gemini',key='visitor-secret',model='visitor-model'))
            try:
                cfg=engine.config()
                self.assertEqual(cfg['provider'],'gemini')
                self.assertEqual(cfg['review_model'],'visitor-model')
                self.assertNotIn('visitor-secret',json.dumps(cfg))
            finally: REQUEST_AI.reset(token)
            self.assertEqual(engine.config()['model'],'server-model')
    def test_context_does_not_leak_to_other_thread(self):
        token=REQUEST_AI.set(dict(provider='gemini',key='visitor-secret',model='visitor-model'))
        try:
            seen=[]
            t=threading.Thread(target=lambda:seen.append(REQUEST_AI.get()));t.start();t.join()
            self.assertEqual(seen,[None])
        finally: REQUEST_AI.reset(token)
    def test_visitor_reports_not_cached(self):
        engine=Investigator();token=REQUEST_AI.set(dict(provider='gemini',key='visitor-secret',model='visitor-model'))
        try:
            with patch.object(engine,'_call_ai',return_value=CASES[0]['report']) as call:
                payload=dict(project=CASES[0]['project'],sources=CASES[0]['sources'],mode='live')
                engine.run(payload);engine.run(payload)
                self.assertEqual(call.call_count,2)
                self.assertEqual(engine.cache,{})
        finally: REQUEST_AI.reset(token)
    def test_disable_server_key(self):
        with patch.dict(os.environ,{'AI_PROVIDER':'gemini','GEMINI_API_KEY':'server-key','ALLOW_SERVER_AI':'false'}):
            self.assertFalse(Investigator().config()['ai_available'])
