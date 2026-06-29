#!/usr/bin/env python
"""
Twin-spaces generator demo (arithmetics.symbolic.twin).

Drives the twin-spaces machinery from Vol. 01 *Twin Spaces: Foundations*:
from a base space (E, ⊙_e), a group G acting on E, and the transport formula
    x ⊙_{eg} y = g⁻¹·((g·x) ⊙_e (g·y)),
it generates candidate groups and spaces and *discovers* the twin operations
that come out — symbolically (monogenic + Lie) and combinatorially (finite).

Run:
    python twin_demo.py
"""

from arithmetics.symbolic.twin import (
    BijectionAction, PermutationAction,
    twin_operation, twin_field, transport_table,
    candidate_base_operations,
    discover_symbolic, discover_finite,
    render_table, to_latex_table, save_results,
    Operation, twin_operation_so2, discover_lie,
)


def banner(title):
    print("\n" + "=" * 74)
    print(" " + title)
    print("=" * 74)


def main():
    banner("PRIMITIVE: transport  x ⊙_{eg} y = g⁻¹·((g·x) ⊙_e (g·y))")

    # --- The exponential hierarchy (monogenic G = ⟨exp⟩) ------------------
    print("\n## Exponential hierarchy  (base operation: +)")
    phi = BijectionAction.exponential()
    for n in (0, 1, -1, -2):
        print(f"   n = {n:>2}:   x ⊙ y  =  {twin_operation(phi, n, 'add').text()}")

    print("\n## Twin field at level -1  (φ = exp)")
    tf = twin_field(phi, -1)
    print(f"   x ⊕ y = {tf['oplus'].text()}      neutral_⊕ = {tf['zero'].text()}")
    print(f"   x ⊗ y = {tf['otimes'].text()}   neutral_⊗ = {tf['one'].text()}")

    # --- A finite transported Cayley table --------------------------------
    banner("FINITE TRANSPORT: C_3 on a non-standard magma")
    C3 = PermutationAction.cyclic(3)
    base = [b for b in candidate_base_operations(3) if b.name == "magma-ex3"][0]
    print("\nbase ⊙_e:\n" + base.text())
    print("\ntwin ⊙_{eσ}  (σ = (0 1 2)):\n" + transport_table(base, C3, (1, 2, 0)).text())

    # --- Discovery: symbolic ---------------------------------------------
    banner("DISCOVERY: symbolic spaces (monogenic ⟨φ⟩ and Lie groups)")
    sym = discover_symbolic()
    print(render_table(sym, ["family", "phi", "base", "twin_op", "trivial"]))

    # --- Discovery: finite ------------------------------------------------
    banner("DISCOVERY: finite spaces (candidate groups × candidate spaces)")
    fin = discover_finite(max_n=4)
    print(render_table(fin, ["group", "base_op", "order_G", "order_L",
                             "index_[G:L]", "num_twin_ops", "trivial",
                             "invariant_magmas"]))

    # --- Compact Lie groups ----------------------------------------------
    banner("COMPACT LIE GROUPS: linearity obstruction & quantum universality")
    print("\n## SO(2): complex multiplication transports to e^{iθ}(z·w)")
    res, theta = twin_operation_so2(Operation.complex_multiplication())
    print("   (x ⊙_θ y)_0 =", res[0])
    print("   (x ⊙_θ y)_1 =", res[1])
    lie = discover_lie(n_samples=400)
    print()
    print(render_table(lie, ["group", "manifold", "operation", "method",
                             "rigid", "kernel_trivial", "Op"]))

    # --- Export -----------------------------------------------------------
    banner("EXPORT")
    p_sym = save_results(sym, "discovery_symbolic")
    p_fin = save_results(fin, "discovery_finite")
    p_lie = save_results(lie, "discovery_lie")
    print("  symbolic ->", p_sym["json"])
    print("           ->", p_sym["csv"])
    print("  finite   ->", p_fin["json"])
    print("           ->", p_fin["csv"])
    print("  lie      ->", p_lie["json"])
    print("           ->", p_lie["csv"])

    print("\n## LaTeX table (finite discovery, first rows)")
    print(to_latex_table(
        fin[:6],
        ["group", "base_op", "index_[G:L]", "num_twin_ops", "trivial"],
        caption="Discovered twin operation spaces",
        label="tab:twin-discovery"))


if __name__ == "__main__":
    main()
