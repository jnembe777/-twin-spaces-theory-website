"""
Candidate catalogues and the discovery machinery.

This module assembles tables of *candidate groups* and *candidate base spaces*,
then runs the transport + classification machinery to *discover* the twin
spaces each (group, space) pair generates.

Two discovery passes:

* :func:`discover_finite` — finite permutation groups acting on finite base
  operations; returns one row per (group, operation) pair with kernel,
  ``[G:L]``, triviality, and the invariant-magma count.
* :func:`discover_symbolic` — monogenic bijection groups and one-parameter Lie
  groups; returns the closed-form twin operation and whether it is trivial
  (the linearity obstruction).

Rendering / export helpers produce console tables, LaTeX tables, and JSON/CSV
files under ``results/twin/``.
"""

import json
import os
from typing import Dict, List, Tuple

import sympy as sp
from sympy import simplify

from arithmetics.symbolic.expressions import x as _x, y as _y
from arithmetics.symbolic.twin.actions import (
    BijectionAction, ContinuousAction, PermutationAction,
)
from arithmetics.symbolic.twin.transport import (
    CayleyTable, twin_operation, twin_operation_continuous,
)
from arithmetics.symbolic.twin.classify import classify


__all__ = [
    "candidate_finite_groups", "candidate_base_operations",
    "candidate_bijections", "candidate_continuous",
    "discover_finite", "discover_symbolic",
    "render_table", "to_latex_table", "save_results",
]


# ---------------------------------------------------------------------------
# Candidate groups
# ---------------------------------------------------------------------------
def candidate_finite_groups(max_n: int = 4) -> List[PermutationAction]:
    """A catalogue of finite candidate groups acting on small finite sets."""
    groups: List[PermutationAction] = []
    for n in range(2, max_n + 1):
        groups.append(PermutationAction.cyclic(n))
    groups.append(PermutationAction.klein_four())
    for n in (3, 4):
        groups.append(PermutationAction.dihedral(n))
    for n in (3, 4):
        groups.append(PermutationAction.symmetric(n))
    return groups


def candidate_bijections() -> List[Tuple[BijectionAction, str]]:
    """Monogenic candidate groups (bijection, base-operation) to explore."""
    return [
        (BijectionAction.identity(), "add"),
        (BijectionAction.exponential(), "add"),    # the exponential hierarchy
        (BijectionAction.power(2), "add"),         # L^2 / power-mean
        (BijectionAction.power(3), "add"),
        (BijectionAction.affine(2, 3), "add"),     # translated addition
        (BijectionAction.power(2), "mul"),         # rigid under × (Example 4)
        (BijectionAction.exponential(), "mul"),
        (BijectionAction.logit(), "add"),          # log-odds addition
    ]


def candidate_continuous() -> List[Tuple[ContinuousAction, str]]:
    """One-parameter Lie candidate groups (action, base-operation)."""
    return [
        (ContinuousAction.translation(), "add"),   # x + y + t
        (ContinuousAction.scaling(), "mul"),       # e^t x y  (non-trivial)
        (ContinuousAction.power(), "mul"),         # x y      (rigid)
    ]


# ---------------------------------------------------------------------------
# Candidate base spaces (finite operations)
# ---------------------------------------------------------------------------
def candidate_base_operations(m: int) -> List[CayleyTable]:
    """A catalogue of candidate base operations on ``E = {0,…,m-1}``."""
    ops: List[CayleyTable] = []
    ops.append(CayleyTable([[(i + j) % m for j in range(m)] for i in range(m)],
                           name=f"+ mod {m}"))
    ops.append(CayleyTable([[(i * j) % m for j in range(m)] for i in range(m)],
                           name=f"× mod {m}"))
    ops.append(CayleyTable([[max(i, j) for j in range(m)] for i in range(m)],
                           name="max"))
    ops.append(CayleyTable([[i for _ in range(m)] for i in range(m)],
                           name="left-proj"))
    if m == 3:
        # The non-standard magma from Vol. 01, Example 3.
        ops.append(CayleyTable([[0, 1, 2], [2, 0, 1], [1, 2, 0]],
                               name="magma-ex3"))
    return ops


# ---------------------------------------------------------------------------
# Discovery passes
# ---------------------------------------------------------------------------
def discover_finite(max_n: int = 4) -> List[dict]:
    """Run the machinery over finite (group, base operation) pairs."""
    rows: List[dict] = []
    for group in candidate_finite_groups(max_n):
        for base in candidate_base_operations(group.size):
            rows.append(classify(base, group))
    return rows


def discover_symbolic() -> List[dict]:
    """Run the machinery over monogenic and Lie (action, base) pairs."""
    rows: List[dict] = []
    for action, base in candidate_bijections():
        twin = twin_operation(action, level=1, base=base)
        base_expr = _x + _y if base == "add" else _x * _y
        trivial = simplify(twin.expr - base_expr) == 0
        rows.append({
            "family": "monogenic ⟨φ⟩",
            "phi": action.name,
            "base": "+" if base == "add" else "·",
            "twin_op": twin.text(),
            "latex": twin.latex(),
            "trivial": trivial,
        })
    for action, base in candidate_continuous():
        twin = twin_operation_continuous(action, base=base)
        base_expr = _x + _y if base == "add" else _x * _y
        trivial = simplify(twin.expr - base_expr) == 0
        rows.append({
            "family": f"Lie {action.group}",
            "phi": action.name,
            "base": "+" if base == "add" else "·",
            "twin_op": twin.text(),
            "latex": twin.latex(),
            "trivial": trivial,
        })
    return rows


# ---------------------------------------------------------------------------
# Rendering & export
# ---------------------------------------------------------------------------
def render_table(rows: List[dict], columns: List[str] = None) -> str:
    """Render a list of dict rows as an aligned console table."""
    if not rows:
        return "(no rows)"
    columns = columns or list(rows[0].keys())
    widths = {c: max(len(str(c)), *(len(str(r.get(c, ""))) for r in rows))
              for c in columns}
    head = " │ ".join(str(c).ljust(widths[c]) for c in columns)
    rule = "─┼─".join("─" * widths[c] for c in columns)
    body = [" │ ".join(str(r.get(c, "")).ljust(widths[c]) for c in columns)
            for r in rows]
    return "\n".join([head, rule, *body])


def to_latex_table(rows: List[dict], columns: List[str] = None,
                   caption: str = "", label: str = "") -> str:
    """Render rows as a LaTeX ``tabular`` (booktabs)."""
    if not rows:
        return ""
    columns = columns or list(rows[0].keys())
    esc = lambda v: str(v).replace("_", r"\_").replace("&", r"\&")
    spec = "l" * len(columns)
    head = " & ".join(r"\textbf{" + esc(c) + "}" for c in columns) + r" \\"
    body = [" & ".join(esc(r.get(c, "")) for c in columns) + r" \\" for r in rows]
    parts = [r"\begin{table}[ht]", r"\centering"]
    if caption:
        parts.append(r"\caption{" + esc(caption) + "}")
    if label:
        parts.append(r"\label{" + label + "}")
    parts += [r"\begin{tabular}{" + spec + "}", r"\toprule", head, r"\midrule",
              *body, r"\bottomrule", r"\end{tabular}", r"\end{table}"]
    return "\n".join(parts)


def save_results(rows: List[dict], name: str,
                 results_dir: str = None) -> Dict[str, str]:
    """Save rows as JSON and CSV under ``results/twin/``; return the paths."""
    if results_dir is None:
        here = os.path.dirname(os.path.abspath(__file__))
        repo = os.path.abspath(os.path.join(here, "..", "..", ".."))
        results_dir = os.path.join(repo, "results", "twin")
    os.makedirs(results_dir, exist_ok=True)

    json_path = os.path.join(results_dir, f"{name}.json")
    with open(json_path, "w") as f:
        json.dump(rows, f, indent=2, default=str)

    csv_path = os.path.join(results_dir, f"{name}.csv")
    if rows:
        columns = list(rows[0].keys())
        with open(csv_path, "w") as f:
            f.write(",".join(columns) + "\n")
            for r in rows:
                f.write(",".join('"' + str(r.get(c, "")).replace('"', "'") + '"'
                                 for c in columns) + "\n")
    return {"json": json_path, "csv": csv_path}
