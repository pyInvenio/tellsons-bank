import unittest

from customer_profile import ProfileNormalizer


class ProfileNormalizerTest(unittest.TestCase):
    def test_normalizes_unicode_name_and_domain(self):
        profile = ProfileNormalizer().normalize(
            "cust_test_001",
            "  Ada   Lovelace  ",
            "ADA@Example.Invalid",
        )

        self.assertEqual(profile.display_name, "Ada Lovelace")
        self.assertEqual(profile.email_domain, "example.invalid")
        self.assertEqual(profile.risk_segment, "REVIEW")


if __name__ == "__main__":
    unittest.main()
