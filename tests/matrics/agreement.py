import unittest

from textflow.metrics.agreement import AgreementScore


class PercentageAgreementTestCase(unittest.TestCase):
    def test_percentage_agreement(self):
        table = [
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
        scorer = AgreementScore(table)
        scores = scorer.percentage()
        self.assertEqual(0.7, scores.iloc[0]['Score'])


if __name__ == '__main__':
    unittest.main()
