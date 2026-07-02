import unittest

from backend.scoring import normalize_score_distribution


class ScoringNormalizationTests(unittest.TestCase):
    def test_normalize_score_distribution_produces_distinct_values(self):
        scores = [0.72, 0.72, 0.72]
        normalized = normalize_score_distribution(scores)

        self.assertEqual(len(normalized), 3)
        self.assertEqual(len(set(normalized)), 3)
        self.assertEqual(normalized[0], 1.0)
        self.assertLess(normalized[-1], 1.0)


if __name__ == "__main__":
    unittest.main()
