import unittest

from risk_scoring import RiskScorecard, RiskSignal


class RiskScorecardTest(unittest.TestCase):
    def test_allows_low_risk_signal_set(self):
        score, decision = RiskScorecard().score([
            RiskSignal("new_device", 20, False),
            RiskSignal("velocity", 30, True),
        ])

        self.assertEqual(score, 30)
        self.assertEqual(decision, "ALLOW")


if __name__ == "__main__":
    unittest.main()
