import copy
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from kinship.agent import OpenAICompatibleClient, ResearchAgent, TOOLS

CASE = json.loads((Path(__file__).resolve().parents[1] / 'examples/synthetic-vietnam-korea-case.json').read_text(encoding='utf-8'))


class MockLocalModel:
    is_remote = False
    def __init__(self): self.turn = 0; self.observed = []
    def complete(self, messages, tools):
        self.turn += 1; self.observed.append(messages)
        if self.turn == 1:
            return {'role':'assistant', 'content': None, 'tool_calls': [
                {'id':'req-1','type':'function','function':{'name':'search_local_case','arguments':json.dumps({'query':'Nguyễn Văn An'})}},
                {'id':'req-2','type':'function','function':{'name':'audit_evidence','arguments':'{}'}}]}
        return {'role':'assistant', 'content':'DRAFT: Case P1 has cited claim C1, but this does not establish identity.'}


class MockRemoteModel(MockLocalModel):
    is_remote = True


class AgentTests(unittest.TestCase):
    def test_tools_have_unique_names_and_restrict_mutation(self):
        names = [x['function']['name'] for x in TOOLS]
        self.assertEqual(len(set(names)), len(names))
        self.assertNotIn('send_email', names)
        self.assertNotIn('edit_case', names)

    def test_guided_mode_never_claims_model_or_archive_search(self):
        result = ResearchAgent(CASE, 'vietnam').run('What next?')
        self.assertEqual(result['mode'], 'guided-offline')
        self.assertEqual(result['plan']['status'], 'draft-not-searched')
        self.assertIn('No AI model', result['answer'])
        self.assertTrue(all(x['record_search_executed'] is False for x in result['archive_leads']))

    def test_model_calls_tools_and_returns_draft(self):
        model = MockLocalModel()
        result = ResearchAgent(CASE, 'vietnam').run('Check name P1', model=model)
        self.assertEqual(result['mode'], 'model-assisted')
        self.assertEqual(model.turn, 2)
        self.assertEqual([x['name'] for x in result['tool_trace']], ['search_local_case','audit_evidence'])
        self.assertIn('DRAFT', result['answer'])
        self.assertIn('local-case-only', model.observed[-1][-2]['content'])

    def test_unknown_tool_rejected_not_run(self):
        agent = ResearchAgent(CASE,'vietnam')
        with self.assertRaisesRegex(ValueError, 'not allowed'):
            agent.call('send_email', {'to': 'someone@example.com'})
        with self.assertRaisesRegex(ValueError, 'Unexpected'):
            agent.call('audit_evidence', {'email': 'fake'})

    def test_remote_model_requires_synthetic_case_and_consent(self):
        with self.assertRaisesRegex(ValueError, 'per-request consent'):
            ResearchAgent(CASE, 'korea').run('Test remote', model=MockRemoteModel())
        private = copy.deepcopy(CASE); private['visibility'] = 'private'
        with self.assertRaisesRegex(ValueError, 'synthetic'):
            ResearchAgent(private, 'korea').run('No private cloud', model=MockRemoteModel(), remote_consent=True)
        result = ResearchAgent(CASE, 'korea').run('Test remote', model=MockRemoteModel(), remote_consent=True)
        self.assertEqual(result['mode'], 'model-assisted')

    def test_endpoint_rejects_arbitrary_http_and_auth_in_url(self):
        with self.assertRaisesRegex(ValueError,'HTTPS'):
            OpenAICompatibleClient('test', 'http://example.com/v1/chat/completions')
        with self.assertRaisesRegex(ValueError,'permission'):
            OpenAICompatibleClient('test', 'https://example.com/v1/chat/completions')
        with self.assertRaisesRegex(ValueError,'credentials'):
            OpenAICompatibleClient('test', 'https://key@example.com/v1/chat/completions', allow_remote=True)
        local = OpenAICompatibleClient('test', 'http://127.0.0.1:11434/v1/chat/completions')
        self.assertFalse(local.is_remote)

    def test_agent_rejects_bad_case_before_tools(self):
        bad = copy.deepcopy(CASE); bad['claims'][0]['artifact_ids']=['A1','A1copy']
        with self.assertRaises(ValueError): ResearchAgent(bad,'vietnam')

    def test_agent_avoids_unverified_ids(self):
        agent = ResearchAgent(CASE,'vietnam')
        with self.assertRaises(ValueError): agent.call('source_evidence', {'artifact_id':'FRAUD'})
        with self.assertRaises(ValueError): agent.call('person_evidence', {'person_id':'FAKE'})

    def test_rejects_empty_question(self):
        with self.assertRaises(ValueError): ResearchAgent(CASE,'korea').run(' ')

if __name__ == '__main__': unittest.main()
