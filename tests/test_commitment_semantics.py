import copy
import unittest
from app.engine import Investigator, validate_report, PROMPT, REVIEW_PROMPT
from app.fixtures import CASES
from app.analysis import claims_from_report
from app.validation import validate_project, AppError

class CommitmentSemantics(unittest.TestCase):
    def run_case(self,index):
        case=CASES[index]
        return Investigator().run(dict(project=case['project'],sources=case['sources'],mode='sample'))['report']
    def test_atlas_separates_observed_target_and_condition(self):
        item=self.run_case(0)['commitments'][0]
        self.assertEqual(item['status'],'overdue')
        self.assertEqual(item['condition_status'],'not_met')
        self.assertEqual({r['source_id'] for r in item['evidence']},{'ATL-E01','ATL-E02','ATL-E03'})
        self.assertIn('does not establish',item['status_reason'])
    def test_beacon_explicitly_incomplete_after_deadline(self):
        item=self.run_case(1)['commitments'][0]
        self.assertEqual(item['status'],'overdue')
        self.assertEqual(item['condition_status'],'not_stated')
    def test_missing_receipt_not_marked_overdue(self):
        self.assertEqual(self.run_case(2)['commitments'][0]['status'],'not_verified')
    def test_invalid_condition_status_rejected(self):
        report=copy.deepcopy(CASES[0]['report']);report['commitments'][0]['condition_status']='violated'
        _,sources=validate_project(CASES[0])
        with self.assertRaises(AppError): validate_report(report,sources)
    def test_legacy_import_does_not_invent_condition(self):
        report=copy.deepcopy(CASES[0]['report'])
        for key in ('condition','condition_status','status_reason'): report['commitments'][0].pop(key)
        result=Investigator().inspect_snapshot(dict(project=CASES[0]['project'],sources=CASES[0]['sources'],report=report))
        self.assertEqual(result['report']['commitments'][0]['condition_status'],'unknown')
        self.assertIn('Legacy',result['report']['commitments'][0]['status_reason'])
    def test_reviewer_gets_conditions_and_action_premises(self):
        claims=claims_from_report(self.run_case(0))
        item=next(c for c in claims if c['section']=='commitments')
        self.assertIn('not_met',item['statement'])
        self.assertTrue(any(c['section']=='next_actions' for c in claims))
