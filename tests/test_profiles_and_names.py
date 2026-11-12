from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from kinship.names import query_variants
from kinship.plan import make_search_plan
from kinship.profiles import get_profile, REGISTRY


class RegionTests(unittest.TestCase):
    def test_three_regions(self):
        self.assertEqual(set(REGISTRY), {"ex-ussr", "vietnam", "korea"})

    def test_unknown_region(self):
        with self.assertRaises(ValueError):
            get_profile("mars")

    def test_vietnam_accent_safe(self):
        self.assertEqual(query_variants("Đặng Thị Hồng"), ["Đặng Thị Hồng", "Dang Thi Hong"])

    def test_korean_does_not_invent_hanja(self):
        self.assertEqual(query_variants("김하늘"), ["김하늘"])

    def test_cyrillic_keeps_original(self):
        self.assertEqual(query_variants("Алёна"), ["Алёна"])

    def test_variants_keep_independent_originals(self):
        result = query_variants("Nguyễn Văn An", ["阮文安", "Nguyen Van An"])
        self.assertEqual(result[0], "Nguyễn Văn An")
        self.assertIn("阮文安", result)
        self.assertEqual(result.count("Nguyen Van An"), 1)

    def test_plan_is_not_claimed_as_search(self):
        plan = make_search_plan("korea", "김하늘")
        self.assertEqual(plan["status"], "draft-not-searched")
        self.assertIn("No archive searched", plan["limitations"])
        self.assertTrue(plan["archive_leads"])

    def test_empty_name_rejected(self):
        with self.assertRaises(ValueError):
            make_search_plan("vietnam", " ")


if __name__ == "__main__":
    unittest.main()
