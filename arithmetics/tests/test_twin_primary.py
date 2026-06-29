"""
Unit tests for the primary decomposition of the decision space (twin.primary).

Each test corresponds to a statement of the primary-decomposition section of
``twin_decision_theory.tex``: ``G ≅ ∏ G_p``, ``Op = G/L ≅ ∏ Op_p`` (abelian),
the unique factorisation of operations, separable decision, and the
order-complexity partition ``|C_d| = φ(d) · m_d``.
"""

import unittest

from arithmetics.symbolic.twin import (
    FiniteGroup, PermutationAction, candidate_base_operations,
    prime_factorization, euler_phi,
    primary_components, primary_projection, op_primary_components,
    operation_factorization, verify_primary_decomposition, primary_decision,
    complexity_classes, verify_complexity_partition, twin_primary_decomposition,
)


class TestNumberTheory(unittest.TestCase):
    def test_prime_factorization(self):
        self.assertEqual(prime_factorization(12), {2: 2, 3: 1})
        self.assertEqual(prime_factorization(7), {7: 1})

    def test_euler_phi(self):
        self.assertEqual(euler_phi(12), 4)
        self.assertEqual(euler_phi(9), 6)


class TestPrimaryComponents(unittest.TestCase):
    """G ≅ ∏ G_p and the projections g ↦ (g_p)."""

    def test_c6_components(self):
        G = FiniteGroup.cyclic(6)
        comps = primary_components(G)
        self.assertEqual({p: len(v) for p, v in comps.items()}, {2: 2, 3: 3})

    def test_projection_reconstructs(self):
        # ∏_p g_p = g for every element of C_12.
        G = FiniteGroup.cyclic(12)
        for g in G.elements:
            prod = G.identity
            for gp in primary_projection(G, g).values():
                prod = G.mul(prod, gp)
            self.assertEqual(prod, g)

    def test_nonabelian_rejected(self):
        G = FiniteGroup.from_permutation_action(PermutationAction.symmetric(3))
        with self.assertRaises(ValueError):
            primary_components(G)


class TestOperationDecomposition(unittest.TestCase):
    """Op = G/L ≅ ∏ Op_p with L = ∏ L_p (automatic for abelian G)."""

    def test_c12_mod_order2(self):
        G = FiniteGroup.cyclic(12)
        L = [0, 6]                       # the order-2 subgroup
        v = verify_primary_decomposition(G, L)
        self.assertTrue(v["valid"])
        self.assertEqual(v["orders_Op_p"], {2: 2, 3: 3})
        self.assertEqual(v["index_GL"], 6)

    def test_index_is_product_of_components(self):
        G = FiniteGroup.cyclic(12)
        L = [0, 6]
        Op_p = op_primary_components(G, L)
        prod = 1
        for Q in Op_p.values():
            prod *= Q.order
        self.assertEqual(prod, G.order // len(L))

    def test_unique_factorization_nonempty(self):
        G = FiniteGroup.cyclic(12)
        L = [0, 6]
        f = operation_factorization(G, L, 5)
        self.assertEqual(sorted(f.keys()), [2, 3])
        for coset in f.values():
            self.assertTrue(len(coset) >= 1)


class TestSeparableDecision(unittest.TestCase):
    """A separable cost is optimised componentwise: ∏|Op_p| -> Σ|Op_p|."""

    def test_search_reduction(self):
        G = FiniteGroup.cyclic(12)
        L = [0, 6]                       # Op_2 (order 2) × Op_3 (order 3)
        costs = {2: (lambda c: 0 if G.identity in c else 1),
                 3: (lambda c: min(c, key=repr))}
        d = primary_decision(G, L, costs)
        self.assertEqual(d["search_full"], 6)      # 2 * 3
        self.assertEqual(d["search_reduced"], 5)    # 2 + 3


class TestComplexityPartition(unittest.TestCase):
    """|C_d| = φ(d) · m_d and Σ_{d|n} |C_d| = |G|."""

    def test_cyclic(self):
        self.assertTrue(verify_complexity_partition(FiniteGroup.cyclic(12))["valid"])

    def test_klein(self):
        V = FiniteGroup.direct_product(FiniteGroup.cyclic(2), FiniteGroup.cyclic(2))
        r = verify_complexity_partition(V)
        self.assertTrue(r["valid"])
        # 3 elements of order 2 = φ(2) · 3 cyclic subgroups.
        self.assertEqual(r["by_order"][2]["|C_d|"], 3)
        self.assertEqual(r["by_order"][2]["m_d"], 3)

    def test_product_c2_c4(self):
        G = FiniteGroup.direct_product(FiniteGroup.cyclic(2), FiniteGroup.cyclic(4))
        self.assertTrue(verify_complexity_partition(G)["valid"])


class TestTwinTieIn(unittest.TestCase):
    """Primary decomposition from a concrete abelian twin action."""

    def test_c6_plus_mod6(self):
        C6 = PermutationAction.cyclic(6)
        base = candidate_base_operations(6)[0]      # + mod 6
        res = twin_primary_decomposition(base, C6)
        self.assertTrue(res["decomposition"]["valid"])
        self.assertEqual(res["decomposition"]["primes"], [2, 3])

    def test_nonabelian_action_rejected(self):
        S3 = PermutationAction.symmetric(3)
        base = candidate_base_operations(3)[0]
        with self.assertRaises(ValueError):
            twin_primary_decomposition(base, S3)


if __name__ == "__main__":
    unittest.main()
