import csv
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from kinship.legacy import import_ex_ussr_registers

HEADERS = {
  'person-register.csv': ['person_id','preferred_label','living_status','names_as_written'],
  'artifact-register.csv': ['artifact_id','source_title','independence_group','archival_reference','repository_or_archive','source_url_or_path'],
  'claims-register.csv': ['claim_id','claim_text','subject_person_ids','artifact_ids','status','rationale'],
  'relationship-register.csv': ['relationship_id','person_a_id','person_b_id','relationship_type','supporting_artifact_ids','status','rationale'],
  'search-log.csv': ['search_id','query','result_status','source_or_domain'],
}


def write(folder, name, rows):
    with (folder/name).open('w',newline='',encoding='utf-8') as handle:
        writer=csv.DictWriter(handle,fieldnames=HEADERS[name]); writer.writeheader(); writer.writerows(rows)


class LegacyImportTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.folder=Path(self.temp.name)
        for name in HEADERS: write(self.folder,name,[])
        write(self.folder,'person-register.csv',[
          {'person_id':'P-1','preferred_label':'Иван','names_as_written':'Иван Петров','living_status':'deceased'},
          {'person_id':'P-2','preferred_label':'Мария','names_as_written':'Мария Петрова','living_status':'unknown'}])
        write(self.folder,'artifact-register.csv',[
          {'artifact_id':'A-1','source_title':'Fictional register','archival_reference':'f. 1 op. 2','repository_or_archive':'Synthetic Archive','independence_group':'G-1'},
          {'artifact_id':'A-2','source_title':'Fictional second register','archival_reference':'f. 5 op. 7','repository_or_archive':'Synthetic Archive','independence_group':'G-2'}])
        write(self.folder,'claims-register.csv',[
          {'claim_id':'C-1','claim_text':'Fictional date recorded','subject_person_ids':'P-1','artifact_ids':'A-1','status':'single-source'}])
        write(self.folder,'relationship-register.csv',[
          {'relationship_id':'R-1','person_a_id':'P-1','person_b_id':'P-2','relationship_type':'parent_of','supporting_artifact_ids':'A-1;A-2','status':'corroborated'}])
        write(self.folder,'search-log.csv',[
          {'search_id':'S-1','query':'Fake archive query','result_status':'no-results','source_or_domain':'Synthetic Catalog'}])

    def import_case(self):
        return import_ex_ussr_registers(self.folder,case_id='synthetic-import-1',question='Which records exist?')

    def test_import_preserves_names_and_provenance(self):
        data=self.import_case()
        self.assertEqual(data['people'][0]['names'][0]['original'],'Иван Петров')
        self.assertEqual(data['people'][1]['living'],None)
        self.assertEqual(data['artifacts'][0]['independence_group'],'G-1')
        self.assertEqual(data['search_log'][0]['result_status'],'no-results')
        self.assertEqual(data['claims'][1]['type'],'parent_of')
        self.assertEqual(data['import_metadata']['format'],'ex-ussr-csv')
        self.assertEqual(data['artifacts'][0]['legacy_ex_ussr']['archival_reference'],'f. 1 op. 2')

    def test_duplicate_source_cannot_justify_corroboration(self):
        path=self.folder/'artifact-register.csv'
        with path.open(encoding='utf-8') as handle:
            rows=list(csv.DictReader(handle))
        rows[1]['independence_group']='G-1'
        write(self.folder,'artifact-register.csv',rows)
        with self.assertRaisesRegex(ValueError,'claim.independence'):
            self.import_case()

    def test_malformed_header_fails_closed(self):
        (self.folder/'claims-register.csv').write_text('wrong,columns\n',encoding='utf-8')
        with self.assertRaisesRegex(ValueError,'Invalid claims-register'):
            self.import_case()

    def test_unsupported_relationship_rejected(self):
        write(self.folder,'relationship-register.csv',[{'relationship_id':'R-1','person_a_id':'P-1','person_b_id':'P-2','relationship_type':'assumed_related','status':'hypothesis'}])
        with self.assertRaisesRegex(ValueError,'explicit mapping'):
            self.import_case()

    def test_multiple_subjects_rejected(self):
        write(self.folder,'claims-register.csv',[{'claim_id':'C-1','claim_text':'Ambiguous','subject_person_ids':'P-1;P-2','status':'hypothesis'}])
        with self.assertRaisesRegex(ValueError,'exactly one unambiguous'):
            self.import_case()

    def test_does_not_interpret_local_file_path_as_public_link(self):
        path=self.folder/'artifact-register.csv'
        with path.open(encoding='utf-8') as handle:
            rows=list(csv.DictReader(handle))
        rows[0]['source_url_or_path']='C:\\Secret\\personal.pdf'
        write(self.folder,'artifact-register.csv',rows)
        self.assertNotIn('url',self.import_case()['artifacts'][0])


if __name__ == '__main__': unittest.main()
