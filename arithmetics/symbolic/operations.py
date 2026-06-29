"""
Symbolic level-``p`` arithmetic operations.

Following ``correction_bis``, the level-``p`` structure is obtained by
conjugating the usual ``(+, ·)`` through the iterated exponential
:math:`\\Phi_p = \\exp^{\\circ p}`:

.. math::

    x \\oplus_p y = \\Phi_p\\big(\\Phi_p^{-1}(x) + \\Phi_p^{-1}(y)\\big), \\qquad
    x \\otimes_p y = \\Phi_p\\big(\\Phi_p^{-1}(x) \\cdot \\Phi_p^{-1}(y)\\big),

with additive identity :math:`\\mathbf{0}_p = \\Phi_p(0)` and multiplicative
identity :math:`\\mathbf{1}_p = \\Phi_p(1)`.

Every generator returns a :class:`Formula`. Passing a concrete integer level
and calling :meth:`Formula.expand_levels` (or :meth:`Formula.simplify`)
recovers the familiar closed forms -- e.g. ``oplus`` at level 1 is ordinary
multiplication.
"""

from typing import Union

import sympy as sp

from arithmetics.symbolic.expressions import (
    Formula, IterExp, IterLog, p as _p, x as _x, y as _y,
)

Number = Union[int, float, sp.Expr]


__all__ = [
    "phi_level", "phi_inverse_level",
    "oplus", "otimes",
    "additive_identity", "multiplicative_identity",
]


def phi_level(arg: Number = _x, level: Number = _p) -> Formula:
    r"""The level isomorphism :math:`\Phi_p(x) = \exp^{\circ p}(x)`."""
    return Formula(IterExp(sp.sympify(arg), sp.sympify(level)),
                   name="Phi_p", description="Phi_p(x) = exp^{o p}(x)")


def phi_inverse_level(arg: Number = _x, level: Number = _p) -> Formula:
    r"""The inverse isomorphism :math:`\Phi_p^{-1}(x) = \log^{\circ p}(x)`."""
    return Formula(IterLog(sp.sympify(arg), sp.sympify(level)),
                   name="Phi_p_inv", description="Phi_p^{-1}(x) = log^{o p}(x)")


def oplus(left: Number = _x, right: Number = _y, level: Number = _p) -> Formula:
    r"""Level-``p`` addition :math:`x \oplus_p y`."""
    left, right, level = map(sp.sympify, (left, right, level))
    inner = IterLog(left, level) + IterLog(right, level)
    return Formula(IterExp(inner, level), name="oplus_p",
                   description="x (+)_p y")


def otimes(left: Number = _x, right: Number = _y, level: Number = _p) -> Formula:
    r"""Level-``p`` multiplication :math:`x \otimes_p y`."""
    left, right, level = map(sp.sympify, (left, right, level))
    inner = IterLog(left, level) * IterLog(right, level)
    return Formula(IterExp(inner, level), name="otimes_p",
                   description="x (x)_p y")


def additive_identity(level: Number = _p) -> Formula:
    r"""The additive identity :math:`\mathbf{0}_p = \Phi_p(0) = \exp^{\circ p}(0)`.

    This is the value a level-``p`` zeta function must reach to have a "zero".
    """
    return Formula(IterExp(sp.Integer(0), sp.sympify(level)),
                   name="zero_p", description="0_p = exp^{o p}(0)")


def multiplicative_identity(level: Number = _p) -> Formula:
    r"""The multiplicative identity :math:`\mathbf{1}_p = \Phi_p(1)`."""
    return Formula(IterExp(sp.Integer(1), sp.sympify(level)),
                   name="one_p", description="1_p = exp^{o p}(1)")
