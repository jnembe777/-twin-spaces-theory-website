"""
The transport primitive: generating twin operations.

Implements the central formula of twin-spaces theory,

.. math::

    x \\odot_{eg} y = g^{-1}\\cdot\\big((g\\cdot x) \\odot_e (g\\cdot y)\\big),

across the three action families of :mod:`arithmetics.symbolic.twin.actions`:

* :func:`twin_operation` — symbolic twin op for a monogenic
  :class:`~arithmetics.symbolic.twin.actions.BijectionAction` (returns a
  :class:`~arithmetics.symbolic.expressions.Formula`);
* :func:`twin_field` — the full twin field ``(⊕_g, ⊗_g)`` with its neutrals;
* :func:`twin_operation_continuous` — symbolic twin op for a one-parameter
  :class:`~arithmetics.symbolic.twin.actions.ContinuousAction`;
* :func:`transport_table` — the transported Cayley table for a finite
  :class:`~arithmetics.symbolic.twin.actions.PermutationAction`.
"""

from typing import List, Optional, Sequence

import sympy as sp
from sympy import simplify

from arithmetics.symbolic.expressions import Formula, x as _x, y as _y


__all__ = [
    "CayleyTable", "twin_operation", "twin_field",
    "twin_operation_continuous", "transport_table",
]


# ---------------------------------------------------------------------------
# Finite Cayley table
# ---------------------------------------------------------------------------
class CayleyTable:
    """A finite binary operation on ``{0,…,size-1}`` as a Cayley table.

    ``table[i][j] = i ⊙ j``. Hashable and comparable so transported tables can
    be de-duplicated to count the operation space.
    """

    def __init__(self, table: Sequence[Sequence[int]],
                 labels: Optional[Sequence[str]] = None, name: str = ""):
        self.table = [list(row) for row in table]
        self.size = len(self.table)
        self.labels = list(labels) if labels else [str(i) for i in range(self.size)]
        self.name = name

    def __eq__(self, other) -> bool:
        return isinstance(other, CayleyTable) and self.table == other.table

    def __hash__(self) -> int:
        return hash(tuple(tuple(row) for row in self.table))

    def text(self) -> str:
        """Render as an aligned text grid."""
        w = max(len(l) for l in self.labels)
        cell = lambda v: str(self.labels[v]).rjust(w)
        head = " " * (w + 1) + "│ " + " ".join(self.labels[j].rjust(w)
                                               for j in range(self.size))
        rule = "─" * (w + 1) + "┼" + "─" * (1 + (w + 1) * self.size)
        rows = [head, rule]
        for i in range(self.size):
            body = " ".join(cell(self.table[i][j]) for j in range(self.size))
            rows.append(f"{self.labels[i].rjust(w)} │ {body}")
        title = f"{self.name}\n" if self.name else ""
        return title + "\n".join(rows)

    def latex(self) -> str:
        """Render as a LaTeX ``array`` Cayley table."""
        cols = "c|" + "c" * self.size
        head = " & ".join([r"\odot"] + self.labels) + r" \\ \hline"
        body = []
        for i in range(self.size):
            row = " & ".join([self.labels[i]] +
                             [self.labels[self.table[i][j]] for j in range(self.size)])
            body.append(row + r" \\")
        return ("\\begin{array}{" + cols + "}\n" + head + "\n"
                + "\n".join(body) + "\n\\end{array}")

    def __repr__(self) -> str:
        return f"CayleyTable(size={self.size}, name={self.name!r})"


# ---------------------------------------------------------------------------
# Symbolic transport — monogenic (bijection) action
# ---------------------------------------------------------------------------
def twin_operation(action, level: int, base: str = "add",
                   do_simplify: bool = True) -> Formula:
    """Generate the twin operation ``x ⊙_{e,level} y`` for a bijection action.

    Args:
        action: a :class:`BijectionAction`.
        level: the group element ``n`` (iteration count).
        base: ``"add"`` (``⊙_e = +``) or ``"mul"`` (``⊙_e = ·``).
        do_simplify: simplify the resulting expression.

    Returns:
        A :class:`Formula` in the shared symbols ``x``, ``y``.
    """
    gx = action.act(level, _x)
    gy = action.act(level, _y)
    combined = gx + gy if base == "add" else gx * gy
    expr = action.act(action.inverse_level(level), combined)
    if do_simplify:
        expr = simplify(expr)
    op = "(+)" if base == "add" else "(x)"
    return Formula(expr, name=f"{op}_{action.name}^{level}",
                   description=f"twin {base} operation at level {level}")


def twin_field(action, level: int, do_simplify: bool = True) -> dict:
    """Generate the full twin field ``(⊕_g, ⊗_g)`` and its neutral elements.

    Returns a dict with keys ``oplus``, ``otimes`` (:class:`Formula`),
    ``zero`` (additive neutral ``φ⁻¹(0)``) and ``one`` (multiplicative neutral
    ``φ⁻¹(1)``).
    """
    inv = action.inverse_level(level)
    zero = action.act(inv, sp.Integer(0))
    one = action.act(inv, sp.Integer(1))
    if do_simplify:
        zero, one = simplify(zero), simplify(one)
    return {
        "oplus": twin_operation(action, level, "add", do_simplify),
        "otimes": twin_operation(action, level, "mul", do_simplify),
        "zero": Formula(zero, name=f"e_(+)_{action.name}^{level}"),
        "one": Formula(one, name=f"e_(x)_{action.name}^{level}"),
    }


# ---------------------------------------------------------------------------
# Symbolic transport — one-parameter Lie action
# ---------------------------------------------------------------------------
def twin_operation_continuous(action, base: str = "mul",
                              do_simplify: bool = True) -> Formula:
    """Generate the twin operation for a one-parameter :class:`ContinuousAction`.

    The result depends symbolically on the group parameter ``action.param``.
    """
    t = action.param
    gx = action.act(t, _x)
    gy = action.act(t, _y)
    combined = gx + gy if base == "add" else gx * gy
    expr = action.act(action.inv_param(t), combined)
    if do_simplify:
        expr = simplify(expr)
    op = "(+)" if base == "add" else "(x)"
    return Formula(expr, name=f"{op}_{action.name}({t})",
                   description=f"twin {base} operation, parameter {t}")


# ---------------------------------------------------------------------------
# Finite transport — permutation action
# ---------------------------------------------------------------------------
def transport_table(base: CayleyTable, action, g: Sequence[int]) -> CayleyTable:
    """Transport a finite operation by a group element ``g``.

    Computes ``x ⊙_{eg} y = g⁻¹(g(x) ⊙_e g(y))`` for every pair.
    """
    g_inv = action.inverse(g)
    m = action.size
    table: List[List[int]] = [
        [action.act(g_inv, base.table[action.act(g, i)][action.act(g, j)])
         for j in range(m)]
        for i in range(m)
    ]
    return CayleyTable(table, base.labels, name=f"{base.name}·g")
