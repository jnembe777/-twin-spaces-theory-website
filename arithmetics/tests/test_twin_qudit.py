"""
Unit tests for the SU(n) Weyl integration / qudit layer (twin.qudit).

Anchored to checkable facts: Haar sampling, the eigen-phase (Vandermonde)
density, the classic CUE moments E[tr U] = 0 and E|tr U|^2 = 1, Schur-character
orthonormality (which pins down the Weyl measure), SU(2) consistency, and the
persistence of universality for qudits.
"""

import math
import unittest

import numpy as np

from arithmetics.symbolic.twin.qudit import (
    sample_unitary, eigenphases, weyl_density, weyl_average,
    schur_character, verify_character_orthonormality,
    qudit_class_decision, qudit_universality,
)


class TestSampling(unittest.TestCase):
    def test_unitary(self):
        rng = np.random.default_rng(0)
        U = sample_unitary(4, rng)
        self.assertTrue(np.allclose(U.conj().T @ U, np.eye(4), atol=1e-10))

    def test_special_unit_determinant(self):
        rng = np.random.default_rng(0)
        U = sample_unitary(4, rng, special=True)
        self.assertAlmostEqual(np.linalg.det(U), 1.0, places=8)

    def test_eigenphases_count(self):
        rng = np.random.default_rng(1)
        th = eigenphases(sample_unitary(3, rng))
        self.assertEqual(len(th), 3)
        self.assertTrue(np.all(th <= math.pi + 1e-12) and np.all(th > -math.pi - 1e-12))


class TestWeylMeasure(unittest.TestCase):
    """The Weyl/CUE eigen-phase measure via its moments."""

    def test_density_positive_and_symmetric(self):
        a = weyl_density([0.3, 1.1, 2.0])
        b = weyl_density([1.1, 0.3, 2.0])    # permutation invariant
        self.assertGreater(a, 0)
        self.assertAlmostEqual(a, b, places=12)

    def test_density_n2_closed_form(self):
        th = [0.4, 1.9]
        expected = abs(np.exp(1j * 0.4) - np.exp(1j * 1.9)) ** 2 / (2 * (2 * math.pi) ** 2)
        self.assertAlmostEqual(weyl_density(th), expected, places=12)

    def test_trace_moments(self):
        # E[tr U] = 0 and E|tr U|^2 = 1 over U(3) (classic CUE facts).
        chi = lambda th: np.sum(np.exp(1j * np.asarray(th)))
        mean = weyl_average(chi, 3, samples=20000, seed=0)
        norm = weyl_average(lambda th: abs(chi(th)) ** 2, 3, samples=20000, seed=1)
        self.assertLess(abs(mean), 0.05)
        self.assertAlmostEqual(norm.real, 1.0, delta=0.05)


class TestSchurCharacters(unittest.TestCase):
    def test_trivial_is_one(self):
        self.assertAlmostEqual(schur_character([0, 0, 0], [0.2, 1.0, 2.5]), 1.0, places=10)

    def test_fundamental_is_trace(self):
        th = [0.2, 1.0, 2.5]
        chi = schur_character([1, 0, 0], th)
        self.assertAlmostEqual(chi, np.sum(np.exp(1j * np.asarray(th))), places=10)

    def test_orthonormality_u3(self):
        parts = [[0, 0, 0], [1, 0, 0], [1, 1, 0], [2, 0, 0]]
        res = verify_character_orthonormality(3, parts, samples=30000, tol=0.07)
        self.assertTrue(res["orthonormal"])


class TestSU2Consistency(unittest.TestCase):
    def test_fundamental_norm_one(self):
        # <chi_fund, chi_fund>_SU(2) = 1.
        val = weyl_average(lambda th: abs(np.sum(np.exp(1j * np.asarray(th)))) ** 2,
                           2, samples=30000, special=True, seed=3)
        self.assertAlmostEqual(val.real, 1.0, delta=0.05)


class TestQuditDecisionAndUniversality(unittest.TestCase):
    def test_class_decision_average(self):
        # Weyl average of |tr U|^2 over SU(3) is close to 1.
        d = qudit_class_decision(lambda th: abs(np.sum(np.exp(1j * np.asarray(th)))) ** 2,
                                 3, special=True, samples=15000, opt_samples=1000)
        self.assertAlmostEqual(d["weyl_average"], 1.0, delta=0.08)

    def test_universality_d3(self):
        u = qudit_universality(3, samples=150, seed=1)
        self.assertTrue(u["kernel_trivial"])
        self.assertEqual(u["Op"], "SU(3)")

    def test_universality_d4(self):
        u = qudit_universality(4, samples=120, seed=1)
        self.assertTrue(u["kernel_trivial"])


if __name__ == "__main__":
    unittest.main()
