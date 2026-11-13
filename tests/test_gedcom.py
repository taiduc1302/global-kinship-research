"""Synthetic-only GEDCOM interchange tests."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from kinship.audit import audit_case
from kinship.gedcom import import_gedcom
from kinship.graph import relationship_graph

DOC = """0 HEAD
1 SOUR FAKE
1 GEDC
2 VERS 5.5.1
2 FORM LINEAGE-LINKED
1 CHAR UTF-8
0 @I1@ INDI
1 NAME Nguyễn Văn /An/
1 SEX M
1 BIRT
2 DATE 4 FEB 1901
2 PLAC Hà Nội
2 SOUR @S1@
3 PAGE Page 12
1 DEAT Y
0 @I2@ INDI
1 NAME 김 /하늘/
1 SEX F
1 BIRT
2 DATE 1905
0 @I3@ INDI
1 NAME Aleksandr /Petrov/
0 @F1@ FAM
1 HUSB @I1@
1 WIFE @I2@
1 CHIL @I3@
1 SOUR @S1@
0 @S1@ SOUR
1 TITL Fictional register, volume 1
0 TRLR
"""


def imported(text=DOC):
    return import_gedcom(text, case_id="synthetic-gedcom", question="Which source records indicate kinship?", region="vietnam")


class GedcomTests(unittest.TestCase):
    def test_valid_tree_and_nonproof_relationships(self):
        case = imported()
        self.assertTrue(audit_case(case).ok)
        self.assertEqual(len(case["people"]), 3)
        self.assertEqual(len([c for c in case["claims"] if c["type"] == "parent_of"]), 2)
        self.assertEqual(len([c for c in case["claims"] if c["type"] == "spouse_of"]), 1)
        self.assertTrue(all(c["status"] == "hypothesis" for c in case["claims"] if c["type"] in ("parent_of", "spouse_of")))
        self.assertEqual(case["visibility"], "private")
        self.assertEqual(case["people"][0]["names"][0]["original"], "Nguyễn Văn An")
        self.assertEqual(case["people"][1]["names"][0]["original"], "김 하늘")
        self.assertEqual(case["people"][2]["living"], None)
        self.assertEqual(case["people"][0]["living"], False)

    def test_source_page_shares_origin_and_does_not_double_count(self):
        case = imported()
        self.assertEqual(len(case["artifacts"]), 2)
        self.assertEqual(len({a["independence_group"] for a in case["artifacts"]}), 1)
        self.assertEqual([c for c in case["claims"] if c["type"] == "birth_date"][0]["status"], "single-source")
        graph = relationship_graph(case)
        self.assertEqual(len(graph["edges"]), 3)
        self.assertFalse(graph["external_search_executed"])
        self.assertTrue(all(len(x["independent_source_groups"]) == 1 for x in graph["edges"]))

    def test_unsupported_version_is_rejected_not_silently_converted(self):
        with self.assertRaisesRegex(ValueError, "Only GEDCOM 5.5.1"):
            imported(DOC.replace("VERS 5.5.1", "VERS 7.0"))

    def test_charset_and_text_limits(self):
        with self.assertRaisesRegex(ValueError, "character set"):
            imported(DOC.replace("CHAR UTF-8", "CHAR ANSEL"))
        with self.assertRaisesRegex(ValueError, "too large"):
            imported(DOC + " " * 512_000)
        with self.assertRaisesRegex(ValueError, "NUL"):
            imported(DOC.replace("FAKE", "FA\x00KE"))

    def test_pointer_references_and_duplicates(self):
        with self.assertRaisesRegex(ValueError, "missing child"):
            imported(DOC.replace("1 CHIL @I3@", "1 CHIL @I404@"))
        with self.assertRaisesRegex(ValueError, "Missing GEDCOM source"):
            imported(DOC.replace("2 SOUR @S1@", "2 SOUR @S404@"))
        with self.assertRaisesRegex(ValueError, "Duplicate GEDCOM pointer"):
            imported(DOC.replace("0 @S1@ SOUR", "0 @I3@ SOUR"))

    def test_cycle_cannot_be_ingested(self):
        cyclic = DOC.replace("0 @S1@ SOUR", "0 @F2@ FAM\n1 HUSB @I3@\n1 CHIL @I1@\n0 @S1@ SOUR")
        with self.assertRaisesRegex(ValueError, "cyclic links"):
            imported(cyclic)

    def test_malformed_levels_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "level transition"):
            imported(DOC.replace("1 NAME Nguyen", "1 NAME Nguyen").replace("2 DATE 1905", "4 DATE 1905"))

    def test_missing_name_is_explicit_not_invented(self):
        case = imported(DOC.replace("1 NAME Aleksandr /Petrov/", "1 SEX U"))
        self.assertIn("Unnamed individual", case["people"][2]["names"][0]["original"])
        self.assertTrue(case["import_metadata"]["warnings"])

    def test_no_unsupported_media_or_residence_data(self):
        case = imported(DOC.replace("1 SEX M", "1 SEX M\n1 RESI\n2 ADDR Secret Address\n1 OBJE @O1@"))
        self.assertNotIn("Secret Address", repr(case))
        self.assertTrue(any("Media or residence" in w for w in case["import_metadata"]["warnings"]))

    def test_unnamed_unsupported_top_level_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "Unsupported top-level"):
            imported(DOC.replace("0 TRLR", "0 _MALICIOUS payload\n0 TRLR"))

    def test_all_claim_edges_preserve_distinct_person_ids(self):
        case = imported(DOC.replace("1 NAME 김 /하늘/", "1 NAME Nguyễn Văn /An/"))
        graph = relationship_graph(case)
        self.assertEqual(len(graph["nodes"]), 3)
        self.assertEqual(len(set(n["id"] for n in graph["nodes"])), 3)
        self.assertEqual(graph["nodes"][0]["label"], graph["nodes"][1]["label"])

    def test_public_case_still_rejects_unknown_living(self):
        case = imported()
        case["visibility"] = "public_historical"
        self.assertFalse(audit_case(case).ok)

    def test_no_auto_access_to_archives(self):
        case = imported()
        self.assertEqual(case["search_log"], [])
        self.assertEqual(case["import_metadata"]["source"], "user-supplied local file")


if __name__ == "__main__":
    unittest.main()
