"""
Group-theoretic decision layer for twin spaces.

This module turns the structural invariants of a group into *decision tools*
for the twin operation space ``Op ≅ G/L``. It realises the framework of
``twin_decision_theory.tex``:

* a finite group is analysed by its **conjugacy classes**, **centralisers**,
  **centre**, and **class equation**
  ``|G| = |Z(G)| + Σ_i [G : C_G(x_i)]``;
* a cost ``J`` that is a **class function** (conjugation invariant) is constant
  on each conjugacy class, so the class equation *enumerates the decision
  cells* and one need only evaluate ``J`` on one representative per class
  (Proposition, reduction principle);
* for a costing that is not conjugation invariant, the decision cells are the
  **level sets** of ``J`` (the honest general fallback);
* for a compact connected Lie group the class equation becomes the **Weyl
  integration formula**; we implement the ``SU(2)`` instance with measure
  ``(2/π) sin²θ`` on the maximal torus ``θ ∈ [0, π]``.

The :class:`FiniteGroup` abstraction is generic (elements + a multiplication),
so abelian groups, direct products, dihedral, symmetric and quaternion groups
all flow through the same machinery, as does the quotient ``G/L``.
"""

from itertools import product as _product
from typing import Callable, Dict, FrozenSet, List, Optional, Sequence, Tuple

__all__ = [
    "FiniteGroup", "class_equation", "is_class_function",
    "decision_report", "class_average", "normalizer",
    "operation_orbits", "twin_decision",
    "su2_weyl_density", "su2_class_average", "su2_class_decision",
]


# ---------------------------------------------------------------------------
# A generic finite group (elements + multiplication)
# ---------------------------------------------------------------------------
class FiniteGroup:
    """A finite group given by its element list and a multiplication.

    Elements must be hashable and (for canonical coset reps) comparable.
    """

    def __init__(self, name: str, elements: Sequence,
                 multiply: Callable, identity, inverse: Optional[Callable] = None):
        self.name = name
        self.elements = list(elements)
        self._mul = multiply
        self.identity = identity
        self._inv_map: Dict = {}
        # Precompute inverses (search if not provided).
        for a in self.elements:
            if inverse is not None:
                self._inv_map[a] = inverse(a)
            else:
                for b in self.elements:
                    if multiply(a, b) == identity:
                        self._inv_map[a] = b
                        break

    # -- group arithmetic --------------------------------------------------
    def mul(self, a, b):
        return self._mul(a, b)

    def inv(self, a):
        return self._inv_map[a]

    def conjugate(self, g, a):
        """Return ``g a g⁻¹``."""
        return self._mul(self._mul(g, a), self._inv_map[g])

    def element_order(self, a) -> int:
        k, x = 1, a
        while x != self.identity:
            x = self._mul(x, a)
            k += 1
        return k

    @property
    def order(self) -> int:
        return len(self.elements)

    def is_abelian(self) -> bool:
        return all(self._mul(a, b) == self._mul(b, a)
                   for a in self.elements for b in self.elements)

    # -- conjugacy structure ----------------------------------------------
    def conjugacy_classes(self) -> List[FrozenSet]:
        seen = set()
        classes = []
        for a in self.elements:
            if a in seen:
                continue
            cls = frozenset(self.conjugate(g, a) for g in self.elements)
            seen |= cls
            classes.append(cls)
        return classes

    def centralizer(self, a) -> List:
        return [g for g in self.elements if self.conjugate(g, a) == a]

    def center(self) -> List:
        return [a for a in self.elements
                if all(self._mul(a, g) == self._mul(g, a) for g in self.elements)]

    def is_normal(self, subgroup: Sequence) -> bool:
        """Test whether ``subgroup`` is normal: ``gNg⁻¹ = N`` for all ``g``."""
        N = set(subgroup)
        return all(self.conjugate(g, a) in N
                   for g in self.elements for a in N)

    # -- quotient by a normal subgroup ------------------------------------
    def quotient(self, normal_subgroup: Sequence) -> "FiniteGroup":
        """Build ``G/N`` for a *normal* subgroup ``N`` (cosets with induced law).

        Raises ``ValueError`` if ``N`` is not normal -- in that case the coset
        space ``G/N`` is only a homogeneous ``G``-set, not a group, and the
        induced multiplication is ill-defined.
        """
        N = list(normal_subgroup)
        if not self.is_normal(N):
            raise ValueError(
                f"subgroup of order {len(N)} is not normal in {self.name}; "
                "G/N is a homogeneous space, not a group")
        N_set = set(N)

        def coset_of(g) -> FrozenSet:
            return frozenset(self._mul(g, n) for n in N)

        cosets = []
        seen = set()
        for g in self.elements:
            c = coset_of(g)
            if c not in seen:
                seen.add(c)
                cosets.append(c)

        rep = {c: min(c, key=repr) for c in cosets}  # canonical representative

        def qmul(cA, cB):
            return coset_of(self._mul(rep[cA], rep[cB]))

        identity_coset = next(c for c in cosets if self.identity in c)
        return FiniteGroup(f"{self.name}/N", cosets, qmul, identity_coset)

    # -- catalogue ---------------------------------------------------------
    @classmethod
    def cyclic(cls, n: int) -> "FiniteGroup":
        return cls(f"C_{n}", list(range(n)),
                   lambda a, b: (a + b) % n, 0, lambda a: (-a) % n)

    @classmethod
    def direct_product(cls, G: "FiniteGroup", H: "FiniteGroup") -> "FiniteGroup":
        elems = [(g, h) for g in G.elements for h in H.elements]
        return cls(f"{G.name}×{H.name}", elems,
                   lambda a, b: (G.mul(a[0], b[0]), H.mul(a[1], b[1])),
                   (G.identity, H.identity),
                   lambda a: (G.inv(a[0]), H.inv(a[1])))

    @classmethod
    def dihedral(cls, n: int) -> "FiniteGroup":
        # elements (r, s): rotation r ∈ Z_n, reflection flag s ∈ {0,1}.
        elems = [(r, s) for s in (0, 1) for r in range(n)]

        def mul(a, b):
            r1, s1 = a
            r2, s2 = b
            if s1 == 0:
                return ((r1 + r2) % n, s2)
            return ((r1 - r2) % n, (s1 + s2) % 2)

        return cls(f"D_{n}", elems, mul, (0, 0))

    @classmethod
    def quaternion8(cls) -> "FiniteGroup":
        # Q_8 = {±1, ±i, ±j, ±k} via the standard multiplication.
        labels = ["1", "-1", "i", "-i", "j", "-j", "k", "-k"]
        table = {
            ("1", x): x for x in labels
        }
        base = {
            ("i", "i"): "-1", ("j", "j"): "-1", ("k", "k"): "-1",
            ("i", "j"): "k", ("j", "k"): "i", ("k", "i"): "j",
            ("j", "i"): "-k", ("k", "j"): "-i", ("i", "k"): "-j",
        }

        def neg(x):
            return x[1:] if x.startswith("-") else "-" + x

        def mul(a, b):
            sa, sb = a.startswith("-"), b.startswith("-")
            ua, ub = (a[1:] if sa else a), (b[1:] if sb else b)
            if ua == "1":
                r = ub
            elif ub == "1":
                r = ua
            else:
                r = base[(ua, ub)]
            if sa ^ sb:
                r = neg(r)
            return r

        return cls("Q_8", labels, mul, "1")

    @classmethod
    def from_permutation_action(cls, action) -> "FiniteGroup":
        return cls(action.name, list(action.elements),
                   action.compose, action.identity(), action.inverse)

    def __repr__(self):
        return f"FiniteGroup({self.name!r}, order={self.order})"


# ---------------------------------------------------------------------------
# The class equation and class functions
# ---------------------------------------------------------------------------
def class_equation(group: FiniteGroup) -> dict:
    """Compute the class equation ``|G| = |Z| + Σ [G : C(x_i)]``."""
    classes = group.conjugacy_classes()
    sizes = sorted(len(c) for c in classes)
    center_size = sum(1 for c in classes if len(c) == 1)
    nontrivial = [s for s in sizes if s > 1]
    eq = f"{center_size}" + (" + " + " + ".join(map(str, nontrivial))
                             if nontrivial else "")
    return {
        "group": group.name,
        "order": group.order,
        "num_classes": len(classes),
        "center_size": center_size,
        "class_sizes": sizes,
        "equation": f"{group.order} = {eq}",
        "abelian": center_size == group.order,
    }


def is_class_function(group: FiniteGroup, cost: Callable) -> bool:
    """Test whether ``cost`` is constant on every conjugacy class."""
    for cls in group.conjugacy_classes():
        values = {cost(x) for x in cls}
        if len(values) > 1:
            return False
    return True


def class_average(group: FiniteGroup, cost: Callable) -> float:
    """Average of a class function: ``(1/|G|) Σ |class_i| · J(rep_i)``.

    This is the finite analogue of the Weyl integral of a class function.
    """
    total = 0.0
    for cls in group.conjugacy_classes():
        rep = next(iter(cls))
        total += len(cls) * cost(rep)
    return total / group.order


# ---------------------------------------------------------------------------
# Decision reports
# ---------------------------------------------------------------------------
def decision_report(group: FiniteGroup, cost: Callable,
                    minimize: bool = True) -> dict:
    """Stratify a group's elements into decision cells under ``cost``.

    If ``cost`` is a class function, the cells are the conjugacy classes
    (reduction guaranteed by the Proposition); otherwise the cells are the
    level sets of ``cost`` (no conjugation-based reduction applies).
    """
    classfn = is_class_function(group, cost)
    if classfn:
        cells = []
        for cls in group.conjugacy_classes():
            rep = min(cls, key=repr)
            cells.append({"representative": rep, "size": len(cls),
                          "cost": cost(rep)})
    else:
        # Level-set partition by cost value.
        buckets: Dict = {}
        for a in group.elements:
            buckets.setdefault(cost(a), []).append(a)
        cells = [{"representative": min(v, key=repr), "size": len(v),
                  "cost": k} for k, v in buckets.items()]

    cells.sort(key=lambda c: c["cost"], reverse=not minimize)
    best = cells[0]
    return {
        "group": group.name,
        "order": group.order,
        "cost_is_class_function": classfn,
        "num_cells": len(cells),
        "reduction": f"{group.order} -> {len(cells)}",
        "cells": cells,
        "optimal": best,
    }


def normalizer(action, subgroup) -> List:
    """The normalizer ``N_G(L) = { w ∈ G : wLw⁻¹ = L }`` (permutation action)."""
    L = set(subgroup)

    def conj(w, a):
        return action.compose(action.compose(w, a), action.inverse(w))

    return [w for w in action.elements if {conj(w, l) for l in L} == L]


def operation_orbits(base, action):
    """Decision cells: orbits of the twin operations under ``N_G(L)``-relabeling.

    The relabeling ``⊙_{eg} ↦ ⊙_{e,wgw⁻¹}`` is well-defined on operations only
    for ``w`` in the normalizer ``N_G(L)`` (otherwise it depends on the chosen
    coset representative). The orbits of this action are the **decision cells**:
    operations interchangeable by a symmetry that respects the kernel. The
    quotient ``N_G(L)/L`` plays the role of a Weyl group of the configuration;
    when ``L ◁ G`` it equals ``Op = G/L`` and the cells are exactly the
    conjugacy classes of that group.

    Returns:
        ``(ops, cells)`` where ``ops`` maps each distinct twin Cayley table to
        the group elements producing it, and ``cells`` is the list of orbits.
    """
    from arithmetics.symbolic.twin.classify import operation_space, structural_kernel
    from arithmetics.symbolic.twin.transport import transport_table

    L = structural_kernel(base, action)
    N = normalizer(action, L)

    def conj(w, a):
        return action.compose(action.compose(w, a), action.inverse(w))

    ops = operation_space(base, action)
    tables = list(ops.keys())
    parent = {t: t for t in tables}

    def find(t):
        while parent[t] != t:
            parent[t] = parent[parent[t]]
            t = parent[t]
        return t

    def union(s, t):
        rs, rt = find(s), find(t)
        if rs != rt:
            parent[rs] = rt

    for t in tables:
        g = ops[t][0]
        for w in N:
            union(t, transport_table(base, action, conj(w, g)))

    comps: Dict = {}
    for t in tables:
        comps.setdefault(find(t), []).append(t)
    return ops, list(comps.values())


def twin_decision(base, action, minimize: bool = True) -> dict:
    """Run the decision machinery on the twin operation space ``Op ≅ G/L``.

    ``Op`` is the coset space ``G/L`` (a homogeneous ``G``-set), of size
    ``[G:L]``; it is a *group* iff the structural kernel ``L`` is normal. The
    decision cells are the orbits under relabeling (:func:`operation_orbits`),
    which is always valid. When ``L ◁ G`` the report also includes the class
    equation of the group ``Op``.

    Args:
        base: a :class:`CayleyTable` base operation.
        action: a :class:`PermutationAction`.

    Returns:
        A report with the kernel/normality status, the number of decision
        cells, a representative twin table and order complexity per cell, and
        (when applicable) the class equation of ``Op``.
    """
    from arithmetics.symbolic.twin.classify import structural_kernel, order_complexity

    L = structural_kernel(base, action)
    G = FiniteGroup.from_permutation_action(action)
    normal = G.is_normal(L)
    N = normalizer(action, L)
    ops, comps = operation_orbits(base, action)

    cells = []
    for comp in comps:
        reps_g = [ops[t][0] for t in comp]
        costs = [order_complexity(base, action, g) for g in reps_g]
        rep_table = min(comp, key=lambda t: t.text())
        cells.append({
            "size": len(comp),
            "cost_min": min(costs),
            "cost_max": max(costs),
            "order_complexity": order_complexity(base, action, ops[rep_table][0]),
            "twin_table": rep_table.text(),
        })
    cells.sort(key=lambda c: c["cost_min"], reverse=not minimize)

    result = {
        "order_G": action.order,
        "order_L": len(L),
        "index_GL": action.order // len(L),
        "order_normalizer": len(N),
        "weyl_order": len(N) // len(L),  # |N_G(L)/L|
        "num_operations": len(ops),
        "L_normal": normal,
        "Op_is_group": normal,
        "num_decision_cells": len(cells),
        "reduction": f"{len(ops)} -> {len(cells)}",
        "cells": cells,
    }
    if normal:
        result["class_equation"] = class_equation(G.quotient(L))
    return result


# ---------------------------------------------------------------------------
# Compact Lie groups: the Weyl integration formula (SU(2))
# ---------------------------------------------------------------------------
def su2_weyl_density(theta: float) -> float:
    """Weyl density of conjugacy classes of ``SU(2)`` on ``θ ∈ [0, π]``.

    Push-forward of the Haar measure to the class angle: ``(2/π) sin²θ``.
    Integrates to 1 over ``[0, π]`` (the continuous class equation).
    """
    import math
    return (2.0 / math.pi) * math.sin(theta) ** 2


def su2_class_average(J: Callable) -> float:
    """Weyl integral of a class function ``J(θ)`` over ``SU(2)``.

    ``∫_0^π J(θ) · (2/π) sin²θ dθ`` — the Lie analogue of :func:`class_average`.
    """
    import mpmath
    return float(mpmath.quad(lambda t: J(t) * (2.0 / mpmath.pi) * mpmath.sin(t) ** 2,
                             [0, mpmath.pi]))


def su2_class_decision(J: Callable, minimize: bool = True,
                       n: int = 721) -> dict:
    """Decide over the conjugacy classes of ``SU(2)`` for a class cost ``J``.

    Scans the class angle ``θ ∈ [0, π]`` and returns the Weyl-averaged cost
    together with the optimal class (angle).
    """
    import math
    grid = [math.pi * i / (n - 1) for i in range(n)]
    values = [(t, J(t)) for t in grid]
    best = (min if minimize else max)(values, key=lambda tv: tv[1])
    return {
        "group": "SU(2)", "manifold": "S^3",
        "weyl_average": su2_class_average(J),
        "optimal_angle": best[0],
        "optimal_cost": best[1],
        "weyl_normalisation": su2_class_average(lambda t: 1.0),
    }
