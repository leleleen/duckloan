import unittest

from duckfine import DuckFine


class TestDuckFine(unittest.TestCase):
    def setUp(self):
        self.fine = DuckFine("M001")

    def test_init_stores_member_id(self):
        self.assertEqual(self.fine.member_id, "M001")

    def test_init_total_owed_starts_at_zero(self):
        self.assertEqual(self.fine.total_owed, 0.0)

    def test_zero_days_late_is_free(self):
        self.assertEqual(self.fine.charge(0), 0.0)

    def test_days_within_grace_period_are_free(self):
        self.assertEqual(self.fine.charge(DuckFine.GRACE_DAYS), 0.0)

    def test_first_day_after_grace_is_charged_one_daily_fee(self):
        self.assertAlmostEqual(
            self.fine.charge(DuckFine.GRACE_DAYS + 1), DuckFine.DAILY_FEE
        )

    def test_fee_scales_with_chargeable_days(self):
        # 6 days late - 2 grace = 4 chargeable days * 0.50
        self.assertAlmostEqual(self.fine.charge(6), 2.00)

    def test_deluxe_doubles_the_fee(self):
        # 6 days late -> 2.00, doubled -> 4.00
        self.assertAlmostEqual(self.fine.charge(6, deluxe=True), 4.00)

    def test_deluxe_within_grace_period_is_free(self):
        self.assertEqual(self.fine.charge(2, deluxe=True), 0.0)

    def test_fee_is_capped_at_max_fee(self):
        self.assertAlmostEqual(self.fine.charge(100), DuckFine.MAX_FEE)

    def test_deluxe_fee_is_capped_at_max_fee(self):
        self.assertAlmostEqual(self.fine.charge(100, deluxe=True), DuckFine.MAX_FEE)

    def test_fee_exactly_at_cap_is_not_reduced(self):
        # 12 days late - 2 grace = 10 chargeable * 0.50 = 5.00
        self.assertAlmostEqual(self.fine.charge(12), 5.00)

    def test_negative_days_late_raises_value_error(self):
        with self.assertRaises(ValueError):
            self.fine.charge(-1)

    def test_negative_days_late_does_not_change_total_owed(self):
        with self.assertRaises(ValueError):
            self.fine.charge(-1)
        self.assertEqual(self.fine.total_owed, 0.0)

    def test_charge_adds_fee_to_total_owed(self):
        fee = self.fine.charge(6)
        self.assertAlmostEqual(self.fine.total_owed, fee)

    def test_total_owed_accumulates_across_charges(self):
        self.fine.charge(6)  # 2.00
        self.fine.charge(4)  # 1.00
        self.assertAlmostEqual(self.fine.total_owed, 3.00)

    def test_free_charge_leaves_total_owed_unchanged(self):
        self.fine.charge(1)
        self.assertEqual(self.fine.total_owed, 0.0)

    def test_total_owed_is_not_shared_between_members(self):
        other = DuckFine("M002")
        self.fine.charge(6)
        self.assertEqual(other.total_owed, 0.0)


if __name__ == "__main__":
    unittest.main()
