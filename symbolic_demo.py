#!/usr/bin/env python
"""
Demonstration of the symbolic formula generator (arithmetics.symbolic).

Generates, typesets, and numerically evaluates the core objects of the
twisted-zeta framework: arithmetic transfers, their defects, the level-p
operations, and the intrinsic zeta function ζ_p(s).

Run:
    python symbolic_demo.py
"""

import mpmath

from arithmetics.symbolic import (
    n, s, alpha,
    exponential_transfer, iterated_exponential_transfer,
    oplus, additive_identity,
    defect, is_cocycle,
    inner_series, zeta_p, zero_condition, reduced_zero_condition,
    empirical_zero_law,
    eval_inner_series, eval_zeta_p,
)


def show(title, formula):
    """Print a formula in all four output formats."""
    print(f"\n## {title}")
    print("  SymPy  :", formula.expr)
    print("  LaTeX  :", formula.latex())
    print("  Unicode:")
    for line in formula.unicode().splitlines():
        print("    " + line)


def main():
    print("=" * 70)
    print(" Symbolic Formula Generator -- Twisted Zeta Functions")
    print("=" * 70)

    # --- Transfers --------------------------------------------------------
    show("Exponential transfer  phi(n) = alpha^n", exponential_transfer(alpha))
    show("Iterated transfer     phi(n) = exp^{o2}(n)",
         iterated_exponential_transfer(2))

    # --- Defect & cocycle -------------------------------------------------
    d = defect(exponential_transfer(alpha))
    show("Defect  delta_alpha(a, b)", d)
    print("\n  Twisted cocycle identity holds:",
          is_cocycle(exponential_transfer(alpha)))

    # --- Level-p operations ----------------------------------------------
    show("Level-p addition  x (+)_p y", oplus())
    show("Additive identity  0_p = exp^{op}(0)", additive_identity())

    # --- Intrinsic zeta ---------------------------------------------------
    show("Inner Dirichlet series  D_p(s)", inner_series())
    show("Intrinsic zeta  zeta_p(s) = Phi_p(D_p(s))", zeta_p())
    print("\n## Zero conditions")
    print("  zeta_p(s) = 0_p   :", zero_condition())
    print("  reduced (D_p=0)   :", reduced_zero_condition())
    show("Empirical zero law", empirical_zero_law())

    # --- Numeric bridge (mpmath) -----------------------------------------
    print("\n" + "=" * 70)
    print(" Numeric evaluation via mpmath")
    print("=" * 70)
    mpmath.mp.dps = 25
    print(f"  D_0(2)    = {eval_inner_series(0, 2)}  (== zeta(3) = {mpmath.zeta(3)})")
    print(f"  zeta_0(2) = {eval_zeta_p(0, 2)}")
    print(f"  zeta_1(3) = {eval_zeta_p(1, 3, terms=5000)}  (level-1, n>=2)")


if __name__ == "__main__":
    main()
