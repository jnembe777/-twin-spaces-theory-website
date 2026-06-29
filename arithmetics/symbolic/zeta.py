"""
Symbolic intrinsic level-``p`` zeta functions.

This is the symbolic form of the *corrected* (intrinsic) definition from
``correction_bis``:

.. math::

    \\zeta_p(s) = \\Phi_p\\!\\left(\\sum_{n=1}^{\\infty}
        \\big(\\Phi_p^{-1}(n)\\big)^{-(s+1)}\\right)
    = \\exp^{\\circ p}\\!\\left(\\sum_{n=1}^{\\infty}
        \\big(\\log^{\\circ p}(n)\\big)^{-(s+1)}\\right).

By injectivity of :math:`\\Phi_p`, the zeros condition
:math:`\\zeta_p(s) = \\mathbf{0}_p` reduces to the vanishing of the inner
classical Dirichlet series :math:`D_p(s)`, which is why the critical line
:math:`\\Re(s) = 1/2` is invariant across levels.
"""

from typing import Union

import sympy as sp
from sympy import Sum, oo, Eq, log

from arithmetics.symbolic.expressions import Formula, IterExp, IterLog, n, s, p as _p
from arithmetics.symbolic.operations import additive_identity

Number = Union[int, float, sp.Expr]


__all__ = [
    "inner_series", "zeta_p", "zero_condition", "reduced_zero_condition",
    "empirical_zero_law",
]


def inner_series(level: Number = _p, start: int = 1) -> Formula:
    r"""The inner classical Dirichlet series :math:`D_p(s)`.

    .. math::

        D_p(s) = \sum_{n=\text{start}}^{\infty}
            \big(\log^{\circ p}(n)\big)^{-(s+1)}.

    Its zeros coincide with those of :math:`\zeta_p(s)`.
    """
    level = sp.sympify(level)
    term = IterLog(n, level) ** (-(s + 1))
    return Formula(Sum(term, (n, start, oo)), name="D_p",
                   description="inner Dirichlet series D_p(s)")


def zeta_p(level: Number = _p, start: int = 1) -> Formula:
    r"""The intrinsic level-``p`` zeta function :math:`\zeta_p(s)`.

    Equals :math:`\Phi_p(D_p(s))`. For ``level = 0`` this collapses to the
    classical series :math:`\sum n^{-(s+1)} = \zeta(s+1)`.
    """
    level = sp.sympify(level)
    series = inner_series(level, start=start).expr
    return Formula(IterExp(series, level), name="zeta_p",
                   description="intrinsic zeta_p(s)")


def zero_condition(level: Number = _p) -> Eq:
    r"""The intrinsic zero condition :math:`\zeta_p(s) = \mathbf{0}_p`.

    Returns a SymPy :class:`~sympy.core.relational.Eq`.
    """
    return Eq(zeta_p(level).expr, additive_identity(level).expr)


def reduced_zero_condition(level: Number = _p) -> Eq:
    r"""The reduced zero condition :math:`D_p(s) = 0`.

    By injectivity of :math:`\Phi_p`, this is equivalent to
    :func:`zero_condition` but lives in the ``s``-plane independently of the
    arithmetic level -- the basis of critical-line invariance.
    """
    return Eq(inner_series(level).expr, 0)


def empirical_zero_law() -> Formula:
    r"""The empirical defect/zero law of the paper.

    .. math::

        \Re(\rho) \approx 0.52 - 0.01 \, \log_{10}(\delta_{\max}).

    Returned as a :class:`Formula` in the symbol ``delta_max``.
    """
    delta_max = sp.Symbol("delta_max", positive=True)
    expr = sp.Rational(52, 100) - sp.Rational(1, 100) * (log(delta_max) / log(10))
    return Formula(expr, name="empirical_zero_law",
                   description="Re(rho) ~ 0.52 - 0.01 log10(delta_max)")
