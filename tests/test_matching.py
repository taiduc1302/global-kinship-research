import unittest

from kinship.matching import compare_catalog_lead

PERSON = {"id": "P1", "names": [{"original": "Nguyễn Văn An", "transliteration": "Nguyen Van An"}], "living": None}
RECORD = {"provider_id": "loc", "record_id": "https://www.loc.gov/item/123/", "source_id": "LOC-123", "kind": "archival_catalog_lead", "title_as_cataloged": "Nguyễn Văn An correspondence", "date_as_cataloged": "1902", "location_as_cataloged": "Vietnam", "identity_verified": False}

class MatchingTests(unittest.TestCase):
    def test_exact_name_is_only_a_lead(self):
        result = compare_catalog_lead(PERSON, RECORD)
        self.assertEqual(result["signals"][0]["type"], "literal_name_mention")
        self.assertTrue(result["review_required"])
        self.assertFalse(result["identity_verified"])
        self.assertFalse(result["claim_created"])
        self.assertFalse(result["merge_performed"])

    def test_name_is_not_inferred_from_shared_surname(self):
        row = dict(RECORD, title_as_cataloged="Huang family genealogy")
        x = compare_catalog_lead(PERSON, row)
        self.assertEqual(x["signals"][0]["type"], "name_not_present_in_catalog_fields")

    def test_supplied_transliteration_mention(self):
        row = dict(RECORD, title_as_cataloged="Nguyen Van An: papers")
        x = compare_catalog_lead(PERSON, row)
        self.assertTrue(any(s["type"] == "literal_name_mention" for s in x["signals"]))

    def test_no_guessing_hanja_or_noms(self):
        korean = {"id": "P2", "names": [{"original": "김하늘"}]}
        row = dict(RECORD, title_as_cataloged="金何", source_id="X")
        self.assertEqual(compare_catalog_lead(korean, row)["signals"][0]["type"], "name_not_present_in_catalog_fields")

    def test_independence_is_not_inflated_by_catalog_hit(self):
        x = compare_catalog_lead(PERSON, RECORD, cited_source_groups=["G1", "G1", "G2"])
        self.assertEqual(x["existing_independent_source_groups"], ["G1", "G2"])
        self.assertEqual(x["new_independent_source_count"], 0)

    def test_reject_invalid_shapes(self):
        for person, record in [(None, RECORD), (PERSON, None), ({"names": []}, RECORD), (PERSON, {"record_id": "X"})]:
            with self.assertRaises(ValueError):
                compare_catalog_lead(person, record)

    def test_reject_fake_verified_catalog(self):
        with self.assertRaises(ValueError):
            compare_catalog_lead(PERSON, dict(RECORD, identity_verified=True))

    def test_dates_and_places_not_assumed_life_events(self):
        x = compare_catalog_lead(PERSON, RECORD)
        self.assertEqual(x["catalog_date"], "1902")
        self.assertEqual(x["catalog_place"], "Vietnam")
        self.assertFalse(x["identity_verified"])
        self.assertNotIn("birth", x)

if __name__ == "__main__":
    unittest.main()