"""
Symbolic formula generator for the twisted zeta framework.

A SymPy-backed engine that mirrors the numeric framework symbolically. Every
generator returns a :class:`~arithmetics.symbolic.expressions.Formula`, which
exposes four output formats:

* the native SymPy object (``.expr``) for exact manipulation,
* LaTeX (``.latex()``),
* console text / Unicode (``.text()`` / ``.unicode()``),
* a numeric bridge to mpmath (``.evalf()`` / ``.lambdify()`` and the helpers in
  :mod:`arithmetics.symbolic.numeric`).

Quick start::

    from arithmetics.symbolic import exponential_transfer, defect, zeta_p

    phi = exponential_transfer(2)          # 2**n
    print(defect(phi).latex())             # delta_phi(a, b) in LaTeX
    print(zeta_p(2).unicode())             # intrinsic zeta_2(s)

Submodules:

* :mod:`~arithmetics.symbolic.expressions` -- core wrapper and iterated ops,
* :mod:`~arithmetics.symbolic.transfers`   -- transfer formulas phi(n),
* :mod:`~arithmetics.symbolic.operations`  -- level-p operations and identities,
* :mod:`~arithmetics.symbolic.defect`      -- defect cocycle,
* :mod:`~arithmetics.symbolic.zeta`        -- intrinsic zeta_p(s),
* :mod:`~arithmetics.symbolic.numeric`     -- mpmath evaluation.
"""

from arithmetics.symbolic.expressions import (
    Formula, IterExp, IterLog,
    n, s, a, b, c, p, x, y, alpha, beta,
)
from arithmetics.symbolic.transfers import (
    identity_transfer,
    exponential_transfer,
    iterated_exponential_transfer,
    affine_transfer,
    polynomial_transfer,
    rational_transfer,
    mixed_exponential_transfer,
    coherent_twist_transfer,
)
from arithmetics.symbolic.operations import (
    phi_level, phi_inverse_level,
    oplus, otimes,
    additive_identity, multiplicative_identity,
)
from arithmetics.symbolic.defect import defect, cocycle_residual, is_cocycle
from arithmetics.symbolic.zeta import (
    inner_series, zeta_p, zero_condition, reduced_zero_condition,
    empirical_zero_law,
)
from arithmetics.symbolic.numeric import (
    eval_formula, eval_inner_series, eval_zeta_p,
)

__all__ = [
    # core
    "Formula", "IterExp", "IterLog",
    "n", "s", "a", "b", "c", "p", "x", "y", "alpha", "beta",
    # transfers
    "identity_transfer", "exponential_transfer",
    "iterated_exponential_transfer", "affine_transfer", "polynomial_transfer",
    "rational_transfer", "mixed_exponential_transfer", "coherent_twist_transfer",
    # operations
    "phi_level", "phi_inverse_level", "oplus", "otimes",
    "additive_identity", "multiplicative_identity",
    # defect
    "defect", "cocycle_residual", "is_cocycle",
    # zeta
    "inner_series", "zeta_p", "zero_condition", "reduced_zero_condition",
    "empirical_zero_law",
    # numeric
    "eval_formula", "eval_inner_series", "eval_zeta_p",
]
