"""
Unit tests for compact Lie group twin operations (twin.lie).

Anchored to the foundations volume: the linearity obstruction for unitary
actions (addition rigid), the exact SO(2) analysis, the SO(3)-invariance of
the cross product, and the SU(2) quantum-universality instance
(``Op ≅ SU(2) ≅ S^3``).
"""

import unittest

import numpy as np
import sympy as sp

from arithmetics.symbolic.twin.lie import (
    LinearAction, Operation,
    twin_operation_so2, kernel_so2, kernel_profile,
)


class TestSO2Symbolic(unittest.TestCase):
    """Exact one-parameter analysis under SO(2)."""

    def test_addition_is_rigid(self):
        info = kernel_so2(Operation.addition(2, "R"))
        self.assertTrue(info["rigid"])
        self.assertEqual(info["kernel"], "SO(2)")

    def test_addition_transports_to_itself(self):
        res, _ = twin_operation_so2(Operation.addition(2, "R"))
        x0, x1, y0, y1 = sp.symbols("x0 x1 y0 y1")
        self.assertEqual(list(res), [x0 + y0, x1 + y1])

    def test_complex_multiplication_kernel_trivial(self):
        # Rotations are not algebra automorphisms of ℂ ⇒ L = {0}, Op ≅ S^1.
        info = kernel_so2(Operation.complex_multiplication())
        self.assertFalse(info["rigid"])
        self.assertTrue(info["trivial"])
        self.assertEqual(info["kernel"], sp.FiniteSet(0))

    def test_complex_multiplication_is_scaled_rotation(self):
        # x ⊙_{eθ} y = e^{iθ}(z·w); check the (real) leading coefficient cos θ.
        res, theta = twin_operation_so2(Operation.complex_multiplication())
        x0, x1, y0, y1 = sp.symbols("x0 x1 y0 y1")
        coeff = sp.Poly(sp.expand(res[0]), x0, x1, y0, y1).coeff_monomial(x0 * y0)
        self.assertEqual(sp.simplify(coeff - sp.cos(theta)), 0)


class TestLieSampledKernels(unittest.TestCase):
    """Monte-Carlo kernels for SO(3) and SU(2)."""

    def test_su2_addition_rigid(self):
        prof = kernel_profile(Operation.addition(2, "C"),
                              LinearAction.SU2(), n_samples=150)
        self.assertTrue(prof["rigid"])

    def test_so3_cross_product_rigid(self):
        # Rotations preserve the cross product: a×b ↦ R(a×b) = Ra×Rb.
        prof = kernel_profile(Operation.cross_product(),
                              LinearAction.SO3(), n_samples=150)
        self.assertTrue(prof["rigid"])

    def test_su2_generic_gate_trivial_kernel(self):
        # Quantum universality: a generic qubit gate has trivial kernel,
        # so Op ≅ SU(2) ≅ S^3.
        prof = kernel_profile(Operation.random_gate(2, seed=1, field="C"),
                              LinearAction.SU2(), n_samples=200)
        self.assertTrue(prof["kernel_trivial"])
        self.assertFalse(prof["rigid"])


class TestLinearActions(unittest.TestCase):
    """Sanity checks on the sampled group elements."""

    def test_su2_is_unitary_det_one(self):
        rng = np.random.default_rng(3)
        U = LinearAction.SU2().sample(rng)
        self.assertTrue(np.allclose(U.conj().T @ U, np.eye(2), atol=1e-12))
        self.assertAlmostEqual(np.linalg.det(U), 1.0, places=10)

    def test_so3_is_orthogonal_det_one(self):
        rng = np.random.default_rng(3)
        R = LinearAction.SO3().sample(rng)
        self.assertTrue(np.allclose(R.T @ R, np.eye(3), atol=1e-10))
        self.assertAlmostEqual(np.linalg.det(R), 1.0, places=10)


if __name__ == "__main__":
    unittest.main()
