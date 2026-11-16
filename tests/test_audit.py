import copy
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from kinship.audit import audit_case
from kinship.report import format_report

FIXTURE = Path(__file__).resolve().parents[1] / "examples" / "synthetic-vietnam-korea-case.json"


def fixture():
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


class EvidenceAuditTests(unittest.TestCase):
    def test_synthetic_case_passes(self):
        result = audit_case(fixture())
        self.assertTrue(result.ok, result.as_dict())

    def test_duplicated_scan_not_independent(self):
        case = fixture()
        case["claims"][0]["artifact_ids"] = ["A1", "A1copy"]
        result = audit_case(case)
        self.assertFalse(result.ok)
        self.assertIn("claim.independence", [x.code for x in result.findings])

    def test_independent_groups_count(self):
        case = fixture()
        case["claims"][0]["artifact_ids"] = ["A1", "A1copy", "A2"]
        self.assertTrue(audit_case(case).ok)

    def test_strongly_corroborated_needs_three_groups(self):
        case = fixture()
        case["claims"][0]["status"] = "strongly-corroborated"
        self.assertFalse(audit_case(case).ok)
        case["artifacts"].append({"id": "A3", "citation": "Entirely fictional third independent register", "independence_group": "G3"})
        case["claims"][0]["artifact_ids"].append("A3")
        self.assertTrue(audit_case(case).ok)

    def test_claim_foreign_keys(self):
        case = fixture()
        case["claims"][0]["object_id"] = "P404"
        self.assertIn("claim.object", [f.code for f in audit_case(case).findings])
        case = fixture()
        case["claims"][0]["artifact_ids"] = ["A404"]
        self.assertIn("claim.artifact_missing", [f.code for f in audit_case(case).findings])

    def test_duplicate_person_ids(self):
        case = fixture()
        case["people"].append(copy.deepcopy(case["people"][0]))
        self.assertIn("people.duplicate", [f.code for f in audit_case(case).findings])

    def test_large_ancestry_chain_is_iterative(self):
        # 1,600 nodes exceed Python's ordinary recursive DFS depth.
        # All rows are synthetic, without private family information.
        import copy
        size = 1600
        case = fixture()
        case["people"] = [
            {"id": f"ST-{i}", "living": None,
             "names": [{"original": f"Fictional person {i}"}]}
            for i in range(size)
        ]
        case["claims"] = [
            {"id": f"SC-{i}", "subject_id": f"ST-{i}",
             "object_id": f"ST-{i + 1}", "type": "parent_of",
             "status": "hypothesis", "artifact_ids": []}
            for i in range(size - 1)
        ]
        self.assertTrue(audit_case(case).ok)
        case["claims"].append({
            "id": "SC-CYCLE", "subject_id": f"ST-{size - 1}",
            "object_id": "ST-0", "type": "parent_of",
            "status": "hypothesis", "artifact_ids": [],
        })
        self.assertIn("claim.parent_cycle", [f.code for f in audit_case(case).findings])

    def test_parent_cycle_detected(self):
        case = fixture()
        case["claims"].append({"id": "C3", "subject_id": "P2", "object_id": "P1", "type": "parent_of", "status": "hypothesis", "artifact_ids": []})
        self.assertIn("claim.parent_cycle", [f.code for f in audit_case(case).findings])

    def test_public_case_rejects_living_and_unknown(self):
        case = fixture()
        case["visibility"] = "public_historical"
        case["people"][0]["living"] = True
        case["people"][1]["living"] = None
        problems = [x.code for x in audit_case(case).findings]
        self.assertEqual(problems.count("privacy.person"), 2)

    def test_public_case_rejects_restricted_artifact(self):
        case = fixture()
        case["visibility"] = "public_historical"
        case["artifacts"][0]["access"] = "restricted"
        self.assertIn("privacy.artifact", [x.code for x in audit_case(case).findings])

    def test_missing_independence_group(self):
        case = fixture()
        case["artifacts"][0].pop("independence_group")
        self.assertIn("artifact.independence", [x.code for x in audit_case(case).findings])

    def test_missing_citation(self):
        case = fixture()
        case["artifacts"][0].pop("citation")
        self.assertIn("artifact.citation", [x.code for x in audit_case(case).findings])

    def test_report_rejects_bad_evidence(self):
        case = fixture()
        case["claims"][0]["artifact_ids"] = ["A1", "A1copy"]
        result = audit_case(case)
        with self.assertRaisesRegex(ValueError, "audit errors"):
            format_report(case, result)

    def test_report_has_auditable_citations(self):
        case = fixture()
        report = format_report(case, audit_case(case))
        self.assertIn("Entirely fictional parish record", report)
        self.assertIn("G1", report)
        self.assertIn("No relationship is automatically approved", report)

    def test_bad_schema(self):
        case = fixture()
        case["schema_version"] = "2"
        self.assertIn("schema.version", [x.code for x in audit_case(case).findings])

    def test_no_claims_warning(self):
        case = fixture()
        case["claims"] = []
        result = audit_case(case)
        self.assertTrue(result.ok)
        self.assertIn("case.empty", [x.code for x in result.findings])

    def test_malformed_rows_handled(self):
        case = fixture()
        case["claims"] = [None]
        self.assertIn("claims.row", [x.code for x in audit_case(case).findings])


if __name__ == "__main__":
    unittest.main()

class MalformedInputTests(unittest.TestCase):
    def test_non_object_case_rejected_without_crash(self):
        result = audit_case(["bad"])
        self.assertFalse(result.ok)

    def test_bad_json_types_are_findings_not_crashes(self):
        case = fixture()
        case["visibility"] = {"bad": "object"}
        case["artifacts"][0]["access"] = []
        case["claims"][0]["status"] = []
        case["claims"][0]["subject_id"] = []
        case["claims"][0]["object_id"] = []
        case["claims"][0]["type"] = []
        result = audit_case(case)
        self.assertFalse(result.ok)
        self.assertIn("claim.status", [x.code for x in result.findings])
