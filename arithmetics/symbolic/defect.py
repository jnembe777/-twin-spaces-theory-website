"""
Symbolic defect cocycle.

The defect of an arithmetic transfer :math:`\\varphi` is

.. math::

    \\delta_\\varphi(a,b) = \\varphi(a)\\varphi(b) - \\varphi(ab),

measuring its failure to preserve multiplication. This module builds the
defect symbolically from a transfer formula (in the index symbol ``n``) and
provides the twisted cocycle expression of Theorem 2.2,

.. math::

    \\varphi(a)\\,\\delta(b,c) + \\delta(a,bc)
        - \\big(\\delta(a,b)\\,\\varphi(c) + \\delta(ab,c)\\big),

whose vanishing is the cocycle identity.
"""

from typing import Union

import sympy as sp

from arithmetics.symbolic.expressions import Formula, n, a as _a, b as _b, c as _c

Number = Union[int, float, sp.Expr]


__all__ = ["defect", "cocycle_residual", "is_cocycle"]


def _phi_of(transfer: Union[Formula, sp.Expr], value) -> sp.Expr:
    """Evaluate a transfer (given as φ(n)) at ``value`` by substituting ``n``."""
    expr = transfer.expr if isinstance(transfer, Formula) else sp.sympify(transfer)
    return expr.subs(n, value)


def defect(transfer: Union[Formula, sp.Expr],
           a: Number = _a, b: Number = _b) -> Formula:
    r"""Build the defect :math:`\delta_\varphi(a,b)` of a transfer.

    Args:
        transfer: The transfer :math:`\varphi(n)` as a :class:`Formula` or
            SymPy expression in the index symbol ``n``.
        a, b: Test points (symbols by default).

    Returns:
        A :class:`Formula` for ``phi(a)*phi(b) - phi(a*b)``.
    """
    a, b = sp.sympify(a), sp.sympify(b)
    expr = _phi_of(transfer, a) * _phi_of(transfer, b) - _phi_of(transfer, a * b)
    return Formula(expr, name="defect", description="delta(a,b)")


def cocycle_residual(transfer: Union[Formula, sp.Expr],
                     a: Number = _a, b: Number = _b,
                     c: Number = _c) -> Formula:
    r"""The twisted cocycle residual (LHS - RHS of Theorem 2.2).

    Returns ``phi(a)*delta(b,c) + delta(a,bc) - delta(a,b)*phi(c) - delta(ab,c)``;
    it is identically zero exactly when the cocycle identity holds.
    """
    a, b, c = sp.sympify(a), sp.sympify(b), sp.sympify(c)
    d = lambda u, v: defect(transfer, u, v).expr
    phi = lambda v: _phi_of(transfer, v)

    lhs = phi(a) * d(b, c) + d(a, b * c)
    rhs = d(a, b) * phi(c) + d(a * b, c)
    return Formula(lhs - rhs, name="cocycle_residual",
                   description="cocycle LHS - RHS")


def is_cocycle(transfer: Union[Formula, sp.Expr]) -> bool:
    """Check symbolically that the twisted cocycle identity holds.

    The residual is simplified to zero for symbolic ``a, b, c``; this holds for
    every transfer (the identity is structural), and serves as a regression
    check on the symbolic machinery.
    """
    return sp.simplify(cocycle_residual(transfer).expr) == 0
