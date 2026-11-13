import copy
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from kinship.research import search_case, person_detail, artifact_detail, case_summary

CASE = json.loads((Path(__file__).resolve().parents[1] / 'examples/synthetic-vietnam-korea-case.json').read_text(encoding='utf-8'))


class LocalResearchTests(unittest.TestCase):
    def test_diacritic_folded_name_search(self):
        results = search_case(CASE, 'Nguyen Van An')
        self.assertEqual(results['results'][0]['id'], 'P1')
        self.assertEqual(results['searched'], 'local-case-only')

    def test_hangul_is_not_romanized(self):
        self.assertEqual(search_case(CASE, '김하늘')['results'][0]['id'], 'P3')
        self.assertEqual(search_case(CASE, 'kim haneul')['total'], 0)

    def test_does_not_infer_links_from_same_surname(self):
        results = search_case(CASE, 'nguyen', kind='people')
        self.assertEqual({r['id'] for r in results['results']}, {'P1','P2'})
        self.assertTrue(all('identity' in r['description'].lower() or 'individual' in r['description'].lower() for r in results['results']))

    def test_artifact_linked_claims_and_shared_group(self):
        result = artifact_detail(CASE, 'A1')
        self.assertEqual(result['independent'], ['A1', 'A1copy'])
        self.assertEqual(result['claims'][0]['id'], 'C1')

    def test_person_detail_reports_relationship_as_claim(self):
        result = person_detail(CASE, 'P1')
        self.assertEqual({a['id'] for a in result['artifacts']}, {'A1', 'A2'})
        self.assertIn('never automatic', result['notice'])

    def test_summary_counts_groups_not_images(self):
        result = case_summary(CASE)
        self.assertEqual(result['source_groups'], 2)
        self.assertEqual(result['artifacts'], 3)

    def test_invalid_case_rejected_even_in_search(self):
        bad = copy.deepcopy(CASE)
        bad['claims'][0]['artifact_ids'] = ['A1','A1copy']
        with self.assertRaisesRegex(ValueError, 'claim.independence'):
            search_case(bad, 'Nguyễn')

    def test_unknown_ids(self):
        with self.assertRaises(ValueError): person_detail(CASE, 'P99')
        with self.assertRaises(ValueError): artifact_detail(CASE, 'A99')

    def test_unknown_kind_and_limit(self):
        with self.assertRaises(ValueError): search_case(CASE, 'An', kind='messages')
        with self.assertRaises(ValueError): search_case(CASE, 'An', limit=100000)
        with self.assertRaises(ValueError): search_case(CASE, 'An', limit=True)

    def test_empty_query_and_overlong(self):
        with self.assertRaises(ValueError): search_case(CASE, '')
        with self.assertRaises(ValueError): search_case(CASE, 'a'*201)


if __name__ == '__main__': unittest.main()
