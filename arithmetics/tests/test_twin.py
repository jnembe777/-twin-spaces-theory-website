"""
Unit tests for the twin-spaces generator (arithmetics.symbolic.twin).

Verifications are anchored to Vol. 01 *Twin Spaces: Foundations*: the
exponential hierarchy table, the linearity obstruction (rigidity), the
classification ``|Op| = [G:L]``, and the invariant-magma counting formula.
"""

import unittest

import sympy as sp
from sympy import exp, log, sqrt, simplify

from arithmetics.symbolic.expressions import x, y
from arithmetics.symbolic.twin import (
    BijectionAction, ContinuousAction, PermutationAction,
    twin_operation, twin_field, twin_operation_continuous, transport_table,
    CayleyTable, structural_kernel, operation_space, classify,
    count_invariant_magmas, order_complexity,
    candidate_base_operations,
)


class TestBijectionHierarchy(unittest.TestCase):
    """The exponential hierarchy (Vol. 01, Thm. exp-hierarchy)."""

    def setUp(self):
        self.phi = BijectionAction.exponential()

    def test_level_0_is_addition(self):
        self.assertEqual(twin_operation(self.phi, 0, "add").expr, x + y)

    def test_level_minus1_is_multiplication(self):
        self.assertEqual(simplify(twin_operation(self.phi, -1, "add").expr - x * y), 0)

    def test_level_1_is_logsumexp(self):
        self.assertEqual(twin_operation(self.phi, 1, "add").expr,
                         log(exp(x) + exp(y)))

    def test_level_minus2_symmetric_power(self):
        # x ⊙_{e,-2} y = x^{ln y} = e^{ln x · ln y} (symmetric power).
        # SymPy yields y**log(x); compare via the logarithm to avoid branch issues.
        expr = twin_operation(self.phi, -2, "add").expr
        self.assertEqual(simplify(log(expr) - log(x) * log(y)), 0)

    def test_twin_field_neutrals(self):
        tf = twin_field(self.phi, -1)
        # φ^{-1}(0)=exp(0)=1 (additive neutral), φ^{-1}(1)=exp(1)=e
        self.assertEqual(tf["zero"].expr, sp.Integer(1))
        self.assertEqual(tf["one"].expr, sp.E)
        self.assertEqual(simplify(tf["oplus"].expr - x * y), 0)


class TestLinearityObstruction(unittest.TestCase):
    """Rigidity vs flexibility (trivial twins iff φ is an automorphism)."""

    def test_identity_is_trivial(self):
        op = twin_operation(BijectionAction.identity(), 1, "add").expr
        self.assertEqual(simplify(op - (x + y)), 0)

    def test_power_trivial_under_multiplication(self):
        # x^p is an automorphism of (ℝ_{>0}, ·): twin = · (Example 4)
        op = twin_operation(BijectionAction.power(2), 1, "mul").expr
        self.assertEqual(simplify(op - x * y), 0)

    def test_power_nontrivial_under_addition(self):
        # x^2 over + gives the Euclidean/L^2 mean, sqrt(x^2+y^2)
        op = twin_operation(BijectionAction.power(2), 1, "add").expr
        self.assertEqual(simplify(op - sqrt(x ** 2 + y ** 2)), 0)

    def test_exp_multiplication_twin_is_addition(self):
        op = twin_operation(BijectionAction.exponential(), 1, "mul").expr
        self.assertEqual(simplify(op - (x + y)), 0)


class TestContinuousActions(unittest.TestCase):
    """One-parameter Lie group actions."""

    def test_translation(self):
        act = ContinuousAction.translation()
        op = twin_operation_continuous(act, "add").expr
        self.assertEqual(simplify(op - (x + y + act.param)), 0)

    def test_scaling_nontrivial(self):
        act = ContinuousAction.scaling()
        op = twin_operation_continuous(act, "mul").expr
        self.assertEqual(simplify(op - x * y * exp(act.param)), 0)

    def test_power_rigid(self):
        act = ContinuousAction.power()
        op = twin_operation_continuous(act, "mul").expr
        self.assertEqual(simplify(op - x * y), 0)


class TestPermutationGroups(unittest.TestCase):
    """Finite group arithmetic and constructors."""

    def test_cyclic_order(self):
        self.assertEqual(PermutationAction.cyclic(5).order, 5)

    def test_symmetric_order(self):
        self.assertEqual(PermutationAction.symmetric(4).order, 24)

    def test_dihedral_order(self):
        self.assertEqual(PermutationAction.dihedral(4).order, 8)

    def test_klein_order(self):
        self.assertEqual(PermutationAction.klein_four().order, 4)

    def test_inverse_compose(self):
        G = PermutationAction.symmetric(4)
        for g in G.elements[:6]:
            ginv = G.inverse(g)
            self.assertEqual(G.compose(g, ginv), G.identity())

    def test_power(self):
        C5 = PermutationAction.cyclic(5)
        gen = (1, 2, 3, 4, 0)
        self.assertEqual(C5.power(gen, 5), C5.identity())


class TestTransportAndClassification(unittest.TestCase):
    """Transport, kernel, and the classification |Op| = [G:L]."""

    def test_transport_involution(self):
        # Transporting by the identity returns the base table.
        C3 = PermutationAction.cyclic(3)
        base = candidate_base_operations(3)[0]
        self.assertEqual(transport_table(base, C3, C3.identity()), base)

    def test_left_projection_is_rigid(self):
        # x ⊙ y = x is preserved by every permutation: L = G, trivial.
        C4 = PermutationAction.cyclic(4)
        proj = [b for b in candidate_base_operations(4) if b.name == "left-proj"][0]
        info = classify(proj, C4)
        self.assertTrue(info["trivial"])
        self.assertEqual(info["order_L"], C4.order)

    def test_index_equals_num_ops(self):
        # |Op| = [G:L] must hold for every (group, base) pair.
        for G in (PermutationAction.cyclic(3), PermutationAction.dihedral(3),
                  PermutationAction.symmetric(3)):
            for base in candidate_base_operations(3):
                info = classify(base, G)
                self.assertEqual(info["num_twin_ops"], info["index_[G:L]"],
                                 f"{G.name} / {base.name}")

    def test_cyclic_addition_three_ops(self):
        C3 = PermutationAction.cyclic(3)
        add = candidate_base_operations(3)[0]
        self.assertEqual(len(operation_space(add, C3)), 3)
        self.assertEqual(len(structural_kernel(add, C3)), 1)

    def test_order_complexity_generator(self):
        # For C_n on addition (L = {e}), the generator has order complexity n.
        C5 = PermutationAction.cyclic(5)
        add = candidate_base_operations(5)[0]
        gen = (1, 2, 3, 4, 0)
        self.assertEqual(order_complexity(add, C5, gen), 5)


class TestCountingFormula(unittest.TestCase):
    """The invariant-magma counting formula."""

    def test_cyclic_n_to_the_n(self):
        for n in (2, 3, 4):
            self.assertEqual(count_invariant_magmas(PermutationAction.cyclic(n)),
                             n ** n)

    def test_symmetric_large_n_is_two(self):
        self.assertEqual(count_invariant_magmas(PermutationAction.symmetric(4)), 2)


if __name__ == "__main__":
    unittest.main()
