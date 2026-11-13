"""Pruebas sintéticas, sin consultar plataformas reales."""
import unittest
import json
from unittest.mock import MagicMock, patch
import job_radar as radar


class RadarTests(unittest.TestCase):
    def setUp(self):
        self.profile = radar.read_json("profile.example.json")
        self.offers = radar.validate_offers(radar.read_json("offers.example.json"), "synthetic")

    def test_relevance_and_rules(self):
        results = radar.rank(self.profile, self.offers)
        self.assertEqual(results[0]["id"], "fictional-1")
        self.assertTrue(results[0]["eligible"])
        self.assertFalse(results[-1]["eligible"])
        self.assertEqual(len(results[-1]["excluded_reasons"]), 2)
        self.assertIn("SCADA", " ".join(results[1]["pending"]))

    def test_unknown_experience(self):
        self.profile["years_experience"] = None
        result = radar.rank(self.profile, self.offers)[0]
        self.assertEqual(result["features"][3], 0)
        self.assertTrue(any("insuficiente" in s for s in result["pending"]))

    def test_partial_failure_and_duplicates(self):
        offers, coverage = radar.collect(["offers.example.json", "offers.example.json", "missing.example.json"])
        self.assertEqual(len(offers), 3)
        self.assertFalse(coverage[-1]["ok"])

    def test_cosine(self):
        a, b = radar.cosine_scores("PLC sensores", ["PLC sensores", "contabilidad fiscal"])
        self.assertAlmostEqual(a, 1)
        self.assertEqual(b, 0)
        self.assertEqual(radar.cosine_scores("", [""]), [0])

    def test_expiry(self):
        self.offers[0]["expires_at"] = "2000-01-01"
        result = next(x for x in radar.rank(self.profile, self.offers) if x["id"] == "fictional-1")
        self.assertFalse(result["eligible"])

    def test_logistic_learning(self):
        # Verifica el cálculo con datos artificiales, no precisión en datos reales.
        rows = ([{"features": [.9, 1, 1, 1], "relevant": 1}] * 10
                + [{"features": [.05, 0, 0, 0], "relevant": 0}] * 10)
        model = radar.train(rows)
        self.assertGreater(radar.predict(rows[0]["features"], model), .8)
        self.assertLess(radar.predict(rows[-1]["features"], model), .2)
        self.assertFalse(model["evaluated"])
        with self.assertRaises(ValueError):
            radar.train(rows[:10])
        with self.assertRaises(ValueError):
            radar.train(rows[:10] * 2)

    def test_invalid_data(self):
        self.profile["years_experience"] = float("nan")
        with self.assertRaises(ValueError):
            radar.validate_profile(self.profile)
        with self.assertRaises(ValueError):
            radar.validate_offers([{"id": "incomplete"}], "synthetic")

    def test_all_sources_failed(self):
        offers, coverage = radar.collect(["missing.example.json"])
        self.assertEqual(offers, [])
        self.assertTrue(all(not c["ok"] for c in coverage))

    def test_https_json_feed_import(self):
        response = MagicMock()
        response.__enter__.return_value.read.return_value = json.dumps(self.offers).encode()
        with patch.object(radar, "urlopen", return_value=response):
            offers, coverage = radar.collect(["https://example.invalid/feed.json"])
        self.assertEqual(len(offers), 3)
        self.assertTrue(coverage[0]["ok"])

    def test_model_ranking_keeps_exclusion_rules(self):
        model = {"weights": [1., 1., 1., 1.], "bias": -2.}
        results = radar.rank(self.profile, self.offers, model)
        self.assertIn("estimated_relevance", results[0])
        self.assertFalse(results[-1]["eligible"])


if __name__ == "__main__":
    unittest.main()
