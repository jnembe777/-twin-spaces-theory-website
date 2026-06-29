"""
Unit tests for the symbolic formula generator (arithmetics.symbolic).
"""

import unittest

import sympy as sp
import mpmath
from mpmath import mp

from arithmetics.symbolic import (
    Formula, IterExp, IterLog,
    n, s, a, b, x, y, alpha,
    identity_transfer, exponential_transfer, iterated_exponential_transfer,
    affine_transfer, polynomial_transfer, rational_transfer,
    mixed_exponential_transfer, coherent_twist_transfer,
    phi_level, phi_inverse_level, oplus, otimes,
    additive_identity, multiplicative_identity,
    defect, cocycle_residual, is_cocycle,
    inner_series, zeta_p, zero_condition, reduced_zero_condition,
    empirical_zero_law,
    eval_formula, eval_inner_series, eval_zeta_p,
)


class TestIteratedOperators(unittest.TestCase):
    """Tests for IterExp / IterLog simplification and expansion."""

    def test_level_zero_is_identity(self):
        self.assertEqual(IterExp(x, 0), x)
        self.assertEqual(IterLog(x, 0), x)

    def test_negative_level_folds(self):
        self.assertEqual(IterExp(x, -2), IterLog(x, 2))
        self.assertEqual(IterLog(x, -2), IterExp(x, 2))

    def test_inverse_cancellation(self):
        self.assertEqual(IterExp(IterLog(x, 3), 3), x)
        self.assertEqual(IterLog(IterExp(x, 3), 3), x)

    def test_doit_expands_concrete_level(self):
        self.assertEqual(IterExp(x, 2).doit(), sp.exp(sp.exp(x)))
        self.assertEqual(IterLog(x, 2).doit(), sp.log(sp.log(x)))

    def test_symbolic_level_stays_symbolic(self):
        self.assertIsInstance(IterExp(x, sp.Symbol("q")), IterExp)

    def test_derivative_chain_rule(self):
        # d/dx exp^{∘2}(x) = exp(x) * exp(exp(x))
        deriv = sp.diff(IterExp(x, 2), x).doit()
        expected = sp.exp(x) * sp.exp(sp.exp(x))
        self.assertEqual(sp.simplify(deriv - expected), 0)


class TestFormulaOutputs(unittest.TestCase):
    """Every formula must produce all four output formats."""

    def test_all_formats_nonempty(self):
        f = zeta_p(2)
        self.assertTrue(f.latex())
        self.assertTrue(f.text())
        self.assertTrue(f.unicode())
        self.assertIsInstance(f.expr, sp.Basic)

    def test_latex_keeps_power_exponent(self):
        # Regression: the summand exponent -(s+1) must survive LaTeX printing.
        latex = inner_series().latex()
        self.assertIn("- s - 1", latex)
        self.assertIn(r"\log^{\circ p}", latex)

    def test_iterated_latex_notation(self):
        self.assertEqual(
            iterated_exponential_transfer(2).latex(),
            r"\exp^{\circ 2}\!\left(n\right)",
        )

    def test_subs_and_immutability(self):
        f = exponential_transfer(alpha)
        g = f.subs(alpha, 2)
        self.assertEqual(g.expr, 2 ** n)
        # original untouched
        self.assertEqual(f.expr, alpha ** n)

    def test_expand_levels(self):
        f = phi_level(x, 2).expand_levels()
        self.assertEqual(f.expr, sp.exp(sp.exp(x)))


class TestTransfers(unittest.TestCase):
    """Symbolic transfer factories."""

    def test_identity(self):
        self.assertEqual(identity_transfer().expr, n)

    def test_exponential(self):
        self.assertEqual(exponential_transfer(2).expr, 2 ** n)

    def test_affine(self):
        self.assertEqual(affine_transfer(3, 1).expr, 3 * n + 1)

    def test_polynomial(self):
        # [0, 1, 1] -> n + n^2
        self.assertEqual(sp.expand(polynomial_transfer([0, 1, 1]).expr),
                         n + n ** 2)

    def test_rational(self):
        self.assertEqual(rational_transfer(1).expr, n / (n + 1))

    def test_mixed_form_validation(self):
        with self.assertRaises(ValueError):
            mixed_exponential_transfer(form="bogus")

    def test_coherent_twist(self):
        self.assertEqual(coherent_twist_transfer("sqrt").expr, sp.sqrt(n))
        with self.assertRaises(ValueError):
            coherent_twist_transfer("nope")


class TestOperations(unittest.TestCase):
    """Level-p operations and identities."""

    def test_oplus_level1_is_product(self):
        # x ⊕_1 y = exp(log x + log y) = x*y for positive x, y
        self.assertEqual(oplus(x, y, 1).simplify().expr, x * y)

    def test_otimes_level1_is_power(self):
        # x ⊗_1 y = exp(log x * log y) = x^{log y}
        result = otimes(x, y, 1).expand_levels().expr
        self.assertEqual(sp.simplify(result - sp.exp(sp.log(x) * sp.log(y))), 0)

    def test_oplus_level2_paper_form(self):
        # x ⊕_2 y = exp(log x · log y)  (Example in correction_bis)
        result = oplus(x, y, 2).expand_levels().simplify()
        expected = sp.exp(sp.log(x) * sp.log(y))
        self.assertEqual(sp.simplify(result.expr - expected), 0)

    def test_additive_identity_levels(self):
        self.assertEqual(additive_identity(0).expr, 0)        # 0_0 = 0
        self.assertEqual(additive_identity(1).expand_levels().expr, 1)  # 0_1 = e^0 = 1

    def test_multiplicative_identity_levels(self):
        self.assertEqual(multiplicative_identity(0).expr, 1)             # 1_0 = 1
        self.assertEqual(multiplicative_identity(1).expand_levels().expr, sp.E)  # 1_1 = e


class TestDefect(unittest.TestCase):
    """Defect and twisted cocycle."""

    def test_identity_zero_defect(self):
        # φ(n)=n: δ = a*b - a*b = 0
        self.assertEqual(sp.simplify(defect(identity_transfer()).expr), 0)

    def test_affine_scaling_zero_defect(self):
        # φ(n)=c*n (no translation) preserves multiplication up to scaling:
        # δ = c^2 ab - c ab ≠ 0 in general, but is structured; just check shape.
        d = defect(affine_transfer(2, 0)).expr
        self.assertEqual(sp.simplify(d - (4 * a * b - 2 * a * b)), 0)

    def test_exponential_defect(self):
        # δ_α(a,b) = α^{a+b} - α^{ab}
        d = defect(exponential_transfer(alpha)).expr
        expected = alpha ** (a + b) - alpha ** (a * b)
        self.assertEqual(sp.simplify(d - expected), 0)

    def test_cocycle_identity_holds(self):
        # The twisted cocycle identity is structural: residual ≡ 0 for any φ.
        for transfer in (
            identity_transfer(),
            exponential_transfer(alpha),
            polynomial_transfer([1, 2, 3]),
            rational_transfer(1),
        ):
            self.assertTrue(is_cocycle(transfer),
                            f"cocycle failed for {transfer.description}")


class TestZeta(unittest.TestCase):
    """Intrinsic zeta function and zero conditions."""

    def test_zeta_p_structure(self):
        # ζ_p(s) = Φ_p(D_p(s))
        z = zeta_p().expr
        self.assertIsInstance(z, IterExp)
        self.assertIsInstance(z.args[0], sp.Sum)

    def test_level_zero_collapses_to_classical(self):
        # ζ_0(s) = Σ n^{-(s+1)}
        z0 = zeta_p(0).expr
        self.assertIsInstance(z0, sp.Sum)
        # summand is n^{-(s+1)}
        self.assertEqual(sp.simplify(z0.function - n ** (-(s + 1))), 0)

    def test_zero_condition_is_equation(self):
        eq = zero_condition(2)
        self.assertIsInstance(eq, sp.Eq)
        # reduced condition: D_p(s) = 0
        red = reduced_zero_condition(1)
        self.assertEqual(red.rhs, 0)

    def test_empirical_law(self):
        f = empirical_zero_law()
        # at delta_max = 1, log term vanishes -> Re(rho) ≈ 0.52
        val = f.subs(sp.Symbol("delta_max", positive=True), 1).expr
        self.assertEqual(sp.nsimplify(val), sp.Rational(52, 100))


class TestNumericBridge(unittest.TestCase):
    """mpmath evaluation of generated formulas."""

    def setUp(self):
        mp.dps = 25

    def test_eval_formula_exponential(self):
        val = eval_formula(exponential_transfer(2), n=10)
        self.assertAlmostEqual(float(val.real), 1024.0, places=6)

    def test_inner_series_level0_is_zeta(self):
        # D_0(s) = Σ n^{-(s+1)} = ζ(s+1); at s=2 -> ζ(3)
        val = eval_inner_series(0, 2, dps=25)
        self.assertAlmostEqual(float(val.real),
                               float(mpmath.zeta(3)), places=12)

    def test_zeta_p_level0_matches_classical(self):
        val = eval_zeta_p(0, 2, dps=25)
        self.assertAlmostEqual(float(val.real),
                               float(mpmath.zeta(3)), places=12)

    def test_zeta_p_level1_finite(self):
        val = eval_zeta_p(1, 3, dps=20, terms=2000)
        self.assertTrue(mpmath.isfinite(val.real))
        self.assertGreater(float(val.real), 0)


if __name__ == "__main__":
    unittest.main()
