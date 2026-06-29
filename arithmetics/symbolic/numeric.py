"""
Numeric bridge from symbolic formulas to mpmath.

The symbolic layer produces exact expressions; this module evaluates them at
arbitrary precision via mpmath. Beyond the generic :meth:`Formula.evalf` and
:meth:`Formula.lambdify`, it provides a dedicated evaluator for the intrinsic
level-``p`` zeta function, summing the inner Dirichlet series with
``mpmath.nsum`` and applying the outer iterated exponential.

The inner series :math:`\\sum (\\log^{\\circ p} n)^{-(s+1)}` has a singular
first term for ``p >= 1`` (``log^{∘p}(1) = 0``), so summation starts at
``n = 2`` by default for positive levels; this matches the convergent regime
discussed in ``correction_bis``.
"""

from typing import Union

import mpmath
from mpmath import mp, mpf, mpc

import sympy as sp

from arithmetics.symbolic.expressions import Formula, IterLog, n, s
from arithmetics.symbolic.zeta import inner_series

Number = Union[int, float, complex]


__all__ = ["eval_formula", "eval_inner_series", "eval_zeta_p", "default_start"]


def default_start(level: int) -> int:
    """First summation index: 1 for level 0, else 2 (skip the singular term)."""
    return 1 if int(level) == 0 else 2


def eval_formula(formula: Formula, dps: int = 30, **subs) -> mpc:
    """Evaluate a closed-form :class:`Formula` at mpmath precision.

    Keyword arguments map symbol *names* to numeric values, e.g.
    ``eval_formula(f, alpha=2, n=3)``.
    """
    mp.dps = dps
    name_map = {sym.name: sym for sym in formula.free_symbols}
    subs_syms = {name_map[k]: v for k, v in subs.items() if k in name_map}
    value = formula.evalf(subs_syms, dps=dps)
    return mpc(value)


def eval_inner_series(level: int, s_value: Number, dps: int = 30,
                      start: int = None, terms: int = None) -> mpc:
    r"""Numerically evaluate the inner Dirichlet series :math:`D_p(s)`.

    Args:
        level: Hierarchy level ``p`` (concrete non-negative integer).
        s_value: Complex argument ``s``.
        dps: mpmath decimal precision.
        start: First summation index (defaults via :func:`default_start`).
        terms: If given, use a finite truncated sum of this many terms instead
            of ``mpmath.nsum`` (useful in the slowly/non-convergent regime).

    Returns:
        :math:`D_p(s)` as an mpmath complex number.
    """
    mp.dps = dps
    level = int(level)
    if start is None:
        start = default_start(level)
    sv = mpc(s_value)

    # Lambdify the summand (log^{∘p}(n))^{-(s+1)} to a fast mpmath callable.
    term = (inner_series(level).expr).function  # the summand of the Sum
    summand = sp.lambdify((n, s), term.doit(), modules="mpmath")

    if terms is not None:
        return mpmath.fsum(summand(mpf(k), sv) for k in range(start, start + terms))
    return mpmath.nsum(lambda k: summand(k, sv), [start, mpmath.inf])


def eval_zeta_p(level: int, s_value: Number, dps: int = 30,
                start: int = None, terms: int = None) -> mpc:
    r"""Numerically evaluate the intrinsic zeta :math:`\zeta_p(s) = \Phi_p(D_p(s))`.

    See :func:`eval_inner_series` for the arguments. The outer iterated
    exponential :math:`\exp^{\circ p}` is applied to the summed series.
    """
    mp.dps = dps
    level = int(level)
    d_value = eval_inner_series(level, s_value, dps=dps, start=start, terms=terms)
    result = d_value
    for _ in range(level):
        result = mpmath.e ** result
    return mpc(result)
