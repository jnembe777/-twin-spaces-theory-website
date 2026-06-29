"""
Unit tests for real arithmetic-task costs (twin.tasks).

These verify the operational claims: the transformed (log) domain is stable
where the original domain overflows/underflows, the pre-computation rule fires
on wide-range data, the speed/stability trade-off in op counts, and optimal
base selection for representation tasks.
"""

import math
import random
import unittest

from arithmetics.symbolic.twin.tasks import (
    Bijection, TransformedTotal, relative_error, total_error,
    dynamic_range, recommend_domain, op_count,
    linearization_rmse, optimal_base, arithmetic_task_report,
)


class TestTransformedTotal(unittest.TestCase):
    """Domain-of-computation decision for the log-likelihood."""

    def setUp(self):
        random.seed(0)
        self.small = [10 ** random.uniform(-9, -1) for _ in range(600)]
        self.task = TransformedTotal(Bijection.logarithm())

    def test_transformed_domain_is_accurate(self):
        self.assertLess(total_error(self.task, self.small, "transformed"), 1e-10)

    def test_original_domain_breaks_down(self):
        # The product underflows to 0, so log(product) = -inf: error is infinite.
        err = total_error(self.task, self.small, "original")
        self.assertTrue(math.isinf(err) or err > 1e3)

    def test_narrow_range_either_domain_ok(self):
        xs = [0.4 + 0.1 * i for i in range(8)]   # ~O(1), short list
        self.assertLess(total_error(self.task, xs, "original"), 1e-9)
        self.assertLess(total_error(self.task, xs, "transformed"), 1e-9)


class TestDataRules(unittest.TestCase):
    def test_dynamic_range(self):
        self.assertAlmostEqual(dynamic_range([1e-3, 1.0, 1e3]), 6.0, places=9)

    def test_recommend_transformed_on_wide(self):
        wide = [1e-30] * 200            # product ~1e-6000, far past float headroom
        self.assertEqual(recommend_domain(wide), "transformed")

    def test_recommend_either_on_narrow(self):
        narrow = [2.0, 3.0, 0.5]
        self.assertEqual(recommend_domain(narrow), "either")

    def test_op_count_tradeoff(self):
        c = op_count(100)
        # transformed domain uses fewer transcendentals than the generic fold
        self.assertEqual(c["transformed_domain"]["transcendental"], 101)
        self.assertEqual(c["naive_fold"]["transcendental"], 297)


class TestRelativeError(unittest.TestCase):
    def test_inf_is_infinite_error(self):
        self.assertTrue(math.isinf(relative_error(float("-inf"), -123.0)))

    def test_basic(self):
        self.assertAlmostEqual(relative_error(1.01, 1.0), 0.01, places=12)


class TestOptimalBase(unittest.TestCase):
    """Optimal-base selection for representation/approximation."""

    def setUp(self):
        self.xs = [float(i) for i in range(1, 21)]

    def test_power_law_picks_loglog(self):
        ys = [3.0 * x ** 2 for x in self.xs]
        self.assertEqual(optimal_base(self.xs, ys)["optimal_base"], "loglog")

    def test_exponential_picks_semilogy(self):
        ys = [2.0 * math.exp(0.3 * x) for x in self.xs]
        self.assertEqual(optimal_base(self.xs, ys)["optimal_base"], "semilogy")

    def test_linear_picks_linear(self):
        ys = [2.0 * x + 1.0 for x in self.xs]
        self.assertEqual(optimal_base(self.xs, ys)["optimal_base"], "linear")

    def test_loglog_residual_tiny_for_power_law(self):
        ys = [3.0 * x ** 2 for x in self.xs]
        self.assertLess(linearization_rmse("loglog", self.xs, ys), 1e-9)


class TestReport(unittest.TestCase):
    def test_report_fields(self):
        random.seed(2)
        probs = [10 ** random.uniform(-8, -1) for _ in range(400)]
        r = arithmetic_task_report(probs)
        self.assertEqual(r["recommend"], "transformed")
        self.assertLess(r["error_transformed_domain"], 1e-10)


if __name__ == "__main__":
    unittest.main()
