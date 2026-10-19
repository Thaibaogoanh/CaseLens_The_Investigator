import copy
import io
import json
import os
import unittest
import urllib.error
from unittest.mock import patch

from app.engine import Investigator, validate_report
from app.fixtures import public_cases
from app.validation import AppError, validate_project, fingerprint


class EngineTests(unittest.TestCase):
    def setUp(self):
        self.engine = Investigator()
        self.cases = public_cases()

    def test_all_replay_reports_have_valid_provenance(self):
        for case in self.cases:
            with self.subTest(case=case['project']['id']):
                result = self.engine.run(case)
                self.assertGreater(result['meta']['verified_references'], 0)
                self.assertEqual(result['meta']['mode'], 'sample')

    def test_mapping_event_uses_occurrence_time_not_email_send_time(self):
        result = self.engine.run(self.cases[0])
        event = next(x for x in result['report']['timeline'] if x['title'] == 'Mapping received')
        self.assertEqual(event['occurred_at'], '2026-10-15T08:45:00Z')

    def test_done_ticket_is_not_fulfilled_commitment(self):
        report = self.engine.run(self.cases[1])['report']
        self.assertEqual(report['commitments'][0]['status'], 'overdue')
        self.assertTrue(any(x['kind'] == 'conflict' for x in report['findings']))

    def test_correction_changes_unknown_to_fulfilled_and_keeps_history(self):
        case = self.cases[2]
        before = self.engine.run(case)['report']
        case['sources'].append(case['supplement'])
        after = self.engine.run(case)['report']
        self.assertEqual(before['summary']['kind'], 'unknown')
        self.assertEqual(after['commitments'][0]['status'], 'fulfilled')
        self.assertGreater(len(after['timeline']), len(before['timeline']))
        self.assertTrue(any(e['title'] == 'Client requests confirmation' for e in after['timeline']))

    def test_correction_timeline_is_sorted_by_event_time(self):
        case = self.cases[2]; case['sources'].append(case['supplement'])
        times = [x['occurred_at'] for x in self.engine.run(case)['report']['timeline']]
        self.assertEqual(times, sorted(times))

    def test_replay_rejects_modified_source(self):
        self.cases[0]['sources'][0]['body'] += ' New facts.'
        with self.assertRaises(AppError) as caught: self.engine.run(self.cases[0])
        self.assertEqual(caught.exception.status, 422)

    def test_source_order_does_not_change_fingerprint(self):
        case = self.cases[0]
        reversed_case = dict(case, sources=list(reversed(case['sources'])))
        self.assertEqual(self.engine.run(case)['meta']['fingerprint'], self.engine.run(reversed_case)['meta']['fingerprint'])

    def test_fingerprint_covers_metadata_and_bodies(self):
        p, s = validate_project(self.cases[0]); first = fingerprint(p, s)
        s[0]['body'] += ' amended'
        self.assertNotEqual(first, fingerprint(p, s))

    def test_mixed_projects_rejected(self):
        case = self.cases[0]; case['sources'].append(self.cases[1]['sources'][0])
        with self.assertRaisesRegex(AppError, 'selected project'): self.engine.run(case)

    def test_duplicate_source_ids_rejected(self):
        case = self.cases[0]; case['sources'].append(copy.deepcopy(case['sources'][0]))
        with self.assertRaisesRegex(AppError, 'Duplicate'): self.engine.run(case)

    def test_empty_input_rejected(self):
        case = self.cases[0]; case['sources'] = []
        with self.assertRaises(AppError): self.engine.run(case)

    def test_non_object_input_rejected(self):
        for bad in ([], None, 'text'):
            with self.subTest(value=bad), self.assertRaises(AppError): self.engine.run(bad)

    def test_naive_timestamp_rejected(self):
        case = self.cases[0]; case['sources'][0]['sent_at'] = '2026-10-15T09:00:00'
        with self.assertRaisesRegex(AppError, 'timezone'): self.engine.run(case)

    def test_large_source_rejected(self):
        self.cases[0]['sources'][0]['body'] = 'x' * 12001
        with self.assertRaises(AppError): self.engine.run(self.cases[0])

    def test_fabricated_quote_rejected(self):
        report = self.engine.run(self.cases[0])['report']
        report['summary']['evidence'][0]['quote'] = 'This never appeared.'
        with self.assertRaisesRegex(AppError, 'unverifiable'): validate_report(report, self.cases[0]['sources'])

    def test_foreign_citation_rejected(self):
        report = self.engine.run(self.cases[0])['report']
        report['summary']['evidence'][0]['source_id'] = 'BCN-E01'
        with self.assertRaises(AppError): validate_report(report, self.cases[0]['sources'])

    def test_unsupported_claim_rejected(self):
        report = self.engine.run(self.cases[0])['report']; report['summary']['evidence'] = []
        with self.assertRaisesRegex(AppError, 'without evidence'): validate_report(report, self.cases[0]['sources'])

    def test_unexpected_fields_and_enum_rejected(self):
        for update in ({'kind': 'certain'}, {'invented': True}):
            report = self.engine.run(self.cases[0])['report']; report['summary'].update(update)
            with self.assertRaises(AppError): validate_report(report, self.cases[0]['sources'])

    def test_invalid_generated_timestamp_rejected(self):
        report = self.engine.run(self.cases[0])['report']; report['timeline'][0]['occurred_at'] = 'yesterday'
        with self.assertRaises(AppError): validate_report(report, self.cases[0]['sources'])

    @patch.dict(os.environ, {}, clear=True)
    def test_missing_key_is_explicit(self):
        case = dict(self.cases[0], mode='live')
        with self.assertRaisesRegex(AppError, 'not configured'): self.engine.run(case)

    def response(self, report):
        return io.BytesIO(json.dumps({'status': 'completed', 'output': [{'content': [{'type': 'output_text', 'text': json.dumps(report)}]}]}).encode())

    @patch.dict(os.environ, {'OPENAI_API_KEY': 'test-not-real', 'AI_DAILY_CALL_LIMIT': '5'}, clear=True)
    def test_provider_contract_and_cache(self):
        report = self.engine.run(self.cases[0])['report']
        with patch('urllib.request.urlopen', return_value=self.response(report)) as mocked:
            one = self.engine.run(dict(self.cases[0], mode='live'))
            two = self.engine.run(dict(self.cases[0], mode='live'))
            self.assertFalse(one['meta']['cached']); self.assertTrue(two['meta']['cached'])
            self.assertEqual(mocked.call_count, 1)
            req = mocked.call_args.args[0]; body = json.loads(req.data)
            self.assertEqual(req.full_url, 'https://api.openai.com/v1/responses')
            self.assertFalse(body['store']); self.assertTrue(body['text']['format']['strict'])
            self.assertNotIn('test-not-real', json.dumps(one))

    @patch.dict(os.environ, {'OPENAI_API_KEY': 'test-not-real', 'AI_DAILY_CALL_LIMIT': '0'}, clear=True)
    def test_daily_budget_blocks_before_provider_call(self):
        with patch('urllib.request.urlopen') as mocked, self.assertRaises(AppError) as caught:
            self.engine.run(dict(self.cases[0], mode='live'))
        self.assertEqual(caught.exception.status, 429); mocked.assert_not_called()

    @patch.dict(os.environ, {'OPENAI_API_KEY': 'test-not-real'}, clear=True)
    def test_provider_failure_does_not_leak_body(self):
        exc = urllib.error.HTTPError('https://api.openai.com', 401, 'unauthorized secret', {}, io.BytesIO(b'PRIVATE'))
        with patch('urllib.request.urlopen', side_effect=exc), self.assertRaises(AppError) as caught:
            self.engine.run(dict(self.cases[0], mode='live'))
        self.assertNotIn('PRIVATE', str(caught.exception)); self.assertNotIn('secret', str(caught.exception))

    @patch.dict(os.environ, {'OPENAI_API_KEY': 'test-not-real'}, clear=True)
    def test_refusal_and_incomplete_handled(self):
        for response in ({'status': 'incomplete'}, {'status': 'completed', 'output': [{'content': [{'type': 'refusal'}]}]}):
            with self.subTest(response=response), patch('urllib.request.urlopen', return_value=io.BytesIO(json.dumps(response).encode())), self.assertRaises(AppError):
                self.engine.run(dict(self.cases[0], mode='live'))

    @patch.dict(os.environ, {'OPENAI_API_KEY': 'test-not-real'}, clear=True)
    def test_live_question_answer_is_validated(self):
        answer = self.engine.run(self.cases[1])['report']['findings'][0]
        with patch('urllib.request.urlopen', return_value=self.response(answer)):
            result = self.engine.ask(dict(self.cases[1], question='Was the incident resolved?'))
        self.assertEqual(result['mode'], 'live'); self.assertEqual(result['answer']['kind'], 'conflict')


if __name__ == '__main__': unittest.main()
