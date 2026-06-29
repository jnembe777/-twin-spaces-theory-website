"""
Primary decomposition of the decision space for abelian groups.

For a finite *abelian* group ``G`` the structural kernel ``L`` is automatically
normal, so the operation space ``Op = G/L`` is an abelian group and decomposes
along the primary (Sylow-``p``) components:

.. math::

    G \\cong \\prod_p G_p, \\quad L = \\prod_p L_p\\ (L_p = L \\cap G_p),
    \\quad\\Longrightarrow\\quad
    Op = G/L \\cong \\prod_p G_p/L_p = \\prod_p Op_p .

This is the "Chinese Remainder Theorem for operations": every twin operation
factors uniquely into ``p``-primary parts, and a *separable* cost is optimised
component by component (search ``∏|Op_p|`` collapses to ``Σ|Op_p|``).

This module provides:

* :func:`primary_components`, :func:`primary_projection` -- the decomposition
  ``G ≅ ∏ G_p`` and the projections ``g ↦ (g_p)``;
* :func:`op_primary_components`, :func:`operation_factorization` -- the induced
  ``Op ≅ ∏ Op_p`` and the unique factorisation of operations;
* :func:`primary_decision` -- componentwise optimisation of a separable cost;
* :func:`complexity_classes`, :func:`verify_complexity_partition` -- the
  order-complexity partition ``|C_d| = φ(d) · m_d`` (the complexity-class
  theorem of the foundations volume).
"""

from typing import Callable, Dict, List

from arithmetics.symbolic.twin.decision import FiniteGroup, class_average  # noqa: F401

__all__ = [
    "prime_factorization", "euler_phi", "group_power",
    "primary_components", "primary_subgroup", "primary_projection",
    "kernel_primary", "op_primary_components", "operation_factorization",
    "verify_primary_decomposition", "primary_decision",
    "complexity_classes", "num_cyclic_subgroups", "verify_complexity_partition",
    "twin_primary_decomposition",
]


# ---------------------------------------------------------------------------
# Number theory helpers
# ---------------------------------------------------------------------------
def prime_factorization(n: int) -> Dict[int, int]:
    """Return the prime factorisation of ``n`` as ``{p: exponent}``."""
    factors: Dict[int, int] = {}
    d = 2
    while d * d <= n:
        while n % d == 0:
            factors[d] = factors.get(d, 0) + 1
            n //= d
        d += 1
    if n > 1:
        factors[n] = factors.get(n, 0) + 1
    return factors


def euler_phi(n: int) -> int:
    """Euler's totient ``φ(n)``."""
    result = n
    for p in prime_factorization(n):
        result -= result // p
    return result


def group_power(G: FiniteGroup, g, k: int):
    """Compute ``g^k`` in ``G`` by fast exponentiation."""
    result = G.identity
    base = g
    while k > 0:
        if k & 1:
            result = G.mul(result, base)
        base = G.mul(base, base)
        k >>= 1
    return result


# ---------------------------------------------------------------------------
# Primary decomposition of an abelian group
# ---------------------------------------------------------------------------
def _order_is_p_power(G: FiniteGroup, g, p: int) -> bool:
    o = G.element_order(g)
    while o % p == 0:
        o //= p
    return o == 1


def primary_components(G: FiniteGroup) -> Dict[int, List]:
    """Return the primary (Sylow-``p``) components ``{p: elements of G_p}``.

    Requires ``G`` abelian (where each ``G_p`` is the unique Sylow ``p``-group).
    """
    if not G.is_abelian():
        raise ValueError("primary decomposition requires an abelian group")
    comps: Dict[int, List] = {}
    for p in prime_factorization(G.order):
        comps[p] = [g for g in G.elements if _order_is_p_power(G, g, p)]
    return comps


def primary_subgroup(G: FiniteGroup, p: int) -> FiniteGroup:
    """The ``p``-primary subgroup ``G_p`` as a :class:`FiniteGroup`."""
    elems = [g for g in G.elements if _order_is_p_power(G, g, p)]
    return FiniteGroup(f"{G.name}_{p}", elems, G.mul, G.identity, G.inv)


def primary_projection(G: FiniteGroup, g) -> Dict[int, "object"]:
    """Project ``g`` onto its primary components: ``g ↦ {p: g_p}``.

    Uses the CRT exponents ``e_p ≡ 1 (mod p^{a_p}), ≡ 0 (mod q)``; then
    ``g_p = g^{e_p}`` and ``∏_p g_p = g``.
    """
    n = G.order
    proj: Dict[int, object] = {}
    for p, a in prime_factorization(n).items():
        pa = p ** a
        q = n // pa
        e = (pow(q % pa, -1, pa) * q) % n
        proj[p] = group_power(G, g, e)
    return proj


# ---------------------------------------------------------------------------
# Induced decomposition of the operation space Op = G/L
# ---------------------------------------------------------------------------
def kernel_primary(G: FiniteGroup, L: List) -> Dict[int, List]:
    """Compatible decomposition of the kernel ``L_p = L ∩ G_p`` (automatic)."""
    out: Dict[int, List] = {}
    for p in prime_factorization(G.order):
        out[p] = [x for x in L if _order_is_p_power(G, x, p)]
    return out


def op_primary_components(G: FiniteGroup, L: List) -> Dict[int, FiniteGroup]:
    """The primary components ``Op_p = G_p / L_p`` of ``Op = G/L``."""
    Lp = kernel_primary(G, L)
    out: Dict[int, FiniteGroup] = {}
    for p in prime_factorization(G.order):
        Gp = primary_subgroup(G, p)
        out[p] = Gp.quotient(Lp[p])
    return out


def operation_factorization(G: FiniteGroup, L: List, g) -> Dict[int, frozenset]:
    """Unique factorisation of the operation ``gL`` into ``p``-primary cosets.

    Returns ``{p: g_p L_p}`` where ``g_p L_p`` lives in ``Op_p = G_p/L_p``.
    """
    Lp = kernel_primary(G, L)
    proj = primary_projection(G, g)
    out: Dict[int, frozenset] = {}
    for p, gp in proj.items():
        out[p] = frozenset(G.mul(gp, n) for n in Lp[p])  # coset g_p L_p in G_p
    return out


def verify_primary_decomposition(G: FiniteGroup, L: List) -> dict:
    """Check ``G ≅ ∏ G_p``, ``L = ∏ L_p`` and ``|Op| = ∏ |Op_p|``."""
    comps = primary_components(G)
    Lp = kernel_primary(G, L)
    Op_p = op_primary_components(G, L)

    order_G_ok = G.order == _prod(len(v) for v in comps.values())
    order_L_ok = len(L) == _prod(len(v) for v in Lp.values())
    index = G.order // len(L)
    order_Op_ok = index == _prod(Q.order for Q in Op_p.values())

    # Reconstruction g = ∏ g_p for every element.
    recon_ok = True
    for g in G.elements:
        proj = primary_projection(G, g)
        prod = G.identity
        for gp in proj.values():
            prod = G.mul(prod, gp)
        if prod != g:
            recon_ok = False
            break

    return {
        "primes": sorted(comps),
        "orders_Gp": {p: len(v) for p, v in comps.items()},
        "orders_Lp": {p: len(v) for p, v in Lp.items()},
        "orders_Op_p": {p: Q.order for p, Q in Op_p.items()},
        "index_GL": index,
        "G_factors": order_G_ok,
        "L_factors": order_L_ok,
        "Op_factors": order_Op_ok,
        "reconstruction": recon_ok,
        "valid": order_G_ok and order_L_ok and order_Op_ok and recon_ok,
    }


def _prod(it) -> int:
    out = 1
    for x in it:
        out *= x
    return out


# ---------------------------------------------------------------------------
# Separable decision over the primary components
# ---------------------------------------------------------------------------
def primary_decision(G: FiniteGroup, L: List,
                     prime_costs: Dict[int, Callable],
                     minimize: bool = True) -> dict:
    """Optimise a separable cost ``J = Σ_p J_p`` componentwise over ``Op``.

    Args:
        prime_costs: ``{p: J_p}`` with ``J_p`` a cost on ``Op_p`` elements.
        minimize: minimise (else maximise) each component.

    Returns:
        The component optima, the combined optimum, and the search reduction
        ``∏|Op_p| -> Σ|Op_p|``.
    """
    Op_p = op_primary_components(G, L)
    pick = min if minimize else max
    components = {}
    combined_cost = 0.0
    full, reduced = 1, 0
    for p, Q in Op_p.items():
        J = prime_costs[p]
        best = pick(Q.elements, key=J)
        components[p] = {"optimum": best, "cost": J(best), "size": Q.order}
        combined_cost += J(best)
        full *= Q.order
        reduced += Q.order
    return {
        "components": components,
        "combined_cost": combined_cost,
        "search_full": full,
        "search_reduced": reduced,
        "reduction": f"{full} -> {reduced}",
    }


# ---------------------------------------------------------------------------
# Order-complexity partition:  |C_d| = φ(d) · m_d
# ---------------------------------------------------------------------------
def complexity_classes(G: FiniteGroup) -> Dict[int, int]:
    """Count elements by order: ``{d: |{g : ord(g) = d}|}``."""
    counts: Dict[int, int] = {}
    for g in G.elements:
        d = G.element_order(g)
        counts[d] = counts.get(d, 0) + 1
    return counts


def num_cyclic_subgroups(G: FiniteGroup, d: int) -> int:
    """Number of cyclic subgroups of order ``d`` in ``G``."""
    subgroups = set()
    for g in G.elements:
        if G.element_order(g) == d:
            subgroups.add(frozenset(group_power(G, g, k) for k in range(d)))
    return len(subgroups)


def verify_complexity_partition(G: FiniteGroup) -> dict:
    """Verify ``|C_d| = φ(d) · m_d`` and ``Σ_{d | n} |C_d| = |G|``."""
    counts = complexity_classes(G)
    checks = {}
    for d, cd in counts.items():
        md = num_cyclic_subgroups(G, d)
        checks[d] = {"|C_d|": cd, "phi(d)": euler_phi(d),
                     "m_d": md, "ok": cd == euler_phi(d) * md}
    total_ok = sum(counts.values()) == G.order
    formula_ok = all(c["ok"] for c in checks.values())
    return {"by_order": checks, "sum_equals_order": total_ok,
            "formula_holds": formula_ok, "valid": total_ok and formula_ok}


# ---------------------------------------------------------------------------
# Tie-in to a concrete twin action
# ---------------------------------------------------------------------------
def twin_primary_decomposition(base, action) -> dict:
    """Primary decomposition of the decision space of a twin action.

    Builds ``G`` from a (necessarily abelian) permutation ``action`` and the
    base operation, computes the structural kernel ``L``, and returns the
    verified factorisation ``Op = G/L ≅ ∏ Op_p`` together with a representative
    twin Cayley table for each operation of each primary component.
    """
    from arithmetics.symbolic.twin.classify import structural_kernel
    from arithmetics.symbolic.twin.transport import transport_table

    G = FiniteGroup.from_permutation_action(action)
    if not G.is_abelian():
        raise ValueError(f"{action.name} is not abelian; primary decomposition "
                         "of the decision space requires an abelian group")
    L = structural_kernel(base, action)
    info = verify_primary_decomposition(G, L)

    Op_p = op_primary_components(G, L)
    component_ops = {}
    for p, Q in Op_p.items():
        tables = []
        for coset in Q.elements:
            g = min(coset, key=repr)
            tables.append(transport_table(base, action, g).text())
        component_ops[p] = tables
    return {"decomposition": info, "component_operations": component_ops}
