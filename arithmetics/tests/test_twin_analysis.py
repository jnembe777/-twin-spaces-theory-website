"""
Unit tests for the analytic layer (twin.analysis).

These pin down the computational discoveries that orient the theory:
the power-mean inequality (AM-GM-HM), the invariant/non-invariant boundary
(exp is the unique additive-to-multiplicative homomorphism), tail-adaptive
phi-concentration base selection, the MGF factorization (the twin identity),
and the non-invariance of primality (twisted primes).
"""

import math
import unittest

import numpy as np

from arithmetics.symbolic.twin.analysis import (
    power_mean, geometric_mean, harmonic_mean, verify_power_mean_inequality,
    quasi_arithmetic_mean, empirical_tail, markov_bound, best_phi_bound,
    mgf_factorizes, invariance_report, homomorphism_add_mul_defect,
    additive_defect, twin_prime_spectrum,
    homomorphism_signature, affine_twisted_prime, verify_affine_prime_formula,
    discover_homomorphism_types, discover_twin_primes,
)


class TestQuasiArithmeticMeans(unittest.TestCase):
    def setUp(self):
        self.xs = [1.0, 2.0, 4.0, 8.0]

    def test_arithmetic(self):
        self.assertAlmostEqual(power_mean(1, self.xs), 3.75)

    def test_geometric_is_exp_mean_log(self):
        g = geometric_mean(self.xs)
        self.assertAlmostEqual(g, math.exp(np.mean(np.log(self.xs))))

    def test_ordering_AM_GM_HM(self):
        self.assertGreater(power_mean(1, self.xs), geometric_mean(self.xs))
        self.assertGreater(geometric_mean(self.xs), harmonic_mean(self.xs))

    def test_power_mean_inequality(self):
        self.assertTrue(verify_power_mean_inequality(
            self.xs, [-3, -2, -1, 0, 1, 2, 3]))

    def test_quasi_arith_matches_power_mean(self):
        m = quasi_arithmetic_mean(lambda x: x ** 2, lambda y: y ** 0.5, self.xs)
        self.assertAlmostEqual(m, power_mean(2, self.xs))


class TestInvarianceBoundary(unittest.TestCase):
    """Which structures does a bijection preserve?"""

    def setUp(self):
        self.sample = [0.5, 1.0, 1.5, 2.0, 2.5, 3.0]

    def test_identity_preserves_additivity(self):
        r = invariance_report(lambda x: x, self.sample)
        self.assertTrue(r["additive (+ -> +)"])
        self.assertTrue(r["isometry (metric)"])

    def test_exp_is_unique_homomorphism(self):
        # exp is the only one mapping + to * (phi(x+y)=phi(x)phi(y)).
        self.assertLess(homomorphism_add_mul_defect(np.exp, self.sample), 1e-9)
        for phi in (lambda x: 2 * x + 1, lambda x: x ** 2, np.log):
            self.assertGreater(homomorphism_add_mul_defect(phi, self.sample), 1e-6)

    def test_exp_breaks_additivity_and_metric(self):
        r = invariance_report(np.exp, self.sample)
        self.assertFalse(r["additive (+ -> +)"])
        self.assertTrue(r["homomorphism (+ -> *)"])
        self.assertGreater(r["metric_distortion"], 2.0)  # not an isometry

    def test_affine_not_additive_homomorphism(self):
        # affine is a similarity (order + metric up to scale) but not a + or *
        # homomorphism -- the source of new, non-trivial twin operations.
        self.assertGreater(additive_defect(lambda x: 2 * x + 1, self.sample), 1e-6)


class TestConcentration(unittest.TestCase):
    """phi-concentration bounds and tail-adaptive base selection."""

    def setUp(self):
        self.rng = np.random.default_rng(0)

    def test_markov_bound_is_valid(self):
        X = np.abs(self.rng.normal(0, 1, 100000))
        a = 2.0
        self.assertLessEqual(empirical_tail(X, a),
                             markov_bound(X, a, lambda x: x) + 0.01)

    def test_light_tail_prefers_exponential(self):
        X = self.rng.normal(0, 1, 200000)
        a = float(np.quantile(X, 0.99))
        self.assertIn("e^", best_phi_bound(X, a)["best"])

    def test_heavy_tail_prefers_polynomial(self):
        X = self.rng.pareto(2.5, 200000) + 1.0
        a = float(np.quantile(X, 0.99))
        self.assertTrue(best_phi_bound(X, a)["best"].startswith("x^"))

    def test_mgf_factorizes_for_independent_sum(self):
        X = self.rng.normal(0, 1, 100000)
        Y = self.rng.normal(0, 1, 100000)
        self.assertTrue(mgf_factorizes(X, Y, 0.5)["factorizes"])


class TestTwistedPrimes(unittest.TestCase):
    """Primality is not invariant: it depends on the twin product."""

    def setUp(self):
        self.spectrum = twin_prime_spectrum(30)

    def test_identity_gives_classical(self):
        self.assertEqual(self.spectrum["identity"],
                         [2, 3, 5, 7, 11, 13, 17, 19, 23, 29])

    def test_square_is_coherent_relabel(self):
        self.assertEqual(self.spectrum["square x^2"], self.spectrum["identity"])

    def test_exponential_collapses_to_additive_primes(self):
        # otimes_phi becomes addition; additive irreducibles are {2, 3}.
        self.assertEqual(self.spectrum["exponential 2^n"], [2, 3])

    def test_affine_is_a_new_prime_set(self):
        affine = self.spectrum["affine 2n+1"]
        self.assertIn(4, affine)        # 4 is irreducible under (+) twin product
        self.assertNotIn(12, affine)    # 12 = 2(*)2 since 2*12+1 = 25 = 5*5
        self.assertNotEqual(set(affine), set(self.spectrum["identity"]))


class TestHomomorphismFrames(unittest.TestCase):
    """The four productive frames discovered by the homomorphism signature."""

    def setUp(self):
        self.sample = [1.2, 1.5, 2.0, 2.5, 3.0]

    def test_exp_is_add_to_mul(self):
        self.assertEqual(homomorphism_signature(np.exp, self.sample)["types"],
                         ["+->*"])

    def test_log_is_mul_to_add(self):
        self.assertEqual(homomorphism_signature(np.log, self.sample)["types"],
                         ["*->+"])

    def test_power_is_mul_to_mul(self):
        self.assertEqual(homomorphism_signature(lambda x: x ** 2, self.sample)["types"],
                         ["*->*"])

    def test_identity_carries_both(self):
        t = homomorphism_signature(lambda x: x, self.sample)["types"]
        self.assertIn("+->+", t)
        self.assertIn("*->*", t)

    def test_affine_shift_is_generic(self):
        self.assertEqual(homomorphism_signature(lambda x: 2 * x + 1, self.sample)["types"],
                         ["generic"])

    def test_discovery_sweep(self):
        rows = {r["phi"]: r["types"] for r in discover_homomorphism_types()}
        self.assertEqual(rows["exp"], ["+->*"])
        self.assertEqual(rows["log"], ["*->+"])
        self.assertEqual(rows["2x+1"], ["generic"])


class TestAffinePrimeFormula(unittest.TestCase):
    """The closed-form characterization of affine twisted primes."""

    def test_predicate_examples(self):
        self.assertTrue(affine_twisted_prime(2, 1, 4))    # prime
        self.assertFalse(affine_twisted_prime(2, 1, 12))  # 2*12+1 = 25 = 5*5

    def test_formula_matches_brute_force(self):
        for c, d in [(2, 1), (1, 1), (3, 1), (1, 2), (2, 3)]:
            self.assertTrue(verify_affine_prime_formula(c, d, 50),
                            f"affine({c},{d})")

    def test_spectrum_classification(self):
        rows = {r["transfer"]: r["kind"] for r in discover_twin_primes(30)}
        self.assertEqual(rows["identity"], "classical")
        self.assertEqual(rows["exponential 2^n"], "additive-collapse")
        self.assertEqual(rows["affine 2n+1"], "new")


if __name__ == "__main__":
    unittest.main()
