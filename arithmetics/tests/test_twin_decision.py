"""
Unit tests for the group-theoretic decision layer (twin.decision).

Each test corresponds to a statement of ``twin_decision_theory.tex``:
the class equation, the class-function reduction principle, the corrected
classification (``Op = G/L`` is a homogeneous space, a group iff ``L`` normal),
the orbit (Burnside) decomposition, and the Weyl integration instance.
"""

import math
import unittest

from arithmetics.symbolic.twin import (
    PermutationAction, candidate_base_operations,
    FiniteGroup, class_equation, is_class_function, class_average,
    decision_report, operation_orbits, twin_decision,
    su2_class_average, su2_class_decision,
)


class TestClassEquation(unittest.TestCase):
    """|G| = |Z| + Σ [G:C(x_i)] across generalised group families."""

    def _check_sum(self, G, n_classes, center, sizes):
        eq = class_equation(G)
        self.assertEqual(eq["order"], sum(eq["class_sizes"]))
        self.assertEqual(eq["num_classes"], n_classes)
        self.assertEqual(eq["center_size"], center)
        self.assertEqual(sorted(eq["class_sizes"]), sorted(sizes))

    def test_cyclic_abelian(self):
        self._check_sum(FiniteGroup.cyclic(6), 6, 6, [1] * 6)

    def test_klein_product(self):
        V = FiniteGroup.direct_product(FiniteGroup.cyclic(2), FiniteGroup.cyclic(2))
        self._check_sum(V, 4, 4, [1] * 4)

    def test_symmetric_3(self):
        G = FiniteGroup.from_permutation_action(PermutationAction.symmetric(3))
        self._check_sum(G, 3, 1, [1, 2, 3])

    def test_symmetric_4(self):
        G = FiniteGroup.from_permutation_action(PermutationAction.symmetric(4))
        self._check_sum(G, 5, 1, [1, 3, 6, 6, 8])

    def test_dihedral_4(self):
        self._check_sum(FiniteGroup.dihedral(4), 5, 2, [1, 1, 2, 2, 2])

    def test_quaternion_8(self):
        # Q_8 and D_4 share the class equation 8 = 2 + 2 + 2 + 2.
        self._check_sum(FiniteGroup.quaternion8(), 5, 2, [1, 1, 2, 2, 2])


class TestClassFunctions(unittest.TestCase):
    """Order is a class function; conjugation-variant costs are not."""

    def test_order_is_class_function(self):
        G = FiniteGroup.from_permutation_action(PermutationAction.symmetric(4))
        self.assertTrue(is_class_function(G, G.element_order))

    def test_noninvariant_cost_is_not(self):
        G = FiniteGroup.from_permutation_action(PermutationAction.symmetric(3))
        # image of the point 0 varies within a conjugacy class
        self.assertFalse(is_class_function(G, lambda p: p[0]))

    def test_class_average_matches(self):
        # C_4 element orders {1,4,2,4} -> mean 11/4.
        G = FiniteGroup.cyclic(4)
        self.assertAlmostEqual(class_average(G, G.element_order), 11 / 4)

    def test_decision_report_reduces(self):
        G = FiniteGroup.from_permutation_action(PermutationAction.symmetric(4))
        rep = decision_report(G, G.element_order)
        self.assertTrue(rep["cost_is_class_function"])
        # A class-function cost yields one cell per conjugacy class: 24 -> 5
        # (orders are 1,2,2,3,4 — two distinct classes share order 2).
        self.assertEqual(rep["num_cells"], 5)
        self.assertEqual(rep["optimal"]["cost"], 1)  # identity class, order 1


class TestNormalityAndQuotient(unittest.TestCase):
    """Op is a group iff L is normal; quotient guards against non-normality."""

    def setUp(self):
        self.S3 = FiniteGroup.from_permutation_action(PermutationAction.symmetric(3))
        self.A3 = [(0, 1, 2), (1, 2, 0), (2, 0, 1)]          # alternating, normal
        self.H = [(0, 1, 2), (1, 0, 2)]                       # a transposition, not normal

    def test_alternating_is_normal(self):
        self.assertTrue(self.S3.is_normal(self.A3))

    def test_transposition_not_normal(self):
        self.assertFalse(self.S3.is_normal(self.H))

    def test_quotient_order(self):
        Q = self.S3.quotient(self.A3)            # S_3 / A_3 ≅ C_2
        self.assertEqual(Q.order, 2)

    def test_quotient_rejects_non_normal(self):
        with self.assertRaises(ValueError):
            self.S3.quotient(self.H)


class TestTwinDecision(unittest.TestCase):
    """The corrected classification and orbit-based decision cells."""

    def setUp(self):
        self.base4 = candidate_base_operations(4)[0]   # + mod 4

    def test_index_equals_num_operations(self):
        # |Op| = [G:L] holds whether or not L is normal.
        for G in (PermutationAction.cyclic(4), PermutationAction.dihedral(4),
                  PermutationAction.symmetric(4)):
            r = twin_decision(self.base4, G)
            self.assertEqual(r["num_operations"], r["index_GL"])

    def test_cyclic_is_group_case(self):
        r = twin_decision(self.base4, PermutationAction.cyclic(4))
        self.assertTrue(r["L_normal"])
        self.assertTrue(r["Op_is_group"])
        self.assertIn("class_equation", r)

    def test_s4_not_normal_weyl_reduction(self):
        # Discovery/correction: L is order-2 and NOT normal in S_4, so Op is a
        # homogeneous space (not a group). The decision cells are the orbits
        # under the Weyl group N_G(L)/L (here of order 2): 12 ops -> 5 cells.
        r = twin_decision(self.base4, PermutationAction.symmetric(4))
        self.assertFalse(r["L_normal"])
        self.assertFalse(r["Op_is_group"])
        self.assertEqual(r["num_operations"], 12)
        self.assertEqual(r["weyl_order"], 2)
        self.assertEqual(r["num_decision_cells"], 5)

    def test_orbits_never_exceed_operations(self):
        ops, cells = operation_orbits(self.base4, PermutationAction.dihedral(4))
        self.assertLessEqual(len(cells), len(ops))


class TestWeylSU2(unittest.TestCase):
    """The class equation as the Weyl integration formula on SU(2)."""

    def test_normalisation(self):
        # ∫_0^π (2/π) sin²θ dθ = 1 (the continuous class equation).
        self.assertAlmostEqual(su2_class_average(lambda t: 1.0), 1.0, places=6)

    def test_character_average_zero(self):
        # E[2 cos θ] = 0 for the standard SU(2) character.
        self.assertAlmostEqual(su2_class_average(lambda t: 2 * math.cos(t)),
                               0.0, places=6)

    def test_class_decision_argmin(self):
        d = su2_class_decision(lambda t: math.sin(t) ** 2, minimize=True)
        self.assertAlmostEqual(d["optimal_angle"], 0.0, places=3)
        self.assertAlmostEqual(d["weyl_normalisation"], 1.0, places=6)


if __name__ == "__main__":
    unittest.main()
