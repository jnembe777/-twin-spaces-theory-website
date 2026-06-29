"""
Classification of twin operations (the machinery's analytical core).

For a finite :class:`~arithmetics.symbolic.twin.actions.PermutationAction`
acting on a base operation, this module computes:

* the **structural kernel** ``L = {g : ⊙_{eg} = ⊙_e}`` (Def. of the kernel);
* the **operation space** ``Op = {⊙_{eg}}`` and the classification
  ``Op ≅ G/L`` with ``|Op| = [G:L]`` (Fundamental Classification Theorem);
* the **counting formula** for *all* ``G``-invariant magmas,
  ``|M_G(E)| = ∏_O |Fix_E(Stab_G(O))|`` over orbits ``O`` of ``G`` on
  ``E × E`` (Fundamental Counting Formula);
* **order complexity** ``κ_ord(⊙_{eg}) = ord(gL)``.

These let us *discover* which twin spaces a (group, space) pair generates.
"""

from typing import Dict, List, Sequence, Tuple

from arithmetics.symbolic.twin.transport import CayleyTable, transport_table


__all__ = [
    "structural_kernel", "operation_space", "classify",
    "count_invariant_magmas", "order_complexity",
]


def structural_kernel(base: CayleyTable, action) -> List[Tuple[int, ...]]:
    """Return the kernel ``L``: group elements that fix the operation."""
    return [g for g in action.elements
            if transport_table(base, action, g) == base]


def operation_space(base: CayleyTable, action) -> Dict[CayleyTable, List]:
    """Map each distinct twin operation to the group elements producing it.

    The keys are the distinct transported tables; ``len`` of the result is
    ``|Op| = [G:L]``.
    """
    space: Dict[CayleyTable, List[Tuple[int, ...]]] = {}
    for g in action.elements:
        table = transport_table(base, action, g)
        space.setdefault(table, []).append(g)
    return space


def classify(base: CayleyTable, action) -> dict:
    """Summarise the discovery for one (group, base operation) pair."""
    kernel = structural_kernel(base, action)
    space = operation_space(base, action)
    order_g = action.order
    order_l = len(kernel)
    return {
        "group": action.name,
        "base_op": base.name,
        "size_E": action.size,
        "order_G": order_g,
        "order_L": order_l,
        "index_[G:L]": order_g // order_l if order_l else None,
        "num_twin_ops": len(space),
        "trivial": len(space) == 1,
        "invariant_magmas": count_invariant_magmas(action),
    }


def count_invariant_magmas(action) -> int:
    """Count all ``G``-invariant magmas on ``E`` via the orbit-product formula.

    ``|M_G(E)| = ∏_{O ∈ Orb_G(E×E)} |Fix_E(Stab_G(O))|``.
    """
    m = action.size
    G = action.elements
    seen = set()
    product = 1
    for i in range(m):
        for j in range(m):
            if (i, j) in seen:
                continue
            # orbit of (i, j) under the diagonal action
            orbit = {(g[i], g[j]) for g in G}
            seen |= orbit
            # stabiliser of the representative pair
            stab = [g for g in G if g[i] == i and g[j] == j]
            # E-points fixed by the whole stabiliser
            fixed = sum(1 for e in range(m) if all(g[e] == e for g in stab))
            product *= fixed
    return product


def order_complexity(base: CayleyTable, action, g: Sequence[int]) -> int:
    """Order complexity ``κ_ord(⊙_{eg}) = min{ k≥1 : ⊙_{eg}^{∘k} = ⊙_e }``.

    Equivalently the order of ``gL`` in ``G/L``.
    """
    g = tuple(g)
    gk = g
    for k in range(1, action.order + 1):
        if transport_table(base, action, gk) == base:
            return k
        gk = action.compose(g, gk)
    return action.order  # fallback (should not be reached for a finite group)
