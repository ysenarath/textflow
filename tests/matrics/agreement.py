import unittest

from textflow.metrics.agreement import AgreementScore

MULTI_CLASS_EXAMPLE = [
    ("r1", "I01", "high"), ("r2", "I01", "high"),
    ("r1", "I02", "high"), ("r2", "I02", "high"),
    ("r1", "I03", "high"), ("r2", "I03", "low"),
    ("r1", "I04", "low"), ("r2", "I04", "high"),
    ("r1", "I05", "low"), ("r2", "I05", "low"),
    ("r1", "I06", "low"), ("r2", "I06", "low"),
    ("r1", "I07", "low"), ("r2", "I07", "low"),
    ("r1", "I08", "low"), ("r2", "I08", "high"),
    ("r1", "I09", "low"), ("r2", "I09", "low"),
    ("r1", "I10", "low"), ("r2", "I10", "low"),
]

MULTI_LABEL_EXAMPLE = [
    ("r1", "I01", "high"), ("r1", "I01", "low"), ("r2", "I01", "high"), ("r2", "I01", "low"),
    ("r1", "I02", "high"), ("r2", "I02", "high"),
    ("r1", "I03", "low"), ("r2", "I03", "low"),
    ("r1", "I04", "low"), ("r1", "I04", "high"), ("r2", "I04", "high"),
    ("r1", "I05", "low"), ("r2", "I05", "low"),
    ("r1", "I06", "low"), ("r2", "I06", "low"),
    ("r1", "I07", "low"), ("r2", "I07", "low"),
    ("r1", "I08", "low"), ("r2", "I08", "high"), ("r2", "I08", "low"),
    ("r1", "I09", "low"), ("r2", "I09", "low"),
    ("r1", "I10", "low"), ("r2", "I10", "low"),
]


class PercentageAgreementTestCase(unittest.TestCase):
    def test_percentage_agreement(self):
        scorer = AgreementScore(MULTI_CLASS_EXAMPLE)
        scores = scorer.percentage()
        self.assertEqual(0.7, scores.iloc[0]['Score'])

    def test_multi_label_percentage_agreement(self):
        scorer = AgreementScore(MULTI_LABEL_EXAMPLE)
        scores = scorer.percentage()
        self.assertLessEqual(0.8, scores.iloc[0]['Score'])


class KappaAgreementTestCase(unittest.TestCase):
    def test_kappa_agreement(self):
        scorer = AgreementScore(MULTI_CLASS_EXAMPLE)
        scores = scorer.kappa()
        self.assertAlmostEqual(0.348, scores.iloc[0]['Score'], places=3)

    def test_multi_label_kappa_agreement(self):
        scorer = AgreementScore(MULTI_LABEL_EXAMPLE)
        scores = scorer.kappa()
        self.assertAlmostEqual(0.699, scores.iloc[0]['Score'], places=3)


if __name__ == '__main__':
    unittest.main()
