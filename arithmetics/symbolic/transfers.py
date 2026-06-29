"""
Symbolic arithmetic transfers.

These factories are the symbolic mirror of the numeric transfer classes in
:mod:`arithmetics.core.transfer`. Each returns a :class:`Formula` for
:math:`\\varphi(n)` expressed in the shared index symbol ``n``.

An arithmetic transfer is a map :math:`\\varphi:(\\ZZ,+)\\to(\\RR_{>0},\\cdot)`;
the symbolic form makes its defect, twisted product, and induced zeta function
amenable to exact manipulation and typesetting.
"""

from typing import Sequence, Union

import sympy as sp
from sympy import exp, log, sqrt, cbrt, Integer, Rational

from arithmetics.symbolic.expressions import (
    Formula, IterExp, n, alpha as _alpha, beta as _beta,
)

Number = Union[int, float, sp.Expr]


__all__ = [
    "identity_transfer",
    "exponential_transfer",
    "iterated_exponential_transfer",
    "affine_transfer",
    "polynomial_transfer",
    "rational_transfer",
    "mixed_exponential_transfer",
    "coherent_twist_transfer",
]


def identity_transfer() -> Formula:
    r"""The identity transfer :math:`\varphi(n) = n` (zero defect)."""
    return Formula(n, name="phi_identity", description="phi(n) = n")


def exponential_transfer(base: Number = _alpha) -> Formula:
    r"""The exponential transfer :math:`\varphi_\alpha(n) = \alpha^{n}`.

    Args:
        base: The exponential base ``alpha``. Defaults to the symbol ``alpha``;
            pass a number for a concrete transfer.
    """
    base = sp.sympify(base)
    return Formula(base ** n, name="phi_exp",
                   description="phi(n) = alpha^n")


def iterated_exponential_transfer(level: Number = 1) -> Formula:
    r"""The iterated-exponential transfer :math:`\varphi(n) = \exp^{\circ p}(n)`.

    This is :math:`\Phi_p` of the hierarchy. ``level`` may be a concrete
    integer or a symbol.
    """
    level = sp.sympify(level)
    return Formula(IterExp(n, level), name="phi_iterated",
                   description="phi(n) = exp^{o p}(n)")


def affine_transfer(c: Number, d: Number = 0) -> Formula:
    r"""The affine transfer :math:`\varphi(n) = c\,n + d`."""
    c, d = sp.sympify(c), sp.sympify(d)
    return Formula(c * n + d, name="phi_affine",
                   description="phi(n) = c*n + d")


def polynomial_transfer(coeffs: Sequence[Number]) -> Formula:
    r"""The polynomial transfer :math:`\varphi(n) = \sum_k a_k n^k`.

    Args:
        coeffs: Coefficients ``[a_0, a_1, ...]`` in ascending degree, matching
            the ordering of :class:`arithmetics.core.transfer.PolynomialTransfer`.
    """
    expr = sum(sp.sympify(coef) * n ** k for k, coef in enumerate(coeffs))
    return Formula(sp.sympify(expr), name="phi_polynomial",
                   description="phi(n) = sum_k a_k n^k")


def rational_transfer(c: Number = 1) -> Formula:
    r"""The rational transfer :math:`\varphi(n) = n / (n + c)`."""
    c = sp.sympify(c)
    return Formula(n / (n + c), name="phi_rational",
                   description="phi(n) = n / (n + c)")


def mixed_exponential_transfer(
    alpha: Number = _alpha,
    beta: Number = _beta,
    form: str = "alpha^n + beta*n",
) -> Formula:
    r"""A mixed exponential transfer combining exponential and other terms.

    Supported ``form`` values mirror
    :class:`arithmetics.core.transfer.MixedExponentialTransfer`:
    ``"alpha^n + beta*n"``, ``"alpha^n * beta^n"``, ``"alpha^n + beta^n"``.
    """
    alpha, beta = sp.sympify(alpha), sp.sympify(beta)
    forms = {
        "alpha^n + beta*n": alpha ** n + beta * n,
        "alpha^n * beta^n": alpha ** n * beta ** n,
        "alpha^n + beta^n": alpha ** n + beta ** n,
    }
    if form not in forms:
        raise ValueError(f"Unknown form: {form!r}. "
                         f"Choose from {sorted(forms)}.")
    return Formula(forms[form], name="phi_mixed",
                   description=f"phi(n) = {form}")


# Bijections available to CoherentTwistTransfer in the numeric framework.
_COHERENT_TWISTS = {
    "log": lambda v: log(v),
    "exp": lambda v: exp(v),
    "x^2": lambda v: v ** 2,
    "sqrt": lambda v: sqrt(v),
    "x^3": lambda v: v ** 3,
    "cbrt": lambda v: cbrt(v),
}


def coherent_twist_transfer(g: str = "log") -> Formula:
    r"""A coherent twist transfer :math:`\varphi(n) = g(n)`.

    Args:
        g: Name of the bijection: one of
            ``"log"``, ``"exp"``, ``"x^2"``, ``"sqrt"``, ``"x^3"``, ``"cbrt"``.
    """
    if g not in _COHERENT_TWISTS:
        raise ValueError(f"Unknown twist {g!r}. "
                         f"Choose from {sorted(_COHERENT_TWISTS)}.")
    return Formula(_COHERENT_TWISTS[g](n), name="phi_coherent",
                   description=f"phi(n) = {g}(n)")
