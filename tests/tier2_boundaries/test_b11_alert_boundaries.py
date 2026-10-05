"""
Tier 2: Boundary 11 (B11) - Look-Ahead Alert Card Boundaries
Validates risk classification boundary thresholds: 49.9 vs 50.0, 74.9 vs 75.0, 84.9 vs 85.0.
"""

import unittest


def classify_risk_index(rh: float) -> str:
    """Classifies risk level based on docs/03 § 5 thresholds."""
    if rh < 50.0:
        return "LOW"
    elif rh < 75.0:
        return "MODERATE"
    elif rh < 85.0:
        return "HIGH"
    else:
        return "CRITICAL"


class TestB11AlertBoundaries(unittest.TestCase):
    def test_01_low_risk_threshold_boundary(self):
        """Score 49.9 is LOW, 50.0 is MODERATE."""
        self.assertEqual(classify_risk_index(49.9), "LOW")
        self.assertEqual(classify_risk_index(50.0), "MODERATE")

    def test_02_moderate_risk_threshold_boundary(self):
        """Score 74.9 is MODERATE, 75.0 is HIGH."""
        self.assertEqual(classify_risk_index(74.9), "MODERATE")
        self.assertEqual(classify_risk_index(75.0), "HIGH")

    def test_03_high_to_critical_threshold_boundary(self):
        """Score 84.9 is HIGH, 85.0 is CRITICAL."""
        self.assertEqual(classify_risk_index(84.9), "HIGH")
        self.assertEqual(classify_risk_index(85.0), "CRITICAL")

    def test_04_target_demo_scenario_score(self):
        """SYN-NHK-05 target score 84.2 is strictly HIGH risk (Yellow Caution)."""
        self.assertEqual(classify_risk_index(84.2), "HIGH")

    def test_05_ceiling_score_100_is_critical(self):
        """Maximum score 100.0 is strictly CRITICAL."""
        self.assertEqual(classify_risk_index(100.0), "CRITICAL")


if __name__ == "__main__":
    unittest.main()
