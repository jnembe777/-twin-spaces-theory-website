"""
Unit tests for the multiplicative pillar (twin.multiplicative).

Pins down the deepening of the ``x -> x`` frame: the corrected twin unit, the
identification of affine twisted arithmetic with the multiplicative monoid of an
arithmetic progression (Hilbert monoid), the corrected twisted primes
(``{n : 2n+1 prime}`` for ``(2,1)``), the non-unique factorization (``100`` and
``441``), and the Euler-product defect that measures it.
"""

import unittest

from arithmetics.zeta.euler_product import sieve_primes
from arithmetics.symbolic.twin.multiplicative import (
    twisted_unit, ap_is_closed, ap_primes, corrected_twisted_primes,
    find_non_unique_factorization, is_unique_factorization, euler_defect,
    compare_to_repo_twisted_primes,
    progression_zeta, progression_zeta_closed,
)


class TestTwinUnitAndMonoid(unittest.TestCase):
    def test_twin_unit(self):
        self.assertEqual(twisted_unit(2, 1), 0.0)   # phi^{-1}(1) = 0, not 1
        self.assertEqual(twisted_unit(1, 2), -1.0)

    def test_closure_condition(self):
        self.assertTrue(ap_is_closed(2, 1))
        self.assertTrue(ap_is_closed(3, 1))
        self.assertFalse(ap_is_closed(3, 2))        # d^2 - d = 2 != 0 mod 3

    def test_odd_monoid_primes_are_odd_primes(self):
        self.assertEqual(ap_primes(2, 1, 30),
                         [3, 5, 7, 11, 13, 17, 19, 23, 29])


class TestCorrectedPrimes(unittest.TestCase):
    def test_affine_2_1_is_sophie_germain_flavoured(self):
        # corrected (2,1)-primes = { n : 2n+1 is prime }
        primes = set(sieve_primes(70))
        expected = [n for n in range(1, 31) if (2 * n + 1) in primes]
        self.assertEqual(corrected_twisted_primes(2, 1, 30), expected)

    def test_correction_differs_from_repo(self):
        cmp = compare_to_repo_twisted_primes(2, 1, 30)
        self.assertFalse(cmp["agree"])              # the repo uses unit = 1
        self.assertEqual(cmp["twin_unit"], 0.0)


class TestNonUniqueFactorization(unittest.TestCase):
    def test_odds_are_a_ufd(self):
        self.assertTrue(is_unique_factorization(2, 1, 300))

    def test_mod3_breaks_at_100(self):
        nu = find_non_unique_factorization(3, 1, 150)
        self.assertEqual(nu["m"], 100)
        facs = {tuple(sorted(f)) for f in nu["factorizations"]}
        self.assertEqual(facs, {(4, 25), (10, 10)})

    def test_hilbert_mod4_breaks_at_441(self):
        nu = find_non_unique_factorization(4, 1, 500)
        self.assertEqual(nu["m"], 441)             # 21^2 = 9*49

    def test_euler_defect_tracks_non_uniqueness(self):
        self.assertAlmostEqual(euler_defect(2, 1, 2.0, 300).real, 0.0, places=12)
        self.assertGreater(euler_defect(3, 1, 2.0, 300).real, 1e-6)


class TestDirichletConnection(unittest.TestCase):
    """The twisted zeta is an explicit Hurwitz / Dirichlet L object."""

    def test_odd_zeta_closed_form(self):
        import mpmath
        # (2,1): sum_{odd} n^{-s} = (1-2^{-s}) zeta(s).
        s = 2.0
        closed = float(progression_zeta_closed(2, 1, s))
        self.assertAlmostEqual(closed, float((1 - 2 ** (-s)) * mpmath.zeta(s)),
                               places=10)

    def test_partial_sum_converges_to_closed(self):
        # partial sum (excluding m=1) + 1 -> closed form
        for c, d in [(2, 1), (3, 1)]:
            closed = float(progression_zeta_closed(c, d, 3.0))
            partial = complex(progression_zeta(c, d, 3.0, 20000)).real + 1.0
            self.assertAlmostEqual(partial, closed, places=6)

    def test_density_is_prime_count(self):
        # pi_phi(N) = pi(2N+1) - 1 for (2,1).
        from arithmetics.zeta.euler_product import sieve_primes
        N = 1000
        primes = set(sieve_primes(2 * N + 1))
        pi_phi = len(corrected_twisted_primes(2, 1, N))
        self.assertEqual(pi_phi, len(primes) - 1)   # exclude the prime 2


if __name__ == "__main__":
    unittest.main()
